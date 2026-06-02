# Automation Layer

Global AI Governance Solutions v1.2 adds lightweight automation for repeatable governance review.

## What v1.2 Adds

- Risk tier calculator
- Governance validator
- Executive report generator
- Policy-as-code starter rules
- JSON schema for AI inventory records
- Sample inventory data
- GitHub Actions workflow scaffold

## Why It Matters

Organizations do not only need AI principles. They need repeatable checks.

v1.2 helps teams identify governance gaps faster:

- Missing owner
- Missing evidence
- Missing monitoring
- Missing shutdown path
- Full autonomy without proper escalation
- High-impact systems without review readiness

## What Automation Does Not Replace

Automation does not replace:

- Legal review
- Security review
- Privacy review
- Human judgment
- Executive accountability
- Board-level risk acceptance
- Sector-specific compliance

## Recommended Workflow

1. Maintain an AI inventory CSV.
2. Run the risk tier calculator.
3. Run the governance validator.
4. Generate the executive report.
5. Close governance gaps before deployment or expansion.
6. Re-run checks after material system changes.

## Command Example

```bash
python automation/scripts/run_governance_checks.py automation/sample-data/sample-ai-inventory.csv --outdir automation/reports
```

## Operating Law

No AI system moves faster than ownership, evidence, authority, and control.
