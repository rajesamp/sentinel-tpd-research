"""Evidence utilities shared by the offline Sentinel-TPD evaluation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PINNED_REVISION = "5ce5d56e57a0acd092435fca5d89b78d0b39ee7b"


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def object_sha(value) -> str:
    return sha(canonical(value))


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def load_json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("nonfinite JSON number")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return path.name


def verify_vendor() -> dict:
    manifest = load_json(ROOT / "vendor/manifest.json")
    if manifest["revision"] != PINNED_REVISION:
        raise ValueError("unexpected Sentinel-TPD revision")
    for record in manifest["files"]:
        path = (ROOT / "vendor/sentinel-tpd" / record["path"]).resolve()
        if not path.is_relative_to((ROOT / "vendor/sentinel-tpd").resolve()):
            raise ValueError("unsafe vendor provenance path")
        value = path.read_bytes()
        if sha(value) != record["sha256"]:
            raise ValueError("vendored SHA-256 mismatch: " + record["path"])
        blob = b"blob " + str(len(value)).encode("ascii") + b"\0" + value
        if hashlib.sha1(blob).hexdigest() != record["git_blob_sha1"]:
            raise ValueError("vendored Git blob mismatch: " + record["path"])
    return {"revision": manifest["revision"], "manifest_sha256": object_sha(manifest),
            "verified_files": len(manifest["files"]), "import_path": "vendor/sentinel-tpd/sentinel_tpd"}


def code_hashes() -> dict:
    paths = set()
    for directory in ("evaluation", "data", "tests", "vendor/sentinel-tpd"):
        paths.update((ROOT / directory).rglob("*.py"))
    paths.update([ROOT / "vendor/manifest.json", ROOT / "research/measurement-protocol.md"])
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(paths) if p.is_file()}


def environment() -> dict:
    clock = time.get_clock_info("perf_counter")
    return {"python": sys.version, "implementation": platform.python_implementation(),
            "interpreter": Path(sys.executable).name, "platform": platform.platform(),
            "machine": platform.machine(), "clock": {"implementation": clock.implementation,
            "resolution_seconds": clock.resolution, "monotonic": clock.monotonic},
            "dependencies": "Python standard library and verified vendored Sentinel-TPD only",
            "power_state": "not measured", "cpu_affinity": "not controlled",
            "background_load": "not controlled", "concurrency": 1}
