# Sovereignty Module

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

This module turns AI sovereignty from strategy language into deployable controls. It answers one question for every AI system: **who ends up owning the value this system creates?**

## Contents

| File | Purpose |
|---|---|
| `ai-sovereignty-control-layer.md` | Core doctrine: the Sovereignty Law, three-layer model, S0–S4 risk tiers, hard gates, operating procedure. |
| `zdr-review-gate.md` | Pass/fail vendor review gate for zero-data-retention protection before sensitive data flows to any external model. |
| `model-routing-decision-tree.md` | Deliberate per-workload routing: sensitivity → assurance level → model path. |
| `compute-assurance-ladder.md` | Four assurance levels from owned hardware to standard third-party usage, with workload mapping. |
| `context-flywheel-register.md` | Register for confirming institutional signal compounds in an organization-owned context layer. |

## Quick Start

1. Read `ai-sovereignty-control-layer.md`.
2. Classify each AI system S0–S4.
3. Complete `../../templates/ai-vendor-zdr-review-record.md` per external provider.
4. Run the checker:

```
python automation/scripts/sovereignty_check.py \
    automation/sample-data/sample-sovereignty-assessment.csv \
    --outdir automation/reports
```

5. Block deployment on any FAIL. Schedule remediation for any CONDITIONAL.

## Core Rule

> No AI system may extract more institutional value than the organization can govern, audit, reverse, or retain.
