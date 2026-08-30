# Context Flywheel Register

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Principle

Two flywheels compound value in AI-heavy organizations:

- **Model flywheel:** usage → signal → structured know-how → improved system → more usage, compounding through model weights.
- **Context flywheel:** usage → signal captured in an owned context/knowledge layer → structured know-how → better workflows → more usage, compounding through the organization's own structured record of actions and decisions.

Whoever captures the signal owns the compounding. If the only assets the organization holds are prompts plus a provider's hidden weights, its know-how is trapped inside a single vendor relationship. Sovereignty requires that the knowledge layer exist independently of any model, and that models interact with institutional knowledge rather than own it.

## Register

Maintain one row per significant AI-assisted workflow. Review quarterly.

| Field | Description |
|---|---|
| workflow_id | Stable identifier. |
| workflow_name | Human-readable name. |
| owner | Accountable owner. |
| signal_generated | What usage signal this workflow produces (decisions, corrections, outcomes, structured actions). |
| capture_location | Where the signal persists: `owned_ontology`, `owned_datastore`, `provider_only`, `not_captured`. |
| capture_structured | yes/no — is the signal structured (entities, relations, actions) or raw text? |
| model_dependency | Can the workflow's accumulated know-how survive a model/provider switch? yes/no. |
| compounding_check | Evidence that captured signal has improved the workflow since last review. |
| leakage_risk | Any path by which this signal reaches provider training pipelines (must be `none` for S2+). |
| review_date / next_review | Last and next quarterly review. |

## Red flags

- `capture_location = provider_only` on any S2+ workflow: institutional know-how is compounding in someone else's system. Escalate.
- `capture_location = not_captured` on a high-usage workflow: signal is being destroyed. Fragmented tooling is usually the cause; consolidate the workflow onto owned software.
- `model_dependency = no` nowhere in the register: if no workflow can survive a provider switch, the organization has no context flywheel — it has a subscription.

## Operating rule

> No owned context layer, no compounding institutional knowledge.
