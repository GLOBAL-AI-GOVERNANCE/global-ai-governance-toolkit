# Portfolio Interoperability

## Optional profile evidence

Toolkit v2.3.0 profile results are additive evidence artifacts. A portfolio handoff may reference `profile-result.json` and its SHA-256 through the existing `evidence_refs` array. This does not change `authority_effect: NONE`, transfer authority, or imply that a declared future dependency such as Stateful Revocation is operational.

This repository remains independently useful as the Global AI Governance Toolkit. Portfolio interoperability is additive.

The optional `automation/contracts/governance-decision-handoff.schema.json` contract provides a bounded reference envelope for carrying a Decision Pack reference into another GLOBAL AI GOVERNANCE repository without turning the handoff into an approval, certification, or deployment authorization.

The Wave A runtime automatically emits this envelope after successful Decision Pack generation. The default target is `agentic-ai-governance` and may be explicitly changed for an authorized consumer. Emission records a reference; it does not transfer authority or trust.

## Contract boundary

A handoff record may identify:

- the source Decision Pack;
- the governed AI system;
- the target repository;
- evidence and authority references;
- an optional configuration reference;
- an immutable artifact digest; and
- an explicit human-review boundary.

The handoff has `authority_effect: NONE`.

Receiving repositories must validate the references they consume. They must not infer that the handoff itself approves deployment, closes a vulnerability, grants action authority, or proves a control effective.

## Assurance Context Binding consumer

`automation/interoperability/assurance_context_binding.py` provides a local, opt-in validator for an explicitly supplied portfolio reference and Assurance Context Binding fixture.

It checks the canonical foundation-to-toolkit handoff, pinned source commit, artifact path, schema conformance, subject/configuration/context match, reference_only, and authority_effect NONE.

It does not retrieve external artifacts, establish external authenticity, or confer operational validity. authority_effect remains NONE.

## Decision Pack / Context Binding consistency

`automation/interoperability/decision_pack_context_consistency.py` provides an optional local check that an explicitly supplied Decision Pack handoff and Assurance Context Binding share the same subject identity and that the handoff's artifact digest matches supplied manifest bytes.

It reuses the source-locked Context Binding validator. It does not generate Decision Packs, retrieve external artifacts, or establish authenticity, operational validity, or approval. authority_effect remains NONE.

## Verification

The existing hosted `AI Governance Checks` workflow discovers and runs `automation/tests/test_portfolio_handoff.py` with the rest of the automation test suite.

## Mission Assurance Interoperability Profile

`mission-assurance-v0.1` is an optional Toolkit profile. It assembles submitted evidence references into a staged review. It does not redefine Agent Trust Passport, verified-closure, resilience, administration, or Peace OS semantics. `authority_effect` remains `NONE`. A PASS is a bounded structural check for the selected stage only.

## Machine learning assurance

`organizational-ai-maturity-v0.1` checks submitted evidence for an accountable human maturity determination. It does not score maturity, declare an organization mature, certify, or authorize deployment. Partial coverage is not framework completion. `authority_effect` remains `NONE`.

## Mission assurance challenge

`automation/assurance/mission-assurance/challenge/` holds a synthetic golden thread and a pilot template. The thread exercises the existing mission-assurance profile. It does not add another gate profile. Metric examples are templates with no measured values.

