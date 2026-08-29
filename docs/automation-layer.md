# Automation Layer

The Global AI Governance Toolkit includes lightweight automation for repeatable AI governance review.

## Current Capabilities

- Versioned canonical inventory and deterministic normalization
- Risk tier calculation
- Governance validation
- Versioned machine findings and result contracts
- Executive report generation
- Deterministic Decision Pack, integrity manifest, and reference-only handoff
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

Installed:

```bash
gag check automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports
```

Repository compatibility entry point:

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
normalized-inventory.json
canonical-inventory.csv
schema-validation-report.md
risk-tier-output.csv
governance-validation-report.md
governance-findings.json
governance-result.json
executive-ai-governance-report.md
decision-pack/
governance-handoff.json
```

## Runtime Boundary

The active runtime consumes:

```text
automation/schemas/ai-system-inventory.schema.json
automation/policy-as-code/governance-rules.yaml
```

The canonical record contract is `automation/contracts/v1/canonical-inventory-record.schema.json`. Normalization produces the compatibility CSV consumed by the existing flat runtime schema before risk calculation. The policy file drives governance findings, severities, messages, and rule identifiers. Missing or malformed runtime sources fail safely with exit code `2`.

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
