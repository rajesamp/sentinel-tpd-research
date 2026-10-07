"""Export a declared author or reviewer view; preserve measured evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from evaluation.report import build_summary

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def excluded(path):
    return ("__pycache__" in path.parts or path.suffix in {".pyc",".aux",".out"}
            or path.name.endswith(".local.json")
            or any(p in {"source-cache","cache","qa","packages",".git"} for p in path.parts))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=["author","anonymous"],required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    destination=args.output.resolve()
    destination.mkdir(parents=True,exist_ok=False)
    anon=args.mode=="anonymous"
    for run in ("frozen-001","frozen-002"):
        if build_summary(ROOT/"results"/run)["status"]!="completed":
            raise ValueError("Cannot export an incomplete scored run")
    include=["data","evaluation","tests","vendor","reproduce.py","LICENSE",
             "research/measurement-protocol.md","research/corpus-provenance.md",
             "results/frozen-001","results/frozen-002",
             "submission/template-provenance.json"]
    if not anon:
        include += ["README.md","NOTICE.md","CITATION.cff","governance","research","manuscript",
                    "tools","submission","output/pdf",".github",
                    "results/python314-verified","results/python314-offline"]
    changes=[]
    copied=set()
    for item in include:
        source=ROOT/item
        if not source.exists():
            raise FileNotFoundError(item)
        files=source.rglob("*") if source.is_dir() else [source]
        for file in files:
            if not file.is_file() or excluded(file.relative_to(ROOT)):
                continue
            relative=file.relative_to(ROOT)
            if relative in copied:
                continue
            if file.suffix==".log" and "results" not in relative.parts:
                continue
            copied.add(relative)
            target=destination/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            original=file.read_bytes()
            raw=original
            if anon and relative==Path("LICENSE"):
                raw=raw.replace(b"Rajeshkumar Sampathrajan",b"Study contributors (names withheld for review)")
            # Only supplementary local-path logs change; scored raw files never do.
            if file.suffix==".log" or file.name=="reproduction.json":
                raw=raw.replace(str(ROOT).encode(),b"<package>")
            target.write_bytes(raw)
            if raw!=original:
                changes.append({"file":str(relative),"original_sha256":sha(original),"exported_sha256":sha(raw)})
    if anon:
        manuscript=destination/"manuscript"; manuscript.mkdir()
        for name in ("paper-anonymous.tex","IEEEtran.cls","references.bib"):
            target=manuscript/("paper.tex" if name=="paper-anonymous.tex" else name)
            shutil.copyfile(ROOT/"manuscript"/name,target)
        pdf=destination/"output/pdf";pdf.mkdir(parents=True)
        shutil.copyfile(ROOT/"output/pdf/paper-anonymous.pdf",pdf/"paper.pdf")
        (destination/"README.md").write_text(
            "# Reviewer artifact\n\nPython 3.11+; standard library and vendored code only. "
            "Run python3 reproduce.py --quick --output /tmp/new-replay from this folder. "
            "The full default reconstructs 47 verified source cases and 70 authored cases; "
            "initial pinned-source acquisition uses HTTPS. External payloads are not bundled. "
            "Use --offline --quick for the smaller 70-case authored-only assay, without network.\n\n"
            "See the manuscript, measurement protocol and corpus provenance. The sink is inert; "
            "empty arguments are not schema-validated operations. Labels are author intent, "
            "not independently adjudicated agent harm. Source and challenge results are separate.\n\n"
            "This is a derived reviewer view, not a new experiment. Executable code and all scored "
            "observations are byte-identical. Author-created copyright names are withheld for review; "
            "upstream notices and third-person citations remain unchanged. Those attributions can "
            "permit inference, so identity concealment is not guaranteed. No anonymous hosting "
            "has been configured. Upload only to a service permitted by the chosen venue.\n")
        (destination/"NOTICE.md").write_text(
            "# Notices\n\nOriginal study code and authored fixtures use the root MIT license. "
            "Manuscript: CC BY 4.0. Exact upstream code retains its own MIT license and notices. "
            "The source corpus is fetched locally and is not redistributed here; MIT declarations "
            "were observed but complete corpus-license evidence remains unresolved. "
            "The supplied IEEE class retains its original notices. See corpus-provenance.md.\n")
        (destination/"ANONYMIZATION.json").write_text(json.dumps({
            "mode":"derived reviewer view; not a new run",
            "executable_code_changed":False,"scored_observations_changed":False,
            "upstream_notices_changed":False,
            "limits":"Third-person baseline citations and retained licenses can permit inference; hosting anonymity is unverified.",
            "changes":changes},indent=2)+"\n")
    # Verify every recorded source dependency against the original freeze.
    for run in ("frozen-001","frozen-002"):
        original_meta=json.loads((ROOT/"results"/run/"metadata.json").read_text())
        for name,expected in original_meta["code_files"].items():
            if sha((destination/name).read_bytes())!=expected:
                raise ValueError("Exported scored dependency differs: "+name)
        if build_summary(destination/"results"/run)!=build_summary(ROOT/"results"/run):
            raise ValueError("Exported results differ: "+run)
    manifest={str(f.relative_to(destination)):sha(f.read_bytes())
              for f in sorted(destination.rglob("*")) if f.is_file()}
    (destination/"SHA256SUMS.json").write_text(json.dumps(manifest,indent=2)+"\n")
    with ZipFile(destination.with_suffix(".zip"),"x",ZIP_DEFLATED,compresslevel=9) as archive:
        for file in sorted(destination.rglob("*")):
            if file.is_file():
                archive.write(file,str(Path(destination.name)/file.relative_to(destination)))
    print(destination.with_suffix(".zip"))

if __name__=="__main__":
    main()
