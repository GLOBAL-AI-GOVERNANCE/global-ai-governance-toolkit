# Automation Layer

The automation layer provides a repeatable path from an AI system inventory CSV to preliminary risk classification, governance findings, and an executive report.

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
5. Blocks the process when findings meet the selected threshold.

Current checks include:

- Named ownership
- Active monitoring
- Shutdown readiness
- Evidence completeness for high-impact systems
- Escalation of full-autonomy systems

## Outputs

```text
risk-tier-output.csv
governance-validation-report.md
executive-ai-governance-report.md
```

## Hosted Verification

The active workflow is:

```text
.github/workflows/ai-governance-checks.yml
```

It verifies the default valid path, the default blocked path, and explicit report-only behavior.

## Reference Files Not Yet Enforced by Runtime

The repository includes:

```text
automation/schemas/ai-system-inventory.schema.json
automation/policy-as-code/governance-rules.yaml
```

These files are reference materials at the current maturity level. The Python runtime does not yet load them. Schema-policy-runtime alignment remains separate engineering work.

## Human Review Boundary

These tools support governance review. They do not replace human judgment, legal review, security review, privacy review, procurement review, compliance review, executive accountability, or board-level risk acceptance.

## Operating Law

> No AI system moves faster than ownership, evidence, authority, and control.
