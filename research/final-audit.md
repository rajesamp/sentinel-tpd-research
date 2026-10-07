# Independent audit of the frozen Sentinel-TPD runs

Both `frozen-001` and `frozen-002` pass this bounded evidence audit. No outstanding material accounting defect was found. The audit reads saved JSON/JSONL directly and does not import evaluation or report functions, rerun the scanner, or execute embedded instructions. It checks the two scored runs against freeze commit `b73b71c3411dbd12b5175a5917d50987a7c00aa5`.

## Evidence integrity

All completion-record hashes, underlying input hashes, canonical provenance digests, saved source-code digests and corresponding Git objects at the freeze commit agree. All 30 acquired source files pass byte-length, SHA-256 and Git blob checks; all 27 source attack IDs/payloads and 20 unchanged benign objects agree with their normalized local cases. All 12 vendored files pass SHA-256 and Git blob checks. The complete machine-readable audit is `research/final-audit.json`.

| Run | Raw JSONL SHA-256 | Completion SHA-256 |
|---|---|---|
| frozen-001 | `4c4a2b0bfe50dce332f5277469c4969e8e171b47808c1b7028d20cb6be86c2fd` | `03d4fe7408616f1d8e1c3e17713bafe09b2bf1b284d8c4bb7f4fa2c12987f37c` |
| frozen-002 | `c565fdec29d5cf2ab08facf711e6c67dd9d533530c04f467a4f54ed972152c71` | `d7ac6542f010ef15d6caf70325aa84c688929e0657013ce228efdf5b9382dd4c` |

Each session contains exactly 468 unique-case records (117 cases × four methods), 3,000 repeated workload calls (three kinds × 1,000 calls), 60 lifecycle records (15 cases × four methods), and 1,200 performance records (five sizes × 60 pairs × two methods × two measurement types). Both runs completed with zero execution errors. All distinct case/method keys and exact workload schedules were checked.

## Recomputed static outcomes

The source denominator is 24 poisoning, three shadowing and 20 benign cases. The authored denominator is 23 poisoning, three shadowing and 44 benign cases. Every split/family confusion matrix, warning count, scanner denial, receipt count and rate in the saved summaries was independently recomputed. The three scanner-based methods have identical static outcomes; their lifecycle policies remain different.

| Split | Method | Kind | Cases | Rule-hit attacks | Prevented attacks | Benign receipts |
|---|---|---|---:|---:|---:|---:|
| source | allow_all | poisoning | 24 | 0/24 | 0/24 | 0/0 |
| source | allow_all | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| source | allow_all | benign | 20 | 0/0 | 0/0 | 20/20 |
| source | registration_only | poisoning | 24 | 17/24 | 17/24 | 0/0 |
| source | registration_only | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| source | registration_only | benign | 20 | 0/0 | 0/0 | 20/20 |
| source | sentinel_tpd | poisoning | 24 | 17/24 | 17/24 | 0/0 |
| source | sentinel_tpd | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| source | sentinel_tpd | benign | 20 | 0/0 | 0/0 | 20/20 |
| source | rescan_each_call | poisoning | 24 | 17/24 | 17/24 | 0/0 |
| source | rescan_each_call | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| source | rescan_each_call | benign | 20 | 0/0 | 0/0 | 20/20 |
| challenge | allow_all | poisoning | 23 | 0/23 | 0/23 | 0/0 |
| challenge | allow_all | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| challenge | allow_all | benign | 44 | 0/0 | 0/0 | 44/44 |
| challenge | registration_only | poisoning | 23 | 4/23 | 4/23 | 0/0 |
| challenge | registration_only | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| challenge | registration_only | benign | 44 | 0/0 | 0/0 | 37/44 |
| challenge | sentinel_tpd | poisoning | 23 | 4/23 | 4/23 | 0/0 |
| challenge | sentinel_tpd | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| challenge | sentinel_tpd | benign | 44 | 0/0 | 0/0 | 37/44 |
| challenge | rescan_each_call | poisoning | 23 | 4/23 | 4/23 | 0/0 |
| challenge | rescan_each_call | shadowing | 3 | 0/3 | 0/3 | 0/0 |
| challenge | rescan_each_call | benign | 44 | 0/0 | 0/0 | 37/44 |

