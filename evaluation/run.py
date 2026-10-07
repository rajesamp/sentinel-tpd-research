"""Reproducible offline Sentinel-TPD assay; no external tools are executed."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gc
from pathlib import Path
import random
import sys
import time
import tracemalloc
import traceback

from evaluation.common import (ROOT, canonical, code_hashes, environment, load_json,
                               object_sha, relative_path, sha, verify_vendor, write_json)
from evaluation.methods import Arm, METHODS, native_allowed

WORKLOADS = (100, 150, 200, 250, 300)
KINDS = ("poisoning", "shadowing", "benign")
LINEAGE = ("source_path", "source_id", "source_case_id", "source_record_sha256",
           "source_file", "source_commit", "source_index", "pair_id", "variant", "surface",
           "authored_context_note",
           "source_injection_point", "projection", "projection_notes", "authored_context",
           "native_metadata_applicable", "policy_reference")


def validate_corpus(corpus):
    if type(corpus) is not dict or type(corpus.get("schema_version")) is not int or corpus["schema_version"] != 1:
        raise ValueError("corpus requires schema_version 1")
    if type(corpus.get("cases")) is not list or not corpus["cases"]:
        raise ValueError("corpus requires nonempty cases")
    seen = set()
    for case in corpus["cases"]:
        if not {"case_id", "family", "label", "tool", "kind", "split"} <= case.keys():
            raise ValueError("incomplete corpus case")
        if case["case_id"] in seen or type(case["case_id"]) is not str or not case["case_id"]:
            raise ValueError("invalid or duplicate case ID")
        seen.add(case["case_id"])
        if case["label"] not in {"attack", "benign"} or case["kind"] not in KINDS:
            raise ValueError("invalid case label or kind")
        if (case["label"] == "benign") != (case["kind"] == "benign"):
            raise ValueError("label/kind conflict")
        if case["split"] not in {"source", "challenge"} or type(case["tool"]) is not dict:
            raise ValueError("invalid case split/tool")
        if type(case["tool"].get("name")) is not str:
            raise ValueError("fixture needs a tool name")
        canonical(case)


def validate_lifecycle(lifecycle):
    if lifecycle.get("schema_version") != 1 or type(lifecycle.get("cases")) is not list:
        raise ValueError("lifecycle requires schema_version 1 cases")
    seen = set()
    for case in lifecycle["cases"]:
        if not {"case_id", "family", "initial_tool", "steps"} <= case.keys() or case["case_id"] in seen:
            raise ValueError("invalid or duplicate lifecycle case")
        seen.add(case["case_id"])
        for step in case["steps"]:
            if step["action"] not in {"register", "refresh", "invoke"}:
                raise ValueError("unknown lifecycle step")
            if step["action"] == "refresh":
                if type(step.get("tools")) is not list:
                    raise ValueError("refresh requires tools")
            elif type(step.get("tool")) is not dict:
                raise ValueError("step requires tool")
            if step["action"] == "invoke" and type(step.get("expected_allowed")) is not bool:
                raise ValueError("invoke requires explicit policy reference")
        canonical(case)


def case_identity(case):
    result = {k: case[k] for k in ("case_id", "family", "label", "kind", "split")}
    result.update({k: case[k] for k in LINEAGE if k in case})
    result.update(case_sha256=object_sha(case), tool_sha256=object_sha(case["tool"]))
    result["has_reference_tools"] = bool(case.get("reference_tools"))
    result["has_host_context"] = bool(case.get("host_context"))
    return result


def make_workloads(corpus, sizes=WORKLOADS):
    output = []
    for kind in KINDS:
        cases = sorted((c for c in corpus["cases"] if c["split"] == "source" and c["kind"] == kind),
                       key=lambda c: c["case_id"])
        if not cases:
            raise ValueError("source workloads require source fixtures for " + kind)
        for size in sizes:
            if type(size) is not int or size <= 0:
                raise ValueError("workload sizes must be positive integers")
            ids = [cases[i % len(cases)]["case_id"] for i in range(size)]
            output.append({"kind": kind, "size": size, "case_ids": ids,
                           "unique_case_ids": sorted(set(ids)), "template_counts": dict(Counter(ids)),
                           "construction": "sorted case-ID round-robin within source kind; repeated templates"})
    return output


def _error(exc):
    # No fixture values or external excerpts are included in failure logs.
    return {"type": type(exc).__name__, "message": str(exc),
            "traceback": traceback.format_exc().replace(str(ROOT), "<package>")}


def invoke(arm, tool, *, sink=None):
    receipts = []
    def default_sink(receipt):
        receipts.append(receipt)
    writer = default_sink if sink is None else lambda receipt: (sink(receipt), receipts.append(receipt))
    started = time.perf_counter_ns()
    native = arm.invoke_native(tool)
    decided = time.perf_counter_ns()
    if native_allowed(native):
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                   "params": {"name": tool["name"], "arguments": {}}}
        writer({"request_utf8": canonical(request).decode("utf-8"),
                "tool_sha256": object_sha(tool), "sink": "inert_local_append"})
    finished = time.perf_counter_ns()
    decision = arm.invocation_record(native, tool)
    return {"decision": decision, "receipts": receipts, "decision_ns": decided - started,
            "decision_to_local_sink_ns": finished - started}


def evaluate_case(case, method):
    result = {"record_type": "unique_case", **case_identity(case), "method": method,
              "status": "completed", "registration": None, "receipts": [], "failure": None}
    try:
        tool = deepcopy(case["tool"])
        arm = Arm(method)
        start = time.perf_counter_ns()
        native = arm.register_native(tool)
        result["registration_ns"] = time.perf_counter_ns() - start
        result["registration"] = arm.registration_record(native, tool)
        result.update(invoke(arm, tool))
        result.update(arm.registration_signals())
        result["any_rule_hit"] |= bool(result["decision"]["findings"])
        result["scanner_denied"] |= bool(method == "rescan_each_call" and not result["decision"]["allowed"])
        result["state"] = arm.state(tool["name"])
    except Exception as exc:
        result.update(status="execution_error", failure=_error(exc))
    return result


def replay_workload(spec, cases):
    """Reuse an isolated native registry per template; avoid tool-name collisions."""
    arms = {}
    registrations = {}
    for case_id in spec["unique_case_ids"]:
        arm = Arm("sentinel_tpd")
        tool = deepcopy(cases[case_id]["tool"])
        native = arm.register_native(tool)
        registrations[case_id] = arm.registration_record(native, tool)
        arms[case_id] = arm
    for index, case_id in enumerate(spec["case_ids"]):
        case = cases[case_id]
        result = {"record_type": "workload_call", **case_identity(case), "method": "sentinel_tpd",
                  "workload_kind": spec["kind"], "workload_size": spec["size"], "call_index": index,
                  "registration": registrations[case_id], "status": "completed", "receipts": [], "failure": None}
        try:
            arm = arms[case_id]
            result.update(invoke(arm, case["tool"]))
            result.update(arm.registration_signals())
        except Exception as exc:
            result.update(status="execution_error", failure=_error(exc))
        yield result


def replay_lifecycle(case, method):
    result = {"record_type": "lifecycle", "case_id": case["case_id"], "family": case["family"],
              "case_sha256": object_sha(case), "method": method, "policy_reference": case.get("policy_reference"),
              "status": "completed", "steps": [], "failure": None}
    try:
        arm = Arm(method)
        initial = deepcopy(case["initial_tool"])
        native = arm.register_native(initial)
        result["initial_registration"] = arm.registration_record(native, initial)
        for index, step in enumerate(case["steps"]):
            row = {"step_index": index, "action": step["action"]}
            if step["action"] == "refresh":
                row["tools_sha256"] = object_sha(step["tools"])
                row["verdicts"] = arm.refresh_native(deepcopy(step["tools"]))
                name = initial["name"]
            else:
                tool = deepcopy(step["tool"])
                name = tool["name"]
                row["tool_sha256"] = object_sha(tool)
                if step["action"] == "register":
                    native = arm.register_native(tool)
                    row["verdict"] = arm.registration_record(native, tool)
                else:
                    row.update(invoke(arm, tool))
                    row["expected_allowed"] = step["expected_allowed"]
                    row["policy_satisfied"] = bool(row["receipts"]) == step["expected_allowed"]
            row["state"] = arm.state(name)
            result["steps"].append(row)
    except Exception as exc:
        result.update(status="execution_error", failure=_error(exc))
    return result


def _benchmark_setup(method, tool):
    arm = Arm(method)
    native = arm.register_native(tool)
    if native is not None and not native.allowed:
        raise ValueError("performance fixture is not admitted")
    request = canonical({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                         "params": {"name": tool["name"], "arguments": {}}})
    receipts = []
    def workload(size):
        for _ in range(size):
            decision = arm.invoke_native(tool)
            if native_allowed(decision):
                receipts.append({"request_bytes": request})
    return arm, receipts, workload


def benchmark(case, *, sizes, warmups, repeats, seed, emit):
    rng = random.Random(seed)
    for size in sizes:
        for pair_index in range(-warmups, repeats):
            for measurement in ("time", "allocation"):
                order = ["allow_all", "sentinel_tpd"]
                rng.shuffle(order)
                for order_index, method in enumerate(order):
                    row = {"record_type": "performance", "measurement": measurement,
                           "phase": "warmup" if pair_index < 0 else "measured", "pair_index": pair_index,
                           "within_process_pair": True, "workload_size": size, "method": method,
                           "method_order": order, "order_index": order_index,
                           "case_id": case["case_id"], "tool_sha256": object_sha(case["tool"]),
                           "status": "completed", "failure": None}
                    try:
                        arm, receipts, action = _benchmark_setup(method, deepcopy(case["tool"]))
                        gc.collect()
                        if measurement == "time":
                            start = time.perf_counter_ns()
                            action(size)
                            row["elapsed_ns"] = time.perf_counter_ns() - start
                            row["ns_per_call"] = row["elapsed_ns"] / size
                        else:
                            if tracemalloc.is_tracing():
                                raise RuntimeError("allocation measurement requires tracing initially disabled")
                            tracemalloc.start(1)
                            baseline, _ = tracemalloc.get_traced_memory()
                            tracemalloc.reset_peak()
                            try:
                                action(size)
                                current, peak = tracemalloc.get_traced_memory()
                            finally:
                                tracemalloc.stop()
                            row.update(initial_traced_bytes=baseline, final_traced_bytes=current,
                                       peak_traced_bytes=peak, incremental_peak_bytes=peak - baseline,
                                       net_traced_bytes=current - baseline,
                                       measurement_api="tracemalloc; traceback_frames=1; not RSS")
                        row["receipt_count"] = len(receipts)
                        row["native_audit_entries"] = len(arm.registry.audit) if arm.registry else 0
                        if len(receipts) != size:
                            raise RuntimeError("performance workload did not enqueue every valid call")
                    except Exception as exc:
                        row.update(status="execution_error", failure=_error(exc))
                        emit(row)
                        raise
                    emit(row)


def run_evaluation(output, corpus_path, *, lifecycle_path=None, label="development", seed=20261006,
                   sizes=WORKLOADS, warmups=10, repeats=50, workload_replay=True, performance=True,
                   benchmark_case_id=None, process_session=None):
    if sys.version_info < (3, 11):
        raise RuntimeError("the pinned package declares Python >=3.11")
    pinned = verify_vendor()
    if warmups < 0 or repeats < 1 or not sizes or len(set(sizes)) != len(sizes):
        raise ValueError("invalid timing repetition/workload configuration")
    corpus_path = Path(corpus_path)
    corpus = load_json(corpus_path)
    validate_corpus(corpus)
    lifecycle = {"schema_version": 1, "cases": []} if lifecycle_path is None else load_json(Path(lifecycle_path))
    validate_lifecycle(lifecycle)
    workloads = make_workloads(corpus, sizes) if workload_replay else []
    cases = {c["case_id"]: c for c in corpus["cases"]}
    if performance:
        if benchmark_case_id is None:
            candidates = sorted(c["case_id"] for c in cases.values() if c["label"] == "benign" and c["split"] == "source")
            if not candidates:
                raise ValueError("performance requires an explicit benign fixture or a source benign fixture")
            benchmark_case_id = candidates[0]
        if benchmark_case_id not in cases or cases[benchmark_case_id]["label"] != "benign":
            raise ValueError("performance fixture must have a benign label")
        _benchmark_setup("sentinel_tpd", cases[benchmark_case_id]["tool"])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    source_map = code_hashes()
    env = environment()
    inputs = {"corpus": {"path": relative_path(corpus_path), "file_sha256": sha(corpus_path.read_bytes()),
                         "content_sha256": object_sha(corpus)}}
    if lifecycle_path is not None:
        inputs["lifecycle"] = {"path": relative_path(Path(lifecycle_path)),
                               "file_sha256": sha(Path(lifecycle_path).read_bytes()), "content_sha256": object_sha(lifecycle)}
    fixture_manifest = {"schema_version": 1, "cases": [case_identity(c) for c in corpus["cases"]],
                        "lifecycle": [{"case_id": c["case_id"], "case_sha256": object_sha(c),
                                       "family": c["family"], "policy_reference": c.get("policy_reference"),
                                       "step_actions": [s["action"] for s in c["steps"]]} for c in lifecycle["cases"]],
                        "workloads": workloads}
    provenance = {"input_sha256": object_sha(inputs), "fixture_manifest_sha256": object_sha(fixture_manifest),
                  "code_sha256": object_sha(source_map), "environment_sha256": object_sha(env)}
    metadata = {"schema_version": 1, "run_id": output.name, "label": label,
                "started_at": datetime.now(timezone.utc).isoformat(), "inputs": inputs,
                "fixture_manifest_sha256": object_sha(fixture_manifest), "provenance": provenance,
                "code_files": source_map, "environment": env, "pinned_vendor": pinned,
                "methods": list(METHODS), "sizes": list(sizes), "seed": seed,
                "process_session": process_session or output.name,
                "performance": {"enabled": performance, "warmup_pairs": warmups, "measured_pairs": repeats,
                                "benchmark_case_id": benchmark_case_id, "pair_unit": "within one process",
                                "methods": ["allow_all", "sentinel_tpd"]},
                "label_scope": "source/authored fixture intent labels, not independently verified semantic ground truth",
                "verification": "visible fixtures; no blind holdout; repeated workloads add no unique templates"}
    write_json(output / "metadata.json", metadata)
    write_json(output / "fixture-manifest.json", fixture_manifest)
    counts = Counter()
    failures = 0
    fatal = None
    with (output / "records.jsonl").open("x", encoding="utf-8") as stream:
        def emit(row):
            nonlocal failures
            row = {"run_id": output.name, "process_session": metadata["process_session"],
                   "provenance": provenance, **row}
            stream.write(canonical(row).decode("utf-8") + "\n")
            stream.flush()
            counts[row["record_type"]] += 1
            failures += row["status"] != "completed"
        try:
            for case in corpus["cases"]:
                for method in METHODS:
                    emit(evaluate_case(case, method))
            for spec in workloads:
                for row in replay_workload(spec, cases):
                    emit(row)
            for case in lifecycle["cases"]:
                for method in METHODS:
                    emit(replay_lifecycle(case, method))
            if performance:
                benchmark(cases[benchmark_case_id], sizes=sizes, warmups=warmups, repeats=repeats,
                          seed=seed, emit=emit)
        except Exception as exc:
            fatal = _error(exc)
            emit({"record_type": "run_failure", "status": "execution_error", "failure": fatal})
    source_unchanged = code_hashes() == source_map
    input_unchanged = sha(corpus_path.read_bytes()) == inputs["corpus"]["file_sha256"]
    if lifecycle_path is not None:
        input_unchanged &= sha(Path(lifecycle_path).read_bytes()) == inputs["lifecycle"]["file_sha256"]
    completion = {"status": "completed" if not failures and not fatal and source_unchanged and input_unchanged else "failed",
                  "finished_at": datetime.now(timezone.utc).isoformat(), "record_counts": dict(counts),
                  "execution_errors": failures, "fatal_error": fatal, "source_unchanged": source_unchanged,
                  "input_unchanged": input_unchanged,
                  "output_sha256": {p.name: sha(p.read_bytes()) for p in output.iterdir() if p.is_file()}}
    write_json(output / "completion.json", completion)
    from evaluation.report import write_report
    write_report(output)
    if completion["status"] != "completed":
        raise RuntimeError("run failed; all evidence retained at " + str(output))
    return completion


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--lifecycle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", default="development")
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--warmups", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=50)
    parser.add_argument("--benchmark-case-id")
    parser.add_argument("--process-session")
    parser.add_argument("--no-workloads", action="store_true")
    parser.add_argument("--no-performance", action="store_true")
    args = parser.parse_args()
    run_evaluation(args.output, args.corpus, lifecycle_path=args.lifecycle, label=args.label,
                   seed=args.seed, warmups=args.warmups, repeats=args.repeats,
                   benchmark_case_id=args.benchmark_case_id, process_session=args.process_session,
                   workload_replay=not args.no_workloads, performance=not args.no_performance)
    print(str(args.output.resolve()))


if __name__ == "__main__":
    main()
