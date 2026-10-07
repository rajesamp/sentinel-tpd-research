"""Build the paper component index from exact preserved evidence, without scoring."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from manuscript.build_paper import bibliography

BASE = "d62ccf1707713b31829a1a480c54fb789ec75c15"
PIN = "5ce5d56e57a0acd092435fca5d89b78d0b39ee7b"


def evidence(path):
    if path.startswith("upstream:"):
        path = path.split(":", 1)[1]
        repo, revision = "rajesamp/sentinel-tpd", PIN
        raw = (ROOT / "vendor/sentinel-tpd" / path).read_bytes()
        entries = json.loads((ROOT / "vendor/manifest.json").read_text())["files"]
        expected = next(x["sha256"] for x in entries if x["path"] == path)
    else:
        repo, revision = "rajesamp/sentinel-tpd-research", BASE
        raw = (ROOT / path).read_bytes()
        saved = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT,
                               check=True, stdout=subprocess.PIPE).stdout
        expected = hashlib.sha256(saved).hexdigest()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError(f"Evidence no longer matches declared immutable revision: {path}")
    return {"repository": repo, "revision": revision, "path": path, "sha256": digest}


def main():
    materials = []
    def add(identifier, kind, status, paths, label=None, title=None, level=None):
        item = {"id": identifier, "kind": kind, "status": status,
                "evidence": [evidence(p) for p in paths]}
        if label:
            item["label"] = label
        if title:
            item["title"] = title
        if level:
            item["level"] = level
        materials.append(item)

    v = ["upstream:sentinel_tpd/scanner.py", "upstream:sentinel_tpd/signals.py",
         "upstream:sentinel_tpd/registry.py", "upstream:sentinel_tpd/audit.py"]
    raw = [f"results/{run}/{name}" for run in ("frozen-001", "frozen-002")
           for name in ("records.jsonl", "summary.json", "completion.json")]
    figures = {
        "fig:architecture": ("implemented", v + ["manuscript/paper-body.tex.in"]),
        "fig:decision": ("implemented", v[:3] + ["manuscript/paper-body.tex.in"]),
        "fig:cycle": ("implemented", v[2:] + ["manuscript/paper-body.tex.in"]),
        "fig:poisoning": ("measured", raw + ["evaluation/report.py", "research/measurement-protocol.md"]),
        "fig:shadowing": ("measured", raw + ["evaluation/report.py", "research/measurement-protocol.md"]),
    }
    tables = {
        "tab:rules": ("implemented", v[:2]),
        "tab:architecture": ("implemented", v + ["research/original-coverage.md"]),
        "tab:fields": ("implemented", [v[0], v[2], "data/lifecycle.json", "research/measurement-protocol.md"]),
        "tab:metrics": ("context", ["research/original-coverage.md", "research/measurement-protocol.md", "evaluation/report.py"]),
        "tab:unique": ("measured", raw + ["data/corpus.json", "data/source-manifest.json", "research/corpus-provenance.md"]),
        "tab:workloads": ("measured", raw + ["evaluation/run.py", "research/measurement-protocol.md"]),
        "tab:lifecycle": ("measured", raw + ["data/lifecycle.json", "evaluation/methods.py"]),
        "tab:cost": ("measured", raw + ["evaluation/run.py", "results/frozen-001/metadata.json", "results/frozen-002/metadata.json"]),
        "tab:patterns": ("context", ["research/original-coverage.md", "data/source-manifest.json", "data/corpus.json", "research/corpus-provenance.md"]),
        "tab:adjacent": ("context", ["manuscript/references.bib", "research/reference-audit.md", "research/sources.json", "research/original-coverage.md"]),
    }
    for kind, mapping in (("figure", figures), ("table", tables)):
        for number, (label, (status, paths)) in enumerate(mapping.items(), 1):
            add(f"{kind}.{number}", kind, status, paths, label=label)
    proposals = ["eq:proposal-metadata", "eq:proposal-poison",
                 "eq:proposal-shadow", "eq:proposal-combined"]
    for number in range(1, 12):
        label = proposals[number - 8] if number >= 8 else None
        if number >= 8:
            status, paths = "proposal", ["research/original-coverage.md", "manuscript/paper-body.tex.in"]
        elif number <= 4:
            status, paths = "implemented", v[:3] + ["manuscript/paper-body.tex.in"]
        else:
            status, paths = "context", ["evaluation/report.py", "research/measurement-protocol.md", "manuscript/paper-body.tex.in"]
        add(f"manuscript.equation.{number}", "equation", status, paths, label=label)
    body = (ROOT / "manuscript/paper.tex").read_text().split("\\begin{document}", 1)[1]
    sections = re.findall(r"\\(section|subsection)\*?\{([^}]+)\}", body)
    parent = ""
    for number, (level, title) in enumerate(sections, 1):
        if level == "section":
            parent = title
        if "Unimplemented Proposal" in parent:
            status, paths = "proposal", ["research/original-coverage.md"]
        elif parent.startswith("Original Pattern"):
            status, paths = "context", ["research/original-coverage.md", "data/source-manifest.json"]
        elif any(term in parent for term in ("Approaches", "Adjacent", "Threat Landscape")):
            status, paths = "context", ["manuscript/references.bib", "research/reference-audit.md", "research/sources.json"]
        elif "Architecture" in parent:
            status, paths = "implemented", v + ["manuscript/paper-body.tex.in"]
        elif "Acknowledgments" in parent:
            status, paths = "context", ["manuscript/paper-body.tex.in", "submission/claims-ledger.md"]
        else:
            status, paths = "measured", raw + ["research/measurement-protocol.md", "manuscript/paper-body.tex.in"]
        add(f"section.{number}", "section", status, paths, title=title, level=level)
    studies = [
        ("inputs", "47 source + 70 authored templates; projection and licensing boundaries",
         ["data/corpus.json", "data/source-manifest.json", "data/fetch_source.py", "data/build_challenges.py", "research/corpus-provenance.md", "research/corpus-acquisition.json"]),
        ("lifecycle", "15 lifecycle traces", ["data/lifecycle.json", "evaluation/methods.py"] + raw),
        ("sessions", "Two measured process sessions; five workload sizes",
         ["research/measurement-protocol.md", "evaluation/run.py", "results/frozen-001/metadata.json", "results/frozen-002/metadata.json"] + raw),
        ("original", "Original questions preserved; old numerical claims unverified", ["research/original-coverage.md"]),
        ("reproduction", "Executable evaluation, acquisition, tests and expected outcomes",
         ["reproduce.py", "data/expected-outcomes.json", "tests/test_evaluation.py", "upstream:tests/test_sentinel_tpd.py", "data/fetch_source.py"]),
    ]
    for key, title, paths in studies:
        add("study." + key, "study", "context" if key == "original" else "measured", paths, title=title)
    references = []
    for key, item in bibliography(ROOT / "manuscript/references.bib").items():
        if not item.get("url"):
            raise ValueError("Reference lacks primary URL: " + key)
        references.append({"key": key, "primary_url": item["url"],
                           "bibliography_path": "manuscript/references.bib",
                           "audit_path": "research/reference-audit.md"})
    manifest = {
        "schema_version": 1, "paper_revision_base": BASE,
        "implementation_repository": "rajesamp/sentinel-tpd", "evaluated_revision": PIN,
        "verified_local_date": "2026-10-07",
        "scope": "Paper component-to-public-evidence traceability; not independent semantic validation. Evidence links use immutable original study revisions. The corrected author block and index are a patch release.",
        "materials": materials, "references": references,
        "limits": ["External source payloads are excluded; verified acquisition pins are public.",
                   "The original uploaded PDF is not redistributed; its pattern/numerical/reference crosswalk is public.",
                   "Weighted equations are unimplemented proposals.",
                   "Citing third-party work does not implement or reproduce its algorithm."],
    }
    (ROOT / "research/paper-evidence-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"materials": len(materials), "figures": len(figures),
                      "tables": len(tables), "equation_rows": 11,
                      "sections": len(sections), "references": len(references)}))


if __name__ == "__main__":
    main()