All-source scanner/native prevention is 17/27 with 20/20 benign receipt completion. Authored scanner/native prevention is 4/26 with 37/44 benign receipt completion: seven intended-benign controls are blocked. These are observations against fixture-intent labels, not evidence of live exploit success or real agent harm.

The native-applicability subset excludes exactly `TPA-022`, `TPA-023` (response payloads projected into descriptions), and `TS-001`, `TS-003` (name/peer-context projections). It contains 43 cases: 23 intended attacks and 20 benign tools. Native prevention is 16/23 and benign completion is 20/20. The two response projections contribute one blocked case; neither name-context projection is blocked. `TPA-024` remains an explicitly source-derived annotation fixture with an authored destructive description; inclusion does not imply annotation scanning or recovered original descriptor behavior.

## Repeated workloads and lifecycle

All 15 source workload schedules match independently reconstructed sorted-ID round-robin streams, including exact repetition counts and remainder weighting. All workload outcome tables and decision/sink timing distributions agree with the raw rows. Repetitions provide no new independent attack templates.

All 60 lifecycle records per session match their ordered frozen steps, tool hashes and declared policy references. Expected outcomes were read from `data/lifecycle.json`; actual outcomes were recomputed from local receipts. Every saved lifecycle summary entry agrees. Native mismatches are:

| Case | Observed receipt | Interpretation |
|---|---:|---|
| LC-12, top-level title change | 1 | Exceeds the published fingerprint fields; mismatch with the stronger host metadata policy. |
| LC-13, annotation change | 1 | Exceeds the published fingerprint fields; mismatch with the stronger host metadata policy. |
| LC-14, malformed schema | 1 | Source-contract probe: schema validity is not enforced by this admission path. |

These local observations are not novel security primitives or demonstrated remote exploits. Other native lifecycle expectations match their declared policy. The audit does not independently reconstruct native audit chains from exported events; it checks the recorded verification booleans and state consistency.

## Performance and independent sessions

For each size and measurement type, each run retains ten warmup pairs and 50 measured pairs. Every sample has exactly N local receipts in both arms; native audit-entry counts are N+1 and control counts are zero. Pair identities, method-order consistency, fixture hashes, timing arithmetic, allocation arithmetic and paired differences pass. Mean, median, nearest-rank p95, min and max were independently recomputed; warmups are excluded from reported measured distributions.

The 3,528 non-performance records match exactly across sessions after removing only `run_id`, `process_session`, `registration_ns`, `decision_ns`, `decision_to_local_sink_ns`, and `audit_head`. Audit heads are cumulative hashes of timestamped entries, so equality is not expected across process sessions. All other saved states, audit counts, verification booleans, findings, decisions and receipts remain in the comparison. The normalized SHA-256 is `2708da2d88645d8ed329a54bda97bdb49bec59560ac651ed3ba6801a4fca68ee` in both sessions.

All 1,200 performance receipt/status identities also match across sessions. Timing, allocation observations and randomized method order are not required to match. The two sessions use different random seeds. These measurements describe local cached checks and audit work against a small inert allow-all denominator; batch-per-call p95 is not individual-request tail latency, and Python allocation peaks are not RSS. Two sessions provide no production-overhead or population-reliability guarantee.

## Public output sanitation

All seven files in each result directory were inspected. No native excerpt, source payload or response-text field is serialized. No exact source substring of at least 60 characters, complete source description/payload string of at least 20 characters, or absolute user/temp path was found. Receipt bodies were decoded and verified to contain only the fixed request structure, tool name and empty arguments; metadata descriptions are absent. Published source-file/commit/index and authored pair/variant/surface lineage is retained. This bounded scan does not prove absence of paraphrased or encoded copies.

## Decisions and limits

Keep source/challenge, unique/repeated, and native/projection denominators separate. Use local receipt observations for enforcement accounting. Do not pool sessions into invented independent security trials, treat local labels as semantic ground truth, or turn above-policy lifecycle mismatches into upstream exploit claims.

This audit covers the two saved frozen runs. It does not certify subsequent packaging, a Python 3.14 wrapper replay, live model/tool selection, remote MCP effects, runtime-response protection, or unseen attacks. Hashes bind saved local evidence; they are not third-party attestation. Fixture authors had relevant prior knowledge, and the study has no blind holdout.

Machine-readable audit SHA-256: `b278a588d3cf0ba5993bb665269465e104996146e77fa27fcec7d9281f4140ba`.
