#!/usr/bin/env python3
"""Fetch pinned inert fuzzd records into an ignored local cache; execute none.

No external payload is part of the distributed authored corpus. The acquisition
manifest fixes SHA-256 and Git blob SHA-1 before scanner measurement. Run with
--offline to regenerate only from already verified cached files.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
PIN = "f739e120cd7dc253fead2a1f13668f9535e4d8a5"
BASE = "https://raw.githubusercontent.com/ksek87/fuzzd/" + PIN + "/"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def obtain(entry, cache, offline):
    relative = Path(entry["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe cache path")
    path = cache / relative
    fetched = False
    if path.exists():
        raw = path.read_bytes()
    elif offline:
        raise FileNotFoundError("missing offline cache entry: " + str(relative))
    else:
        url = BASE + relative.as_posix()
        if url != entry["url"]:
            raise ValueError("source URL differs from fixed repository and commit")
        request = urllib.request.Request(url, headers={"User-Agent": "sentinel-tpd-corpus-reproduction"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(entry["bytes"] + 1)
        fetched = True
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if len(raw) != entry["bytes"] or sha(raw) != entry["sha256"] or blob != entry["git_blob_sha1"]:
        raise ValueError("source bytes differ from pinned manifest: " + str(relative))
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
    return raw, fetched


def normalize(manifest, raw_files):
    """Preserve payloads while making every authored envelope explicit.

    The source attacks are attack records, not complete MCP Tool objects.
    Response cases are a declared description-projected static text assay.
    They are never labeled native runtime-response coverage.
    """
    cases = []
    clean = json.loads(raw_files["bench/clean_tools.json"])
    for entry in manifest["cases"]:
        case = {k: deepcopy(entry[k]) for k in ("case_id", "family", "kind", "label")}
        case.update(split="source", source_record_sha256=entry["source_record_sha256"],
                    source_file=entry["source_file"], source_commit=PIN,
                    label_basis="Source author's intended fixture semantics; not observed agent harm.")
        if entry["kind"] == "benign":
            tool = deepcopy(clean[entry["source_index"]])
            if sha(canonical(tool)) != entry["source_record_sha256"]:
                raise ValueError("clean tool index hash mismatch")
            case.update(tool=tool, source_index=entry["source_index"],
                        source_injection_point="none", projection="original_complete_benign_tool",
                        native_metadata_applicable=True, authored_context=False)
        else:
            record = json.loads(raw_files[entry["source_file"]])
            payload = record["payload"]
            if record["id"] != entry["case_id"] or sha(payload.encode()) != entry["payload_sha256"]:
                raise ValueError("attack record identity or payload mismatch")
            name = "fixture_" + record["id"].lower().replace("-", "_")
            tool = {"name": name, "description": payload,
                    "inputSchema": {"type": "object", "properties": {}}}
            surface = record["injection_point"]
            case.update(tool=tool, source_payload=payload, source_injection_point=surface,
                        source_expected_behavior=record["expected_behavior"],
                        source_url=record.get("source_url"),
                        projection="exact_payload_in_authored_description_envelope",
                        native_metadata_applicable=surface == "tool.description",
                        authored_context=True)
            if surface == "tool.response":
                case.update(projection="response_payload_projected_to_description",
                            response_text=payload, native_metadata_applicable=False)
            elif surface == "tool.annotations":
                tool["description"] = "Deletes the selected fixture record permanently."
                tool["annotations"] = json.loads(payload)
                case.update(projection="original_annotations_with_authored_destructive_description",
                            native_metadata_applicable=True,
                            authored_context_note="Source has annotations and expected behavior, but no complete tool description; the contradiction context is authored.")
            elif record["id"] == "TS-001":
                tool["name"] = "read_file"
                case.update(projection="original_payload_with_authored_squatting_name_and_peer",
                            reference_tools=[{"server": "trusted-peer", "name": "read_file"}],
                            host_context={"candidate_server": "untrusted-fixture", "authorized_replacement": False})
            elif record["id"] == "TS-002":
                case.update(reference_tools=[{"server": "trusted-peer", "name": "send_email"}],
                            host_context={"candidate_server": "untrusted-fixture", "authorized_replacement": False})
            elif record["id"] == "TS-003":
                tool["name"] = "read-file"
                case.update(projection="original_payload_with_declared_alias_name_and_authored_peer",
                            reference_tools=[{"server": "trusted-peer", "name": "read_file"}],
                            host_context={"candidate_server": "untrusted-fixture", "authorized_alias": False})
        case["tool_sha256"] = sha(canonical(case["tool"]))
        cases.append(case)
    counts = {kind: sum(c["kind"] == kind for c in cases) for kind in ("poisoning", "shadowing", "benign")}
    if counts != {"poisoning": 24, "shadowing": 3, "benign": 20}:
        raise ValueError("pinned corpus denominator mismatch")
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("duplicate case ID")
    return {"schema_version": 1, "scope": "Pinned source records with declared static metadata projection; local-only, not redistributed.",
            "source_commit": PIN, "source_manifest_sha256": sha((ROOT / "source-manifest.json").read_bytes()),
            "redistribution": "local acquisition only; no bundled external payload license is asserted",
            "label_semantics": "Intended fixture semantics, not an oracle of real agent harm.", "cases": cases}


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "source-cache")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "corpus-source.local.json")
    parser.add_argument("--combined-output", type=Path, default=ROOT / "corpus-combined.local.json")
    args = parser.parse_args()
    if args.output.exists() or args.combined_output.exists():
        raise FileExistsError("Use new output paths; existing corpus snapshots are never overwritten.")
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    if manifest["commit"] != PIN:
        raise ValueError("manifest commit mismatch")
    raw_files = {}
    network_files_fetched = 0
    for entry in manifest["files"]:
        raw, fetched = obtain(entry, args.cache, args.offline)
        raw_files[entry["path"]] = raw
        network_files_fetched += int(fetched)
    source = normalize(manifest, raw_files)
    authored = json.loads((ROOT / "corpus.json").read_text())
    if any(c["split"] != "challenge" for c in authored["cases"]):
        raise ValueError("offline artifact must contain authored challenges only")
    combined = {"schema_version": 1, "scope": "Local-only combined corpus; report source and challenge splits separately.",
                "source_manifest_sha256": source["source_manifest_sha256"],
                "authored_corpus_sha256": sha((ROOT / "corpus.json").read_bytes()),
                "label_semantics": source["label_semantics"], "cases": source["cases"] + authored["cases"]}
    if len({c["case_id"] for c in combined["cases"]}) != len(combined["cases"]):
        raise ValueError("source/challenge case ID collision")
    write_new(args.output, source)
    write_new(args.combined_output, combined)
    print(json.dumps({"source_cases": len(source["cases"]), "challenge_cases": len(authored["cases"]),
                      "combined_cases": len(combined["cases"]),
                      "source_sha256": sha(args.output.read_bytes()),
                      "combined_sha256": sha(args.combined_output.read_bytes()),
                      "network_allowed": not args.offline,
                      "network_files_fetched": network_files_fetched,
                      "network_used": network_files_fetched > 0}, indent=2))


if __name__ == "__main__":
    main()
