# Sentinel-TPD offline evaluation

Run `frozen-002`; label `frozen-visible-fixtures-repeat`; status **completed**.

Fixture counts: source:benign=20, source:poisoning=24, source:shadowing=3, challenge:poisoning=23, challenge:benign=44, challenge:shadowing=3.

## Unique challenge templates

| Method | Rule-hit attacks | Prevented attacks | Blocked / rule-hit attacks | Benign completed | Allowed warnings | Errors |
|---|---:|---:|---:|---:|---:|---:|
| allow_all | 0/26 (0.0%) | 0/26 (0.0%) | 0/0 | 44/44 (100.0%) | 0 | 0 |
| registration_only | 4/26 (15.4%) | 4/26 (15.4%) | 4/4 (100.0%) | 37/44 (84.1%) | 0 | 0 |
| sentinel_tpd | 4/26 (15.4%) | 4/26 (15.4%) | 4/4 (100.0%) | 37/44 (84.1%) | 0 | 0 |
| rescan_each_call | 4/26 (15.4%) | 4/26 (15.4%) | 4/4 (100.0%) | 37/44 (84.1%) | 0 | 0 |

## Unique source templates

| Method | Rule-hit attacks | Prevented attacks | Blocked / rule-hit attacks | Benign completed | Allowed warnings | Errors |
|---|---:|---:|---:|---:|---:|---:|
| allow_all | 0/27 (0.0%) | 0/27 (0.0%) | 0/0 | 20/20 (100.0%) | 0 | 0 |
| registration_only | 17/27 (63.0%) | 17/27 (63.0%) | 17/17 (100.0%) | 20/20 (100.0%) | 0 | 0 |
| sentinel_tpd | 17/27 (63.0%) | 17/27 (63.0%) | 17/17 (100.0%) | 20/20 (100.0%) | 0 | 0 |
| rescan_each_call | 17/27 (63.0%) | 17/27 (63.0%) | 17/17 (100.0%) | 20/20 (100.0%) | 0 | 0 |

## Repeated source workloads: original Tables III–VI questions

Detection below means any matched rule; prevented means no actual local sink receipt. Denominators are repeated calls, not new templates.

| Kind | Calls | Unique IDs | Rule-hit attacks | Prevented attacks | Blocked / rule-hit attacks | Benign completed | Mean local decision µs | Min µs | Max µs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| poisoning | 100 | 24 | 70/100 (70.0%) | 70/100 (70.0%) | 70/70 (100.0%) | 0/0 | 17.527 | 13.968 | 28.452 |
| poisoning | 150 | 24 | 105/150 (70.0%) | 105/150 (70.0%) | 105/105 (100.0%) | 0/0 | 17.710 | 13.832 | 59.947 |
| poisoning | 200 | 24 | 139/200 (69.5%) | 139/200 (69.5%) | 139/139 (100.0%) | 0/0 | 20.238 | 14.008 | 504.132 |
| poisoning | 250 | 24 | 175/250 (70.0%) | 175/250 (70.0%) | 175/175 (100.0%) | 0/0 | 18.496 | 12.980 | 68.322 |
| poisoning | 300 | 24 | 211/300 (70.3%) | 211/300 (70.3%) | 211/211 (100.0%) | 0/0 | 17.160 | 13.133 | 58.137 |
| shadowing | 100 | 3 | 0/100 (0.0%) | 0/100 (0.0%) | 0/0 | 0/0 | 22.559 | 21.680 | 24.128 |
| shadowing | 150 | 3 | 0/150 (0.0%) | 0/150 (0.0%) | 0/0 | 0/0 | 23.002 | 21.371 | 37.243 |
| shadowing | 200 | 3 | 0/200 (0.0%) | 0/200 (0.0%) | 0/0 | 0/0 | 22.936 | 21.274 | 25.062 |
| shadowing | 250 | 3 | 0/250 (0.0%) | 0/250 (0.0%) | 0/0 | 0/0 | 23.562 | 22.007 | 72.305 |
| shadowing | 300 | 3 | 0/300 (0.0%) | 0/300 (0.0%) | 0/0 | 0/0 | 24.024 | 20.365 | 82.612 |
| benign | 100 | 20 | 0/0 | 0/0 | 0/0 | 100/100 (100.0%) | 25.504 | 21.388 | 126.705 |
| benign | 150 | 20 | 0/0 | 0/0 | 0/0 | 150/150 (100.0%) | 24.027 | 21.336 | 72.626 |
| benign | 200 | 20 | 0/0 | 0/0 | 0/0 | 200/200 (100.0%) | 24.843 | 22.248 | 68.684 |
| benign | 250 | 20 | 0/0 | 0/0 | 0/0 | 250/250 (100.0%) | 24.810 | 22.114 | 68.587 |
| benign | 300 | 20 | 0/0 | 0/0 | 0/0 | 300/300 (100.0%) | 25.152 | 22.768 | 39.230 |

## Paired benign cost: original Table VII question

Cold registration is outside measurement. Native registry checking and audit logging remain inside. All values below describe one process session.

