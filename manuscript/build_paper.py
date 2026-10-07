#!/usr/bin/env python3
"""Build two standalone manuscripts from checked frozen records; never score cases.

The class is embedded byte-for-byte. Bibliography metadata is deliberately parsed
only in the simple, single-line-field format maintained in references.bib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.common import verify_vendor
from evaluation.report import build_summary
from reproduce import deterministic_view

METHODS = ("allow_all", "registration_only", "sentinel_tpd", "rescan_each_call")
ALIASES = dict(zip(METHODS, ("A", "R", "S", "C")))
RELEASE = "https://github.com/rajesamp/sentinel-tpd-research/releases/tag/v0.1.0"
SIZES = (100, 150, 200, 250, 300)


def esc(value):
    mapping = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
               "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(c, c) for c in str(value))


def frac(value):
    n, d = value["numerator"], value["denominator"]
    return f"{n}/{d}" if d else "--"


def rate(value):
    return f"{100 * value['rate']:.2f}\\%" if value["rate"] is not None else "undefined"


def table(caption, label, headers, rows, columns, *, wide=True, note=""):
    env = "table*" if wide else "table"
    width = r"\textwidth" if wide else r"\columnwidth"
    lines = [rf"\begin{{{env}}}[t]\centering\footnotesize", rf"\caption{{{caption}}}\label{{{label}}}",
             r"\setlength{\tabcolsep}{3pt}", rf"\begin{{tabularx}}{{{width}}}{{{columns}}}\toprule",
             " & ".join(headers) + r" \\\midrule"]
    lines += [" & ".join(str(v) for v in row) + r" \\" for row in rows]
    lines += [r"\bottomrule\end{tabularx}"]
    if note:
        lines.append(r"\par\smallskip\parbox{" + width + "}{" + note + "}")
    lines.append(rf"\end{{{env}}}")
    return "\n".join(lines)


def bibliography(path):
    entries, current = {}, None
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("%"):
            continue
        header = re.fullmatch(r"@\w+\{([^,]+),", line.strip())
        field = re.fullmatch(r"\s*(\w+)\s*=\s*\{(.*)\},?\s*", line)
        if header:
            if current is not None or header[1] in entries:
                raise ValueError(f"bibliography header at {lineno}")
            current = header[1]
            entries[current] = {}
        elif line.strip() == "}":
            if current is None:
                raise ValueError(f"bibliography end at {lineno}")
            current = None
        elif field and current is not None:
            entries[current][field[1]] = field[2]
        else:
            raise ValueError(f"unsupported bibliography syntax at {lineno}")
    if current is not None or len(entries) != 34:
        raise ValueError("expected 34 complete bibliography entries")
    return entries


def render_bibliography(entries, body):
    keys = []
    for group in re.findall(r"\\cite\{([^}]+)\}", body):
        for key in group.split(","):
            if key not in entries:
                raise ValueError("unknown citation " + key)
            if key not in keys:
                keys.append(key)
    keys += [key for key in entries if key not in keys]
    lines = [r"\clearpage", r"\begin{thebibliography}{99}"]
    for key in keys:
        e = entries[key]
        parts = [e["author"].replace(" and ", ", "), "``" + e["title"] + "''"]
        venue = e.get("journal", e.get("booktitle", e.get("howpublished")))
        if venue:
            parts.append(r"\emph{" + venue + "}")
        for field, prefix in (("volume", "vol. "), ("number", "no. "), ("pages", "pp. ")):
            if field in e:
                if field == "pages" and key in {"orig2", "orig11"}:
                    prefix = "Art. no. "
                parts.append(prefix + e[field])
        if "eprint" in e:
            parts.append("arXiv:" + e["eprint"])
        if "year" in e:
            parts.append(e["year"])
        text = ", ".join(parts) + "."
        if "note" in e:
            text += " " + e["note"] + "."
        if "doi" in e:
            text += r" DOI: \url{" + e["doi"] + "}."
        if "url" in e:
            text += r" [Online]. Available: \url{" + e["url"] + "}."
        lines.append(r"\bibitem{" + key + "}" + text)
    return "\n".join(lines + [r"\end{thebibliography}"])


def rule_table():
    from evaluation.methods import SIGNALS, DENY_AT
    if len(SIGNALS) != 10 or DENY_AT != 3:
        raise ValueError("the manuscript requires the pinned ten-rule default policy")
    descriptions = (
        "Selected instruction, system, important, admin and hidden tags",
        "Selected direct instructions to the model or assistant",
        "Selected instructions to hide activity from the user",
        "Selected precedence, override and before-anything-else language",
        "Selected credential paths and secret-related terms",
        "Selected instructions about other tools or future messages/calls",
        "Selected requests for full conversation, context or system prompts",
        "Selected transmission verbs near an explicit URL or email address",
        "Long base64-like substrings; no decoding",
        "Selected urgent or threatening language",
    )
    rows = [(esc(s.signal_id), f"M{s.severity}", descriptions[i]) for i, s in enumerate(SIGNALS)]
    return table("The ten frozen text rules. The verdict is maximum severity; M3 is the default deny threshold.",
                 "tab:rules", ["Signal ID", "Level", "Matched evidence (lexical scope)"], rows,
                 "llX", note="M1 and M2 alone remain allowed; neither finding counts nor weak-rule sums replace the threshold.")


def architecture_table():
    rows = [
        ("MCP Client", "External integration", "A trusted host calls the library; no native MCP client or proxy transport."),
        ("Metadata Analysis", "Selected fields", "Text traversal and a canonical name/description/input-schema projection."),
        ("Poisoning Detection", "Lexical rules", "Ten regex signals with maximum severity; no learned classifier."),
        ("Shadowing Detection", "Partial overlap", "Cross-tool wording only; no provider identity, name similarity or capability model."),
        ("Runtime Monitor", "Lifecycle checks", "Pre-invocation fingerprint and quarantine state; no running-tool behavior observation."),
        ("Threat Assessment", "Threshold policy", "Maximum matched severity; original weighted scores are unimplemented."),
        ("Policy Enforcement", "Host-mediated", "Allow/deny and logical registry quarantine; no process isolation."),
        ("Security Log", "Hash-chain audit", "In-memory events, optional JSONL; no immutable storage or external anchoring."),
    ]
    result = table("Implementation status of the eight original architecture modules.", "tab:architecture",
                   ["Original module", "Status", "Supported boundary"], rows, "llX")
    fields = [
        (r"\texttt{name}, \texttt{description}", "Yes, if strings", "Yes", "Discovery/selection text"),
        (r"\texttt{inputSchema} / alias", "Nested description/title", "Entire object", "Input definition; call validation belongs to the host/server"),
        ("Top-level title, annotations", "No", "No", "May be displayed/consumed under the selected protocol version"),
        ("Tool results, remote behavior", "Not observed", "Not observed", "Outside the metadata invocation hook"),
    ]
    result += "\n" + table("Scanned, fingerprinted and host-consumed fields are different sets.", "tab:fields",
        ["Surface", "Text scanning", "Fingerprint", "Possible host use"], fields, "l l l X",
        note="LC-03/09 test covered mutations; LC-12/13 expose omitted top-level fields. A host must align its displayed/executed definition with its declared policy. Protocol fields vary by version; this is a coverage finding, not a new mechanism.")
    return result


def metrics_table():
    rows = [
        ("TPDR (III)", "Rule-hit poisoning / poisoning labels", "Report threshold denial and local prevention separately; not live-agent harm."),
        ("TSDR (IV)", "Rule-hit shadowing / shadowing labels", "Three unique source templates; no inferred identity-detector accuracy."),
        ("Response time (V)", "Local pre-invocation decision interval", "Mean/min/max for stated paths; no remote detection/containment clock."),
        ("ABR (VI)", "Blocked / detected attacks", "Conditional denominator; also report blocked/all and benign false blocks."),
        ("RSO (VII)", r"Paired $(T_S-T_A)/T_A$", "Identical inert enqueues; baseline excludes a remote tool/model."),
        ("Memory cost (VII)", "Incremental Python peak allocation", "Separate traced bytes and baseline difference; not RSS or memory percent."),
    ]
    return table("Crosswalk from the six original metrics to measured quantities (original table numbers in parentheses).",
                 "tab:metrics", ["Original metric", "Operational quantity", "Interpretation"], rows, "llX")


def kind_fraction(summary, manifest, split, kind):
    families = {c["family"] for c in manifest["cases"] if c["split"] == split and c["kind"] == kind}
    groups = [summary["by_family"][split + ":" + family]["sentinel_tpd"]["attack_prevention"] for family in families]
    return {"numerator": sum(g["numerator"] for g in groups), "denominator": sum(g["denominator"] for g in groups)}


def unique_table(s):
    rows = []
    for split in ("source", "challenge"):
        for method in METHODS:
            r = s["by_split"][split][method]
            rows.append((split, ALIASES[method], frac(r["attack_rule_detection"]), frac(r["attack_prevention"]),
                         frac(r["blocking_among_rule_hit_attacks"]), frac(r["benign_completion"]),
                         r["allowed_rule_warnings"]))
    return table("Unique-template outcomes. Every numerator comes from a rule finding or observed local receipt.",
                 "tab:unique", ["Split", "Arm", "Attack hit", "Prevented", "Blocked/hit", "Benign enqueue", "Warnings"],
                 rows, r"ll*{5}{>{\centering\arraybackslash}X}", note="A: allow all; R: registration only; S: actual Sentinel-TPD registry; C: rescan each call. Warnings are allowed cases with any rule hit. -- means a zero denominator, not zero conditional effectiveness.")


def workload_table(s):
    rows = []
    for w in s["workloads"]:
        a, d = w["outcomes"], w["local_decision_ns"]
        hits = a["rule_signal_confusion"]["true_positive"] + a["rule_signal_confusion"]["false_positive"]
        blocked = a["receipt_prevention_confusion"]["true_positive"] + a["receipt_prevention_confusion"]["false_positive"]
        rows.append((w["kind"], w["size"], len(w["unique_case_ids"]), hits, blocked, a["actual_receipts"],
                     *(f"{d[k]/1000:.3f}" for k in ("mean", "min", "max"))))
    return table("Repeated source workloads (Sentinel-TPD, session 1). Decision intervals in microseconds.",
                 "tab:workloads", ["Kind", "$N$", "$U$", "$H$", "$B$", "$E$", "Mean", "Min", "Max"],
                 rows, r"l*{8}{>{\centering\arraybackslash}X}", note="$U$: unique IDs; $H$: any-rule hits; $B$: no receipt; $E$: enqueues. Exact ID order and repetition multiplicities are in the frozen fixture manifest. Poisoning IDs TPA-001--024, shadowing TS-001--003, benign BENIGN-001--020 are repeated round-robin; all fifteen rows add no new independent templates.")


def lifecycle_table(s):
    names = ["Unchanged control", "Dictionary key reordering", "Benign covered mutation", "Poisoned covered mutation",
             "Restore after quarantine", "Clean refresh recovery", "Poisoned refresh", "Catalogue withdrawal",
             "Nested schema mutation", "Unregistered name", "Changed name / typo", "Top-level title mutation",
             "Annotation mutation", "Null-schema admission", "Direct register after quarantine"]
    grouped = {}
    for row in s["lifecycle"]:
        grouped.setdefault(row["case_id"], {})[row["method"]] = row
    rows = []
    for i, (case, methods) in enumerate(sorted(grouped.items())):
        vector = lambda steps: "[" + ",".join(str(x) for x in steps) + "]"
        expected = [int(x["expected_allowed"]) for x in methods["sentinel_tpd"]["invocations"]]
        for m in METHODS:
            if [int(x["expected_allowed"]) for x in methods[m]["invocations"]] != expected:
                raise ValueError("inconsistent lifecycle expectation")
        actual = [vector(x["receipt_count"] for x in methods[m]["invocations"]) for m in METHODS]
        scope = "Host policy" if case in ("LC-12", "LC-13") else "Doc probe" if case == "LC-14" else "Published lifecycle"
        rows.append((case, names[i], *actual, vector(expected), scope))
    return table("Lifecycle receipt vectors; one entry per invocation in the case's ordered trace.", "tab:lifecycle",
                 ["ID", "Control or change", "A", "R", "S", "C", "Expected", "Expectation scope"], rows,
                 "lXccccc l", note="1 is an actual local receipt, 0 is no receipt. LC-12/13 apply a stronger full-displayed-metadata host policy, not a promise of the pinned fingerprint contract. LC-14 probes the documented malformed-schema claim. These scoped discrepancies are not pooled into an upstream-vulnerability rate.")


def cost_table(s, t):
    rows = []
    for size in SIZES:
        g, h = s["performance"][str(size)], t["performance"][str(size)]
        a, b = g["allow_all"], g["sentinel_tpd"]
        rows.append((size, f"{a['batch_ns_per_call']['p50']/1000:.3f}",
                     f"{b['batch_ns_per_call']['p50']/1000:.3f}", f"{b['batch_ns_per_call']['p95']/1000:.3f}",
                     f"{g['paired_time_increment_ns_per_call']['p50']/1000:.3f}",
                     f"{g['paired_time_overhead_percent']['p50']:.1f}",
                     f"{a['incremental_peak_python_bytes']['p50']/1024:.2f}",
                     f"{b['incremental_peak_python_bytes']['p50']/1024:.2f}",
                     f"{g['paired_peak_allocation_difference_bytes']['p50']/1024:.2f}",
                     f"{h['sentinel_tpd']['batch_ns_per_call']['p50']/1000:.3f}"))
    return table("Paired inert-enqueue cost. Time is microseconds per call; allocation is KiB per $N$-call batch.",
        "tab:cost", ["$N$", "$A_{50}$", "$S_{50}$", "$S_{95}$", "$\\Delta_{50}$", "Time \\%", "$A_K$", "$S_K$", "$\\Delta_K$", "$S_{50}^{(2)}$"],
        rows, r"r*{9}{>{\centering\arraybackslash}X}", note="Session 1: medians (50), nearest-rank p95 (95), median paired time difference and overhead percent, median incremental Python peaks and their paired difference. Final column is session 2's time median. Quantiles describe batch-per-call averages, not single-call tails. Time percent uses the very small allow-all baseline; no memory percentage or RSS is reported.")


def plot(s, kind):
    selected = [w for w in s["workloads"] if w["kind"] == kind]
    coords = lambda metric: " ".join(f"({w['size']},{100*w['outcomes'][metric]['rate']:.6f})" for w in selected)
    label = "Poisoning" if kind == "poisoning" else "Shadowing"
    return r"""\begin{figure}[t]\centering
