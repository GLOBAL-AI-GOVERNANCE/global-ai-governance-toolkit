# Changelog
## [Unreleased]

- Pin the README, site, `llms.txt`, and machine interface to v2.7.1. The machine interface version stays 1.2.0.
- The Connect page and `llms.txt` add Claude Code and Grok CLI setup, the full Anthropic MCP connector shape, and an Action Level guard section linking to AI Governance MCP examples. The product map gains the `#products` anchor.
- Pin AI Governance MCP references on the Connect page and in `llms.txt` to v0.3.1, which ships the Action Level guard and bundles toolkit v2.7.1.
- Links that open a page at a section, such as `connect.html#guard`, land on the section at once instead of animating the scroll on load. Smooth scrolling for in-page links and the reduced-motion setting are unchanged.
- Packaging: the distribution name is `global-ai-governance`, so future wheel and sdist files are named `global_ai_governance-<version>`. The command `gaig` and the import package `gaig_toolkit` are unchanged, and assets of existing releases keep their names. The package is not on PyPI yet.
- The wheel installs only `gaig_toolkit` at the top level: the reference tooling ships under `gaig_toolkit/_bundled/automation` instead of a top-level `automation` package, and `automation/tests` is no longer in the wheel. Repository scripts, CI paths, and the GitHub Action are unchanged.
- Package metadata: SPDX license `MIT` with license files, classifiers, and project links. README links are absolute and pinned to the release tag so they resolve on package indexes.
- The Release Assets workflow gains PyPI and TestPyPI trusted-publishing jobs that upload only the wheel and sdist. Both stay skipped until a repository variable enables them, so no upload happens now.

## [2.7.1] - 2026-10-23 - Plain Run Output

- `gaig check` and `gaig verify` print "Output contracts and Decision Pack integrity verified." in place of an internal phase name.
- A blocked `gaig check` run keeps its first line, "Governance validation blocked by CRITICAL findings." (or HIGH), then prints where the reports were written, the top three blocking findings to fix, and that `--fail-on none` generates the Decision Pack for review without failing.
- The browser check labels risk tiers as coming from the built-in calculator.
- The Release Assets workflow also attaches a CycloneDX SBOM of the clean wheel install and records a GitHub build-provenance attestation for every asset in `SHA256SUMS`. Applies to releases published after this change; existing releases are unchanged.
- Three profile schemas (Auditable AI assurance case, CISO AI risk, Quantum-AI convergence exercise) gain an `$id` like the other schemas. Required fields, types, and validation results are unchanged.
- Remove the completed rename migration note. This changelog and the release notes remain the record of the rename.
- Exit codes, flags, structured errors, JSON outputs, schemas, contracts, findings, and check logic are unchanged. No capability, authority, certification, or external reproducibility claim is strengthened. `authority_effect` remains NONE.

## [2.7.0] - 2026-10-23 - `gaig` Only

- Breaking: remove the deprecated `gag` command, the `gag_toolkit` import package, and the GitHub Action's `GAG_CHECK_REPORT_DIR`, `GAG_CHECK_EXIT_CODE`, and `GAG_CHECK_GATE_STATE` exports. Use `gaig`, `gaig_toolkit`, and `GAIG_CHECK_*`. Earlier releases are unchanged.
- Machine interfaces, `llms.txt`, and the site describe only the `gaig` and `gaig-mcp` names.
- No capability, schema, contract, or check-logic change. No capability, authority, certification, or external reproducibility claim is strengthened. `authority_effect` remains NONE.

## [2.6.1] - 2026-10-23 - First-Run Experience

