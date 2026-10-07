# Independent critique of the revised Sentinel-TPD manuscript

Review date: 2026-10-06. Scope: `manuscript/paper-body.tex.in`, pinned Sentinel-TPD source and manifest, measurement/provenance records, original-coverage dossier, original manuscript extraction, and selected evaluator code needed to check claimed measurement boundaries. No experiments were scored or rerun. No new bibliography search or publication action was undertaken. This file is the reviewer's only modification.

Pinned implementation inspected: `5ce5d56e57a0acd092435fca5d89b78d0b39ee7b`. The template contains substitution markers, including results, corpus protocol, metrics, timing, and appendix tables. This review therefore does not validate a completed manuscript's numerical claims or rendered layout.

## Overall judgment

The current revision substantially repairs the original manuscript's methodological description. It follows the original five-section structure, names all twelve original poisoning patterns and three shadowing families, and retains the six original measurement questions with revised operational definitions. It accurately describes the implemented maximum-severity rule, selected-field scan, three-field fingerprint, name-indexed registry, refresh/quarantine behavior, and local enforcement boundary. It is particularly good that missing semantic shadowing, response inspection, behavior monitoring, isolation, and provider authentication are explicit limitations rather than invented implementation features.

The present supported contribution is a **reproducible characterization of one fixed implementation plus controlled counterexamples**, not a demonstrated new general runtime defense. Full conference formatting is feasible. A competitive full security research contribution has not yet been established merely by preserving sections, running fixed cases, or publishing an artifact. The paper needs a sharper independently useful finding and stronger evidence for its importance; no acceptance prediction follows from this review.

## Preservation and source alignment

| User's intended continuity | Current status | Integration obligation |
| --- | --- | --- |
| Twelve poisoning patterns | All are named in Section I; source coverage maps them to TPA-013–024. | The generated appendix must show every named pattern and the actual observable mechanism or absence, with source-derived decisions separated from semantic success. |
| Three shadowing families | Name squatting, capability override, and typosquatting remain explicit. | Keep per-family rows even when only lexical overlap is measurable. Do not promote the cross-tool steering regex into a general shadowing detector. |
| Source composition | Provenance fixes 24 poisoning records, three shadowing records, and 20 benign tools. | Describe normalized/projected records accurately; these are not 47 unmodified MCP tool definitions. |
| Taxonomy precision | The source has 15 poisoning labels; the original narrative names the last twelve. | Preserve this distinction rather than saying the twelve names are merely an arbitrary regrouping of all 24 records. The first twelve records contribute three additional labels. |
| Six original study metrics | Detection, shadowing detection, response cost, conditional blocking, runtime overhead, and memory cost are retained. | Explicitly state where the measurement has changed, especially detection versus admission findings, local invocation-check time, and traced Python bytes instead of process-memory percentage. |
| Original main section structure | Sections I–V retain the original order and subject. | Preserve the scientific flow while removing repeated draft-history explanations from the final narrative. |
| Original eight architecture functions | Intended generated architecture table plus source-coverage dossier distinguishes implemented, partial, and external components. | Check the substituted table; the template alone cannot confirm its entries. |
| Actual Sentinel implementation | Ten fixed rules; maximum severity; default threshold three; partial fingerprint and raw-name registry are faithfully described. | Keep unimplemented weighted scores as historical design proposals only, if retained at all. |

## Prioritized material issues

### 1. High: the full-conference contribution needs a falsifiable finding beyond faithful implementation description

**Location:** Abstract; Section I, “Research questions and contributions”; Sections IV–V.

The manuscript honestly says its contribution is an implemented-system characterization, and disclaims novelty of the underlying ingredients. That is preferable to inventing novelty, but the paper does not yet identify the important new conclusion a security researcher should learn from studying this particular library. The same author developed Sentinel; the fixtures are visible and specification-aware. Pinning and reproducibility make evidence checkable but do not establish a research contribution on their own.

**Feasible strengthening:** articulate a narrow candidate finding around the difference between (a) text fields inspected, (b) fields fingerprinted, and (c) metadata and context consumed by an integrating host. Use matched transformations and lifecycle examples to show exactly which obligations fail at each boundary. This is a candidate study structure, not an assertion that the idea is novel. Establish originality against the closest inspected work before making any first/new claim.

For a stronger full research paper, add independent evidence of consequence and generality: another real host integration, independently adjudicated examples, or comparable implementations with different scanning/fingerprinting boundaries. If that work is absent, position the existing evidence as a bounded case study and artifact contribution. A longer literature review or more repetitions of the same fixtures will not close this gap.

### 2. High: “valid call” and “benign completion” overstate the actual receipt experiment

**Location:** Template Section IV, comparison arms around lines 267–272; metrics around lines 283–287; timing around lines 302–308. See `evaluation/run.py::_benchmark_setup` and the measurement protocol's receipt boundary.

