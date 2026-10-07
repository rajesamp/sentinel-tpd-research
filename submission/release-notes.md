# Sentinel-TPD research artifact v0.1.0

Conference-format manuscript and reproducible implementation study of MCP tool
poisoning, tool shadowing and metadata mutation. This release preserves the
original draft's pattern families and study questions, with claims derived from
the pinned Sentinel-TPD implementation and recorded observations.

## Download

- `paper.pdf`: author manuscript, 10 A4 pages; 7 pages of main text.
- `paper-anonymous.pdf`: manuscript with author block omitted and third-person
  source citations retained.
- `sentinel-tpd-author-v0.1.0.zip`: paper sources, evidence, source audits and
  submission preparation documents.
- `sentinel-tpd-reviewer-v0.1.0.zip`: derived reviewer artifact with exact scored
  code and observations. Author-facing documents are omitted. Required upstream
  attribution and baseline citations remain and can permit identity inference.
- `SHA256SUMS.txt`: hashes of the four download artifacts.

Extract either archive and run `python3 reproduce.py --quick --output /tmp/new-replay`
from its root with Python 3.11+. Choose a new output directory. The default
reconstructs source inputs through pinned HTTPS acquisition; `--offline --quick`
evaluates the smaller authored-only assay. No model account or dependency
installation is required. External source payloads are not redistributed.

## Verified evidence

- 47 pinned source templates and 70 authored challenges, reported separately;
  four evaluation arms and 15 lifecycle traces.
- Two measured process sessions, retaining raw observations and five workload
  sizes of 100–300 repeated local calls.
- Nine evaluation tests and 17 unmodified upstream tests.
- Linux reproduction checks passed for offline Python 3.11, 3.12 and 3.14 and
  full pinned-source Python 3.12.
- The sealed reviewer ZIP was freshly extracted and replayed on Python 3.14:
  30 source files fetched and hash-verified, deterministic outcomes matched the
  saved reference, and regenerated reports were byte-identical. Its separate
  authored-only offline replay also passed.
- Both PDFs compiled, and all ten anonymous pages were visually inspected.

Sentinel-TPD prevented local enqueue for 17/27 source attack-labeled templates
and 4/26 authored attack-labeled challenges; benign enqueues were 20/20 and
37/44 respectively. All three source shadowing templates were missed. These
are metadata/local-receipt outcomes with an inert sink, not real-agent attack
success or safe server execution. Labels are visible author intent without
independent human adjudication. Timing is descriptive and machine-specific.

## Submission status

Prepared as a full conference draft using the supplied EuroS&P 2027 A4 class.
This is a public research artifact, not an accepted proceedings paper or an
actual conference submission. Novelty, significance and acceptance remain
reviewer judgments. The manuscript makes no new-primitive or first-work claim.

The human author must review scientific claims, provide contact/conflict details
and attest publication clearance and exclusive submission. The reviewer archive
still needs venue-permitted anonymous hosting or an allowed supplementary upload;
this public GitHub release must not be used as an anonymous reviewer link where
the venue excludes GitHub. See `submission/readiness.md` and
`submission/registration-draft.md` in the repository.

Archive bytes were sealed before the final extracted-package replay and
publication audit. Those later validation records are available separately in
the repository; they are not represented as contents of the earlier ZIPs.

Original code and authored fixtures: MIT. Manuscript: CC BY 4.0. Vendored code
and the supplied IEEE class retain their own notices. Source-corpus reuse terms
are discussed in `NOTICE.md` and the provenance dossier.
