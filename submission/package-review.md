# Package and fresh-reproduction review

Review date: 2026-10-06 (local project date). Reviewer: source/novelty specialist agent. This is a bounded, read-only implementation audit, not an independent human review or a new experiment. Only this report was written.

## Result

**No material current defect was established in the reviewed reproduction/export logic.** The present frozen evidence and included replay inputs pass the read-only checks below. Final reviewer-export validation remains pending because the anonymous manuscript/PDF and archives were not yet present when inspected; the coordinator was generating them concurrently.

Reviewed entry points:

- `tools/export_artifact.py`
- `reproduce.py`
- `.github/workflows/reproduce.yml`
- Supporting dependency/provenance, source-acquisition and reporting code
- Metadata, completion seals, raw records and fixture manifests for `frozen-001` and `frozen-002`

No assay, benchmark, test suite, acquisition command, exporter or PDF compiler was executed during this review.

## Actionable findings and remaining release checks

### No established code defect requiring a patch

No missing executable dependency, overwritten frozen file, bundled complete external payload, or contradictory anonymity promise was found in the current inspected file set. Findings are deliberately not manufactured from hypothetical future edits.

### Pending: inspect the actual reviewer export after generation

At inspection, `manuscript/paper-anonymous.tex` and `output/pdf/paper-anonymous.pdf` did not yet exist, and `packages/` had no ZIP archives. This is expected concurrent work, not evidence that the exporter is defective. The reviewer source/PDF and final archive therefore have **not** been examined here.

Before declaring the reviewer package complete:

1. Verify the generated anonymous source/PDF omit the author block and own author-facing prose, including PDF metadata.
2. Check the actual ZIP member list and file hashes, not just the export selection logic.
3. Ensure no author archive or author PDF was placed inside the reviewer archive.
4. Preserve the README's explicit limit that baseline attribution and third-person references permit identity inference.

The exporter is fail-closed for missing required inputs: it raises instead of silently publishing a partial ZIP. A failed attempt can leave its newly created destination directory behind, so retries require a new output directory; existing evidence is not overwritten.

## Evidence-preservation checks

Both frozen runs record **18 dependency files**, and all 18 current file SHA-256 values match each run's `metadata.json`. These are scored dependency hashes, not a claim that later packaging glue was executed during the original measurement.

For both runs:

- Every completion-sealed file (`metadata.json`, `records.jsonl`, `fixture-manifest.json`) matches its recorded SHA-256.
- Current local corpus and lifecycle file/content hashes match the frozen input records.
- All 70 authored challenge cases match their corresponding frozen per-case identities.
- Completion records report completed runs, zero execution errors, unchanged source and unchanged inputs. This review checked their seals; it did not re-run their measurements.

The exporter copies scored records without transformations. Its only byte changes are the declared author-created root-license name replacement in reviewer mode and root-path replacement in supplementary `.log`/`reproduction.json` files. It checks all recorded scored dependencies in the destination and compares summaries reconstructed from exported raw evidence with the original summaries.

`evaluation.report.build_summary` checks raw-file hashes, metadata provenance, record counts, fixture identities, duplicate records and expected record coverage before reporting. Frozen observations retain raw timing/allocation samples; a derived export is not represented as a new run.

## Fresh-reproduction path

The inspected path requires Python 3.11+ and the standard library plus vendored Sentinel-TPD. All imported local modules, tests, vendor files, authored data, lifecycle data and expected-outcome references needed by `reproduce.py` are selected for both exports.

- Default replay acquires pinned source files, verifies byte length, SHA-256 and Git blob SHA-1, reconstructs the declared source projections, then combines them with the 70 authored cases.
- `--offline` selects only authored cases and omits source workloads/performance. It is correctly described as a smaller assay, not a reproduction of the full source corpus.
- `--cached-source` requires an already populated, validated local cache. A fresh archive cannot use it immediately because excluded external source files are not bundled.
- The runner uses fresh output directories and exclusive file creation. Existing frozen runs and previous replay outputs are not overwritten.
- It regenerates reports from new raw records and byte-compares the three derived outputs.
- It compares deterministic summary outcomes with the saved reference while excluding timestamps, audit-head bytes and performance. Therefore “outcomes match” is narrower than byte-identical replay or matching timing.
- Initial HTTPS availability, DNS/TLS trust and repository retention remain external dependencies. Network failures are surfaced rather than replaced with different input data.

