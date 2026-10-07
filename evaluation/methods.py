"""Authored comparison policies using the actual unmodified pinned scanner.

These controls are not other named defenses. All receipts are inert local calls.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from pathlib import Path
import sys

from evaluation.common import ROOT, object_sha

sys.path.insert(0, str(ROOT / "vendor/sentinel-tpd"))
from sentinel_tpd import ToolRegistry
from sentinel_tpd import scanner
from sentinel_tpd.signals import DENY_AT, SIGNALS

if not Path(scanner.__file__).resolve().is_relative_to((ROOT / "vendor/sentinel-tpd").resolve()):
    raise ImportError("loaded scanner is not this package's pinned vendor")

METHODS = ("allow_all", "registration_only", "sentinel_tpd", "rescan_each_call")


def public_verdict(verdict, tool) -> dict:
    """Keep native decisions and match locations, omit external payload excerpts."""
    positions = defaultdict(deque)
    if isinstance(tool, dict):
        for field_path, text in scanner._iter_text_fields(tool):
            for signal in SIGNALS:
                for match in signal.pattern.finditer(text):
                    positions[(signal.signal_id, field_path)].append((match.start(), match.end()))
    findings = []
    for finding in verdict.findings:
        offsets = positions[(finding.signal_id, finding.field_path)]
        if not offsets:
            raise RuntimeError("native finding cannot be linked to its original match offsets")
        start, end = offsets.popleft()
        findings.append({"signal_id": finding.signal_id, "severity": finding.severity,
                         "field_path": finding.field_path, "start_character": start,
                         "end_character": end})
    return {"tool_name": verdict.tool_name, "allowed": verdict.allowed,
            "max_severity": verdict.max_severity, "reason": verdict.reason,
            "findings": findings, "deny_at": DENY_AT}


class Arm:
    def __init__(self, method: str):
        if method not in METHODS:
            raise ValueError("unknown method")
        self.method = method
        self.registry = ToolRegistry() if method == "sentinel_tpd" else None
        self.cached = None
        self.cached_tool = None

    def register_native(self, tool):
        """Actual security operation; reporting transformation happens later."""
        if self.method == "allow_all":
            verdict = None
        elif self.registry is not None:
            verdict = self.registry.register(tool)
        else:
            verdict = scanner.scan_tool_metadata(tool)
        self.cached = verdict
        self.cached_tool = deepcopy(tool)
        return verdict

    def registration_record(self, native, tool) -> dict:
        if native is None:
            return {"tool_name": tool.get("name"), "allowed": True, "max_severity": 0,
                    "findings": [], "reason": "authored allow-all control; no inspection", "deny_at": None}
        return public_verdict(native, tool)

    def invoke_native(self, tool):
        if self.method == "allow_all":
            return True
        if self.method == "registration_only":
            if self.cached is None:
                raise ValueError("no initial registration decision")
            return self.cached
        if self.registry is not None:
            return self.registry.check_invocation(tool)
        return scanner.scan_tool_metadata(tool)

    def invocation_record(self, native, tool) -> dict:
        if self.method == "allow_all":
            return {"allowed": True, "reason": "authored allow-all control; no inspection",
                    "findings": [], "inspection": "none"}
        if self.registry is not None:
            return {"allowed": native.allowed, "reason": native.reason, "tool_name": native.tool_name,
                    "findings": [], "inspection": "native_registered_fingerprint_and_quarantine"}
        source = self.cached_tool if self.method == "registration_only" else tool
        record = public_verdict(native, source)
        record["inspection"] = "reuse_initial_decision" if self.method == "registration_only" else "native_rescan"
        return record

    def refresh_native(self, tools):
        if self.registry is not None:
            native = self.registry.rescan_on_refresh(tools)
            # Cases use one intended tool; keep latest registration signal for
            # observation, not as a replacement for native invocation checks.
            self.cached = native[0] if native else None
            self.cached_tool = deepcopy(tools[0]) if tools else None
            return [self.registration_record(v, tool) for v, tool in zip(native, tools)]
        # Explicit refresh is a new registration boundary for the authored arms.
        return [self.registration_record(self.register_native(tool), tool) for tool in tools]

    def state(self, name: str) -> dict:
        if self.registry is None:
            return {"native_registry": False}
        return {"native_registry": True, "registered": self.registry.is_registered(name),
                "quarantined": self.registry.is_quarantined(name),
                "audit_entries": len(self.registry.audit), "audit_head": self.registry.audit.head,
                "audit_verification": self.registry.audit.verify()[0]}

    def registration_signals(self) -> dict:
        if self.cached is None:
            return {"any_rule_hit": False, "scanner_denied": False}
        return {"any_rule_hit": bool(self.cached.findings), "scanner_denied": not self.cached.allowed}


def native_allowed(native) -> bool:
    return native if type(native) is bool else bool(native.allowed)
