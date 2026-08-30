# AI Sovereignty Control Layer

Part of Global AI Governance Toolkit — v2.2.0

## Purpose

AI governance answers whether a system is visible, owned, risk-tiered, evidenced, monitored, correctable, and stoppable. AI sovereignty answers a further question: who ends up owning the value the system creates.

An organization that adopts AI without sovereignty controls can lose three assets at once: its data, its workflow know-how, and its negotiating leverage over providers. This module adds operational controls so that AI adoption compounds institutional value inside the organization instead of exporting it.

## The Sovereignty Law

> No AI system may extract more institutional value than the organization can govern, audit, reverse, or retain.

Operating rules derived from the law:

1. No ZDR or equivalent protection, no sensitive data.
2. No model liquidity, no strategic dependency.
3. No audit trail, no production agent.
4. No granular permissions, no tool access.
5. No rollback path, no autonomous action.
6. No owned context layer, no compounding institutional knowledge.

These rules extend the existing portfolio doctrine: No owner, no deployment. No inventory, no governance. No evidence, no approval. No shutdown path, no frontier release. Human authority remains accountable.

## The Three-Layer Model

Sovereignty decisions are made per workload across three layers:

**Compute layer.** The physical infrastructure running models and software. The key question: is the assurance that data will not be retained or exposed structural (physical or technical isolation) or contractual (a promise)? Structural assurance is stronger. See `compute-assurance-ladder.md`.

**Model layer.** Model intelligence treated as modular and substitutable, never as the system of record. The key questions: can the organization switch providers with low friction, and is institutional data or output feeding provider training pipelines? See `model-routing-decision-tree.md` and `policies/model-liquidity-policy.md`.

**Control layer.** The organization-owned system where workflows, permissions, agents, logs, and structured context live. This is the only layer where institutional advantage can compound safely, because it is the only layer the organization fully controls.

## Sovereignty Risk Tiers

Every AI system is classified before deployment:

| Tier | Name | Description | Minimum controls |
|---|---|---|---|
| S0 | Public / No Institutional Signal | Public information only; no sensitive data or proprietary workflow. | Owner, inventory record. |
| S1 | Internal Productivity | Internal work, low sensitivity; no PII, client data, credentials, or confidential material. | S0 controls + approved tooling. |
| S2 | Sensitive Enterprise Workflow | Business-sensitive data, client context, internal process knowledge, or strategic work. | S1 controls + ZDR or structural assurance, training prohibition, audit logging, owned context capture. |
| S3 | High-Alpha / Regulated / Client-Impacting | Client-facing, regulated, proprietary, or decision-support workflows. | S2 controls + routing record, human oversight, shutdown path. |
| S4 | Sovereign / Core Institutional Knowledge | Trade secrets, classified-equivalent sensitivity, critical infrastructure, strategic advantage, or broad agentic access. | S3 controls + structural compute assurance (owned or attested), granular agent permissions, rollback. |

## Hard Gates and Advisory Controls

The automation in `automation/scripts/sovereignty_check.py` enforces two classes of control:

**Hard gates (G01–G10).** Deployment-blocking. Any failure produces a FAIL verdict and a non-zero exit code suitable for CI enforcement. They cover ownership, inventory, ZDR for sensitive data, training prohibition, agent permissions, audit logging, rollback for autonomous action, human oversight, shutdown authority, and structural assurance for sovereign workloads.

**Advisory controls (A01–A04).** Sovereignty debt. Findings produce a CONDITIONAL verdict and must be remediated on a documented schedule. They cover metadata-retention review beyond content-only ZDR, model liquidity, routing documentation, and organization-owned context capture.

## Operating Procedure

1. Inventory the AI system and assign an owner.
2. Classify the workload S0–S4.
3. Complete the ZDR review gate for every external provider involved (`zdr-review-gate.md`).
4. Record a routing decision: sensitivity → assurance level → model path (`templates/ai-model-routing-record.md`).
5. Run the sovereignty check and attach the report to the approval record:

```
python automation/scripts/sovereignty_check.py \
    automation/sample-data/sample-sovereignty-assessment.csv \
    --outdir automation/reports
```

6. Resolve all hard-gate failures before deployment. Log advisory findings with remediation owners and dates.
7. Re-run the check on every material change: new provider, new data class, new agent capability, new autonomy level.

## Attribution and Scope

This module is an original governance implementation. It operationalizes concepts that are publicly discussed across the industry — zero data retention, model liquidity, compute assurance, and organization-owned context — into controls, tiers, gates, schemas, and automation authored for Global AI Governance Toolkit. It is not legal advice; contract terms must be reviewed by qualified counsel.
