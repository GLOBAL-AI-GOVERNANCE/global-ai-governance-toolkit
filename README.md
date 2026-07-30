# Global AI Governance Toolkit

Turn one AI system record into a risk-tiered, human-reviewed governance report with explicit ownership, evidence, monitoring, and shutdown expectations.

**Maturity:** Working public reference toolkit. The automation path is tested in GitHub Actions and blocks critical governance findings by default. This repository is not a certification, legal opinion, regulatory determination, or guarantee of production readiness.

## Start Here

The current automation pipeline:

1. Reads an AI system inventory CSV.
2. Calculates a preliminary risk tier.
3. Checks ownership, monitoring, shutdown readiness, evidence, and autonomy conditions.
4. Produces a governance validation report.
5. Produces an executive governance report.
6. Returns a failing exit code when critical findings are present.

### Quick Start

**Prerequisite:** Python 3.11 is used in hosted CI.

```bash
python automation/scripts/run_governance_checks.py \
  automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports
```

Default behavior is fail-closed for `CRITICAL` findings:

- No flag: block `CRITICAL` findings and return exit code `1`.
- `--fail-on high`: block `HIGH` and `CRITICAL` findings.
- `--fail-on none`: explicit report-only mode; retain findings but return exit code `0`.

## Current Outputs

The pipeline writes four artifacts to the selected output directory:

```text
schema-validation-report.md
risk-tier-output.csv
governance-validation-report.md
executive-ai-governance-report.md
```

Schema or policy configuration errors return exit code `2`. Governance findings that meet the selected threshold return exit code `1`.

These outputs support review and decision preparation. They do not replace final human judgment or required legal, security, privacy, compliance, procurement, or executive review.

## Governance Gate

The current validator checks for conditions including:

- Missing named owner
- Inactive monitoring
- Missing shutdown path
- Incomplete evidence for high-impact systems
- Full autonomy without Critical or Frontier review

The governing rule is:

> No AI system moves faster than ownership, evidence, authority, and control.

Supporting doctrine:

- No owner, no deployment.
- No inventory, no governance.
- No evidence, no approval.
- No shutdown path, no frontier release.
- No trust without verification.

## Active Verification

The active workflow is located at:

```text
.github/workflows/ai-governance-checks.yml
```

It runs on:

- Pull requests
- Pushes to `main`
- Manual dispatch

Hosted verification proves:

- Valid input exits `0` under the default threshold.
- Critical input exits `1` under the default threshold.
- Explicit report-only mode exits `0` while preserving critical findings.
- External GitHub Actions are pinned to immutable commit SHAs.

## Current Scope

### Automation

The `/automation` directory contains:

- Risk tier calculator
- Governance validator
- Executive report generator
- One-command governance pipeline
- Passing and intentionally blocked fixtures
- Sample inventory data
- Sample generated reports
- Runtime-enforced JSON inventory schema
- Runtime-enforced governance policy with stable rule identifiers
- Active GitHub Actions workflow

### Practical Governance Materials

The repository also includes:

- Governance checklists
- Policies
- Templates
- Implementation guides
- Sample registers
- Spreadsheet tools
- Example system reviews
- Enterprise adoption resources

### Enterprise Adoption Resources

The `/enterprise` directory includes materials for:

- Board and executive reporting
- Governance charters
- Decision memos
- 30/60/90/180-day rollout planning
- Department rollout
- Evidence binders
- Vendor onboarding and procurement review
- Role-based training
- Sector adoption
- Metrics, registers, and workbooks

## Schema-Policy-Runtime Alignment

The one-command pipeline now consumes:

```text
automation/schemas/ai-system-inventory.schema.json
automation/policy-as-code/governance-rules.yaml
```

Runtime order:

1. Validate CSV structure and values against the checked-in inventory schema.
2. Calculate the preliminary risk tier.
3. Evaluate the risk-tiered record against the checked-in governance policy.
4. Write findings with stable rule identifiers.
5. Apply the selected failure threshold.
6. Generate the executive report when the gate permits continuation.

The policy file is JSON-compatible YAML so the runtime can parse it with the Python standard library. Unsupported schema keywords, malformed policy, missing source files, invalid required fields, and invalid enumerated values fail safely.

Current limitations:

- The runtime supports the flat inventory-schema keywords used by this repository and fails closed on unsupported keywords.
- Risk-tier calculation remains built-in logic and is not yet externalized as policy.
- The current pipeline produces governance reports, not the complete future AI Governance Decision Pack.
- The legacy `governance-os.yaml` file remains a configuration reference and is not the runtime policy source.

## Human Authority

AI and automation may assist with classification, comparison, validation, and first-pass reporting.

Humans remain responsible for:

- Confirming system ownership
- Reviewing evidence quality
- Interpreting context
- Accepting or rejecting risk
- Approving deployment or expansion
- Defining monitoring and escalation
- Exercising restriction, suspension, rollback, or shutdown authority

## Repository Map

- `.github/workflows`: active hosted verification.
- `automation`: scripts, tests, fixtures, sample data, reports, runtime schema, and runtime governance policy.
- `checklists`: deployment and review checklists.
- `docs`: doctrine, risk tiers, approval gates, monitoring, shutdown, automation, adoption, and release documentation.
- `enterprise`: enterprise rollout, reporting, evidence, procurement, training, sector, and workbook materials.
- `examples`: example AI system reviews.
- `implementation-guides`: implementation sequencing and governance-board guidance.
- `policies`: acceptable use, autonomous-agent, human-authority, sensitive-data, and vendor policies.
- `sample-registers`: sample AI system register.
- `spreadsheets`: CSV templates and governance workbook materials.
- `templates`: operational governance templates.
- `tools`: practical governance tools.
- `governance-os.yaml`: legacy machine-readable configuration reference.

## Version Lineage

The repository preserves the following development lineage:

- v1.0: Governance OS
- v1.1: Practical Toolkit
- v1.2: Automation Layer
- v2.0: Enterprise Adoption Package
- Current public identity: Global AI Governance Toolkit

Historical version names remain in version-specific release records where appropriate.

## Security, Contributions, and License

- Review [SECURITY.md](SECURITY.md) before reporting a vulnerability.
- Review [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.
- Review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation expectations.
- Licensed under the [MIT License](LICENSE).