| Calls | Method | Mean ns/call | p50 ns/call | p95 ns/call | Mean incremental Python peak bytes |
|---|---|---:|---:|---:|---:|
| 100 | allow_all | 233.103 | 213.260 | 394.600 | 19360 |
| 100 | sentinel_tpd | 19060.538 | 18269.330 | 24639.770 | 73170 |
| 150 | allow_all | 197.831 | 197.140 | 220.033 | 29072 |
| 150 | sentinel_tpd | 17688.920 | 17553.653 | 20090.840 | 108644 |
| 200 | allow_all | 193.549 | 190.837 | 198.865 | 38496 |
| 200 | sentinel_tpd | 17703.344 | 17766.713 | 18418.275 | 143542 |
| 250 | allow_all | 196.706 | 189.876 | 228.156 | 48240 |
| 250 | sentinel_tpd | 18938.983 | 18154.570 | 24700.788 | 179080 |
| 300 | allow_all | 185.866 | 183.048 | 215.903 | 57792 |
| 300 | sentinel_tpd | 17770.274 | 17654.282 | 20216.293 | 215434 |

## Lifecycle observations

Each expected result is scoped to its named policy; metadata coverage expectations may exceed the upstream fingerprint contract.

| Case | Method | Policy reference | Actual receipts per invocation | Policy matched per invocation |
|---|---|---|---|---|
| LC-01 | allow_all | published fingerprint/quarantine behavior | 1 | True |
| LC-01 | registration_only | published fingerprint/quarantine behavior | 1 | True |
| LC-01 | sentinel_tpd | published fingerprint/quarantine behavior | 1 | True |
| LC-01 | rescan_each_call | published fingerprint/quarantine behavior | 1 | True |
| LC-02 | allow_all | published fingerprint/quarantine behavior | 1 | True |
| LC-02 | registration_only | published fingerprint/quarantine behavior | 1 | True |
| LC-02 | sentinel_tpd | published fingerprint/quarantine behavior | 1 | True |
| LC-02 | rescan_each_call | published fingerprint/quarantine behavior | 1 | True |
| LC-03 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-03 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-03 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-03 | rescan_each_call | published fingerprint/quarantine behavior | 1 | False |
| LC-04 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-04 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-04 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-04 | rescan_each_call | published fingerprint/quarantine behavior | 0 | True |
| LC-05 | allow_all | published fingerprint/quarantine behavior | 1,1 | False,False |
| LC-05 | registration_only | published fingerprint/quarantine behavior | 1,1 | False,False |
| LC-05 | sentinel_tpd | published fingerprint/quarantine behavior | 0,0 | True,True |
| LC-05 | rescan_each_call | published fingerprint/quarantine behavior | 0,1 | True,False |
| LC-06 | allow_all | published fingerprint/quarantine behavior | 1,1 | False,True |
| LC-06 | registration_only | published fingerprint/quarantine behavior | 1,1 | False,True |
| LC-06 | sentinel_tpd | published fingerprint/quarantine behavior | 0,1 | True,True |
| LC-06 | rescan_each_call | published fingerprint/quarantine behavior | 0,1 | True,True |
| LC-07 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-07 | registration_only | published fingerprint/quarantine behavior | 0 | True |
| LC-07 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-07 | rescan_each_call | published fingerprint/quarantine behavior | 0 | True |
| LC-08 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-08 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-08 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-08 | rescan_each_call | published fingerprint/quarantine behavior | 1 | False |
| LC-09 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-09 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-09 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-09 | rescan_each_call | published fingerprint/quarantine behavior | 0 | True |
| LC-10 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-10 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-10 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-10 | rescan_each_call | published fingerprint/quarantine behavior | 1 | False |
| LC-11 | allow_all | published fingerprint/quarantine behavior | 1 | False |
| LC-11 | registration_only | published fingerprint/quarantine behavior | 1 | False |
| LC-11 | sentinel_tpd | published fingerprint/quarantine behavior | 0 | True |
| LC-11 | rescan_each_call | published fingerprint/quarantine behavior | 1 | False |
| LC-12 | allow_all | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-12 | registration_only | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-12 | sentinel_tpd | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-12 | rescan_each_call | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-13 | allow_all | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-13 | registration_only | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-13 | sentinel_tpd | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-13 | rescan_each_call | stronger host full-displayed-metadata policy; not a promised upstream field | 1 | False |
| LC-14 | allow_all | scanner module fail-closed schema-validation statement; source-contract probe | 1 | False |
| LC-14 | registration_only | scanner module fail-closed schema-validation statement; source-contract probe | 1 | False |
| LC-14 | sentinel_tpd | scanner module fail-closed schema-validation statement; source-contract probe | 1 | False |
| LC-14 | rescan_each_call | scanner module fail-closed schema-validation statement; source-contract probe | 1 | False |
| LC-15 | allow_all | published fingerprint/quarantine behavior | 1,1 | False,False |
| LC-15 | registration_only | published fingerprint/quarantine behavior | 1,1 | False,False |
| LC-15 | sentinel_tpd | published fingerprint/quarantine behavior | 0,0 | True,True |
| LC-15 | rescan_each_call | published fingerprint/quarantine behavior | 0,1 | True,False |

## Interpretation limits

- Labels reflect authored fixture intent, not semantic ground truth or live exploit success.
- Any-rule-hit detection, scanner denial and actual local receipt prevention are distinct.
- Repeated source workloads add no unique templates and imply no learning trend.
- The static assay submits one projected tool; supplied peer tools/host context are lineage, not model-selection tests.
- Performance pairs are within one process; p95 is nearest-rank over batch-per-call averages.
- tracemalloc measures incremental Python allocation peaks, not RSS or memory overhead percent.
- Lifecycle expectations name a policy reference; failures are not automatically upstream vulnerabilities.
- No external MCP tool, live agent, model selection or remote side effect is tested.

Exact composition, confusion matrices, paired differences and all raw measurement samples are retained in JSON. No confidence intervals are inferred from dependent fixtures or within-process repetitions.