- First-run experience patch. Lead the README with a plain-language opener and a no-install browser path. Simplify the Quick Start so it runs from a fresh clone without changing tracked files.
- Point the site's MCP setup at `gaig-mcp` and record the completed rename in `docs/GAIG_RENAME_MIGRATION.md`.
- Site accessibility and metadata: add a favicon, page descriptions, and share-preview tags; raise small text sizes; show a visible focus ring on every interactive control; extend reduced-motion handling.
- No command, schema, contract, or behavior change. `gag` remains a deprecated alias. No capability, authority, certification, or external reproducibility claim is strengthened. `authority_effect` remains NONE.

## [2.6.0] - 2026-10-23 - Primary Command `gaig`

- The installed command is now `gaig`. `gag` remains installed as a deprecated alias with the same entry point and unchanged output.
- The import package is now `gaig_toolkit`. `gag_toolkit` remains as a deprecated alias package that re-exports it, so `python -m gag_toolkit.cli` keeps working.
- Add a composite GitHub Action (`action.yml`) that runs `gaig check` on an inventory CSV, fails on findings at the selected threshold, and labels its summary non-authorizing. It exports `GAIG_CHECK_REPORT_DIR`, `GAIG_CHECK_EXIT_CODE`, and `GAIG_CHECK_GATE_STATE`, plus the deprecated `GAG_CHECK_*` names with the same values.
- Add a Release Assets workflow that builds the wheel and sdist from a release tag and attaches them with `SHA256SUMS`.
- Machine interface and `llms.txt` command strings use `gaig`.
- No capability, authority, or contract change. `authority_effect` remains NONE.

## [2.5.3] - 2026-10-23 - Assurance State Integrity

- Assurance state integrity patch. Correct stale profile-registration documentation, current profile and browser documentation, and the organizational-maturity interoperability heading and boundaries. Correct Quantum-AI publication-status semantics. Do not strengthen capability, authority, certification, or external reproducibility claims. `authority_effect` remains NONE.

## [2.5.2] - 2026-10-23 - Release Surface Integrity

- Release surface integrity patch. Correct the public status badge. No maturity semantic change. No machine-interface semantic change. No authority change. `authority_effect` remains NONE.

## [2.5.1] - 2026-10-23 - Public Reference Integrity

- Public reference integrity patch. Correct current-release references. Preserve v2.5.0 maturity semantics. No runtime or authority change. `authority_effect` remains NONE.

## [2.5.0] - 2026-10-23 - Organizational AI Maturity Evidence

- Add organizational AI maturity evidence profile `organizational-ai-maturity-v0.1`. A human determines maturity. Automation checks whether submitted evidence can carry that determination. There is no maturity score. `authority_effect` remains NONE.
- Add a local-only maturity browser. Partial coverage is not framework completion. The adapter catalog remains the structural source.
- Machine-interface version is 1.2.0. `supported` remains equal to the browser list.

## [2.4.0] - 2026-10-23 - Assurance Interoperability & Agent Connectivity

- Split machine-interface profile discovery into `cli_supported` and `browser_supported`. `supported` remains equal to the browser list. Machine-interface version is 1.1.0. `authority_effect` remains NONE.
- Package metadata identifies 2.4.0.
- Register independent assurance, mission assurance, and machine-learning assurance for CLI use. The browser still renders only Auditable AI, the synthetic Quantum-AI exercise, and CISO accountability.
- Independent assurance requires a complete submitted qualification summary. CONDITIONAL, future, and expired qualifications cannot pass. Native authenticity is not established.
- Mission assurance can consume qualification, unresolved-decision, and protected-concern-disposition references. Expired or not-qualified records, blocking unresolved decisions, and HOLD/STALE concern effects fail closed. Absence of a reference is not evidence of absence.
- Add native portfolio reference checks, a local Assurance Context Binding consumer, and a Decision Pack / Context Binding consistency check. These do not retrieve external artifacts or confer authority.
- Add the mission-assurance challenge and the unregistered offline synthetic agent-action evidence example.
- Browser workspace: a newer input clears the previous preview, results, machine output, and Decision Pack downloads. A per-input token prevents an earlier evaluation from rendering after a newer input.
- Browser accessibility: evaluation views use the ARIA tab pattern; the machine-output switch exposes aria-pressed; scrollable regions are focusable; skip links are present; evaluation status is announced politely. CSV errors name the column and row without echoing cell contents.
- Add a synthetic browser example with governance gaps.
- Add `llms.txt`, shared navigation, and a Connect page for local agent setup. Remote MCP use requires allowed hosts and a bearer token. No hosted endpoint is operated.
- Add history privacy and pull-request identity checks.

