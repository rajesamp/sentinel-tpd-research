# Corpus provenance and frozen fixture contract

The study uses two separate datasets: the original paper's referenced fuzzd
source records, acquired locally at a fixed commit, and a redistributable corpus
of newly authored challenges. Source and challenge results must retain separate
denominators. Labels express the respective authors' intended fixture semantics;
they are not an oracle of actual agent harm, trusted-server identity, or successful
exploitation. No embedded instruction is executed.

## Pinned source and redistribution decision

Repository: [ksek87/fuzzd at the pinned revision](https://github.com/ksek87/fuzzd/tree/f739e120cd7dc253fead2a1f13668f9535e4d8a5).
Commit: `f739e120cd7dc253fead2a1f13668f9535e4d8a5`; recorded commit time:
`2026-06-15T22:29:22-04:00`; Git tree:
`ffa7b991501835028ef8d0fbc8ce82a684c2f52e`.

The exact source includes 24 records at `corpus/tool_poisoning/TPA-001.json`
through `TPA-024.json`, three at `corpus/tool_shadowing/TS-001.json` through
`TS-003.json`, and 20 complete benign tool definitions in `bench/clean_tools.json`.
The benign objects have no source case IDs: `BENIGN-001` through `BENIGN-020` are
explicit study-assigned, stable one-based array indices. Attack IDs are unchanged.
The unrelated rug-pull records and MCPTox 485-tool benchmark are not included or
silently added to these denominators.

The pinned [Cargo.toml](https://github.com/ksek87/fuzzd/blob/f739e120cd7dc253fead2a1f13668f9535e4d8a5/Cargo.toml)
declares `MIT`; the pinned [README](https://github.com/ksek87/fuzzd/blob/f739e120cd7dc253fead2a1f13668f9535e4d8a5/README.md)
also identifies MIT licensing. However, the complete pinned tree has no license,
copying, copyright, or notice file, and no separate corpus license was located.
This is recorded as MIT intent with missing license-text evidence, not as a claim
that the authors declared their repository unlicensed. The agreed conservative
distribution choice is to omit external payloads from the artifact and provide a
pinned local-acquisition script. No absent copyright holder or license notice is
invented. Any later permission or license clarification must be recorded as a
separate source rather than retroactively asserted for this revision.

`data/source-manifest.json` publishes source IDs, labels, family counts, source
paths, payload character/byte counts, SHA-256 digests, Git blob SHA-1 identities,
and fixed raw-source URLs. It contains no external attack payloads or complete
benign descriptions. Thirty source files are fixed: 27 attack records, one benign
array, and the two licensing-evidence files. Raw and normalized source data remain
in ignored local paths:

- `data/source-cache/`
- `data/corpus-source.local.json`
- `data/corpus-combined.local.json`

Exporters must explicitly exclude those paths and all `data/*.local.json` files;
Git ignore rules alone are not a redistribution policy for arbitrary ZIP tools.
The files intended for distribution are `data/corpus.json`,
`data/build_challenges.py`, `data/fetch_source.py`, `data/source-manifest.json`,
and `data/.gitignore`, alongside separately owned study inputs such as lifecycle
fixtures. Published scanner outputs should preserve metrics, offsets, labels,
source IDs, and hashes while omitting copied external payload excerpts.

## Actual source taxonomy

The pinned source has **15** poisoning subcategory labels, not 12. Grouping some
of them in narrative prose does not reduce the source's actual family count.
All 15, plus all three shadowing labels, are retained in the authored challenges.

| Poisoning family | Exact source IDs |
| --- | --- |
| `explicit_trigger_hijacking` | TPA-001–004 |
| `implicit_trigger_background_hijacking` | TPA-005–008 |
| `persistent_instruction_injection` | TPA-009–012 |
| `unrelated_prerequisite_injection` | TPA-013 |
| `fake_enabling_prerequisite` | TPA-014 |
| `argument_hijacking` | TPA-015 |
| `xml_tag_injection` | TPA-016 |
| `fake_system_tag_injection` | TPA-017 |
| `parasitic_toolchain` | TPA-018 |
| `cross_tool_exfiltration` | TPA-019 |
| `message_hijacking` | TPA-020 |
| `unicode_obfuscation` | TPA-021 |
| `response_context_invalidation` | TPA-022 |
| `forced_reexecution_loop` | TPA-023 |
| `annotation_deception` | TPA-024 |

The three shadowing families are `name_squatting` (TS-001),
`capability_override` (TS-002), and `typosquatting` (TS-003).

## Normalization lineage and scope

The source attack files are attack records, **not complete MCP Tool definitions**.
The 47 normalized cases must not be described as 47 unmodified source tool
definitions. Each case preserves source identity, complete source-file hash,
source injection point, exact payload, and an explicit projection descriptor.
The raw records remain locally available for checking that mapping.

- TPA-001–021: the exact source payload becomes `tool.description` in an authored
  inert envelope with a deterministic fixture name and empty object input schema.
- TPA-022–023: the source injection point is `tool.response`. For the declared
  static-text assay, the exact response payload is also projected into the
  descriptor's description. `response_text` preserves the response payload,
  `projection=response_payload_projected_to_description`, and
  `native_metadata_applicable=false`. A detector hit here is recognition of that
  text under the projection, not demonstrated runtime-response inspection.
- TPA-024: the exact source JSON payload supplies the annotation values. Because
  the record provides no complete tool definition, an explicitly authored
  description supplies a destructive operation to make the contradiction
  inspectable. `projection=original_annotations_with_authored_destructive_description`
  and `authored_context=true`. This is a source-derived contradiction fixture,
  not a recovered original full descriptor or a test of confirmation dialogs.
- TS-001 and TS-003: authored/inferred names and explicit trusted-peer context
  turn the source's name-oriented scenario into a tool fixture. The exact source
  payload remains the description. These cases require contextual interpretation;
  a metadata scanner alone cannot authenticate the claimed server origin.
- TS-002: the exact payload remains the description; a declared peer and host
  authorization context are added explicitly.
- All 20 benign entries: complete source tool objects are copied without changing
  fields, including the original fixture `_meta.is_attack=false` field. Detector
  implementations must not use fixture-label metadata as their answer.

Case-level `tool_sha256` hashes are computed from canonical, key-sorted UTF-8 JSON.
The original source-file digests use original bytes. The source manifest lists
both raw-file lineage and, for each benign array element, its canonical object
hash. Existing outputs are never overwritten by the acquisition script.

## Authored challenge split

`data/corpus.json` contains 70 fixed, newly authored cases: 23 poisoning attacks,
three shadowing attacks, and 44 benign cases. Each of the 18 taxonomy families
has an imperative attack, a security-training quotation, and an administrative
prevention mention. The benign forms deliberately retain suspicious vocabulary
inside a clearly quoted or forbidden behavior. They are intended to expose false
positives rather than guarantee any detector an easy benign set.

Eight additional fixed variants each contain an attack/benign pair: zero-width
Unicode insertion, fullwidth Unicode conversion, XML priority wrapping, XML entity
encoding, argument schema defaults, argument examples, nested schema descriptions,
and annotation text. Arguments/defaults are inert metadata values, not executed
tool calls. Pair IDs and variants are retained so repeated expressions cannot be
mistaken for independent real-world attacks. The combined local corpus has 117
cases, but source47 and challenge70 results must remain separately reportable.

The challenge author had prior knowledge of related Sentinel code from the
earlier lifecycle study. These are specification-aware fixtures, not blinded or
publicly preregistered holdout examples. Their labels and text were frozen before
this study's detector measurements, and no detector outcomes were used to revise
them. A future edit requires preserving the old corpus and recording new hashes.

## Freeze identifiers

| Artifact | SHA-256 |
| --- | --- |
| Published source manifest | `e7a0ff35222a5639584c6acdbec492ceb5762a199b098c905a00a2387b0b5f74` |
| Authored offline corpus | `a26ac0771ea329ec2f7aaf265336afbe318a67e39aef99d97ee8af3ff38dc128` |
| Local normalized source corpus | `d4f37648cc9d16b785e1a6d0164b825057f448f0cfbe181aa1ed8e5b45e9f063` |
| Local combined corpus | `41438f7a9960bae5a3dd8709a27c57df955328ac3d8f689b3f73d2e5ffdab3e1` |

The companion `research/corpus-acquisition.json` records source, licensing,
normalization, validation, and these freeze identifiers in machine-readable form.
The frozen hashes were sent to the coordinator and experiment runner before
headline measurements. A fresh network acquisition independently reproduced both
local normalized corpus files byte-for-byte from all 30 pinned URLs. No attack
instruction, repository executable, or source benchmark shell script was run.

## Acquisition and benchmark commands

From a fresh artifact directory, network acquisition is explicit:

```sh
python3 data/fetch_source.py
```

This validates both SHA-256 and Git blob SHA-1 for every downloaded file before
use, then writes the two ignored local corpus outputs. The URL always names the
fixed revision. With a previously verified cache, use `--offline`. Existing
outputs cause an error rather than silent replacement; supply new `--output` and
`--combined-output` paths if a second preserved derivation is wanted.
The acquisition receipt distinguishes permitted networking from actual use:
`network_allowed` records the selected mode, while `network_files_fetched` and
`network_used` record successful downloads. Both cached modes reproduced the
frozen corpus with zero downloads, and a tampered cache entry was rejected.

The source-based study, retaining the separate challenge split, is run through
the experiment runner's declared interface:

```sh
python3 -m evaluation.run --corpus data/corpus-combined.local.json --lifecycle data/lifecycle.json --output results/source-study-001 --label frozen-source-and-authored
python3 -m evaluation.report results/source-study-001 --output results/source-study-001-regenerated
```

An artifact reviewer without network access can run the authored smoke study:

```sh
python3 -m evaluation.run --corpus data/corpus.json --lifecycle data/lifecycle.json --output results/authored-smoke-001 --label authored-offline-smoke --no-workloads --no-performance
```

The source-specific repeated workload study requires the source split and must
not silently substitute authored cases when source acquisition is unavailable.
These commands document interfaces; this corpus-provisioning task does not claim
to have executed detector measurements or generated benchmark outcomes.
