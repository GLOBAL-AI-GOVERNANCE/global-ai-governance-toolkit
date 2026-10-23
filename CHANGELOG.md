# Changelog
## Unreleased

Candidate notes for a later v2.5.0 tag. This section is not a published release. The published GitHub Release remains v2.4.0 until that tag exists.

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
