# Model Routing Decision Tree

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Principle

Sovereignty is a series of deliberate, per-workload decisions across the stack. No workload reaches a model by default; every workload is routed based on sensitivity, capability requirement, cost, and control. Record every routing decision in `templates/ai-model-routing-record.md`.

## The Tree

**Step 0 — Prerequisites complete?**
Owner assigned, inventory record complete, ZDR review gate passed for every external provider in scope. If not → **HOLD. Do not implement yet.** Close the gaps first.

**Step 1 — Does this workflow need model inference at all?**
If deterministic software solves the problem, build and own the tool in the control layer. No model means no extraction surface. → **END: owned deterministic tool.**

**Step 2 — Does the control layer meet sovereignty criteria?**
Model-agnostic routing, granular permissions, audit + log, adaptive cybersecurity, reversible branching, owned context capture. If not → **HOLD: human-in-the-loop, read-only AI only** until the control layer passes.

**Step 3 — Classify the knowledge involved (S0–S4) and pick the assurance level.**
Structural assurance beats contractual. Match the workload to the strongest rung it needs.

**Step 4 — Route:**

| Workload class | Route | End state |
|---|---|---|
| S4, zero-tolerance / classified-equivalent | Owned, air-gapped hardware | Air-gapped sovereign environment on adaptable owned compute. |
| S4, core secrets, self-host viable | Owned or dedicated hardware | Self-hosted open-weight model on owned/dedicated compute. |
| S3–S4, know-how must compound in-house | Fine-tune open weights | Fine-tuned open model — the model flywheel stays inside the organization. |
| S2–S4, context is the asset | Owned ontology + context layer | Model-agnostic access; institutional knowledge lives outside every provider. |
| S3, sensitive, no owned hardware | Attested compute | Rented GPU + hardware attestation; confidential compute with verified execution. |
| S2–S3, needs frontier capability | ZDR cloud | Closed frontier model under confirmed ZDR; no retention, no training. |
| S1, internal low-risk | Enterprise privacy mode | Redaction, capped retention, audit. |
| S0, public/commodity | Any model, swappable | Standard usage; no secrets, retention risk accepted. |

**Step 5 — Re-route triggers.**
New provider, new data class, new agent capability, new autonomy level, provider policy change, or incident → return to Step 0.

## Two rules that override everything

1. **When capability and sovereignty conflict on S4 data, sovereignty wins.** Use a less capable model on structural assurance rather than a frontier model on contractual promises.
2. **Never let a routing exception become a routing default.** Exceptions expire; defaults are reviewed.
