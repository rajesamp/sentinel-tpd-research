"""Derive all descriptive tables from saved, checked raw evaluation records."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics

from evaluation.common import load_json, object_sha, sha, write_json


def fraction(n, d):
    return {"numerator": n, "denominator": d, "rate": n / d if d else None}


def confusion(rows, prediction):
    counts = {"true_positive": 0, "false_negative": 0, "false_positive": 0, "true_negative": 0}
    for row in rows:
        positive = bool(prediction(row))
        key = ("true_positive" if positive else "false_negative") if row["label"] == "attack" else (
               "false_positive" if positive else "true_negative")
        counts[key] += 1
    counts["evaluated"] = sum(counts.values())
    return counts


def assay_summary(rows):
    complete = [r for r in rows if r["status"] == "completed"]
    attacks = [r for r in complete if r["label"] == "attack"]
    benign = [r for r in complete if r["label"] == "benign"]
    detected = [r for r in attacks if r["any_rule_hit"]]
    blocked = lambda r: len(r["receipts"]) == 0
    return {"scheduled_records": len(rows), "evaluated_records": len(complete),
            "execution_errors": len(rows) - len(complete),
            "unique_templates": len({r["case_id"] for r in rows}),
            "actual_receipts": sum(len(r["receipts"]) for r in rows),
            "rule_signal_confusion": confusion(complete, lambda r: r["any_rule_hit"]),
            "receipt_prevention_confusion": confusion(complete, blocked),
            "attack_rule_detection": fraction(len(detected), len(attacks)),
            "attack_prevention": fraction(sum(blocked(r) for r in attacks), len(attacks)),
            "blocking_among_rule_hit_attacks": fraction(sum(blocked(r) for r in detected), len(detected)),
            "benign_completion": fraction(sum(not blocked(r) for r in benign), len(benign)),
            "benign_false_block": fraction(sum(blocked(r) for r in benign), len(benign)),
            "allowed_rule_warnings": sum(r["any_rule_hit"] and not blocked(r) for r in complete),
            "allowed_attack_rule_warnings": sum(r["any_rule_hit"] and not blocked(r) for r in attacks),
            "scanner_denials": sum(r["scanner_denied"] for r in complete),
            "returned_deny_with_receipt": sum(not r["decision"]["allowed"] and bool(r["receipts"]) for r in complete),
            "returned_allow_without_receipt": sum(r["decision"]["allowed"] and not r["receipts"] for r in complete)}


def distribution(values):
    if not values:
        return {"samples": 0, "mean": None, "p50": None, "p95": None, "min": None, "max": None}
    values = sorted(values)
    return {"samples": len(values), "mean": statistics.mean(values), "p50": statistics.median(values),
            "p95": values[math.ceil(0.95 * len(values)) - 1], "min": values[0], "max": values[-1]}


def build_summary(run_dir):
    run_dir = Path(run_dir)
    metadata = load_json(run_dir / "metadata.json")
    manifest = load_json(run_dir / "fixture-manifest.json")
    completion = load_json(run_dir / "completion.json")
    for name, expected in completion["output_sha256"].items():
        if sha((run_dir / name).read_bytes()) != expected:
            raise ValueError("raw artifact hash mismatch: " + name)
    for field, value in (("input_sha256", metadata["inputs"]), ("fixture_manifest_sha256", manifest),
                         ("code_sha256", metadata["code_files"]), ("environment_sha256", metadata["environment"])):
        if object_sha(value) != metadata["provenance"][field]:
            raise ValueError("underlying provenance mismatch: " + field)
    with (run_dir / "records.jsonl").open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    if dict(Counter(r["record_type"] for r in rows)) != completion["record_counts"]:
        raise ValueError("raw record counts disagree with completion")
    fixtures = {c["case_id"]: c for c in manifest["cases"]}
    lifecycle_cases = {c["case_id"]: c for c in manifest["lifecycle"]}
    workloads = {(w["kind"], w["size"]): w for w in manifest["workloads"]}
    seen = set()
    for row in rows:
        if row["provenance"] != metadata["provenance"] or row["run_id"] != metadata["run_id"]:
            raise ValueError("record provenance mismatch")
        kind = row["record_type"]
        if kind in {"unique_case", "workload_call"}:
            fixture = fixtures.get(row["case_id"])
            if fixture is None or any(row[k] != fixture[k] for k in ("case_sha256", "tool_sha256", "label", "split", "kind", "family")):
                raise ValueError("record fixture identity mismatch")
        if kind == "unique_case":
            key = kind, row["case_id"], row["method"]
        elif kind == "workload_call":
            spec = workloads[row["workload_kind"], row["workload_size"]]
            if spec["case_ids"][row["call_index"]] != row["case_id"] or row["method"] != "sentinel_tpd":
                raise ValueError("workload replication order mismatch")
            key = kind, row["workload_kind"], row["workload_size"], row["call_index"]
        elif kind == "lifecycle":
            fixture = lifecycle_cases[row["case_id"]]
            if row["case_sha256"] != fixture["case_sha256"] or row["policy_reference"] != fixture["policy_reference"]:
                raise ValueError("lifecycle identity mismatch")
            if row["status"] == "completed" and [s["action"] for s in row["steps"]] != fixture["step_actions"]:
                raise ValueError("lifecycle step coverage mismatch")
            key = kind, row["case_id"], row["method"]
        elif kind == "performance":
            key = kind, row["measurement"], row["workload_size"], row["pair_index"], row["method"]
            if (row["case_id"] != metadata["performance"]["benchmark_case_id"]
                    or row["tool_sha256"] != fixtures[row["case_id"]]["tool_sha256"]
                    or row["phase"] != ("warmup" if row["pair_index"] < 0 else "measured")):
                raise ValueError("performance fixture/phase mismatch")
            if row["status"] == "completed" and row["receipt_count"] != row["workload_size"]:
                raise ValueError("performance sample contains missing receipts")
        elif kind == "run_failure":
            continue
        else:
            raise ValueError("unknown raw record type")
        if key in seen:
            raise ValueError("duplicate raw record")
        seen.add(key)
    expected_keys = {("unique_case", c, m) for c in fixtures for m in metadata["methods"]}
    expected_keys |= {("lifecycle", c, m) for c in lifecycle_cases for m in metadata["methods"]}
    expected_keys |= {("workload_call", w["kind"], w["size"], i) for w in manifest["workloads"] for i in range(w["size"])}
    if metadata["performance"]["enabled"]:
        expected_keys |= {("performance", measurement, size, i, method)
                         for measurement in ("time", "allocation") for size in metadata["sizes"]
                         for i in range(-metadata["performance"]["warmup_pairs"], metadata["performance"]["measured_pairs"])
                         for method in metadata["performance"]["methods"]}
    if not seen <= expected_keys or (completion["status"] == "completed" and seen != expected_keys):
        raise ValueError("record coverage differs from frozen manifest")
    unique = [r for r in rows if r["record_type"] == "unique_case"]
    by_split = {split: {method: assay_summary([r for r in unique if r["split"] == split and r["method"] == method])
                       for method in metadata["methods"]} for split in sorted({r["split"] for r in unique})}
    by_family = {split + ":" + family:
                 {method: assay_summary([r for r in unique if r["split"] == split
                                          and r["family"] == family and r["method"] == method])
                  for method in metadata["methods"]}
                 for split, family in sorted({(r["split"], r["family"]) for r in unique})}
    native_subset = {method: assay_summary([r for r in unique if r["split"] == "source" and r["method"] == method
                                          and r.get("native_metadata_applicable", True)]) for method in metadata["methods"]}
    workload_results = []
    for spec in manifest["workloads"]:
        selected = [r for r in rows if r["record_type"] == "workload_call"
                    and (r["workload_kind"], r["workload_size"]) == (spec["kind"], spec["size"])]
        workload_results.append({"kind": spec["kind"], "size": spec["size"],
                                 "unique_case_ids": spec["unique_case_ids"], "template_counts": spec["template_counts"],
                                 "outcomes": assay_summary(selected),
                                 "local_decision_ns": distribution([r["decision_ns"] for r in selected if r["status"] == "completed"]),
                                 "local_decision_and_sink_ns": distribution([r["decision_to_local_sink_ns"] for r in selected if r["status"] == "completed"])})
    performance = {}
    measured = [r for r in rows if r["record_type"] == "performance" and r["phase"] == "measured" and r["status"] == "completed"]
    for size in metadata["sizes"]:
        selected = [r for r in measured if r["workload_size"] == size]
        if not selected:
            continue
        group = {}
        for method in metadata["performance"]["methods"]:
            times = [r for r in selected if r["method"] == method and r["measurement"] == "time"]
            memory = [r for r in selected if r["method"] == method and r["measurement"] == "allocation"]
            group[method] = {"batch_elapsed_ns": distribution([r["elapsed_ns"] for r in times]),
                             "batch_ns_per_call": distribution([r["ns_per_call"] for r in times]),
                             "incremental_peak_python_bytes": distribution([r["incremental_peak_bytes"] for r in memory]),
                             "absolute_traced_peak_bytes": distribution([r["peak_traced_bytes"] for r in memory]),
                             "time_pairs": len(times), "allocation_pairs": len(memory)}
        paired_time = []
        paired_memory = []
        lookup = {(r["measurement"], r["pair_index"], r["method"]): r for r in selected}
        for i in range(metadata["performance"]["measured_pairs"]):
            a = lookup.get(("time", i, "allow_all"))
            b = lookup.get(("time", i, "sentinel_tpd"))
            if a and b:
                paired_time.append({"pair_index": i, "incremental_ns_per_call": b["ns_per_call"] - a["ns_per_call"],
                                    "overhead_percent": (b["elapsed_ns"] - a["elapsed_ns"]) / a["elapsed_ns"] * 100})
            a = lookup.get(("allocation", i, "allow_all"))
            b = lookup.get(("allocation", i, "sentinel_tpd"))
            if a and b:
                paired_memory.append({"pair_index": i, "incremental_peak_difference_bytes": b["incremental_peak_bytes"] - a["incremental_peak_bytes"]})
        group["paired_time_increment_ns_per_call"] = distribution([r["incremental_ns_per_call"] for r in paired_time])
        group["paired_time_overhead_percent"] = distribution([r["overhead_percent"] for r in paired_time])
        group["paired_peak_allocation_difference_bytes"] = distribution([r["incremental_peak_difference_bytes"] for r in paired_memory])
        group["paired_differences"] = {"time": paired_time, "allocation": paired_memory}
        performance[str(size)] = group
    lifecycle_results = [{"case_id": r["case_id"], "family": r["family"], "method": r["method"],
                          "policy_reference": r["policy_reference"], "status": r["status"],
                          "invocations": [{"step_index": s["step_index"], "expected_allowed": s["expected_allowed"],
                                           "decision_allowed": s["decision"]["allowed"], "receipt_count": len(s["receipts"]),
                                           "policy_satisfied": s["policy_satisfied"], "state": s["state"]}
                                          for s in r["steps"] if s["action"] == "invoke"]}
                         for r in rows if r["record_type"] == "lifecycle"]
    return {"schema_version": 1, "run_id": metadata["run_id"], "label": metadata["label"],
            "status": completion["status"], "provenance": metadata["provenance"],
            "process_session": metadata["process_session"], "record_counts": completion["record_counts"],
            "fixture_counts": dict(Counter(c["split"] + ":" + c["kind"] for c in manifest["cases"])),
            "by_split": by_split, "by_family": by_family, "source_native_metadata_subset": native_subset,
            "workloads": workload_results, "performance": performance, "lifecycle": lifecycle_results,
            "interpretation": ["Labels reflect authored fixture intent, not semantic ground truth or live exploit success.",
                               "Any-rule-hit detection, scanner denial and actual local receipt prevention are distinct.",
                               "Repeated source workloads add no unique templates and imply no learning trend.",
                               "The static assay submits one projected tool; supplied peer tools/host context are lineage, not model-selection tests.",
                               "Performance pairs are within one process; p95 is nearest-rank over batch-per-call averages.",
                               "tracemalloc measures incremental Python allocation peaks, not RSS or memory overhead percent.",
                               "Lifecycle expectations name a policy reference; failures are not automatically upstream vulnerabilities.",
                               "No external MCP tool, live agent, model selection or remote side effect is tested."]}


def markdown(summary):
    def f(value):
        n, d = value["numerator"], value["denominator"]
        return f"{n}/{d}" + (f" ({100*n/d:.1f}%)" if d else "")
    lines = ["# Sentinel-TPD offline evaluation", "", f"Run `{summary['run_id']}`; label `{summary['label']}`; status **{summary['status']}**.",
             "", "Fixture counts: " + ", ".join(f"{k}={v}" for k, v in summary["fixture_counts"].items()) + ".", ""]
    for split, methods in summary["by_split"].items():
        lines += [f"## Unique {split} templates", "",
                  "| Method | Rule-hit attacks | Prevented attacks | Blocked / rule-hit attacks | Benign completed | Allowed warnings | Errors |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
        for method, r in methods.items():
            lines.append(f"| {method} | {f(r['attack_rule_detection'])} | {f(r['attack_prevention'])} | "
                         f"{f(r['blocking_among_rule_hit_attacks'])} | {f(r['benign_completion'])} | {r['allowed_rule_warnings']} | {r['execution_errors']} |")
        lines.append("")
    lines += ["## Repeated source workloads: original Tables III–VI questions", "",
              "Detection below means any matched rule; prevented means no actual local sink receipt. Denominators are repeated calls, not new templates.", "",
              "| Kind | Calls | Unique IDs | Rule-hit attacks | Prevented attacks | Blocked / rule-hit attacks | Benign completed | Mean local decision µs | Min µs | Max µs |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in summary["workloads"]:
        r, d = row["outcomes"], row["local_decision_ns"]
        values = ["—" if d[k] is None else f"{d[k]/1000:.3f}" for k in ("mean", "min", "max")]
        lines.append(f"| {row['kind']} | {row['size']} | {len(row['unique_case_ids'])} | {f(r['attack_rule_detection'])} | "
                     f"{f(r['attack_prevention'])} | {f(r['blocking_among_rule_hit_attacks'])} | {f(r['benign_completion'])} | {' | '.join(values)} |")
    lines += ["", "## Paired benign cost: original Table VII question", "",
              "Cold registration is outside measurement. Native registry checking and audit logging remain inside. All values below describe one process session.", "",
              "| Calls | Method | Mean ns/call | p50 ns/call | p95 ns/call | Mean incremental Python peak bytes |",
              "|---|---|---:|---:|---:|---:|"]
    for size, group in summary["performance"].items():
        for method in ("allow_all", "sentinel_tpd"):
            r = group[method]
            d = r["batch_ns_per_call"]
            peak = r["incremental_peak_python_bytes"]["mean"]
            values = ["—" if d[k] is None else f"{d[k]:.3f}" for k in ("mean", "p50", "p95")]
            lines.append(f"| {size} | {method} | {' | '.join(values)} | {peak if peak is not None else '—'} |")
    lines += ["", "## Lifecycle observations", "",
              "Each expected result is scoped to its named policy; metadata coverage expectations may exceed the upstream fingerprint contract.", "",
              "| Case | Method | Policy reference | Actual receipts per invocation | Policy matched per invocation |",
              "|---|---|---|---|---|"]
    for row in summary["lifecycle"]:
        lines.append(f"| {row['case_id']} | {row['method']} | {str(row['policy_reference']).replace('|', '/')} | "
                     f"{','.join(str(s['receipt_count']) for s in row['invocations'])} | "
                     f"{','.join(str(s['policy_satisfied']) for s in row['invocations'])} |")
    lines += ["", "## Interpretation limits", ""] + ["- " + x for x in summary["interpretation"]]
    lines += ["", "Exact composition, confusion matrices, paired differences and all raw measurement samples are retained in JSON. No confidence intervals are inferred from dependent fixtures or within-process repetitions.", ""]
    return "\n".join(lines)


def latex(summary):
    esc = lambda s: str(s).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")
    lines = ["% Generated exclusively from saved raw records.", r"\begin{tabular}{llrrrr}",
             r"Split & Method & Hit attacks & Blocked attacks & Benign calls & Warnings \\", r"\hline"]
    for split, methods in summary["by_split"].items():
        for method, r in methods.items():
            f = lambda k: f"{r[k]['numerator']}/{r[k]['denominator']}"
            lines.append(f"{esc(split)} & {esc(method)} & {f('attack_rule_detection')} & {f('attack_prevention')} & "
                         f"{f('benign_completion')} & {r['allowed_rule_warnings']} " + r"\\")
    lines += [r"\end{tabular}", "", r"\begin{tabular}{lrrrrr}",
              r"Kind & Calls & Hit attacks & Blocked/hit & Benign calls & Mean decision ns \\", r"\hline"]
    for row in summary["workloads"]:
        r = row["outcomes"]
        f = lambda k: f"{r[k]['numerator']}/{r[k]['denominator']}"
        mean = row["local_decision_ns"]["mean"]
        lines.append(f"{esc(row['kind'])} & {row['size']} & {f('attack_rule_detection')} & "
                     f"{f('blocking_among_rule_hit_attacks')} & {f('benign_completion')} & "
                     + (f"{mean:.3f}" if mean is not None else "--") + " " + r"\\")
    lines += [r"\end{tabular}", "", r"\begin{tabular}{llrrr}",
              r"Calls & Method & Mean ns/call & p95 ns/call & Peak Python bytes \\", r"\hline"]
    for size, methods in summary["performance"].items():
        for method in ("allow_all", "sentinel_tpd"):
            r = methods[method]
            d = r["batch_ns_per_call"]
            if d["mean"] is not None:
                peak = r["incremental_peak_python_bytes"]["mean"]
                lines.append(f"{size} & {esc(method)} & {d['mean']:.3f} & {d['p95']:.3f} & "
                             + (f"{peak:.1f}" if peak is not None else "--") + " " + r"\\")
    return "\n".join(lines + [r"\end{tabular}", ""])


def write_report(run_dir, output=None):
    run_dir = Path(run_dir)
    output = run_dir if output is None else Path(output)
    paths = [output / p for p in ("summary.json", "summary.md", "tables.tex")]
    if any(p.exists() for p in paths):
        raise FileExistsError("report destination already contains output; choose a new directory")
    summary = build_summary(run_dir)
    output.mkdir(parents=True, exist_ok=True)
    write_json(paths[0], summary)
    for path, text in ((paths[1], markdown(summary)), (paths[2], latex(summary))):
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_report(args.run_dir, args.output)
    print(str(args.output.resolve()))


if __name__ == "__main__":
    main()
