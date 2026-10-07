# Author PDF review for v0.1.1

Status: **layout correction needed before final approval**. The requested author/repository placement and links are correct, but the author PDF grew from ten to eleven pages and leaves an acknowledgment fragment alone on page 8. This finding has been sent to the coordinator. No source, PDF, rendered image, experiment or archive was modified by this review.

## Artifact and coverage

- Reviewed PDF: `output/pdf/paper.pdf`
- Reviewed SHA-256: `f29e16119580682ba968abbc08dca26193194ee38257b755e29a5f96e7b69faa`
- Actual page count: **11**, all A4 (595.28 × 841.89 points).
- Rendered coverage: **11/11 pages**, including the additional `output/qa/author-v0.1.1/page-11.png` beyond the ten anticipated by the task.
- References begin on page **9**; pre-reference content spans **8** pages.
- Preserved v0.1.0 author PDF: **10** pages, references beginning on page **8**, SHA-256 `7f5d9f99cc996a83d656ddc1a85caa86c23d0a63e5b3c9ba697506bdaf0160ee`.

## Verified changes

Page 1 shows the exact requested order, with the repository immediately beneath the author:

1. Rajeshkumar Sampathrajan
2. rajesamp/sentinel-tpd
3. Independent Researcher

The repository line has an actual PDF `/Link` annotation to `https://github.com/rajesamp/sentinel-tpd`; its rectangle is `[254.103, 665.256, 341.172, 674.061]` in PDF points. The release-availability paragraph on page 7 contains clickable annotations to `https://github.com/rajesamp/sentinel-tpd-research/releases/tag/v0.1.1`. This verifies embedded link destinations, not network availability or publication status.

The anonymous PDF retains SHA-256 `fe1989cf91bd6e54e3455f7859ff5cae3599b4505c6d045e106fc210499256f7`, identical to the previously reviewed anonymous artifact. Anonymous-source byte identity was not independently rechecked in this bounded PDF review.

## Visual and diagnostic findings

All eleven supplied page images were visually inspected. No clipping, overlap, unreadable figure/table labels, missing caption, or text outside the margins was observed. Figures 1–5 and Tables 1–10 remain legible. The title block is centered and clearly separated from the abstract.

One material pagination regression remains: page 8 contains only the concluding lines of the AI-assistance acknowledgment, leaving almost the entire page empty and moving references to page 9. The prior author PDF had no such extra pre-reference page. The coordinator should restore the prior ten-page/seven-body-page layout, or explicitly record acceptance of the changed pagination; no fix was made within this read-only scope.

`output/pdf/paper.log` contains no `Overfull`, `undefined`, or TeX error lines beginning with `!`. Its final output message reports eleven pages, consistent with the PDF. Absence of compile warnings does not resolve the visual pagination finding.

## Decisions, uncertainty and coverage gaps

The requested repo line/link passes. Full layout approval is withheld pending the identified pagination issue; all other inspected layout elements pass this bounded review. The preserved prior artifact provides the page-count comparison.

The task did not validate GitHub publication, release-index alignment, archives, scientific claims or numerical results. The anonymous PDF hash is checked, but anonymous source provenance is left to the coordinator. Later regenerated author bytes require a follow-up check, and the current review must not be represented as approval of an unseen replacement PDF.

## Inspected render hashes

| Page | SHA-256 |
|---|---|
| `page-01.png` | `97bc37a2dc3de2c69bef64b8c54288c9f267e38bcc9dbd4757a2086a9295eb07` |
| `page-02.png` | `83404a79038b2395b1aa00bd0d74e66cc127598b8c9c7c4b74e16f238cec8960` |
| `page-03.png` | `04dc9cc5e53a8f4e739743b48541fa26c556aacafc225c59fb80a262be8c7476` |
| `page-04.png` | `ecbc8c3d2791bd2e9bfffa185d0949b5f8bbe9a45795e191a652bda468007bfc` |
| `page-05.png` | `1087572629c4f735e29e9adc95d144a06048da7b3b21fb5cb80045c878323996` |
| `page-06.png` | `1e8baa52b9d08636012b19d1b0b24d283a7d5369492b309de313486f3f88b398` |
| `page-07.png` | `39647d0cff64a85da455f5984964acc06688d4e7c3c2df357d33709dde852242` |
| `page-08.png` | `39488aaff4f1a038e0ed251474834eeb138b97f131b8e5549e82365ef2d42613` |
| `page-09.png` | `513297432c738e756338222fe8b0739d8bd7f4113a4bcd6200d38dc9144270e8` |
| `page-10.png` | `ef720f6652ca4b8894997a1a2f3d503d3f95c413e230a6fa4c53e0d403664a34` |
| `page-11.png` | `49a8c61d657120f5b464d4768ae4902107d49b51849b64191926f06f3d36fa45` |
