"""Negative controls for the offline paper traceability gate."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools/audit_traceability.py"
spec = importlib.util.spec_from_file_location("traceability", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.put("manuscript/paper.tex", r"""% A preamble label must not be counted: \label{ignored}
\begin{document}
\begin{figure}\caption{A}\label{fig:a}\end{figure}
\begin{table*}\caption{B}\label{tab:b}\end{table*}
\begin{equation}x=1\end{equation}
\begin{align}y=2\label{eq:y}\\z=3\end{align}
\cite{sentineltpd}\begin{thebibliography}{1}
\bibitem{sentineltpd}Source.\end{thebibliography}\end{document}""")
        self.put("manuscript/references.bib", "@misc{sentineltpd,\n url = {https://github.com/" + audit.IMPLEMENTATION + "/tree/" + audit.REVISION + "}\n}\n")
        self.put("research/reference-audit.md", "Source identity checked.")
        self.put("README.md", "Implementation https://github.com/" + audit.IMPLEMENTATION + "\nResearch https://github.com/" + audit.RESEARCH)
        self.put("evidence.txt", "unchanged evidence")
        self.put("evaluation/frozen.py", "# measured dependency\n")
        vendor_content = b"# pinned implementation\n"
        self.put("vendor/sentinel-tpd/native.py", vendor_content.decode())
        vendor = {"revision": audit.REVISION, "files": [{"path": "native.py", "sha256": audit.sha(vendor_content),
                  "git_blob_sha1": hashlib.sha1(b"blob " + str(len(vendor_content)).encode() + b"\0" + vendor_content).hexdigest()}]}
        self.put_json("vendor/manifest.json", vendor)
        self.put("data/input.json", "{\"fixture\":1}\n")
        for path in ("data/corpus.json", "data/lifecycle.json", "data/source-manifest.json"):
            self.put_json(path, {"public_fixture": True})
        record = {"repository": audit.RESEARCH, "revision": audit.BASE, "path": "evidence.txt", "sha256": audit.sha(b"unchanged evidence")}
        self.manifest = {"schema_version": 1, "paper_revision_base": audit.BASE,
            "implementation_repository": audit.IMPLEMENTATION, "evaluated_revision": audit.REVISION,
            "materials": [{"id": "figure.a", "kind": "figure", "label": "fig:a", "status": "context", "evidence": [record]},
                          {"id": "table.b", "kind": "table", "label": "tab:b", "status": "measured", "evidence": [record]}],
            "references": [{"key": "sentineltpd", "primary_url": "https://github.com/" + audit.IMPLEMENTATION,
                            "bibliography_path": "manuscript/references.bib", "audit_path": "research/reference-audit.md"}]}
        for i, label in enumerate((None, "eq:y", None), 1):
            item = {"id": f"manuscript.equation.{i}", "kind": "equation", "status": "implemented", "evidence": [record]}
            if label:
                item["label"] = label
            self.manifest["materials"].append(item)
        for name in ("frozen-001", "frozen-002"):
            prefix = "results/" + name + "/"
            fixtures = {"cases": [1]}
            code = {"evaluation/frozen.py": audit.sha((self.root / "evaluation/frozen.py").read_bytes())}
            inputs = {"corpus": {"path": "data/input.json", "file_sha256": audit.sha((self.root / "data/input.json").read_bytes()), "content_sha256": audit.canonical_sha({"fixture": 1})}}
            inputs["excluded"] = {"path": "data/corpus-combined.local.json", "file_sha256": audit.sha(b"external"), "content_sha256": audit.canonical_sha({"external": True})}
            metadata = {"code_files": code, "inputs": inputs, "environment": {}, "pinned_vendor": {"revision": audit.REVISION, "manifest_sha256": audit.canonical_sha(vendor)},
                        "provenance": {"code_sha256": audit.canonical_sha(code), "input_sha256": audit.canonical_sha(inputs),
                                       "environment_sha256": audit.canonical_sha({}), "fixture_manifest_sha256": audit.canonical_sha(fixtures)}}
            self.put_json(prefix + "metadata.json", metadata)
            self.put_json(prefix + "fixture-manifest.json", fixtures)
            self.put(prefix + "records.jsonl", json.dumps({"record_type": "unique_case", "provenance": metadata["provenance"]}) + "\n")
            completion = {"status": "completed", "execution_errors": 0, "source_unchanged": True, "input_unchanged": True,
                          "record_counts": {"unique_case": 1}, "output_sha256": {p: audit.sha((self.root / prefix / p).read_bytes()) for p in ("metadata.json", "fixture-manifest.json", "records.jsonl")}}
            self.put_json(prefix + "completion.json", completion)
        anchors = ("data/corpus.json", "data/lifecycle.json", "data/source-manifest.json",
                   "results/frozen-001/completion.json", "results/frozen-002/completion.json")
        self.manifest["materials"].append({"id": "study.public-provenance", "kind": "study", "status": "measured",
            "evidence": [{"repository": audit.RESEARCH, "revision": audit.BASE, "path": path,
                          "sha256": audit.sha((self.root / path).read_bytes())} for path in anchors]})
        self.manifest_path = self.root / "research/paper-evidence-manifest.json"

    def put(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def put_json(self, path, content):
        self.put(path, json.dumps(content))

    def run_audit(self):
        self.put_json("research/paper-evidence-manifest.json", self.manifest)
        return audit.audit(self.root, self.manifest_path)

    def test_complete_inventory_and_frozen_dependencies(self):
        result = self.run_audit()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(len(result["inventory"]["equation"]), 3)
        self.assertEqual(result["inventory"]["figure"], ["fig:a"])
        self.assertEqual(len(result["frozen_runs"]), 2)
        self.assertFalse((self.root / "data/corpus-combined.local.json").exists())
        self.assertEqual(len(result["frozen_runs"][0]["excluded_inputs"]), 1)
        self.assertFalse(result["frozen_runs"][0]["excluded_inputs"][0]["verified"])

    def test_removed_figure_mapping_fails(self):
        self.manifest["materials"].pop(0)
        with self.assertRaisesRegex(audit.AuditError, "figure mapping coverage"):
            self.run_audit()

    def test_tampered_evidence_fails(self):
        self.put("evidence.txt", "modified")
        with self.assertRaisesRegex(audit.AuditError, "SHA-256 mismatch"):
            self.run_audit()

    def test_missing_bibliography_mapping_fails(self):
        self.manifest["references"] = []
        with self.assertRaisesRegex(audit.AuditError, "bibliography mapping coverage"):
            self.run_audit()

    def test_removed_unlabelled_equation_mapping_fails(self):
        self.manifest["materials"] = [m for m in self.manifest["materials"] if m["id"] != "manuscript.equation.3"]
        with self.assertRaisesRegex(audit.AuditError, "equation mapping coverage"):
            self.run_audit()

    def test_changed_frozen_dependency_fails(self):
        self.put("evaluation/frozen.py", "# tampered\n")
        with self.assertRaisesRegex(audit.AuditError, "SHA-256 mismatch: evaluation"):
            self.run_audit()

    def test_traversal_and_symlink_escape_fail(self):
        record = self.manifest["materials"][0]["evidence"][0]
        record["path"] = "../outside"
        with self.assertRaisesRegex(audit.AuditError, "unsafe evidence path"):
            self.run_audit()
        record["path"] = "escape"
        (self.root / "escape").symlink_to(SCRIPT)
        with self.assertRaisesRegex(audit.AuditError, "escapes repository"):
            self.run_audit()

    def test_duplicate_or_extra_mapping_fails(self):
        extra = deepcopy(self.manifest["materials"][0])
        extra["id"] = "figure.duplicate"
        self.manifest["materials"].append(extra)
        with self.assertRaisesRegex(audit.AuditError, "figure mapping coverage"):
            self.run_audit()

    def test_existing_audit_output_is_not_overwritten(self):
        self.run_audit()
        output = self.root / "audit.json"
        output.write_text("preserve me")
        with patch.object(audit, "ROOT", self.root):
            self.assertEqual(audit.main(["--manifest", str(self.manifest_path), "--output", str(output)]), 1)
        self.assertEqual(output.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