\begin{tikzpicture}
\begin{axis}[width=\columnwidth,height=0.67\columnwidth,xmin=90,xmax=310,ymin=0,ymax=100,
xtick={100,150,200,250,300},ytick={0,25,50,75,100},grid=major,
xlabel={Repeated calls},ylabel={Rate (\%)},tick label style={font=\footnotesize},
label style={font=\footnotesize},legend style={font=\scriptsize,at={(0.5,0.97)},anchor=north}]
\addplot+[blue,mark=o,thick] coordinates {""" + coords("attack_rule_detection") + r"""};
\addlegendentry{Rule-hit detection}
\addplot+[black,dashed,mark=x,thick] coordinates {""" + coords("attack_prevention") + r"""};
\addlegendentry{No-receipt prevention}
\end{axis}\end{tikzpicture}
\caption{""" + label + r""" rates on repeated source templates. The two curves coincide; the axis is fixed at 0--100\%. Repetition changes integer composition, not a learned detector.}
\label{fig:""" + kind + r"""}\end{figure}"""


def pattern_table():
    entries = [
        ("TPA-013", "Unrelated prerequisites", "No prerequisite/dependency reasoner."),
        ("TPA-014", "Fake enabling prerequisites", "No validation of claimed necessity."),
        ("TPA-015", "Argument hijacking", "Lexical parameter-smuggling signal; no approved-argument binding."),
        ("TPA-016", "XML-tag injection", "Selected tag patterns; not arbitrary XML interpretation."),
        ("TPA-017", "Fake system tags", "Selected tag forms in traversed strings only."),
        ("TPA-018", "Parasitic toolchains", "Lexical steering; no toolchain graph or call-sequence monitor."),
        ("TPA-019", "Cross-tool exfiltration", "Lexical paths/destinations; no runtime data-flow tracking."),
        ("TPA-020", "Message hijacking", "Lexical instruction signals; no message-origin proof."),
        ("TPA-021", "Unicode obfuscation", "No Unicode normalization, confusable matching or deobfuscation."),
        ("TPA-022", "Response injection", "Response projected into description; no actual tool-result inspection."),
        ("TPA-023", "Forced re-execution", "Response projection; no loop or invocation-count monitor."),
        ("TPA-024", "Annotation deception", "Annotations omitted; authored destructive-description context disclosed."),
        ("TS-001", "Name squatting", "Raw name key is not provider authentication; authored peer context."),
        ("TS-002", "Capability override", "No semantic comparison of competing capabilities."),
        ("TS-003", "Typosquatting", "No name-similarity detector; authored alias/peer context."),
    ]
    return table("All twelve original poisoning patterns and three shadowing patterns are retained.",
                 "tab:patterns", ["Source ID", "Original pattern", "Implemented scope or explicit gap"], entries,
                 "llX", note="TPA-001--004, 005--008 and 009--012 additionally retain explicit-trigger, implicit-background-trigger and persistent-instruction families. Thus the source has fifteen poisoning category labels, not twelve independent implemented detectors.")


def adjacent_table():
    rows = [
        (r"\cite{orig10}", "Multimodal poisoning / ShadowCast", "Representation poisoning is not MCP name/descriptor shadowing."),
        (r"\cite{orig11}", "Shadow AI governance", "Unsanctioned AI adoption differs from competing tool identities."),
        (r"\cite{orig12}", "Shadow AI risk/governance", "Organizational controls do not validate this metadata detector."),
        (r"\cite{orig14}", "AI security and policy", "Governance context; no reproduced MCP defense mechanism."),
        (r"\cite{orig15}", "Mutated web/WAF payloads", "Mutation motivates controls; web filtering rates do not transfer."),
        (r"\cite{orig16}", "Federated data-poisoning defense", "Training-data robustness differs from inference-time tool metadata."),
        (r"\cite{orig17}", "Federated poisoning visualization", "Failure visualization is methodological context, not MCP efficacy."),
        (r"\cite{orig18}", "DNS parser logic", "Malformed-input reasoning differs from this scanner's contract."),
        (r"\cite{orig19}", "Container attack/defense", "Execution isolation is a separate boundary absent from registry quarantine."),
        (r"\cite{orig20}", "Medical-image poisoning", "Image-model defenses and metrics are not implemented here."),
    ]
    return table("Retained adjacent references and transfer limits.", "tab:adjacent", ["Ref.", "Domain", "Limit"], rows, "llX")


PROPOSAL = r"""
\section{Original Formal Expressions: Unimplemented Proposal}\label{app:proposal}
The following four expressions preserve the original design proposal. None defines
the risk computation evaluated in this paper. The first is a metadata abstraction;
the remaining three propose weighted scores:
\begin{align}
 M_i &= \{N_i,D_i,C_i,P_i,R_i\},\label{eq:proposal-metadata}\\
 R_p(i) &= \sum_{j=1}^{k} w_jx_{ij},\label{eq:proposal-poison}\\
 R_s(i) &= \alpha S_n(i)+\beta S_c(i)+\gamma S_t(i),\label{eq:proposal-shadow}\\
 R(i) &= \lambda R_p(i)+(1-\lambda)R_s(i)+\delta B_i.\label{eq:proposal-combined}
