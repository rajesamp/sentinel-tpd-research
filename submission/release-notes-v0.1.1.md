# Sentinel-TPD research artifact v0.1.1

This patch adds a clickable `rajesamp/sentinel-tpd` repository line immediately
beneath Rajeshkumar Sampathrajan's name in the author manuscript. The repository
and Independent Researcher affiliation share that line. The author PDF remains
10 A4 pages, with seven main-body pages. The anonymous source and PDF are
byte-identical to version 0.1.0. Scientific content, labels, runtime modules and
frozen observations are unchanged; no new experiment is claimed.

## Implementation alignment

The live Sentinel-TPD repository matched the evaluated revision
`5ce5d56e57a0acd092435fca5d89b78d0b39ee7b` on 2026-10-07: all 12 recorded files
matched before documentation changes. The research-alignment update was merged
through [pull request 1](https://github.com/rajesamp/sentinel-tpd/pull/1) after its
required CI passed. Main revision `c9926b6783646afa55dfee909ceb4660404349f1`
preserves all five runtime modules and the other original non-README files.

The upstream README now describes the observed field, schema and host-control
boundaries, and links all paper materials. Its CI checks changed or added runtime
modules against the evaluated baseline. A failure requires alignment review and
new measurements where behavior changes; updating a hash is not re-evaluation.

## Complete paper references

[Paper evidence index](https://github.com/rajesamp/sentinel-tpd-research/blob/codex/sentinel-tpd-paper/research/paper-evidence-index.md)
maps all 10 tables, five figures, 11 equations, sections/subsections, lifecycle
traces and 34 bibliography entries. The machine-readable manifest verifies 58
material entries, including 27 structural section/subsection headings. The human
index also covers the abstract and bibliography. Proposal equations, implemented
methods, measured observations and third-party literature are distinguished.

Actual published GitHub trees were checked for 51 unique indexed blob files,
403 blob links and 304 line targets. Bibliographic primary links preserve
attribution; third-party publications and excluded external payloads are not
copied into this release. Source pins and reconstruction code remain public.

Run `python3 tools/audit_traceability.py --output /tmp/new-traceability.json` in
the author artifact or repository to verify coverage and local evidence hashes.
The manifest-maintenance generator requires the repository's Git history; it is
not needed to run the assay or verifier. The reviewer artifact retains the nine
scored evaluation tests and 17 upstream tests, with author-side publication
maintenance tests excluded.

## Downloads and limits

Download the two PDFs, author and reviewer ZIPs, and `SHA256SUMS.txt`.
For a fresh assay, extract a package and run
`python3 reproduce.py --quick --output /tmp/new-replay` from its root with
Python 3.11+. This reconstructs pinned source inputs through HTTPS; `--offline
--quick` runs the smaller authored-only assay. Quick replay omits performance.

Original version 0.1.0 remains unchanged. This public release is not an anonymous
reviewer host or a conference submission. Required upstream notices and
third-person citations can permit identity inference. Source/checksum traceability
does not establish semantic attack prevention, independent human review or
acceptance-level novelty. See the manuscript and submission checklist.
