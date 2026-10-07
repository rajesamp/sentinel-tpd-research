#!/usr/bin/env python3
"""Fail-closed, offline paper/evidence audit. No GitHub availability claim is made."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = "rajesamp/sentinel-tpd-research"
IMPLEMENTATION = "rajesamp/sentinel-tpd"
REVISION = "5ce5d56e57a0acd092435fca5d89b78d0b39ee7b"
BASE = "d62ccf1707713b31829a1a480c54fb789ec75c15"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode())


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise AuditError("nonfinite JSON constant: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def safe_file(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative and "\x00" not in relative,
            "invalid evidence path")
    path = PurePosixPath(relative)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in relative.split("/")),
            "unsafe evidence path: " + relative)
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "evidence path escapes repository: " + relative)
    require(resolved.is_file(), "required file missing: " + relative)
    return resolved


def check_hash(path, expected, description):
    require(isinstance(expected, str) and HEX64.fullmatch(expected), "invalid SHA-256: " + description)
    require(sha(path.read_bytes()) == expected, "SHA-256 mismatch: " + description)


def strip_comments(source):
    # Percent is a comment only when preceded by an even number of backslashes.
    lines = []
    for line in source.splitlines():
        end = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            before = index
            while before and line[before - 1] == "\\":
                before -= 1
            if (index - before) % 2 == 0:
                end = index
                break
        lines.append(line[:end])
    return "\n".join(lines)


def paper_inventory(source):
    require(source.count(r"\begin{document}") == 1, "paper must have exactly one document body")
    body = strip_comments(source.split(r"\begin{document}", 1)[1])
    require(body.count(r"\end{document}") == 1, "paper document end missing or duplicated")
    body = body.split(r"\end{document}", 1)[0]
    all_labels = re.findall(r"\\label\{([^}]+)\}", body)
    require(len(all_labels) == len(set(all_labels)), "duplicate paper label")
    inventory = {"figure": [], "table": [], "equation": [], "section": []}
    inventory["section"] = [{"level": level, "title": title} for level, title in
                            re.findall(r"\\(section|subsection)\*?\{([^}]+)\}", body)]
    for kind in ("figure", "table"):
        pattern = r"\\begin\{(" + kind + r"\*?)\}(.*?)\\end\{\1\}"
        blocks = list(re.finditer(pattern, body, re.S))
        require(len(blocks) == len(re.findall(r"\\begin\{" + kind + r"\*?\}", body))
                == len(re.findall(r"\\end\{" + kind + r"\*?\}", body)), "unbalanced " + kind + " environments")
        for block in blocks:
            labels = re.findall(r"\\label\{([^}]+)\}", block[2])
            require(len(labels) == 1, kind + " must have exactly one label")
            inventory[kind].append(labels[0])
    environments = r"equation\*?|align\*?|gather\*?|multline\*?"
    matches = list(re.finditer(r"\\begin\{(" + environments + r")\}(.*?)\\end\{\1\}", body, re.S))
    require(len(matches) == len(re.findall(r"\\begin\{(?:" + environments + r")\}", body))
            == len(re.findall(r"\\end\{(?:" + environments + r")\}", body)), "unbalanced equation environment")
    # Fail rather than silently miss display forms unsupported by this bounded parser.
    require(not re.search(r"\\\[|\$\$|\\begin\{(?:eqnarray|alignat|flalign)", body), "unsupported display equation syntax")
    for block in matches:
        rows = re.split(r"\\\\(?:\[[^\]]*\])?", block[2]) if block[1].rstrip("*") in ("align", "gather") else [block[2]]
        for row in rows:
            if not row.strip():
                continue
            labels = re.findall(r"\\label\{([^}]+)\}", row)
            require(len(labels) <= 1, "multiple labels on an equation row")
            inventory["equation"].append({"id": "manuscript.equation." + str(len(inventory["equation"]) + 1),
                                          "label": labels[0] if labels else None})
    bibkeys = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", body)
    require(bibkeys and len(bibkeys) == len(set(bibkeys)), "missing or duplicate paper bibliography key")
    citations = {k.strip() for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", body) for k in group.split(",")}
    require(citations <= set(bibkeys), "paper has unresolved citation keys")
    inventory["bibliography"] = sorted(bibkeys)
    return inventory


def verify_frozen(root):
    vendor = load(safe_file(root, "vendor/manifest.json"))
    require(vendor["revision"] == REVISION and vendor["files"], "invalid vendor manifest")
    for record in vendor["files"]:
        path = safe_file(root / "vendor/sentinel-tpd", record["path"])
        check_hash(path, record["sha256"], "vendor/" + record["path"])
        content = path.read_bytes()
        git_blob = b"blob " + str(len(content)).encode("ascii") + b"\0" + content
        require(hashlib.sha1(git_blob).hexdigest() == record["git_blob_sha1"], "vendor Git-blob mismatch")
    runs = []
    for name in ("frozen-001", "frozen-002"):
        prefix = "results/" + name + "/"
        metadata = load(safe_file(root, prefix + "metadata.json"))
        completion = load(safe_file(root, prefix + "completion.json"))
        fixtures = load(safe_file(root, prefix + "fixture-manifest.json"))
        require(completion["status"] == "completed" and completion["execution_errors"] == 0
                and completion["source_unchanged"] is True and completion["input_unchanged"] is True,
                "frozen run is not a successful unchanged run: " + name)
        require({"metadata.json", "fixture-manifest.json", "records.jsonl"} <= set(completion["output_sha256"]),
                "frozen output digest coverage missing")
        for filename, expected in completion["output_sha256"].items():
            require("/" not in filename and "\\" not in filename, "unsafe frozen output filename")
            check_hash(safe_file(root, prefix + filename), expected, prefix + filename)
        require(metadata["code_files"], "empty frozen code map")
        for path, expected in metadata["code_files"].items():
            check_hash(safe_file(root, path), expected, path)
        for key, content in (("code_sha256", metadata["code_files"]), ("input_sha256", metadata["inputs"]),
                             ("environment_sha256", metadata["environment"]), ("fixture_manifest_sha256", fixtures)):
            require(canonical_sha(content) == metadata["provenance"][key], "frozen provenance mismatch: " + key)
        require(metadata["inputs"], "empty frozen inputs")
        verified_inputs, excluded_inputs = 0, []
        for record in metadata["inputs"].values():
            # External source payloads are deliberately absent from the public artifact.
            # Do not opportunistically verify a private cache and change the audit scope.
            if record["path"] == "data/corpus-combined.local.json":
                require(HEX64.fullmatch(record["file_sha256"]) and HEX64.fullmatch(record["content_sha256"]),
                        "invalid external input provenance digest")
                excluded_inputs.append({"path": record["path"], "expected_file_sha256": record["file_sha256"],
                                        "verified": False, "reason": "external source bytes require acquisition replay"})
                continue
            path = safe_file(root, record["path"])
            check_hash(path, record["file_sha256"], record["path"])
            require(canonical_sha(load(path)) == record["content_sha256"], "frozen input content mismatch")
            verified_inputs += 1
        require(metadata["pinned_vendor"]["revision"] == REVISION, "frozen vendor revision mismatch")
        require(metadata["pinned_vendor"]["manifest_sha256"] == canonical_sha(vendor), "frozen vendor manifest mismatch")
        records = [json.loads(line) for line in safe_file(root, prefix + "records.jsonl").read_text().splitlines() if line.strip()]
        require(dict(Counter(r["record_type"] for r in records)) == completion["record_counts"], "frozen raw record-count mismatch")
        require(all(r["provenance"] == metadata["provenance"] for r in records), "frozen raw provenance mismatch")
        runs.append({"run": name, "code_files_verified": len(metadata["code_files"]),
                     "public_inputs_verified": verified_inputs, "excluded_inputs": excluded_inputs,
                     "vendor_files_verified": len(vendor["files"]),
                     "raw_records_verified": len(records),
                     "metadata_sha256": sha((root / prefix / "metadata.json").read_bytes())})
    return runs


def audit(root, manifest_path):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path).resolve()
    manifest = load(manifest_path)
    require(manifest["schema_version"] == 1, "unsupported manifest schema")
    require(manifest["paper_revision_base"] == BASE, "paper base revision differs from agreed anchor")
    require(manifest["implementation_repository"] == IMPLEMENTATION, "wrong implementation repository")
    require(manifest["evaluated_revision"] == REVISION, "wrong evaluated revision")
    paper_path = safe_file(root, "manuscript/paper.tex")
    inventory = paper_inventory(paper_path.read_text())
    materials = manifest["materials"]
    require(isinstance(materials, list) and materials, "empty materials list")
    ids, mapped, evidence = set(), {"figure": [], "table": [], "equation": {}, "section": []}, {}
    for material in materials:
        require(isinstance(material["id"], str) and material["id"] and material["id"] not in ids, "empty or duplicate material id")
        ids.add(material["id"])
        kind = material["kind"]
        require(kind in {"figure", "table", "equation", "section", "study"}, "unknown material kind")
        require(material["status"] in {"implemented", "measured", "proposal", "context"}, "unknown material status")
        if kind in ("figure", "table"):
            require(isinstance(material.get("label"), str) and material["label"], "figure/table mapping lacks label")
            mapped[kind].append(material["label"])
        elif kind == "equation":
            mapped["equation"][material["id"]] = material.get("label")
        elif kind == "section":
            mapped["section"].append({"level": material.get("level", "section"),
                                      "title": material.get("title")})
        require(isinstance(material["evidence"], list) and material["evidence"], "material lacks evidence: " + material["id"])
        for record in material["evidence"]:
            repo, revision, path = record["repository"], record["revision"], record["path"]
            require(repo in {RESEARCH, IMPLEMENTATION}, "unapproved evidence repository")
            require(isinstance(revision, str) and HEX40.fullmatch(revision), "invalid evidence revision")
            if repo == IMPLEMENTATION:
                require(revision == REVISION, "implementation evidence is not evaluated revision")
            base = root if repo == RESEARCH else root / "vendor/sentinel-tpd"
            local = safe_file(base, path)
            check_hash(local, record["sha256"], repo + ":" + path)
            key = (repo, revision, path)
            require(key not in evidence or evidence[key]["sha256"] == record["sha256"], "conflicting evidence hash")
            evidence[key] = {**record, "github_url": "https://github.com/" + repo + "/blob/" + revision + "/" + quote(path, safe="/")}
    for kind in ("figure", "table"):
        require(Counter(mapped[kind]) == Counter(inventory[kind]), kind + " mapping coverage differs from paper")
    require(mapped["equation"] == {e["id"]: e["label"] for e in inventory["equation"]}, "equation mapping coverage differs from paper")
    require(mapped["section"] == inventory["section"], "section mapping coverage differs from paper")
    public_anchors = {"data/corpus.json", "data/lifecycle.json", "data/source-manifest.json",
                      "results/frozen-001/completion.json", "results/frozen-002/completion.json"}
    mapped_public_paths = {path for repo, revision, path in evidence if repo == RESEARCH}
    require(public_anchors <= mapped_public_paths, "public input/manifest/frozen-seal evidence coverage missing")
    references = manifest["references"]
    require(isinstance(references, list), "references must be a list")
    require(Counter(r["key"] for r in references) == Counter(inventory["bibliography"]), "bibliography mapping coverage differs from paper")
    bib = safe_file(root, "manuscript/references.bib").read_text()
    bibkeys = re.findall(r"@\w+\{([^,]+),", bib)
    require(Counter(bibkeys) == Counter(inventory["bibliography"]), "bibliography source keys differ from built paper")
    for reference in references:
        url = reference["primary_url"]
        require(isinstance(url, str) and url == url.strip() and not any(c.isspace() for c in url), "invalid primary URL")
        parsed = urlsplit(url)
        require(parsed.scheme in ("https", "http") and bool(parsed.netloc) and parsed.username is None, "invalid primary URL")
        require(reference["bibliography_path"] == "manuscript/references.bib"
                and reference["audit_path"] == "research/reference-audit.md", "unexpected reference evidence paths")
        safe_file(root, reference["bibliography_path"])
        safe_file(root, reference["audit_path"])
    readme = safe_file(root, "README.md").read_text()
    for repo in (RESEARCH, IMPLEMENTATION):
        require(re.search(re.escape("https://github.com/" + repo) + r"(?=[/)\s#?]|$)", readme), "README must distinguish both repository URLs")
    native_entry = re.search(r"@\w+\{sentineltpd,\s*(.*?)\n\}", bib, re.S)
    require(native_entry and "https://github.com/" + IMPLEMENTATION + "/tree/" + REVISION in native_entry[1],
            "implementation citation must point to evaluated source revision")
    frozen = verify_frozen(root)
    return {"schema_version": 1, "status": "passed", "offline": True,
            "manifest_sha256": sha(manifest_path.read_bytes()), "paper_sha256": sha(paper_path.read_bytes()),
            "paper_revision_base": BASE, "implementation_repository": IMPLEMENTATION, "evaluated_revision": REVISION,
            "inventory": inventory, "materials_verified": len(materials),
            "evidence": [evidence[k] for k in sorted(evidence)], "references_verified": len(references),
            "frozen_runs": frozen, "repository_distinction_verified": True,
            "limits": ["Local evidence bytes and mappings verified; remote GitHub existence and revision contents require separate live verification.",
                       "External source bytes require acquisition replay; excluded local corpus inputs are not verified by this audit.",
                       "Traceability does not establish semantic claim validity, independent replication, or peer review."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "research/paper-evidence-manifest.json")
    parser.add_argument("--output", type=Path, help="new audit JSON file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        result = audit(ROOT, args.manifest)
        text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(text)
        else:
            sys.stdout.write(text)
        return 0
    except (AuditError, OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write(json.dumps({"status": "failed", "error": str(exc)}) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