\end{align}
Here $N,D,C,P,R$ denote name, description, capabilities, parameters and relationships;
$x$ denotes proposed poisoning features; $S_n,S_c,S_t$ denote proposed name,
capability and contextual similarity; and $B$ denotes proposed behavioral evidence.
The pinned code has no distinct capability/relationship analysis, fitted feature
weights, corresponding similarity functions or observed execution-behavior term.
No coefficients are estimated in this study. The measured implementation instead
uses maximum rule severity and the stated fingerprint/quarantine policy.
"""


def content(s, t, manifest, metadata):
    source, challenge = (s["by_split"][k]["sentinel_tpd"] for k in ("source", "challenge"))
    native = s["source_native_metadata_subset"]["sentinel_tpd"]
    kp = {split: {kind: frac(kind_fraction(s, manifest, split, kind)) for kind in ("poisoning", "shadowing")}
          for split in ("source", "challenge")}
    ranges = []
    for summary in (s, t):
        medians = [g["sentinel_tpd"]["batch_ns_per_call"]["p50"] / 1000 for g in summary["performance"].values()]
        ranges.append(f"{min(medians):.3f}--{max(medians):.3f}")
    abstract = (f"Across 47 pinned source templates, the registry prevents local enqueue for {frac(source['attack_prevention'])} "
        f"attack-labeled cases ({rate(source['attack_prevention'])}), while retaining {frac(source['benign_completion'])} benign enqueues. "
        f"On 70 authored challenges the corresponding counts are {frac(challenge['attack_prevention'])} and {frac(challenge['benign_completion'])}. "
        "All three source shadowing templates are missed. Fifteen lifecycle traces separate covered mutation/quarantine behavior "
        "from omitted metadata fields. Two process sessions measure five workloads of 100--300 repeated local calls; "
        f"session 1 registry median cost is {ranges[0]} microseconds per call, including audit and receipt storage.")
    corpus = r"""The additional 70 authored challenge templates contain 23 poisoning, three
