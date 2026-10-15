"""Opt-in, local consistency check between an explicitly supplied Decision Pack handoff
and an Assurance Context Binding.

Does not generate Decision Packs, retrieve external artifacts, or confer authority.
"""
from __future__ import annotations

import hashlib
from typing import Any

from automation.interoperability.assurance_context_binding import validate_assurance_context_binding
from automation.scripts.contract_verifier import ContractError, validate_instance


def validate_decision_pack_context_consistency(
    handoff: dict[str, Any],
    handoff_schema: dict[str, Any],
    manifest_bytes: bytes,
    portfolio_reference: dict[str, Any],
    binding_fixture: dict[str, Any],
    binding_schema: dict[str, Any],
    *,
    expected_subject_id: str,
    expected_configuration_digest: str,
    expected_context_boundary: str,
) -> dict[str, Any]:
    """Validate handoff schema, Context Binding, subject match, and artifact digest.

    Returns a non-authorizing consistency result. Does not establish operational validity.
    """
    if not isinstance(handoff, dict):
        raise ContractError("handoff must be an object")

    # Validate handoff against its native schema
    try:
        validate_instance(handoff, handoff_schema, base=None)  # type: ignore[arg-type]
    except ContractError as exc:
        raise ContractError(f"handoff schema failure: {exc}") from exc

    if handoff.get("authority_effect") != "NONE":
        raise ContractError("handoff authority_effect must be NONE")
    if handoff.get("source_repository") != "global-ai-governance-toolkit":
        raise ContractError("handoff source_repository mismatch")
    if handoff.get("source_artifact_type") != "AI_GOVERNANCE_DECISION_PACK_REFERENCE":
        raise ContractError("handoff source_artifact_type mismatch")

    # Preserve and reuse the source-locked Context Binding validator
    binding_result = validate_assurance_context_binding(
        portfolio_reference,
        binding_fixture,
        binding_schema,
        expected_subject_id=expected_subject_id,
        expected_configuration_digest=expected_configuration_digest,
        expected_context_boundary=expected_context_boundary,
    )

    # Exact subject identity match
    if handoff.get("system_id") != binding_fixture.get("subject_id"):
        raise ContractError("system_id does not match binding subject_id")
    if handoff.get("system_id") != expected_subject_id:
        raise ContractError("system_id does not match expected subject")

    # Artifact digest integrity against supplied manifest bytes
    expected_digest = handoff.get("artifact_digest")
    if not isinstance(expected_digest, str) or not expected_digest.startswith("sha256:"):
        raise ContractError("artifact_digest malformed")
    actual = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
    if actual != expected_digest:
        raise ContractError("artifact_digest does not match supplied manifest bytes")

    # Configuration comparison only when both sides provide a value; no silent equality assumption
    handoff_config = handoff.get("configuration_ref")
    if handoff_config is not None and handoff_config != expected_configuration_digest:
        raise ContractError("configuration_ref does not match expected configuration digest")

    return {
        "consistent": True,
        "reference_only": True,
        "authority_effect": "NONE",
        "subject_id": expected_subject_id,
        "review_boundary": handoff.get("review_boundary"),
        "note": "Local consistency check only. Does not establish authenticity, current trust, operational validity, or approval.",
        "binding_result": binding_result,
    }
