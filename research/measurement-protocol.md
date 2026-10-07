# Measurement protocol for the pinned Sentinel-TPD study

This is a prospective implementation record, not a public preregistration. Source
and authored fixture labels are visible during development. Freeze the corpus,
lifecycle specification and evaluation code before a scored run. Preserve failed
runs and label any subsequent fixes. Python 3.11 or newer is required by the pinned
package. The evaluation uses only that unmodified package and the standard library.

## Four explicitly named methods

- `allow_all`: authored control; no metadata inspection and every call is enqueued.
- `registration_only`: run the actual scanner at registration, snapshot its
  descriptor/decision and reuse the decision without call-time metadata checking.
- `sentinel_tpd`: use actual `ToolRegistry.register`, `check_invocation` and, for
  explicit refreshes, `rescan_on_refresh`. Native audit logging remains enabled.
- `rescan_each_call`: actual scanner at registration and on each invocation. It
  makes a fresh content decision; it has no registry fingerprint or quarantine.

The controls are simple authored policies, not substitutes for other named
defenses. Each unique template gets its own method instance, avoiding accidental
tool-name collisions across independent fixtures. There is no model, tool selection,
remote MCP server, runtime behavior classifier or external side effect.

## Inputs, labels and source preservation

The schema-version-1 corpus contains cases with `case_id`, `family`, `label`,
`kind`, `split` and `tool`. Labels are `attack` or `benign`, kinds are poisoning,
shadowing or benign, and splits are source or challenge. Labels describe source or
author intent; they are not semantic ground truth, live exploit success, or a
random population sample. Projected source records retain their projection,
injection-point and native-metadata-applicability flags. A response payload projected
into a description tests that projection, not native response inspection. A tool
described relative to a peer does not establish actual model-selection behavior.

Each unique source and challenge template is evaluated once under every method.
Source and challenge counts and confusion matrices remain separate. The exact
source 24 poisoning / 3 shadowing / 20 benign composition is input provenance,
not silently fabricated when another corpus is supplied. Authored-only runs can
disable source workloads; they cannot stand in for the source-corpus experiment.

The separately supplied lifecycle schema has initial metadata and ordered register,
refresh and invoke steps. Each invoke declares `expected_allowed`. The runner logs
actual receipts, native quarantine/registration flags and the policy reference.
Full-metadata expectations may deliberately exceed the published fingerprint
projection. These mismatches must not all be called upstream vulnerabilities.
Direct clean registration and `rescan_on_refresh` remain distinct operations.

External corpus payloads remain in ignored local input files. Public evidence stores
case/tool/source-record hashes, source IDs/paths and projection lineage. Native
scanner findings retain signal ID, severity, field path and character offsets; their
excerpts are omitted. Offsets come from the pinned scanner's field iterator and
pattern catalog, matched back to actual returned findings. The complete corpus's
byte and canonical-content hashes are recorded, but its external descriptions are
not copied into public result directories. A pinned fetch can reconstruct the exact
inputs. Local receipts contain a tool name, fixed empty argument object and tool
hash, with no metadata description. They represent an inert enqueue stub, not a
schema-validated or remotely executed call.

## Detection, enforcement and benign tradeoffs

Any returned rule finding is a rule hit. This is separate from scanner denial at
the configured M3 threshold. An M1/M2 finding may be allowed and is counted as an
allowed warning. The study reports two confusion matrices against the declared
fixture labels: rule-hit classification and actual receipt prevention. It also
reports scanner denials, all-attack prevention, blocking among rule-hit attacks,
benign completion and benign false blocking. Actual receipts, not returned status,
determine whether a call reached the local sink. Execution failures remain separate
and are never credited as prevention. Raw numerators and denominators accompany
rates; dependent fixtures do not receive binomial confidence intervals.

## Original Tables III–VI workload questions

For each size 100, 150, 200, 250 and 300, construct three separate streams:
poisoning, shadowing and benign. Within each source kind, sort case IDs and repeat
them round-robin until exactly N calls are produced. Preserve the complete ID order
and per-template repetition counts. These are balanced repetitions, not N new
independent attacks. Remainders can alter weighted rates slightly; more repetitions
do not train the scanner or imply a learning trend.

