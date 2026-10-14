# Agent Action Evidence Review Example (candidate)

**Status:** proposed, independently runnable synthetic example. Not a tagged release.

This offline reference checks the internal consistency of submitted agent-action records, declared policy windows, approvals, and local evidence bytes. It emits a deterministic object shaped like the existing optional profile-result contract, with authority_effect: NONE and PENDING_HUMAN_DECISION. It does not grant permission, verify live execution, or prove source telemetry authenticity. Its PASS means only that the supplied artificial records passed the bounded checks.

## Run from repository root

```bash
python examples/agent_action_assurance/witness.py \
  examples/agent_action_assurance/fixtures/valid.json \
  --evidence-root examples/agent_action_assurance/fixtures \
  --evaluation-time 2026-10-14T12:00:00Z \
  --outdir /tmp/agent-action-assurance

python -m unittest discover \
  -s examples/agent_action_assurance/tests -v
```

Exit codes: 0 for bounded PASS or CONDITIONAL, 1 for fail-closed FAIL, and 2 for malformed or unsupported input. The caller must inspect profile-result.json, not treat exit 0 as authorization or operational assurance.

## Contract: version 0.1.0 (proposed, not registered)

Input fields: schema_version, case_id, agent_id, sdk, policy, monitor_status, observation_coverage, actions, and evidence. sdk is a provenance declaration, not verified by this script. Policy defines its id, authorized tool identifiers, tools requiring approval, validity dates and optional revocation date. Each action declares an exact policy id, tool, occurrence time, control decision, execution observation, approval state, and evidence file reference. Each evidence entry binds a relative local filename to a SHA-256 digest.

The profile-result.json output conforms to the structural fields of the existing profile-result schema. Its profile_id is a candidate name not added to the profile registry. Promotion requires a separate proposal. Do not treat it as a first-party production profile.

Every state remains bounded:

- PASS: all supplied synthetic records satisfy this local consistency checker; data provenance and operational effectiveness are not established.
- CONDITIONAL: no critical consistency mismatch but unobserved execution remains unresolved.
- FAIL: synthetic policy, monitoring, scope, time, approval, or evidence inconsistencies were detected.
- All outputs: authority_effect: NONE; review_disposition: PENDING_HUMAN_DECISION.

## Security and evidence boundaries

- No raw prompt, chain-of-thought, customer secret, PII, or proprietary evaluation record should be placed in public fixtures.
- Reject duplicate JSON keys, nonfinite numbers, oversized files, malformed dates, duplicate records, unknown enums, path traversal and symlinked evidence.
- Validate local evidence byte digest, not source truth, signature, issuer trust, monitor integrity or independent collection.
- observation_coverage: COMPLETE_DECLARED is a self-report. It does not establish genuine telemetry completeness. NOT_OBSERVED does not prove non-execution.
- The example has no runtime hooks, pre-tool interception, remote requests, credential checks, authorization, encryption, or credential/session termination.
- Human review and independent evaluation remain separate.
