# Automation Layer

The automation layer provides a repeatable path from an AI system inventory CSV to preliminary risk classification, policy-driven findings, an executive report, and a human-review Decision Pack.

## Quick Start

```bash
python automation/scripts/run_governance_checks.py \
  automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports
```

## Failure Thresholds

- Default: block `CRITICAL` findings and return exit code `1`.
- `--fail-on high`: block `HIGH` and `CRITICAL` findings.
- `--fail-on none`: explicit report-only mode; retain findings while returning exit code `0`.

## What the Pipeline Does

1. Calculates a preliminary risk tier.
2. Checks required governance conditions.
3. Writes a governance validation report.
4. Writes an executive governance report.
5. Generates a deterministic Decision Pack when the gate permits.
6. Blocks the process when findings meet the selected threshold.

Current checks include:

- Named ownership
- Active monitoring
- Shutdown readiness
- Evidence completeness for high-impact systems
- Escalation of full-autonomy systems

## Outputs

```text
schema-validation-report.md
risk-tier-output.csv
governance-validation-report.md
executive-ai-governance-report.md
decision-pack/
```

Schema or policy configuration errors return exit code `2`. Governance findings that meet the selected threshold return exit code `1`.

## Hosted Verification

The active workflow is:

```text
.github/workflows/ai-governance-checks.yml
```

It verifies the default valid path, the default blocked path, and explicit report-only behavior.

## Runtime Sources of Truth

The pipeline consumes:

```text
automation/schemas/ai-system-inventory.schema.json
automation/policy-as-code/governance-rules.yaml
```

The schema validates required fields and enumerated values before risk calculation. The policy file drives governance findings and stable rule identifiers. Missing or malformed runtime sources fail safely.

Risk-tier logic remains implemented in `risk_tier_calculator.py` and is not yet externalized as policy.

## Human Review Boundary

These tools support governance review. They do not replace human judgment, legal review, security review, privacy review, procurement review, compliance review, executive accountability, or board-level risk acceptance.

## Operating Law

> No AI system moves faster than ownership, evidence, authority, and control.

## Decision Pack

The generated `decision-pack/` directory contains:

```text
executive-summary.md
system-profile.md
risk-and-findings.md
evidence-and-ownership.md
decision-record.md
action-plan.md
manifest.json
```

The pack is deterministic and records a pending human decision. It does not approve deployment, certify compliance, or accept risk.

Rebuild the checked-in reference:

```bash
python automation/scripts/build_decision_pack_example.py
```

Verify that it has not drifted:

```bash
python automation/scripts/build_decision_pack_example.py --check
```
