# Sentinel-TPD reproducible research

An implemented-system study of tool poisoning, tool shadowing and metadata
mutation. It preserves the original manuscript's patterns and workload questions,
but derives claims from the pinned code and saved observations. This is a research
artifact and conference draft, not an accepted publication or a security guarantee.

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
the same scanner on each call. Source and challenge results are never pooled.

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