The template calls the operation a “fixed benign call” and calls performance a “paired valid-call benchmark.” The evaluator serializes an empty argument object and appends an inert local receipt. It does not validate that object against each input schema or execute the intended tool. Some fixture tools require arguments. Consequently, admission and enqueue can be observed without establishing a valid request or successful benign task.

**Required wording repair:** use “inert local enqueue” or “admitted-definition call-check benchmark.” Name the utility proxy “benign-labelled definition enqueue rate” or define “local completion” prominently as one expected inert receipt. Do not let it become ordinary task-completion rate in captions, abstract results, or conclusion. This does not invalidate the local metadata-policy experiment; it corrects its unit.

**Stronger alternative:** author valid, schema-checked benign arguments and deterministic benign tool implementations, then measure task completion separately. That requires new evidence, not a relabeling of current receipts.

### 3. High: projected source records must remain distinguishable in every headline result

**Location:** Sections I, III “Shadowing, identity and scope,” IV “Inputs”; `research/corpus-provenance.md`; `evaluation/report.py` native-subset filtering.

The provenance work correctly identifies response-payload projection for TPA-022/023, authored descriptive context for TPA-024, and contextual/name augmentation for shadowing records. These transformations can change the attack surface. A regex match on a response copied into a description is not native response-injection detection, and a synthetic descriptive phrase is not evidence that annotation inconsistency was detected.

The reporter provides a `source_native_metadata_subset`, and the template says subgroups will be reported. This is good, but the unresolved result/template markers prevent verification that prominent tables and abstract numbers preserve that distinction. A single source-poisoning percentage over all projected records can easily be read more broadly than intended even when a limitation later explains the projection.

**Integration requirement:** show native-applicable and projected/context-augmented subgroup denominators alongside the complete source assay, with explicit record IDs. For the original twelve-pattern matrix, mark each row as native text scan, projected text assay, contextual identity scenario, or unsupported runtime surface. Keep source, authored challenge, lifecycle, and repeated-workload denominators separate throughout. Reconfirm that the metrics table retains all three shadowing rows rather than presenting only one pooled rate.

### 4. Medium/high: comparison arms answer mechanism-isolation questions, not competitive defense efficacy

**Location:** Section IV “Comparison arms and observed enqueues”; `evaluation/methods.py`; lifecycle protocol.

Registration-only, pinned Sentinel, and rescan-per-call all use the same scanner. On unchanged, newly registered definitions, similar content outcomes are an expected consequence of the design, not independent evidence of robustness. The informative difference is lifecycle state: membership, mutation history, explicit refresh, and what each arm intentionally retains. An invocation denial after an unregistered name is presented does not establish typosquatting recognition.

The lifecycle reference already distinguishes native fingerprint policy from a stronger full-displayed-metadata policy. Preserve that distinction in summaries. A stronger-policy mismatch is an integration requirement or scope boundary; it is not automatically a violated upstream promise. Likewise, an arm explicitly lacking a registry should not be described as unsuccessfully implementing a registry guarantee.

**Feasible strengthening:** present a compact arm-capability matrix, followed by per-lifecycle-policy results. Explain which contrasts isolate current-content scanning, mutation detection, and persistent quarantine. If the final paper claims a detection/cost tradeoff against contemporary defenses, it needs compatible implementations and matched input units; the current four arms cannot support that stronger comparison. At minimum, time registration-only and rescanning as well if their cost tradeoff is part of the research conclusion.

### 5. Medium/high: the original workload sizes are useful continuity controls, but not scalability evidence

**Location:** RQ2; Section IV “Metrics and five workload levels,” timing and allocation; measurement protocol.

The template appropriately explains deterministic round-robin repetition and composition effects. Retaining 100–300 invocations preserves the original study question, but it does not introduce new attacks, more difficult cases, a request-rate experiment, or learning. A static detector's rate at these counts mainly checks stable replay and denominator accounting.

The performance benchmark uses one admitted source-benign definition, one host, within-process pairs, a serial adapter, and native audit growth. Those are valid descriptive boundaries, already disclosed. They do not support general low overhead, scalability, whole-agent latency, or total memory claims. In particular, audit-list growth is part of the measured workload, so per-call cost or allocation changes cannot be attributed solely to classification or hashing.

**Feasible strengthening:** keep the five legacy sizes but make the primary cost analysis vary declared descriptor byte length/schema depth and allow/deny paths. Use separate process sessions and more than one admitted benign descriptor. Keep registration scan, cached invocation, fresh rescan, refresh, audit retention, and local receipt costs identifiable. Report absolute time and traced bytes before percentage overhead. A matched instrumentation-only control can separate audit/storage cost from fingerprint cost if the paper makes that attribution. No confidence interval should treat inner loop calls as independent experimental sessions.

### 6. Medium: the six preserved metrics need a prominent old-question/new-measurement crosswalk

**Location:** Section IV metrics, timing, interpretation; generated `@@METRICS_TABLE@@`.

