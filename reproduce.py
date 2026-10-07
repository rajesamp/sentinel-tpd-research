#!/usr/bin/env python3
"""Reproduce the pinned study without installing packages or using a model.

Default: reconstruct 47 source cases plus 70 authored challenges. --offline:
authored challenges only. --cached-source: full corpus with no network requests.
Existing evidence is never overwritten. Timing is descriptive, not a match target.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def deterministic_view(summary):
    lifecycle = [{k: row[k] for k in ("case_id", "method", "policy_reference", "status", "invocations")}
                 for row in summary["lifecycle"]]
    return {"fixture_counts": summary["fixture_counts"], "by_split": summary["by_split"],
            "by_family": summary["by_family"],
            "workloads": [{k: row[k] for k in ("kind", "size", "unique_case_ids", "outcomes")}
                          for row in summary["workloads"]], "lifecycle": lifecycle}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--offline", action="store_true")
    modes.add_argument("--cached-source", action="store_true")
    parser.add_argument("--quick", action="store_true", help="omit performance measurement")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required by the pinned library")
    from evaluation.common import verify_vendor
    status = {"python": sys.version, "vendor": verify_vendor(), "commands": [],
              "input_mode": "authored-only" if args.offline else "source-and-authored",
              "network_permitted": not args.offline and not args.cached_source}
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "vendor/sentinel-tpd")
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    def run(command, name):
        with (output / name).open("x", encoding="utf-8") as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, text=True)
        safe = [Path(command[0]).name] + [x.replace(str(ROOT), "<package>")
                                        .replace(str(output), "<replay>") for x in command[1:]]
        status["commands"].append({"argv": safe, "log": name, "returncode": result.returncode})
        if result.returncode:
            raise RuntimeError("stage failed; inspect " + name)

    try:
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "authored-tests.log")
        run([sys.executable, "-m", "unittest", "vendor/sentinel-tpd/tests/test_sentinel_tpd.py", "-v"], "upstream-tests.log")
        corpus = ROOT / "data/corpus.json"
        if not args.offline:
            corpus = output / "corpus-combined.local.json"
            command = [sys.executable, "data/fetch_source.py", "--output", str(output / "corpus-source.local.json"),
                       "--combined-output", str(corpus)]
            if args.cached_source:
                command.append("--offline")
            run(command, "source-acquisition.log")
        command = [sys.executable, "-m", "evaluation.run", "--corpus", str(corpus),
                   "--lifecycle", "data/lifecycle.json", "--output", str(output / "assay"),
                   "--label", "reproduction-visible-fixtures", "--process-session", output.name]
        if args.quick or args.offline:
            command.append("--no-performance")
        if args.offline:
            command.append("--no-workloads")
        run(command, "assay.log")
        run([sys.executable, "-m", "evaluation.report", str(output / "assay"),
             "--output", str(output / "regenerated")], "report.log")
        for name in ("summary.json", "summary.md", "tables.tex"):
            if (output / "assay" / name).read_bytes() != (output / "regenerated" / name).read_bytes():
                raise RuntimeError("report regeneration mismatch: " + name)
        status["report_regeneration_identical"] = True
        reference = ROOT / "data/expected-outcomes.json"
        if reference.exists():
            expected = json.loads(reference.read_text())
            actual = deterministic_view(json.loads((output / "assay/summary.json").read_text()))
            if args.offline:
                expected = {**expected, "fixture_counts": {k: v for k, v in expected["fixture_counts"].items() if k.startswith("challenge:")},
                            "by_split": {"challenge": expected["by_split"]["challenge"]},
                            "by_family": {k: v for k, v in expected["by_family"].items() if k.startswith("challenge:")},
                            "workloads": []}
            if actual != expected:
                raise RuntimeError("deterministic outcomes differ from the saved reference")
            status["deterministic_outcomes_match_reference"] = True
        status["status"] = "completed"
    except Exception as exc:
        status.update(status="failed", error=str(exc))
        raise
    finally:
        with (output / "reproduction.json").open("x", encoding="utf-8") as stream:
            json.dump(status, stream, indent=2)
            stream.write("\n")
    print("Reproduction completed:", output)


if __name__ == "__main__":
    main()
