# Original-manuscript coverage and implementation boundary

Audit date: 2026-10-06. This dossier preserves the original research questions, named attack patterns, architecture, equations, metrics and 24-reference lineage. It distinguishes preservation from validation: the original manuscript is a source of proposed claims, while pinned code and new experiment records are the evidence for implementation and measured outcomes.

The extracted input is `/private/tmp/runtime-paper-coverage-20261006.txt`, SHA-256 `67b01e9bdd1583430c193639ea6ab19448dd4d3a9fa6bf6190de55ac9bb11e8e`. Scientific manuscript content occupies original PDF pages 4–9. Pages 1–3 are similarity-report material; its similarity percentage does not establish scientific novelty or correctness.

## Pinned evidence and terminology

The subject is [Sentinel-TPD at 5ce5d56e57a0acd092435fca5d89b78d0b39ee7b](https://github.com/rajesamp/sentinel-tpd/tree/5ce5d56e57a0acd092435fca5d89b78d0b39ee7b). Exact file digests are in `vendor/manifest.json`. Relevant files are `sentinel_tpd/signals.py`, `scanner.py`, `registry.py` and `audit.py`.

The external source is [fuzzd at f739e120cd7dc253fead2a1f13668f9535e4d8a5](https://github.com/ksek87/fuzzd/tree/f739e120cd7dc253fead2a1f13668f9535e4d8a5). `data/source-manifest.json` records exact files, hashes, labels and provenance. It contains 24 poisoning records, three shadowing records and 20 benign tools. The 24 poisoning records have **15 category labels**. The original manuscript names twelve of those categories, corresponding to TPA-013 through TPA-024. TPA-001 through TPA-012 contribute three additional categories with four records each. Do not rename all 24 records as twelve categories.

Corpus labels describe author-supplied attack intent. A scanner match is not evidence that an agent followed an attack, that a semantic family was recognized generally, or that an external side effect was prevented. Use raw new experiment records for findings; the code mapping below is a static coverage hypothesis.

The repository package and README declare MIT, but the pinned tree has no LICENSE/COPYING/NOTICE file or corpus-specific license text. The study records that evidence without claiming a resolved redistribution grant. External payloads and normalized records are acquired locally from pinned sources and excluded from the distributed artifact; source hashes and the acquisition procedure are distributable. The separately authored challenge cases can be distributed.

## All twelve original poisoning patterns

Signal names below refer to the ten actual rules, not twelve separate family detectors. Every row is retained even where no direct detector exists.

| Original pattern | Pinned source record / label | Actual candidate overlap | Boundary or missing mechanism |
|---|---|---|---|
| Unrelated prerequisite injection | TPA-013, `unrelated_prerequisite_injection` | Direct-model address, priority claim, sensitive path, or exfiltration wording may match. | No prerequisite/dependency reasoner; arbitrary prerequisite semantics are not classified. |
| Fake enabling prerequisites | TPA-014, `fake_enabling_prerequisite` | The same imperative or priority-language rules may match literal phrases. | Does not establish whether a claimed prerequisite is necessary or genuine. |
| Argument hijacking | TPA-015, `argument_hijacking` | Parameter-smuggling rule recognizes requests to include full conversation/context or similar phrases. | No general argument-authority model, runtime argument binding, or validation of call arguments against an approved request. |
| XML-tag injection | TPA-016, `xml_tag_injection` | Imperative-tag rule recognizes selected names such as important, system, instruction, admin and hidden. | Not a general XML parser or instruction/data separation mechanism; arbitrary tags are not covered. |
| Fake system-tag injection | TPA-017, `fake_system_tag_injection` | Imperative-tag rule includes selected angle-bracket and bracketed instruction/system forms. | Only scanned strings and exact regular-expression families are checked. |
| Parasitic toolchains | TPA-018, `parasitic_toolchain` | Cross-tool steering and priority wording may match. | No toolchain graph, dependency verification, or runtime call-sequence analysis. |
| Cross-tool exfiltration | TPA-019, `cross_tool_exfiltration` | Cross-tool steering, sensitive paths, parameter smuggling and explicit exfiltration destination rules may match. | No inter-tool data-flow tracking or external transmission observation. |
| Message hijacking | TPA-020, `message_hijacking` | Direct-model address and cross-tool/future-message steering may match. | No message-origin or message-integrity proof. |
| Unicode obfuscation | TPA-021, `unicode_obfuscation` | An untouched suspicious phrase might still match another rule. | No Unicode normalization, confusable matching, or deobfuscation. Base64-like blob detection is a different, weaker signal. |
| Response injection | TPA-022, `response_context_invalidation` | Suspicious text included in a scanned descriptor may match existing lexical rules. | Actual tool-result/response content is not a scanner input. Keep the original name and the source label distinct. |
| Forced re-execution | TPA-023, `forced_reexecution_loop` | Some commands may overlap direct-address or priority expressions. | No loop monitor, invocation counter, or repeated-call behavioral detector. |
| Annotation deception | TPA-024, `annotation_deception` | A suspicious phrase duplicated into a scanned description may match. | Top-level MCP annotations are neither text-scanned nor included in the canonical metadata fingerprint. No annotation-trust interpreter. |

Additional pinned source families, retained as a corpus expansion: `explicit_trigger_hijacking` (TPA-001–004), `implicit_trigger_background_hijacking` (TPA-005–008), and `persistent_instruction_injection` (TPA-009–012). They are not additional implemented rule classes. Their lexical matches must be measured per record.

## All three original shadowing patterns

| Original pattern | Pinned source record | Actual mechanism | Boundary |
|---|---|---|---|
| Name squatting | TS-001, `name_squatting` | Registry entries are keyed by a tool's bare name. Metadata is fingerprinted. | A bare-name key is not provider identity authentication or a name-squatting detector. Registration collision/replacement must be tested separately. |
| Capability override | TS-002, `capability_override` | Explicit priority/cross-tool claims may match lexical rules. | No semantic capability comparison or authorization ordering between providers. |
| Typosquatting | TS-003, `typosquatting` | Name is one scanned text field. | No edit-distance, confusable-name, namespace, or trusted-name similarity detector. |

A high detection fraction on the three source records would describe those records' wording. It would not prove general shadowing detection; benign-looking collision and name-variation controls are necessary to assess the missing identity mechanism.

## Ten implemented signals and policy

| Signal ID | Severity | Implemented evidence |
|---|---:|---|
| TPD-IMPERATIVE-TAG | M4 | Selected instruction/system/important/admin/hidden tags and selected bracket forms |
| TPD-DIRECT-MODEL-ADDRESS | M3 | Selected direct instructions to the model/assistant and “ignore previous” variants |
| TPD-CONCEALMENT | M4 | Selected instructions to hide activity from the user |
| TPD-PRIORITY-CLAIM | M3 | Selected override, precedence and before-anything-else claims |
| TPD-SENSITIVE-PATH | M3 | Selected credential paths and secret-related terms |
| TPD-CROSS-TOOL-STEER | M3 | Selected instructions controlling other tools or subsequent messages/calls |
| TPD-PARAM-SMUGGLE | M3 | Selected requests to pass full conversation, context or system prompts |
| TPD-EXFIL-DEST | M4 | Selected send/post/upload/email verbs near a URL or email destination |
| TPD-ENCODED-BLOB | M2 | Long base64-like substrings; no decoding or semantic inspection |
| TPD-URGENCY | M1 | Selected threatening or urgent language |

Rules use regular expressions with case-insensitive and dot-all matching. The scanner examines top-level `name` and `description`, and recursively examines `description` and `title` strings under `inputSchema`/`input_schema`. It does not scan top-level title, annotations, outputSchema or tool results. Fingerprinting and text scanning have different coverage: the canonical metadata includes name, description and the input-schema object, whereas text matching only visits the listed text-bearing fields.

The verdict is the **maximum** matched severity. At the default `deny_at=3`, severity M3 or M4 denies and M1/M2 alone allows. Multiple weak findings do not accumulate into a stronger score. A finding and a denial are separate measurements. A configurable threshold means a prose statement that M4 is “never overridable” is not an independently enforced invariant across arbitrary caller configuration.

## Original architecture preserved with implementation status

The original eight-module pipeline is retained as a design vocabulary. The new paper should show the implemented path clearly and label the remaining blocks as external integration or proposed extensions.

| Original module | Pinned implementation status | Accurate paper language |
|---|---|---|
| MCP Client | External integration point | A host calls this local Python library; the pinned package is not an MCP client or proxy transport implementation. |
| Metadata Analysis | Implemented in selected fields | Scanner walks named text fields; canonicalization serializes a selected metadata projection. |
| Poisoning Detection | Implemented lexical signals | Ten deterministic regular expressions produce findings and maximum severity. |
| Shadowing Detection | Partial lexical overlap only | Explicit cross-tool/priority wording can be detected; identity and name-similarity models are absent. |
| Runtime Monitor | Limited lifecycle checks | Registry admission and pre-invocation fingerprint comparison, plus refresh and quarantine handling; no general execution-behavior monitor. |
| Threat Assessment | Implemented threshold policy | Maximum severity is compared with a configurable threshold; original weighted scores are not implemented. |
| Policy Enforcement | Local allow/deny and registry quarantine | Host must honor the verdict. Quarantine is a registry state, not process isolation or sandboxing. |
| Security Log | Implemented hash-chain audit records | Hash-linked events in memory and optional JSONL; not immutable storage or independent anchoring. A writer with full control can reconstruct a chain. |

Canonical metadata SHA-256 values support comparison within a process. They are not signatures, authenticated server identity, complete descriptor/request binding, or proof of authorization. The registry stores entries by name; it does not bind execution arguments, principal identity or a complete MCP call to an approval. Registration checks and caller dispatch are separate actions.

Refresh rebuilds the registered set from current descriptors. A clean descriptor can lift a prior quarantine. This is actual behavior to measure; do not silently reinterpret it as persistent revocation or ABA-safe authorization. The separate dispatch-conformance artifact studies a different, stronger contract and remains a separate artifact.

## Original equations preserved as proposals

| Original expression | Original intent | Status in the pinned implementation |
|---|---|---|
| Metadata tuple \(M_i=\{N_i,D_i,C_i,P_i,R_i\}\) | Names, descriptions, capabilities, parameters and relationships | Only name, description and input-schema data have concrete canonical fields; capabilities and relationships are not distinct structured analyses. |
| Poisoning score \(R_p=\sum_j w_jx_{ij}\) | Weighted suspicious features | Not implemented. The scanner uses maximum severity, not a weighted sum. |
| Shadowing score \(R_s=\alpha S_n+\beta S_c+\gamma S_t\) | Name, capability and context similarity | Not implemented. No corresponding similarity functions or fitted coefficients are present. |
| Combined score \(R=\lambda R_p+(1-\lambda)R_s+\delta B\) | Combine poisoning, shadowing and behavioral risk | Not implemented. There is no execution-behavior term or calibrated combined score. |

These equations may appear in a clearly labelled design-proposal appendix to preserve the original research trajectory. They must not be the explanation of measured Sentinel-TPD verdicts. No data in this dossier establishes trained weights, calibrated probabilities or learning across workload sizes.

## Original metrics and operational definitions

| Original metric | Preserve the question | Required interpretation for reproducible measurements |
|---|---|---|
| Tool Poisoning Detection Rate (TPDR) | How many labelled poisoning cases are flagged? | Define finding-based detection separately from threshold denial. State denominator, source/challenge split and case counts. A descriptor verdict is not live-agent attack prevention. |
| Tool Shadowing Detection Rate (TSDR) | How many labelled shadowing cases are flagged? | Keep the three source labels distinct from identity/lifecycle controls. Do not infer semantic shadowing coverage from lexical wording in three records. |
| Response time, mean of \(t_{detect}-t_{invoke}\) | What is the processing latency? | Original post-invocation phrasing does not describe admission scanning. Name each measured boundary: metadata scan, registration, pre-invocation check or refresh. State clock, repetitions, warmup, host and summaries. |
| Attack Blocking Rate (ABR), \(N_b/N_d\) | How often are detected attacks blocked? | This conditions on detection; it is not denied/all malicious. When the same local verdict implements detection and block, it can be tautological. Report counts and a denominator that matches the claim. |
| Runtime Security Overhead (RSO), \((T_s-T_b)/T_b\) | Added work relative to a baseline | Use paired measurements with identical workload and boundary. A faster lexical ablation is not an unsecured full-agent baseline. |
| Memory overhead | What storage/allocation burden is introduced? | Name the measured quantity (e.g. Python allocation peak or process RSS), baseline and units. Do not rename traced Python bytes as total process memory. |

TPDR uses detected poisoning divided by total poisoning; TSDR uses detected shadowing divided by total shadowing. The original prose has an inconsistent numerator around the shadowing discussion; preserve the intended metric from its table, not an apparent typesetting error. The new paper should report benign false positives as well as malicious-label recall; the original list alone does not measure useful preservation.

## Historical numerical claims: retained, not reproduced

The following ledger preserves the original Tables III–VII. These numbers are **not new experimental results** and must not populate the new results section. No accompanying raw logs, exact workload-generation schedule, hardware configuration or seeds were available in the original PDF.

| Original table / quantity | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---|---:|---:|---:|---:|---:|
| III: poisoning attempts | 100 | 150 | 200 | 250 | 300 |
| III: poisoning detections | 91 | 139 | 188 | 238 | 288 |
| III: reported TPDR (%) | 91 | 92.7 | 94 | 95.2 | 96 |
| IV: shadowing attempts | 100 | 150 | 200 | 250 | 300 |
| IV: shadowing detections | 89 | 137 | 185 | 235 | 285 |
| IV: reported TSDR (%) | 89 | 91.3 | 92.5 | 94 | 95 |
| V: mean response (ms) | 42 | 39 | 36 | 33 | 30 |
| V: minimum response (ms) | 35 | 33 | 30 | 28 | 25 |
| V: maximum response (ms) | 50 | 47 | 44 | 40 | 37 |
| VI: detected attacks | 91 | 139 | 188 | 238 | 288 |
| VI: blocked attacks | 84 | 130 | 178 | 228 | 278 |
| VI: reported ABR (%) | 92.3 | 93.5 | 94.7 | 95.8 | 96.5 |
| VII: baseline execution (ms) | 100 | 125 | 150 | 175 | 200 |
| VII: secured execution (ms) | 108 | 134 | 160 | 184 | 209 |
| VII: reported runtime overhead (%) | 8 | 7.2 | 6.7 | 5.1 | 4.5 |
| VII: reported memory overhead (%) | 5.2 | 4.8 | 4.4 | 4.0 | 3.7 |

The original levels increase the number of attempts; repeated execution alone does not make a deterministic scanner learn. Claims that sensitivity improves with workload scale require a documented change in inputs, parameters or learning mechanism. These monotonic trends cannot be attributed to the pinned implementation from the available evidence.

## Original references and new direct comparators

All 24 old references are retained in `reference-audit.md` and `sources.json`. BibTeX keys `orig1`–`orig20` preserve scholarly-reference numbering; `fuzzd`, `fuzzdpoison`, `fuzzdshadow`, `mcptoxrepo` preserve originals 21–24. Version corrections are explicit, including two omitted authors and article-number/page-number distinctions.

Originals 1–9 and 13 provide direct MCP/agent context. Originals 10–12 and 14–20 are adjacent methodology or governance, retained in an appendix with domain and transfer limits. They do not establish the efficacy of this scanner, and their methods are not claimed as implemented merely because the original prose used “adapted” or “applied.”

Added direct references are published MCP-Guard, the versioned MCPShield preprint and versioned Semantic Attacks on Tool-Augmented LLMs. They prevent an unsupported claim that static metadata analysis, staged screening, descriptor integrity or runtime defense is new. ETDI, Handle-Capability Protocol, attested server admission and protocol specifications supply related identity/control boundaries. Incremental scope is a transparent, pinned implementation study and controlled negative findings; no new security primitive or first-analysis claim is established here.

The original MCPTox “485 attack definitions across 45 servers” statement is not validated. The published AAAI record reports 1,348 malicious test cases, 353 tools and 45 servers; the older arXiv abstract reports 1,312 cases. Definitions, tasks, tools and servers are different counting units. No MCPTox records were fetched as part of the new measured source corpus.

## Coverage gaps and use constraints

- This is a targeted preservation audit, not an exhaustive review or independent human peer review.
- Most original references were checked for bibliographic identity; exact method-reading scope is recorded per source. Do not expand abstract-level verification into a claim of reproduced methods.
- No third-party defense was run or benchmarked. Cross-paper rates use different corpora, models, boundaries and cost measures.
- Static code overlap is not measured per-family success. New case-level results and controls own that evidence.
- Original result tables remain unverified; preserving their record is not endorsing their scientific validity.
- Corpus-label breadth does not resolve the absence of runtime response, semantic-name, provider-identity or behavioral analysis.