shadowing and 44 benign controls. Source and challenge results are always separate.
Each of the four arms sees every template once: 468 case/arm records per process
session. Labels encode authored intent, not adjudicated semantic ground truth.
TPA-022/023 tool-response payloads are projected into descriptions; TS-001/003
use declared authored name/peer context. These four are excluded from the native
metadata-applicability subgroup. TPA-024 retains its annotations and adds declared
authored destructive-description context, including within that subgroup.
The 43-record subgroup therefore does not erase all augmentation or establish
native annotation detection. Peer context is lineage, not an evaluated model-selection task.

The public artifact contains the authored corpus, source manifest, exact source
hashes and pinned acquisition procedure. External descriptions are local-only:
the pinned repository declares MIT in package/README metadata but supplies no
LICENSE file or corpus-specific reuse terms. Public raw records keep case/tool
hashes, rule IDs, field paths, match offsets and receipt evidence without payload
excerpts. No corpus labels or thresholds are tuned after the scoring freeze.
"""
    perf = metadata["performance"]
    timing = (f"Two separate CPython 3.12.14 processes on one Intel Core i9-9880H (2.30 GHz), "
        "16 GiB MacBookPro16,1 running macOS 26.6.2 produced the two full sessions. "
        f"For each $N$, each process uses {perf['warmup_pairs']} warmup and {perf['measured_pairs']} measured pairs "
        "with seeded randomized arm order. These are within-process pairs, not independent process sessions. "
        r"The monotonic \texttt{perf\_counter\_ns} clock uses \texttt{mach\_absolute\_time} (reported 1 ns resolution). "
        "Concurrency is one; CPU affinity, power and background load were not controlled or measured.\n\n"
        r"The paired assay repeatedly checks the admitted definition BENIGN-001 and enqueues an inert request with \texttt{\{\}} arguments. "
        "No argument-schema validation or remote task completion is asserted. Cold registration, copying, request serialization, "
        "collection and random ordering occur before timing. The timed loop includes the registry invocation check, native audit "
        "timestamps, hashing and list growth, plus receipt-dictionary storage. A and S receive the same request shape and $N$. "
        "Each time sample is the whole batch elapsed time divided by $N$; medians and nearest-rank p95 are over 50 batch means.\n\n"
        r"A separate \texttt{tracemalloc} pass (one traceback frame) executes the same $N$ checks and enqueues "
        "after setup and peak reset. It records each arm's peak minus its pre-loop traced baseline, and the paired difference "
        "between arms. Audit and receipt accumulation therefore remain in allocation cost. Raw samples preserve nanoseconds "
        "and bytes. No confidence interval is inferred from dependent fixtures or repeated calls.")
    results = r"\subsection{Unique-case detection, prevention and benign controls}" + "\n" + unique_table(s) + "\n"
    results += (f"The three scanner-based arms agree on unchanged unique templates. Source prevention is {frac(source['attack_prevention'])}: "
        f"{kp['source']['poisoning']} poisoning and {kp['source']['shadowing']} shadowing. Challenge prevention is "
        f"{frac(challenge['attack_prevention'])}: {kp['challenge']['poisoning']} poisoning and {kp['challenge']['shadowing']} shadowing. "
        f"The corresponding benign enqueues are {frac(source['benign_completion'])} and {frac(challenge['benign_completion'])}; "
        f"{challenge['benign_false_block']['numerator']} challenge controls are false blocks. "
        "All allow-all cases produce receipts. In these scored fixtures every rule-hit attack is blocked, so the conditional "
        "blocked/hit ratio is 100\\%; its restricted denominator must not replace the all-attack rates. "
        "Allowed warnings are zero in these fixtures, although the M1/M2 policy permits them and dedicated unit controls exercise that distinction.\n\n"
        f"In the source native-metadata subgroup, {frac(native['attack_prevention'])} attack labels are blocked "
        f"({rate(native['attack_prevention'])}) and {frac(native['benign_completion'])} benign labels enqueue. "
        "The denominator is 23 attack and 20 benign records. The four omitted projections and TPA-024 augmentation are described above; "
        "this is a scoped subgroup, not agent-level attack success.\n")
    results += r"\subsection{Repeated workload levels}" + "\n" + workload_table(s) + "\n"
    results += ("Table~\\ref{tab:workloads} preserves the five workload levels for each kind. "
        "Every poisoning row repeats 24 unique IDs; shadowing repeats three and benign repeats 20. "
        "Figures~\\ref{fig:poisoning} and~\\ref{fig:shadowing} show count-derived rates on a common 0--100\\% axis. "
        "All benign workload calls enqueue. These streams assess this fixed repeated schedule and local decision cost; "
        "they do not estimate a learning or sensitivity trend.\n")
    results += plot(s, "poisoning") + "\n" + plot(s, "shadowing") + "\n"
    results += r"\subsection{Lifecycle effects and field boundaries}" + "\n" + lifecycle_table(s) + "\n"
    results += r"""The registry rejects benign covered mutation (LC-03) that rescanning