Repeated workloads use the actual native registry. Register each unique source
template once in its own registry outside its repeated call stream. Reuse that
registry for the template's calls, preserving native cached-check/audit costs and
avoiding cross-template name collision confounds. Rule detection refers to the
registration findings; repeated fingerprint checks do not invent new semantic
findings. The resulting table separates rule-hit attacks, denied/enqueued calls and
benign completion. Scanner findings and actual blocking need not have equal counts.

For the original response-time question, record `perf_counter_ns` immediately before
the actual invocation decision and immediately after it returns. This measures a
local call-time decision, including native registry audit work, not milliseconds from
a remote attack's activation to behavioral detection. Separately record the interval
through the inert sink append. Reporting/offset extraction is outside both intervals;
sink measurement includes request serialization and tool hashing. Summaries retain
mean, min, max, median and nearest-rank p95 nanoseconds. They are descriptive only.

## Original Table VII cost question

Use one explicitly recorded source-benign template (by default the lexicographically
first source-benign case; an explicit ID may override it). The template must actually
pass native registration. An authored-only run must select a benign case explicitly.
For each N, pair `allow_all` with `sentinel_tpd`: 10 warmup pairs then 50 measured
pairs within one process, randomized method order with seed 20261006 by default.
These are within-process pairs, not 60 independent process sessions. Preserve raw
warmups and exclude them from headline summaries. Record a process-session label;
separate CLI invocations are separate sessions.

Construct the method, copy the tool, perform cold registration and serialize the
fixed request before timing. Collect garbage before each measured batch. The timed
region is a loop of N native decisions plus actual local receipt-dictionary appends
for allowed calls. Native fingerprinting, quarantine checks, audit timestamping,
audit hashing and audit-list growth remain inside Sentinel-TPD's interval. Both arms
retain N local receipts. No scanner rescan, initialization, report generation or
network delay is attributed to this cached-call measurement. Successful samples
must contain exactly N actual sink receipts.

Measure allocation in a separate pass with fresh method state and the identical N
calls/receipts. Start `tracemalloc` with one traceback frame after setup, record its
initial current bytes, reset the peak, execute the batch, and retain current and peak
bytes before stopping tracing. Incremental Python peak is peak minus initial current.
Report absolute traced peaks and each arm's incremental peaks, plus the paired
Sentinel-minus-control difference in bytes. These are Python allocator observations,
not resident memory, process isolation cost or a memory-overhead percentage. Do not
time the traced allocation pass or subtract it from untraced timing.

Timing summaries include mean, median and nearest-rank p95 batch-per-call averages,
absolute batch times, paired nanosecond differences and paired time-overhead
percentages with the named allow-all denominator. They are not individual-request
tail latency or production overhead. Background load, power state and CPU affinity
are not controlled. No confidence intervals are inferred from within-process pairs.

## Evidence and commands

The runner verifies every pinned vendor SHA-256 and Git blob identity before a run.
Every output path is new; existing directories/files are rejected. Metadata records
Python/platform/timer details without user-specific absolute paths, source-file hashes,
input hashes and the deterministic sanitized fixture/workload manifest. Raw JSONL
retains all returned decisions, receipt outcomes, timing/allocation samples and failures.
Source and input hashes are checked again at the end. Reports verify artifact and
embedded hashes, case identities and exact expected record coverage before deriving
Markdown, JSON and LaTeX table data. Regeneration produces identical report bytes
from the same raw run. Hashes are tamper evidence, not external attestation or WORM.

Development checks:

```sh
python3 -m unittest discover -s tests -p test_evaluation.py -v
python3 -m evaluation.run --corpus data/corpus-combined.local.json --lifecycle data/lifecycle.json --output results/development-001 --label development --warmups 1 --repeats 2
```

After the coordinator freezes inputs/code and approves a scored run:

```sh
python3 -m evaluation.run --corpus data/corpus-combined.local.json --lifecycle data/lifecycle.json --output results/frozen-001 --label frozen-visible-fixtures --process-session session-1
python3 -m evaluation.report results/frozen-001 --output results/frozen-001-regenerated
```

For an offline authored-only assay, use `--corpus data/corpus.json --no-workloads
--no-performance` and a new output directory. Do not merge source, authored,
lifecycle and replicated-call denominators or transfer the original paper's
unverified numerical scores into these results.
