# Sealed archive review

Review date: 2026-10-06 (local project date). Read-only agent review of the actual sealed release ZIPs. No archive, scored evidence, source code or prior review was edited. No experiment or replay was run by this reviewer.

## Result

**No material packaging defect found in these exact archive bytes.** Manifest coverage and hashes pass, frozen evidence is preserved, excluded external corpus/cache files are absent, and the reviewer package contains the anonymous manuscript/PDF rather than the author versions. The coordinator's saved fresh replay reports success.

This closes the archive/PDF-metadata inspection gaps in the earlier `submission/package-review.md` for the two hashes below. That earlier report remains a historical record of its original scope.

## Exact archives reviewed

Paths are relative to the project root.

| Archive | Bytes | ZIP members | Manifest entries |
|---|---:|---:|---:|
| `output/packages/release-v0.1.0/sentinel-tpd-author-v0.1.0.zip` | 2,061,500 | 107 | 106 |
| `output/packages/release-v0.1.0/sentinel-tpd-reviewer-v0.1.0.zip` | 1,255,809 | 53 | 52 |

Author archive SHA-256:

`da6ce5d100edf0bcb2a1205b11dca4d993aedd9cdaedaaee8274718846569d4d`

Reviewer archive SHA-256:

`6c798c5400b8789bad1d728459d29752fa62e98a8fe4742f605e983911ae0ddd`

Each ZIP has one top-level package directory. Every member was read successfully. Each internal `SHA256SUMS.json` covers every other file: no mismatched digest, unlisted file, missing file, duplicate member, absolute member path or parent-traversal component was found. The checksum file does not hash itself, as expected.

## Frozen evidence and code preservation

For both archives and both `frozen-001` and `frozen-002`:

- All 18 dependency files match their frozen metadata SHA-256 values.
- All completion-sealed raw files match the saved digests.
- Every archived file in each frozen run is byte-identical to the corresponding current frozen file in the project.
- All Python files present in the reviewer package are byte-identical to their counterparts in the author package.

No scored observation was rewritten to conceal local identity. The reviewer `ANONYMIZATION.json` records one root-license transformation and explicitly states that executable code, scored observations and upstream notices remain unchanged.

## Actual exclusion checks

Neither ZIP contains `*.local.json`, `source-cache`, `cache`, `__pycache__` or a `.git` directory. The authored `data/corpus.json`, source hash manifest and pinned acquisition/normalization code are present. The `.gitignore` files are intentional configuration, not Git history.

Against all 30 locally cached pinned source files and all 27 attack-record payloads, scanning the actual decompressed members found:

- No byte-identical raw external source file.
- No complete attack payload in literal UTF-8 or either ordinary JSON-escaped form checked.

This supports exclusion of the known external source corpus, not a universal proof against every transformed fragment. Upstream vendored tests remain a separately licensed code dependency.

The reviewer ZIP does **not** contain the own-author `CITATION.cff`, author README, body template, manuscript builder, author-specific submission records, author PDF, author archive, governance files or reference-audit/source dossier. It includes the designated reviewer README, protocol and provenance instructions, frozen evidence, replay code, baseline code, references and one manuscript/PDF pair.

## Reviewer manuscript and PDF

Actual byte comparisons establish:

- Reviewer `manuscript/paper.tex` equals the author's packaged `manuscript/paper-anonymous.tex`.
- Reviewer `output/pdf/paper.pdf` equals the author's packaged `output/pdf/paper-anonymous.pdf`.
- Reviewer PDF bytes differ from the author's `output/pdf/paper.pdf`.

The reviewer source has an empty author declaration. Extracted first-page text proceeds from the title to the abstract without an author block.

The reviewer PDF has **10 pages**. Its document information contains only:

- Creator: `LaTeX with hyperref`
- Producer: `xdvipdfmx (0.1)`
- CreationDate: `D:20261007031404-00'00'`

No PDF Author field, XMP metadata or embedded file attachment was present. This inspection concerns text identity and metadata; it does not substitute for the coordinator's visual layout review.

## Permitted identity remnants and limits

Reviewer text-file scans found author names/handles only in:

- Third-person bibliography entries for Sentinel-TPD and the separate dispatch artifact, including the embedded manuscript bibliography.
- The exact upstream vendor manifest URL, license, README and package metadata.

The PDF contains corresponding third-person references on page 8. No local `/Users/` or `/private/tmp/` workspace path was found in the reviewer text files, and no such path or additional author marker was found in extracted PDF text.

The root license identifies “Study contributors (names withheld for review).” Upstream license and author attribution remain intact. The reviewer README and anonymization record expressly disclose that baseline notices and references permit identity inference.

These are permitted remnants under the stated packaging policy, **not complete anonymity**. Public release ownership, hosting identity and venue-specific review requirements are outside this byte-level review. Mandatory baseline notices should not be removed to manufacture a stronger anonymity claim.

## Observed fresh replay evidence

Read-only evidence location:

`/private/tmp/sentinel-tpd-package-replay-luhea4m8/full-replay/reproduction.json`

The coordinator's saved record reports:

- Python 3.14.8 and verification of 12 vendored files.
- Source-and-authored input mode.
- Zero return codes for authored tests, upstream tests, source acquisition, assay and report regeneration.
- `report_regeneration_identical: true`.
- `deterministic_outcomes_match_reference: true`.
- `status: completed`.

The accompanying acquisition log records 30 files fetched over the network, 47 source cases, 70 authored challenges and 117 combined cases. Its combined corpus SHA-256 is:

`41438f7a9960bae5a3dd8709a27c57df955328ac3d8f689b3f73d2e5ffdab3e1`

That is the frozen corpus file hash. The new assay completion record is completed. The recorded replay command disables performance, so this establishes saved evidence of deterministic replay, not fresh timing reproduction. This reviewer inspected the records; it did not independently execute the replay or establish independent human replication.

## Handoff and residual concerns

**Result:** no actionable packaging defect established for the exact sealed hashes above.

**Artifact:** `submission/archive-review.md`, written after sealing and intentionally not inserted into the sealed archives during this audit.

**Decisions:** preserve both archives unchanged; retain original evidence and required upstream notices; describe the reviewer package as a derived view with explicit inference limits.

**Uncertainty:** remote CI status, publication/upload bytes and venue-specific anonymity acceptance were not inspected.

**Coverage gaps:** no new experiment, no independent human review, no new visual rendering audit and no claim of complete identity concealment. Any later ZIP change requires a new hash and review of the changed bytes.