accepts, showing that integrity checks add a different property from suspicious-text
detection. Quarantine remains after byte restoration and direct registration
(LC-05/15); a clean refresh recovers it (LC-06). Withdrawal and unknown/changed names
are denied by the registry controls. A clean definition still passes after top-level
title or annotation changes (LC-12/13), consistent with the field crosswalk.
The null-schema probe (LC-14) also enqueues. Its documented validation expectation
and the stronger host policies are kept distinct from the published fingerprint
behavior. No actual multiserver dispatcher binding or remote server behavior is tested.
"""
    results += "\n" + r"\subsection{Paired time and allocation cost}" + "\n" + cost_table(s, t) + "\n"
    results += (f"Across $N$, the registry's median batch-per-call cost ranges from {ranges[0]} $\\mu$s in session 1 "
        f"and {ranges[1]} $\\mu$s in session 2. "
        "The two sessions agree on all deterministic outcomes after excluding only timestamp-dependent audit-head hashes. "
        "Timing remains session-specific; the second session is not pooled to manufacture more independent hosts. "
        "Large time percentages reflect comparison with a sub-microsecond inert allow-all loop, not total agent latency. "
        "Python peaks include retained audit and receipt data and grow with the batch; they are not a leak diagnosis or resident-memory claim.\n")
    return {"ABSTRACT_RESULTS": abstract, "RULE_TABLE": rule_table(), "ARCHITECTURE_TABLE": architecture_table(),
            "CORPUS_PROTOCOL": corpus, "METRICS_TABLE": metrics_table(), "TIMING_PROTOCOL": timing,
            "RESULTS": results, "PATTERN_TABLE": pattern_table(), "ADJACENT_TABLE": adjacent_table()}


def build(primary, secondary):
    verify_vendor()
    s, t = build_summary(primary), build_summary(secondary)
    if s["status"] != "completed" or t["status"] != "completed":
        raise ValueError("both source runs must be completed")
    if deterministic_view(s) != deterministic_view(t):
        raise ValueError("frozen sessions differ on deterministic outcomes")
    expected = {"source:poisoning": 24, "source:shadowing": 3, "source:benign": 20,
                "challenge:poisoning": 23, "challenge:shadowing": 3, "challenge:benign": 44}
    if s["fixture_counts"] != expected or s["record_counts"] != {"unique_case": 468, "workload_call": 3000, "lifecycle": 60, "performance": 1200}:
        raise ValueError("frozen study shape differs from manuscript protocol")
    manifest = json.loads((primary / "fixture-manifest.json").read_text())
    metadata = json.loads((primary / "metadata.json").read_text())
    other_metadata = json.loads((secondary / "metadata.json").read_text())
    for m in (metadata, other_metadata):
        if m["performance"]["warmup_pairs"] != 10 or m["performance"]["measured_pairs"] != 50:
            raise ValueError("expected full 10/50 paired measurements")
    if s["process_session"] == t["process_session"]:
        raise ValueError("process session labels must be distinct")
    template = (ROOT / "manuscript/paper-body.tex.in").read_text()
    entries = bibliography(ROOT / "manuscript/references.bib")
    replacements = content(s, t, manifest, metadata)
    outputs = {}
    for anonymous in (False, True):
        values = dict(replacements)
        values["AUTHOR"] = (r"\author{}" if anonymous else
            r"\author{\IEEEauthorblockN{Rajeshkumar Sampathrajan}\IEEEauthorblockA{Independent Researcher}}")
        values["AVAILABILITY"] = (r"The anonymous supplementary artifact contains frozen records, provenance, source acquisition instructions, the authored corpus, tests and deterministic report generation."
            if anonymous else r"The versioned research artifact is available at \url{" + RELEASE + "}.")
        values["AVAILABILITY"] += (r" Both frozen process sessions, exact workload composition and all raw time/allocation samples are retained. "
            r"Python 3.11 or later is required. Source acquisition uses pinned downloads; an authored-only mode operates offline. "
            r"The source corpus is not redistributed. Reproduction regenerates tables from checked raw records and separately checks deterministic outcome agreement.")
        body = template
        for key, value in values.items():
            body = body.replace("@@" + key + "@@", value)
        body = body.replace("Our earlier dispatch-conformance artifact", "A separate dispatch-conformance artifact")
        body = body.replace("fixed benign call", "fixed inert local request")
        body = body.replace("paired valid-call benchmark", "paired admitted-definition benchmark")
        body = body.replace("Audit logging and copying contribute to cost", "Audit logging and receipt storage contribute to cost")
        body = body.replace("Benign completion is the fraction of benign-labeled cases with\none expected local receipt.",
            "Benign enqueue completion is the fraction of benign-labeled cases with\none expected local receipt; argument-schema validity and remote task completion are not tested.")
        if anonymous:
            body = body.replace("This study shares human authorship\nwith Sentinel, so public code is not evidence of independent third-party validation.",
                "Developer familiarity with the implementation and specification-aware fixture construction create potential selection bias. Public code is not evidence of independent third-party validation.")
            body = body.replace("Known fixed rules, shared authorship and specification-aware cases create",
                                "Known fixed rules, investigator familiarity and specification-aware cases create")
        body += "\n" + PROPOSAL
        body = body.replace("@@BIBLIOGRAPHY@@", render_bibliography(entries, body))
        if re.search(r"@@\w+@@", body):
            raise ValueError("unfilled template placeholder")
        if anonymous and (RELEASE in body or "Our earlier" in body or "shares human authorship" in body or "shared authorship" in body):
            raise ValueError("anonymous body retains explicit author linkage")
        cls = (ROOT / "manuscript/IEEEtran.cls").read_bytes()
        prefix = b"% Generated by build_paper.py from verified frozen records; do not edit.\n\\begin{filecontents*}[overwrite]{IEEEtran.cls}\n"
        preamble = r"""
\end{filecontents*}
\RequirePackage[T1]{fontenc}
\documentclass[compsoc,conference,a4paper,10pt,times]{IEEEtran}
\usepackage{amsmath,amssymb,booktabs,tabularx,array,url,graphicx}
\usepackage{xurl}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage[hidelinks]{hyperref}
\urlstyle{same}
\begin{document}
"""
        outputs["paper-anonymous.tex" if anonymous else "paper.tex"] = prefix + cls + preamble.encode() + body.encode() + b"\n\\end{document}\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, default=ROOT / "results/frozen-001")
    parser.add_argument("--secondary", type=Path, default=ROOT / "results/frozen-002")
    args = parser.parse_args()
    outputs = build(args.primary.resolve(), args.secondary.resolve())
    for filename, payload in outputs.items():
        path = ROOT / "manuscript" / filename
        path.write_bytes(payload)
        print(filename, "sha256=" + hashlib.sha256(payload).hexdigest(), "bytes=" + str(len(payload)))


if __name__ == "__main__":
    main()
