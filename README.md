# Global AI Governance Toolkit

<!-- gag:nav -->
[![Global AI Governance](https://img.shields.io/badge/Global_AI_Governance-portfolio-0b100d)](https://github.com/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE) ![Status](https://img.shields.io/badge/status-v2.5.0_released-brightgreen) ![authority_effect](https://img.shields.io/badge/authority__effect-NONE-lightgrey)

**[Connect your agent](https://global-ai-governance.github.io/global-ai-governance-toolkit/connect.html#agents)** · **[Read the spec](https://global-ai-governance.github.io/global-ai-governance-toolkit/connect.html#spec)** · [All products](https://github.com/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE#product-map)
<!-- /gag:nav -->

Turn an AI system inventory record into policy-driven findings and a reproducible, human-reviewed AI Governance Decision Pack.

**Maturity:** Working public reference toolkit. The automation path is tested in GitHub Actions and blocks critical governance findings by default. This repository is not a certification, legal opinion, regulatory determination, or guarantee of production readiness.

**Published release:** v2.5.0 — Organizational AI Maturity Evidence. A human determines organizational maturity. The toolkit checks submitted evidence and does not score, certify, or authorize.

## Start Here

Open the live local-first browser:

**[https://global-ai-governance.github.io/global-ai-governance-toolkit/](https://global-ai-governance.github.io/global-ai-governance-toolkit/)**

The hosted browser reflects current `main`, which may move ahead of the tagged v2.4.0 release. Agents start at [`web/llms.txt`](web/llms.txt) and [`web/machine-interface.json`](web/machine-interface.json); the [Connect page](web/connect.html) covers Model Context Protocol (MCP) setup, pilots, and specifications.

Primary browser actions are:

- **Run sample**: a synthetic clean inventory
- **Run example with gaps**: a synthetic inventory that shows governance findings
- **Load CSV**
- **Review and download the Decision Pack**

Neither example is a real security assessment, and a passing result does not authorize deployment.

The browser uses the same generated contract and policy bundle as the CLI. Parity tests protect normalization, findings, result states, and the non-authorizing handoff boundary.

First-time users can run the sample, download the contract-generated blank CSV template, load a completed inventory, review plain-language guidance alongside stable technical rule IDs, and download the Decision Pack. Agents and technical integrations can begin with [`web/machine-interface.json`](web/machine-interface.json) instead of scraping prose.

For a reviewed local copy:

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/web/`.

### Static hosting boundary

The browser is deployed through the repository-native [GitHub Pages workflow](.github/workflows/pages.yml), with GitHub Actions as the Pages source.

Static hosting does not change the data boundary: CSV content is read by the browser on the local device, processing occurs in browser memory, and downloads are generated locally. The site has no backend, upload path, application login, telemetry, service worker, or runtime network request. Organizations should still serve a reviewed commit and apply their own browser, device, and data-handling controls.

Install from a reviewed checkout in an isolated Python 3.11 environment:

```bash
python -m pip install .
gag check automation/fixtures/valid-ai-inventory.csv \
  --outdir /tmp/gag-output \
  --evaluation-time 2026-08-29T12:00:00Z
gag verify /tmp/gag-output
```

The installed CLI and the repository-relative compatibility script use the same local, network-free reference runtime. See [Machine Interfaces](docs/MACHINE_INTERFACES.md), [Compatibility Policy](docs/COMPATIBILITY.md), and [Local Data Handling](docs/LOCAL_DATA_HANDLING.md).

The current automation pipeline:

1. Normalizes a supported canonical, generated-human, or safely mapped legacy CSV.
2. Validates versioned canonical records and calculates a preliminary risk tier.
3. Checks ownership, monitoring, shutdown readiness, evidence, and autonomy conditions.
4. Produces versioned JSON findings and an aggregate governance result.
5. Produces the existing human reports and deterministic Decision Pack.
6. Verifies the integrity manifest and emits a non-authorizing handoff.
7. Returns a failing exit code when findings meet the selected threshold.

### Quick Start

**Prerequisite:** Python 3.11 is used in hosted CI.

```bash
python automation/scripts/run_governance_checks.py \
  automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports \
  --fail-on none
```

The bundled sample intentionally includes systems with critical control gaps. The quick start therefore uses explicit report-only mode so the toolkit can generate a blocked-state Decision Pack for review. Remove `--fail-on none` to exercise the default fail-closed gate.

Default behavior is fail-closed for `CRITICAL` findings:

- No flag: block `CRITICAL` findings and return exit code `1`.
- `--fail-on high`: block `HIGH` and `CRITICAL` findings.
- `--fail-on none`: explicit report-only mode; retain findings but return exit code `0`.

## AI Sovereignty Control Layer

v2.2.0 adds an additive, local-first sovereignty assessment path for organizations reviewing whether strategic AI use preserves institutional control.

The sovereignty checker evaluates declared controls for data retention and training use, model/provider dependency, compute assurance, permissions, auditability, rollback, human oversight, shutdown, and owned context. It does not attest provider behavior, certify compliance, authorize deployment, or replace legal, privacy, security, procurement, executive, or board review.

Run the passing reference assessment:

```bash
python automation/scripts/sovereignty_check.py \
  automation/sample-data/sample-sovereignty-assessment-pass.csv \
  --outdir automation/reports
```

The sovereignty checker is additive to the primary Decision Pack runtime. `governance-os.yaml` remains a legacy configuration reference and is not promoted back into runtime policy by this release.

## Advanced Profiles

v2.4.0 adds independent assurance, mission assurance, and machine-learning assurance for CLI use, alongside the Auditable AI, synthetic Quantum-AI, and CISO accountability profiles published in v2.3.0. The browser renders those original three. They follow one additive path:

Decision Pack → optional advanced profile → profile result + evidence → accountable human review → optional non-authorizing handoff.

Profiles emit the common deterministic `profile-result.json` with `authority_effect: NONE`. They may reference a Decision Pack but never rewrite it, approve deployment, accept risk, certify compliance, attest provider behavior, establish safety, or transfer authority. See [`automation/profiles/registry.json`](automation/profiles/registry.json).

## Current Outputs

The pipeline writes canonical and machine-readable artifacts alongside the existing human reports and Decision Pack:

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
- No sovereignty, no strategic AI.

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
- Deterministic Decision Pack generator and drift checker
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
- The current Decision Pack prepares evidence for human review; it does not approve deployment, certify compliance, or accept risk.
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
- `examples`: example AI system reviews and a reproducible Decision Pack reference.
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
- v2.1.0: Decision-Ready Governance
- v2.2.0: AI Sovereignty Control Layer
- v2.3.0: Assurance & Accountability Profiles
- v2.4.0: Assurance Interoperability & Agent Connectivity
- v2.5.0: Organizational AI Maturity Evidence
- Current public identity: Global AI Governance Toolkit

Historical version names remain in version-specific release records where appropriate.

## Release Verification

- Review [v2.4.0 release notes](release-notes/v2.4.0.md).
- Review [v2.3.0 release readiness](docs/release-readiness-v2.3.0.md).
- Review the [v2.3.0 release notes](release-notes/v2.3.0-assurance-accountability-profiles.md).
- Review the [v2.4.0 release gate](docs/release-readiness-v2.4.0.md).
- Run `python -B automation/scripts/validate_repository.py`.
- Run `python -B automation/scripts/build_decision_pack_example.py --check`.

## Security and License

- Security boundary: [SECURITY.md](SECURITY.md).
- Licensed under the [MIT License](LICENSE).

<!-- gag:footer -->
## Part of Global AI Governance

This toolkit is the **GOVERN + MEASURE** layer and the flagship entry point: inventory in, findings and a human Decision Pack out.

- **Connect your agent:** [llms.txt](https://global-ai-governance.github.io/global-ai-governance-toolkit/llms.txt), [machine-interface.json](https://global-ai-governance.github.io/global-ai-governance-toolkit/machine-interface.json), and the [AI Governance Model Context Protocol Server](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp) (AI Governance MCP; command `gag-mcp`). Compatible with MCP-based agents.
- **Read the spec:** [versioned specifications](https://global-ai-governance.github.io/global-ai-governance-toolkit/connect.html#spec) and the [product map](https://github.com/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE#product-map).

Outputs are non-authorizing (`authority_effect: NONE`). Not affiliated with or endorsed by any AI lab or platform.
<!-- /gag:footer -->