“Their operational definitions now match the code” is correct, but several are substantively different from the original claims: rule findings arise during registration, repeated call-time checks inspect a cached fingerprint and quarantine state, response time is a local decision interval, and memory is Python allocator observation. Calling all of these preserved metrics without an explicit crosswalk risks suggesting reproduction of the original runtime detection and memory percentages.

**Required integration:** the metrics table should have columns for original question, exact measured event/population, numerator/denominator or timing interval, unit, and what it does not establish. In particular, distinguish TPDR/TSDR based on any rule finding from denial-based recall; identify repeated registration findings as reused observations; retain conditional blocking separately from all-attack local enqueue prevention; and label allocation bytes rather than memory-overhead percentage. Do not reuse the old numerical tables or claim to reproduce them.

### 7. Medium: the final paper should read as a standalone study, not an account of repairing a previous draft

**Location:** Multiple references to “original” studies, patterns, workloads and equations; Section IV preservation subsection; adjacent-work appendix.

The preservation ledger is useful for the author, but repeated explanations of how the paper repairs an earlier draft take space from the actual research result. The same applies to long retention of domain-adjacent references merely because they appeared previously. The template does distinguish their scope correctly; the remaining issue is relevance and presentation, not bibliographic misconduct.

**Feasible strengthening:** retain the five main sections and requested taxonomy, while phrasing the submitted paper's questions directly. Move the old-to-new equation/metric/history map to the companion dossier or a compact appendix. Keep adjacent citations only where they support a specific methodological statement. A focused related-work comparison of actual input surfaces, state handling, evaluation units, and reported guarantees would do more for the research argument than a larger citation count.

## Source fidelity details worth preserving

- `scanner.py` returns maximum finding severity rather than an additive or calibrated risk. Low-severity findings do not accumulate. The template states this correctly.
- Scanning covers top-level name/description and nested schema descriptions/titles, while fingerprinting covers the entire selected input-schema value plus name/description. This difference is scientifically useful and accurately stated.
- The canonical projection uses `inputSchema or input_schema`, so truthiness and the alias affect representation. The implementation uses ordinary Python JSON serialization with `default=str`, not a general canonical-JSON security standard. If the final methods claim exact canonicalization or fail-closed JSON/schema validation, include these details or restrict the claim to the tested JSON inputs.
- The scanner checks dictionary input and a nonempty string name, but does not implement the broadly documented malformed-schema denial. The template appropriately makes this a source-contract probe; do not silently repair the vendor and claim the repaired behavior belongs to the pinned revision.
- Direct `register` and `rescan_on_refresh` differ in quarantine recovery. The manuscript describes that distinction correctly.
- Raw-name lookup and fingerprints do not authenticate providers or bind invocation arguments. The separate dispatch artifact must stay separate, as the template already specifies.
- Hash-linked audit entries provide local consistency evidence; they are not immutable or independently anchored. The current scope language is appropriate.

## Minimum integration checks before calling the manuscript complete

1. Replace all template markers and confirm every retained pattern, architecture component and metric appears in the generated paper.
2. Trace each abstract/conclusion numerical statement to a saved scored run and explicitly named population; do not import development numbers or prior-artifact results by convenience.
3. Correct valid-call/task-completion wording to match inert receipt evidence.
4. Put native/projected/contextual subgroup distinctions next to headline detection numbers.
5. Keep lifecycle results partitioned by native promise versus stronger integrating-host policy.
6. Ensure conference claims remain within one pinned scanner and local harness unless additional integrations/measurements are actually completed.
7. Check final citations and rendering separately; neither is established by this template review.

## Decisions, uncertainty, and coverage gaps

- **Choice:** preserve the original taxonomy and scientific questions while revising claims to actual observations. **Rejected alternative:** preserve unsupported weighted algorithms or historical percentages as though measured. **Reason:** continuity does not justify inventing implementation or evidence.
- **Choice:** assess full-conference substance separately from full-conference format. **Rejected alternative:** declare the paper ready from artifact completeness alone. **Reason:** novelty, importance and generality require an argued contribution and supporting evidence.
- **Choice:** treat scope mismatch and upstream-contract violation separately. **Rejected alternative:** label every full-metadata expectation miss as an upstream vulnerability. **Reason:** the public implementation advertises a particular scanned/fingerprinted projection, while some lifecycle controls intentionally ask for a stronger host policy.
- **Choice:** credit the source-grounded limitations already present. **Rejected alternative:** demand an LLM for every claim. **Reason:** deterministic metadata-policy and lifecycle claims can be studied offline; claims about model susceptibility and harmful remote effects cannot.
- **Uncertainty:** final generated results, populated tables, abstract values, exact native/projected denominators, final bibliography rendering, and any changes made by the coordinator after this reading.
- **Coverage gaps:** no scored experiments, raw-result adjudication, independent human labeling, external novelty survey, full live-host integration, concurrency proof, rendered PDF inspection, or venue-specific submission-policy assessment in this task.