## [2.3.0] - 2026-08-29 - Assurance & Accountability Profiles

- Added one common deterministic, non-authorizing profile result spine and registry-driven `gag profile` CLI.
- Added Auditable AI release-candidate, synthetic Quantum-AI convergence research, and experimental CISO accountability profiles.
- Added a local-only browser Profile Result viewer, machine discovery, synthetic fixtures, and bounded verification coverage while preserving Contract v1 and the primary Decision Pack runtime.

## [2.2.0] - 2026-08-29 - AI Sovereignty Control Layer

- Released the local-first browser, machine interface, contract-generated templates, and first-time-use improvements that accumulated on `main` after v2.1.0.
- Added the bounded AI Sovereignty Control Layer, including the sovereignty checker, S0-S4 assessment tiers, hard and advisory controls, ZDR review, model liquidity, compute assurance, permissions, audit, rollback, and owned-context materials.
- Added dedicated sovereignty CI while preserving the primary Decision Pack runtime, human authority, and existing evidence boundary.

## [2.1.0] - 2026-07-29 — Decision-Ready Governance

- Made critical governance findings fail closed by default.
- Connected the checked-in inventory schema to runtime validation.
- Connected the checked-in governance policy to runtime findings.
- Added stable governance rule identifiers.
- Added safe exit code `2` for schema, policy, input, and configuration failures.
- Added deterministic AI Governance Decision Pack generation.
- Added checked-in reference output and drift checking.
- Added repository integrity validation and release-readiness evidence.
- Preserved final approval, risk acceptance, and deployment decisions as human-owned.


## [2.0] - 2026-06-01 — Enterprise Adoption Package

- Added `/enterprise` directory.
- Added board and executive reporting pack.
- Added Executive AI Governance Board Charter.
- Added Executive AI Governance Decision Memo template.
- Added Quarterly AI Risk Report template.
- Added Enterprise 30/60/90/180-day rollout plan.
- Added department rollout playbook.
- Added audit-ready evidence binder.
- Added vendor onboarding package.
- Added procurement AI review gate.
- Added role-based training materials.
- Added sector adoption tracks.
- Added executive dashboard metrics.
- Added sample department adoption and enterprise risk registers.
- Added enterprise adoption workbook.

## [1.2] - 2026-06-01 — Automation Layer

- Added `/automation` directory.
- Added AI risk tier calculator.
- Added governance validator.
- Added executive governance report generator.
- Added one-command automation pipeline.
- Added JSON schema for AI system inventory records.
- Added policy-as-code starter rules.
- Added sample AI inventory data.
- Added GitHub Actions workflow scaffold.
- Added v1.2 release notes and automation documentation.

## [1.1] - 2026-06-01 — Practical Toolkit

- Added `/tools` practical governance tools.
- Added `/checklists` deployment approval checklist.
- Added `/spreadsheets` CSV templates and Excel workbook.
- Added `/sample-registers` AI system register.
- Added `/implementation-guides` 30/60/90-day implementation guide and Executive AI Governance Board Charter.
- Added v1.1 operating path: Practical Toolkit after v1.0 Governance OS.

## [1.0] - 2026-06-01 — Aligned Order

- Initial public release of Global AI Governance Solutions.
- Added core doctrine, 12 Governance Commandments, 9-Layer Execution Stack, and `governance-os.yaml`.
- Added templates, policies, and examples.
- Established the operating principle: No trust without verification.
