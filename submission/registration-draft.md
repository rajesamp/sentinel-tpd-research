# Conference registration draft

Title: SENTINEL-TPD: Reproducible Runtime Evaluation of Tool Poisoning, Tool Shadowing, and Metadata Mutation in MCP

Author: Rajeshkumar Sampathrajan. Affiliation: Independent Researcher.

Abstract:

Tool metadata can carry instructions that compete with an agent's task, and a registered definition can change before invocation. These concerns motivate runtime gates, but a returned metadata verdict does not establish semantic attack prevention or safe server behavior. We evaluate SENTINEL-TPD at a fixed source revision, retaining poisoning, shadowing, risk decisions, response cost and blocking as separate study questions. The implementation combines ten deterministic text rules with metadata fingerprints, logical quarantine and a hash-chained audit. Across 47 pinned source templates, the registry prevents local enqueue for 17/27 attack-labeled cases (62.96%), while retaining 20/20 benign enqueues. On 70 authored challenges the corresponding counts are 4/26 and 37/44. All three source shadowing templates are missed. Fifteen lifecycle traces separate covered mutation/quarantine behavior from omitted metadata fields. Two process sessions measure five workloads of 100–300 repeated local calls; session 1 registry median cost is 17.237–17.806 microseconds per call, including audit and receipt storage. The contribution is a source-grounded coverage and lifecycle study with pinned inputs, explicit benign controls, observed local enqueues and regenerable results. The results characterize an implemented metadata gate; model selection, hidden server behavior and process isolation require additional mechanisms and experiments.

Suggested topics: MCP security; tool poisoning; runtime policy enforcement; security evaluation; reproducibility.

Contact email, complete conflicts, originality/exclusivity and publication-clearance declarations require the human author. No portal registration or submission has been performed. The venue must be confirmed before uploading the reviewer package.
