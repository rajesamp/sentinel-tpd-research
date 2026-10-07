# Sentinel-TPD reproducible research

An implemented-system study of tool poisoning, tool shadowing and metadata
mutation. It preserves the original manuscript's patterns and workload questions,
but derives claims from the pinned code and saved observations. This is a research
artifact and conference draft, not an accepted publication or a security guarantee.

[Version 0.1.1 downloads](https://github.com/rajesamp/sentinel-tpd-research/releases/tag/v0.1.1)
include the author and anonymous PDFs, author and reviewer archives, and file
checksums. Read [submission preparation](submission/readiness.md) before any
conference upload. Post-sealing validation is recorded in
[fresh-package replay](submission/fresh-package-replay.json) and the repository's
archive review; it is separate from the sealed archive contents.

## Implementation and paper evidence

The implementation repository is
[rajesamp/sentinel-tpd](https://github.com/rajesamp/sentinel-tpd).
This [rajesamp/sentinel-tpd-research](https://github.com/rajesamp/sentinel-tpd-research)
repository contains the paper, assay, fixtures, references and recorded evidence.
They serve different roles. The live implementation was verified on 2026-10-07
at the paper's exact evaluated revision
`5ce5d56e57a0acd092435fca5d89b78d0b39ee7b`: all 12 recorded files matched before
the documentation update. The research update changes documentation and paper
attribution, not the measured runtime modules or frozen observations.

Start with the [paper-to-evidence index](research/paper-evidence-index.md), covering
every figure, table, equation, section and all 34 bibliography keys. Its
[machine-readable manifest](research/paper-evidence-manifest.json) records exact
GitHub revisions, paths and file hashes. Third-party studies are attributed and
linked; their algorithms are not claimed as implemented here. External corpus
payloads are acquired by verified pins and are not redistributed.

Run `python3 tools/audit_traceability.py --output /tmp/new-traceability.json`
to check coverage, evidence hashes and the frozen scored dependencies. See
[upstream alignment](research/upstream-alignment.json) for the live-revision
check. A later implementation change requires a new recorded comparison and,
when behavior changes, new experiments; it must not silently replace this paper's
immutable baseline. Version 0.1.0 remains available with its original bytes.

## Reproduce

Python 3.11 or newer; no package installation or model account is required.
Run from this repository. Always choose a new output directory.

```sh
python3 reproduce.py --output results/my-replay
```

The default reconstructs 47 pinned source cases (24 poisoning, 3 shadowing,
20 benign) and combines them with 70 self-authored challenges (26 attack-labeled,
44 benign). It verifies each source file before use. Initial source acquisition
may use HTTPS; evaluation and the inert sink are local. External payload inputs
are saved only in ignored `*.local.json` files. See NOTICE.md before source reuse.

```sh
python3 reproduce.py --offline --quick --output results/my-offline-replay
python3 reproduce.py --cached-source --quick --output results/my-cached-replay
```

`--offline` evaluates the 70 authored cases and lifecycle probes only. It does
not reproduce the external-corpus or workload results. `--cached-source` uses
the verified local source cache and rejects missing or changed files. `--quick`
omits performance measurement. The full run measures 10 warmup and 50 measured
pairs for each original workload size in one process session. Timing and Python
allocation peaks are descriptive and are not required to match another machine.

The pipeline runs evaluation and upstream tests, verifies vendor hashes, preserves
raw JSONL, regenerates reports byte-identically and compares deterministic outcomes
with the saved reference when available. Failures remain in their output folder.
Four arms separate allow-all, initial registration only, native Sentinel-TPD and
the same scanner on each call. Final scored source and challenge results are
separate. Preserved development-001 predates the split-qualified family-report
fix: its family table is legacy pooled and is not used for manuscript claims.

## Scope

Calls end at an inert recording sink with fixed empty arguments. Outcomes measure
metadata decisions and local enqueues, not real agent instruction following,
schema-valid remote operations, harmful side effects or production overhead.
Warnings and denials differ. Quarantine is registry state. The pinned scanner
does not implement the original draft's weighted semantic risk or OS isolation.
Cases were visible during development; there is no blind holdout or independent
human label adjudication. Read research/measurement-protocol.md and the paper's
limitations before interpreting rates.

Manuscript sources, reference audit, original coverage map, raw observations,
submission checklist and release packages accompany the final version. Public
author hosting must not be used as an anonymous reviewer link where a venue
requires anonymous services. The separate anonymous export is a derived view;
original evidence remains preserved.
