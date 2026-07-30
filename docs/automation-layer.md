# Automation Layer

The Global AI Governance Toolkit includes lightweight automation for repeatable AI governance review.

## Current Capabilities

- Risk tier calculation
- Governance validation
- Executive report generation
- Passing and intentionally blocked fixtures
- Active GitHub Actions verification
- Fail-closed handling of critical findings
- Explicit report-only mode

## Why It Matters

Organizations need more than principles. They need repeatable checks that reveal missing ownership, evidence, monitoring, shutdown readiness, and escalation.

The current pipeline helps identify:

- Missing owner
- Missing evidence
- Missing monitoring
- Missing shutdown path
- Full autonomy without proper escalation
- High-impact systems without review readiness

## Recommended Workflow

1. Maintain an AI inventory CSV.
2. Run the one-command pipeline.
3. Review the preliminary risk tier.
4. Review every governance finding.
5. Assign human owners and required reviewers.
6. Close critical gaps before deployment or expansion.
7. Re-run checks after material system changes.

## Command

```bash
python automation/scripts/run_governance_checks.py \
  automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports
```

The command blocks `CRITICAL` findings by default.

- Use `--fail-on high` for a stricter gate.
- Use `--fail-on none` only for an explicit report-only run.

## Generated Artifacts

```text
schema-validation-report.md
risk-tier-output.csv
governance-validation-report.md
executive-ai-governance-report.md
```

## Runtime Boundary

The active runtime consumes:

```text
automation/schemas/ai-system-inventory.schema.json
automation/policy-as-code/governance-rules.yaml
```

The schema validates the inventory before risk calculation. The policy file drives governance findings, severities, messages, and rule identifiers. Missing or malformed runtime sources fail safely with exit code `2`.

The current schema validator supports the flat schema keywords used by this repository and fails closed when unsupported keywords appear. Risk-tier calculation remains built-in logic.

## What Automation Does Not Replace

Automation does not replace:

- Human judgment
- Legal review
- Security review
- Privacy review
- Procurement review
- Compliance review
- Executive accountability
- Board-level risk acceptance
- Sector-specific obligations

## Operating Law

> No AI system moves faster than ownership, evidence, authority, and control.
