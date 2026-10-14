#!/usr/bin/env python3
"""Synthetic, offline, non-authorizing agent action evidence review sidecar.

This is a candidate example; it is not a runtime guardrail,
independent assessor, credential verifier, or observation/tracing system.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PROFILE = "agent-action-boundary-v0.1"
VERSION = "0.1.0-prototype"
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
MAX_BYTES = 1024 * 1024
TOP_FIELDS = {"schema_version", "case_id", "agent_id", "sdk", "policy", "monitor_status", "observation_coverage", "actions", "evidence"}
POLICY_FIELDS = {"id", "authorized_tools", "approval_required_for", "valid_from", "valid_until", "revoked_at"}
ACTION_FIELDS = {"id", "tool", "policy_id", "at", "control_decision", "execution_observation", "approval", "evidence_ref"}
EVIDENCE_FIELDS = {"reference", "sha256"}

class InvalidInput(ValueError):
    pass

def strict_pairs(pairs):
    out = {}
    for key, val in pairs:
        if key in out:
            raise InvalidInput("duplicate JSON object key")
        out[key] = val
    return out

def parse_json(raw: bytes):
    if len(raw) > MAX_BYTES:
        raise InvalidInput("input exceeds one MiB")
    try:
        data = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=strict_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(InvalidInput("nonfinite JSON number")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidInput("invalid UTF-8 or JSON") from exc
    return data

def utc(value: str) -> datetime:
    if not isinstance(value, str) or not UTC_PATTERN.fullmatch(value):
        raise InvalidInput("UTC timestamp must use YYYY-MM-DDTHH:MM:SSZ")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise InvalidInput("invalid calendar timestamp") from exc

def object_fields(value, required, label):
    if not isinstance(value, dict) or set(value) != required:
        raise InvalidInput(f"{label} must be an object with exactly the documented fields")

def nonempty(value, label):
    if not isinstance(value, str) or not value or len(value) > 200:
        raise InvalidInput(f"{label} must be a nonempty bounded string")

def parse_input(data):
    object_fields(data, TOP_FIELDS, "root")
    if data["schema_version"] != "0.1.0":
        raise InvalidInput("unsupported input schema_version")
    for key in ("case_id", "agent_id", "sdk"):
        nonempty(data[key], key)
    # sdk is a provenance declaration, not proof of using a particular SDK.
    object_fields(data["policy"], POLICY_FIELDS, "policy")
    policy = data["policy"]
    nonempty(policy["id"], "policy.id")
    for key in ("authorized_tools", "approval_required_for"):
        val = policy[key]
        if not isinstance(val, list) or len(val) > 200 or len(set(map(str, val))) != len(val):
            raise InvalidInput(f"policy.{key} must be a unique bounded list")
        for term in val:
            nonempty(term, key)
    if not set(policy["approval_required_for"]).issubset(set(policy["authorized_tools"])):
        raise InvalidInput("approval-required tools must be among declared authorized tools")
    if policy["valid_from"] and utc(policy["valid_from"]) > utc(policy["valid_until"]):
        raise InvalidInput("policy validity window is reversed")
    utc(policy["valid_until"])
    if policy["revoked_at"] is not None:
        utc(policy["revoked_at"])
    if data["monitor_status"] not in ("ACTIVE", "DISABLED", "UNKNOWN"):
        raise InvalidInput("invalid monitor_status")
    if data["observation_coverage"] not in ("COMPLETE_DECLARED", "INCOMPLETE", "UNKNOWN"):
        raise InvalidInput("invalid observation_coverage")
    if not isinstance(data["actions"], list) or not 0 < len(data["actions"]) <= 200:
        raise InvalidInput("actions requires 1-200 records")
    if not isinstance(data["evidence"], list) or not 0 < len(data["evidence"]) <= 200:
        raise InvalidInput("evidence requires 1-200 records")
    action_ids, evidence_refs = set(), set()
    for record in data["actions"]:
        object_fields(record, ACTION_FIELDS, "action")
        for key in ("id", "tool", "policy_id", "evidence_ref"):
            nonempty(record[key], key)
        utc(record["at"])
        if record["id"] in action_ids:
            raise InvalidInput("duplicate action id")
        action_ids.add(record["id"])
        if record["control_decision"] not in ("ALLOW", "DENY", "UNKNOWN"):
            raise InvalidInput("unknown control decision enum")
        if record["execution_observation"] not in ("EXECUTED", "NOT_OBSERVED", "UNKNOWN"):
            raise InvalidInput("unknown execution observation enum")
        if record["approval"] not in ("GRANTED", "NOT_REQUIRED", "DENIED", "UNKNOWN"):
            raise InvalidInput("unknown approval enum")
    for record in data["evidence"]:
        object_fields(record, EVIDENCE_FIELDS, "evidence")
        nonempty(record["reference"], "evidence.reference")
        if not isinstance(record["sha256"], str) or not SHA_PATTERN.fullmatch(record["sha256"]):
            raise InvalidInput("evidence.sha256 must be sha256:<64 lowercase hex>")
        if record["reference"] in evidence_refs:
            raise InvalidInput("duplicate evidence reference")
        evidence_refs.add(record["reference"])
    return data

def finding(code, severity, message, action):
    return {"id": f"{PROFILE}:{code}", "severity": severity, "message": message, "action": action}

def local_evidence(root: Path, reference: str):
    # Relative paths with POSIX separators only; reject symlinks and path escapes.
    if "\\" in reference or not re.fullmatch(r"[A-Za-z0-9._/-]+", reference):
        return None
    rel = Path(reference)
    if rel.is_absolute() or any(x in ("..", ".") for x in rel.parts):
        return None
    path = root / rel
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        return None
    if not path.is_file():
        return None
    try:
        path.resolve().relative_to(root.resolve())
        if path.stat().st_size > MAX_BYTES:
            return None
        return path.read_bytes()
    except (OSError, ValueError):
        return None

def evaluate(data, input_raw, evaluation_time, evidence_root):
    parse_input(data)
    instant = utc(evaluation_time)
    p = data["policy"]
    f = {}
    def flag(code, msg, remedy, severity="CRITICAL"):
        f[code] = finding(code, severity, msg, remedy)
    policy_start = utc(p["valid_from"]) if p["valid_from"] else None
    expiry = utc(p["valid_until"])
    revoked = utc(p["revoked_at"]) if p["revoked_at"] else None
    if instant > expiry or (policy_start and instant < policy_start):
        flag("POLICY_NOT_CURRENT", "Policy is outside declared validity at evaluation time.", "Refresh authority and repeat assessment.")
    if revoked and instant >= revoked:
        flag("POLICY_REVOKED", "Supplied policy states revocation by evaluation time.", "Do not promote old authority; review a distinct authorization.")
    if data["monitor_status"] != "ACTIVE":
        flag("MONITOR_NOT_ACTIVE", "Supplied monitoring status is not ACTIVE.", "Restore and independently verify monitoring.")
    if data["observation_coverage"] != "COMPLETE_DECLARED":
        flag("COVERAGE_GAP", "Supplied observation coverage is incomplete or unknown.", "Reconcile missing observations.")
    evidence_by_ref = {e["reference"]: e for e in data["evidence"]}
    references = []
    for e in data["evidence"]:
        raw = local_evidence(evidence_root, e["reference"])
        references.append({"type": "LOCAL_PATH", "reference": e["reference"], "sha256": e["sha256"]})
        if raw is None:
            flag("EVIDENCE_MISSING_OR_UNSAFE", "An evidence path cannot be safely read.", "Supply bounded, existing files under the evidence root.")
        elif "sha256:" + hashlib.sha256(raw).hexdigest() != e["sha256"]:
            flag("EVIDENCE_DIGEST_MISMATCH", "Supplied evidence digest does not match local bytes.", "Investigate the source and regenerate verified evidence.")
    authorized = set(p["authorized_tools"])
    approval_required = set(p["approval_required_for"])
    for a in data["actions"]:
        if a["evidence_ref"] not in evidence_by_ref:
            flag("UNBOUND_ACTION_EVIDENCE", "An action has no evidence-manifest entry.", "Bind the action to a checked local evidence artifact.")
        if a["policy_id"] != p["id"]:
            flag("POLICY_ID_MISMATCH", "An action references another policy.", "Reconcile exact policy identity.")
        at = utc(a["at"])
        if at > instant:
            flag("FUTURE_ACTION", "An action timestamp is after evaluation_time.", "Reconcile timeline before using the record.")
        if a["execution_observation"] == "UNKNOWN":
            flag("UNKNOWN_EXECUTION", "Action execution observation is unknown.", "Obtain independently attributable telemetry.")
        elif a["execution_observation"] == "NOT_OBSERVED":
            flag("EXECUTION_NOT_ESTABLISHED", "No execution was observed; absence of observation is not proof of prevention.", "Verify telemetry coverage and relevant action outcome.", severity="HIGH")
        if a["execution_observation"] == "EXECUTED":
            if a["tool"] not in authorized:
                flag("UNAUTHORIZED_TOOL_EXECUTED", "An undeclared tool was reported as executed.", "Investigate unauthorized action and prevent repetition.")
            if a["control_decision"] != "ALLOW":
                flag("ACTION_EXECUTED_WITHOUT_ALLOW", "An action was reported executed without an ALLOW decision.", "Investigate the enforcement discrepancy.")
            if a["tool"] in approval_required and a["approval"] != "GRANTED":
                flag("MISSING_REQUIRED_APPROVAL", "Approval-required tool executed without a granted approval.", "Review actual approval source before action.")
            if a["approval"] == "DENIED":
                flag("DENIED_APPROVAL_EXECUTED", "A denied-approval action executed.", "Investigate the approval bypass.")
            if (policy_start and at < policy_start) or at > expiry or (revoked and at >= revoked):
                flag("EXECUTED_OUTSIDE_AUTHORITY_WINDOW", "Executed action is outside declared authority window.", "Investigate expiry or revocation violation.")
    findings = sorted(f.values(), key=lambda x: x["id"])
    status = "FAIL" if any(x["severity"] == "CRITICAL" for x in findings) else ("CONDITIONAL" if findings else "PASS")
    result = {
        "schema_version":"1.0.0", "profile_id":PROFILE, "profile_version":VERSION,
        "source_artifact_sha256":"sha256:"+hashlib.sha256(input_raw).hexdigest(),
        "decision_pack_manifest":None, "authority_effect":"NONE", "evaluation_time":evaluation_time,
        "status":status,
        "summary": {
            "FAIL":"Submitted synthetic records contain a fail-closed inconsistency; no permission is granted.",
            "CONDITIONAL":"Submitted synthetic records require further evidence and human review; no permission is granted.",
            "PASS":"Submitted synthetic records passed bounded consistency checks; operational truth is not established."
        }[status],
        "findings":findings,
        "evidence_references":sorted(references,key=lambda x:(x["type"],x["reference"])),
        "details": {
            "case_id":data["case_id"],"agent_id":data["agent_id"],"sdk_claim":data["sdk"],
            "action_count":len(data["actions"]),"review_disposition":"PENDING_HUMAN_DECISION",
            "observation_provenance_verified":False,"runtime_enforcement":False,
            "independent_assessment":False,"external_affiliation":False,
            "limitations":"Submitted telemetry and policy declarations have not been independently authenticated; file digests establish only local byte integrity."
        }
    }
    return result

def run(input_path:Path, outdir:Path, evaluation_time:str, evidence_root:Path|None=None):
    raw=input_path.read_bytes()
    data=parse_json(raw)
    root=evidence_root or input_path.parent
    output=evaluate(data,raw,evaluation_time,root)
    outdir.mkdir(parents=True,exist_ok=True)
    canonical=(json.dumps(output,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")
    (outdir/"profile-result.json").write_bytes(canonical)
    return (1 if output["status"]=="FAIL" else 0),output

def main():
    parser=argparse.ArgumentParser(description="Offline, synthetic agent action-assurance reference")
    parser.add_argument("input",type=Path)
    parser.add_argument("--outdir",type=Path,required=True)
    parser.add_argument("--evaluation-time",required=True)
    parser.add_argument("--evidence-root",type=Path)
    args=parser.parse_args()
    try:
        code,_=run(args.input,args.outdir,args.evaluation_time,args.evidence_root)
    except (InvalidInput,OSError) as e:
        print(f"input error: {e}",file=sys.stderr)
        raise SystemExit(2) from e
    raise SystemExit(code)

if __name__=="__main__":
    main()