The current workflow supplies offline jobs for Python 3.11, 3.12 and 3.14 and a full pinned-source deterministic job on Python 3.12. **Workflow configuration is not evidence that those remote jobs have run or passed.** This audit makes no new cross-platform success claim.

## External-payload exclusion

The export selection excludes `*.local.json`, `source-cache`, cache directories, Python bytecode and package output directories. It includes the authored corpus, source hash manifest, normalization/acquisition code and frozen observation records.

A read-only scan of the current files selected by the exporter found:

- No byte-identical external raw source file.
- No complete source-attack payload in its literal UTF-8 form or the two ordinary JSON-escaped forms checked.
- No selected local combined/source corpus snapshot or source-cache member.

The observation representation removes payload excerpts from scanner findings and records signal IDs, field paths and character ranges. Source-input payloads are not copied through the runner's explicit lineage field list. These checks support exclusion of the known corpus bytes, not a universal proof that no transformed fragment can ever appear in arbitrary future files.

The GitHub Actions upload for the full-source job selects assay records, regenerated reports, reproduction status and logs explicitly; the locally reconstructed `*.local.json` inputs are outside those upload paths. Offline uploads contain authored-only replay outputs. No CI job executes attack payloads as tool actions; the study's call sink is inert.

Vendored upstream test fixtures are a separate, licensed code dependency and remain unmodified. Their presence must not be confused with redistribution of the excluded fuzzd raw corpus.

## Reviewer identity boundary

The predicted reviewer file set omits own `CITATION.cff`, author README, governance/research-source dossiers, editable body template and author PDF. The exporter supplies a reviewer README and substitutes the anonymous manuscript/PDF. The root MIT copyright name is replaced with a declared reviewer label.

The scan found author identity only in the expected categories within the currently available reviewer selection:

- The root license, which the exporter explicitly rewrites.
- Third-person bibliography entries for Sentinel-TPD and the separate dispatch artifact.
- Exact upstream vendor manifest URL, license, README and package metadata.

No additional local home-directory or temporary-workspace marker was found in the available selected text files outside those declared categories. The anonymous source and PDF were unavailable and are excluded from this conclusion.

Retaining upstream notices and third-person citations can identify or permit inference of the author. That limitation is both necessary to the stated package policy and explicitly disclosed. It is **not** complete anonymity, and no anonymous hosting or venue-specific reviewer-policy approval is established here. Do not scrub mandatory upstream license notices or claim that preserving them prevents identity inference.

## Acceptable limitations

- The two freezes are author-generated evidence, cryptographically linked within the artifact, not independent replication.
- Hash consistency detects accidental changes relative to the saved seals; the seals are not externally timestamped or signed by an independent party.
- The full source corpus requires first-use network acquisition; the authored-only offline mode is intentionally smaller.
- Timing and memory observations are platform-specific. Deterministic replay excludes performance from the equality target.
- The release SHA256 manifest binds exported packaging glue as well as evidence. Original measured dependency hashes deliberately cover the scored implementation/protocol; later exporter, workflow and replay convenience code are not retroactively claimed as measured dependencies.
- This review did not execute CI or reproduce experiments, inspect a final PDF, or verify a final ZIP.

## Handoff

**Result:** no established material code defect; actual reviewer artifact checks remain pending.

**Artifact:** `submission/package-review.md`.

**Decisions:** preserve raw evidence; retain licensed upstream attribution; keep full-source and authored-only replay claims separate; state identity-inference limits.

**Uncertainty:** anonymous document/PDF and archive bytes did not exist at inspection; remote CI outcomes are unverified.

**Coverage gaps:** no experiment execution, no PDF metadata inspection, no final archive extraction/manifest verification, no venue-specific anonymity ruling.

