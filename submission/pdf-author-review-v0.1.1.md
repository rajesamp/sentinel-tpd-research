# Final author PDF review for v0.1.1

Result: **pass for the inspected final PDF**. The previous orphan acknowledgment page is resolved. All ten corrected page images were inspected individually, and no material clipping, overlap, unreadable figure/table/caption, or unresolved pagination defect was found. No source, PDF, image, experiment or archive was modified by this review.

## Exact final artifact

- PDF: `output/pdf/paper.pdf`
- SHA-256: `f0fc933354e4d09c6410c46f06d0bf442538b7a0b257ad9c4fd1dc99b0e8b228`
- Coverage: **10/10 rendered pages**, `output/qa/author-v0.1.1-final/page-01.png` through `page-10.png`.
- All pages are A4: MediaBox 595.28 × 841.89 points.
- References begin on page **8** after **7 body pages**.
- The full acknowledgment now fits on page 7.

## Author block and links

The first page places `Rajeshkumar Sampathrajan` above a single line containing `rajesamp/sentinel-tpd` followed by `Independent Researcher`. The implementation repository is therefore immediately beneath the author name, and the compact line preserves the ten-page layout.

An actual PDF link annotation on page 1 targets `https://github.com/rajesamp/sentinel-tpd`; its rectangle is `[200.129, 665.256, 287.198, 674.061]` in PDF points. The page-7 release-availability URL has PDF link annotations targeting `https://github.com/rajesamp/sentinel-tpd-research/releases/tag/v0.1.1`. Embedded destinations were checked without opening the websites.

## Visual and compilation checks

| Pages | Coverage | Result |
|---|---|---|
| 1 | Title, author/repository line, abstract and body | Clear centered author block; no crowding or clipping. |
| 2–3 | Architecture, decision figures, rule table and equations | Figures 1–3, Table 1 and labels/captions fit and remain legible. |
| 4–5 | Field/metric tables, plots and methods | Tables 2–4 and Figures 4–5 fit; axes and captions are readable. |
| 6 | Unique/workload/lifecycle results | Tables 5–7 and their notes are separated and readable. |
| 7 | Performance table, conclusion and full disclosure | Table 8 fits; no orphan continuation page remains. |
| 8–9 | References, appendix headings and equations | URLs wrap within columns; no collision or clipping. |
| 10 | Pattern and adjacent-study tables | Tables 9–10 and notes are readable and within margins. |

The final `output/pdf/paper.log` contains no `Overfull`, `undefined`, or TeX error lines beginning with `!`; its final output message reports ten pages. Both the log and direct PDF page count agree.

## Historical finding and unchanged anonymous artifact

The earlier eleven-page regression report was moved without changing its bytes to `submission/history/pdf-author-review-layout-001.md` (SHA-256 `ce6f9978ad5f99db291108263f400fce97a468e26dec0868777ba510da1c91d5`). It describes the superseded author PDF with SHA-256 `f29e16119580682ba968abbc08dca26193194ee38257b755e29a5f96e7b69faa`; it is historical evidence, not a finding against this final PDF.

The anonymous PDF remains SHA-256 `fe1989cf91bd6e54e3455f7859ff5cae3599b4505c6d045e106fc210499256f7`, identical to the previously reviewed anonymous artifact. No anonymous-source change was made by this reviewer.

## Decisions, uncertainty and coverage gaps

The requested repository placement, clickable repository/release destinations and restored pagination pass. No further visual correction is requested for these exact final bytes.

This bounded review does not certify website availability, GitHub publication, release-index alignment, archive membership, scientific accuracy, numerical reproduction or a source-level semantic diff. Source-content preservation remains the coordinator’s integration responsibility. A later regenerated PDF must not inherit this exact-byte review without checking the resulting artifact.

## Final render hashes

| Render | SHA-256 |
|---|---|
| `page-01.png` | `902a9ca6c2cbe52ce17915aab6ab3edca57c4c3411a9108b07e11e1a95aaec73` |
| `page-02.png` | `cb37842b12b47391d1b5cb4d0db12f6f010be104236b66d86748588a79c9bd1a` |
| `page-03.png` | `b1462074ac1738366b8d9d135a83f0e534e30647bd5f1a6ef83a0a3db7fd8adf` |
| `page-04.png` | `4bebc58ebd3833540f443de2fca867d833e4d70e9d119e7be8c4432aac460df6` |
| `page-05.png` | `54df290494d3fac74360b25de17ecf74916faf16f7de7b97c708196808e80577` |
| `page-06.png` | `dce98584c8f106db10cafdd9d83749af14136f911bcbea35be879a98b39b97d3` |
| `page-07.png` | `1d33e0b108d26fa09e93490ac747702238f22d7dc4bd97cf2c4bc36f2177554b` |
| `page-08.png` | `513297432c738e756338222fe8b0739d8bd7f4113a4bcd6200d38dc9144270e8` |
| `page-09.png` | `ef720f6652ca4b8894997a1a2f3d503d3f95c413e230a6fa4c53e0d403664a34` |
| `page-10.png` | `49a8c61d657120f5b464d4768ae4902107d49b51849b64191926f06f3d36fa45` |
