# Changelog
## [Unreleased]

- Add the agent setup guide, `docs/AGENT_SETUP.md`, published at `https://ai-governance.solutions/AGENT_SETUP.md`: every command an agent runs to install the CLI, run AI Governance MCP, register it with a client, add the Action Level guard, and try Agentic AI Governance and Verified Vulnerability Governance, with the expected result after each step and a done check. `llms.txt` opens with an agent setup section, the connect page adds `#setup` with an instruction to give an agent, the landing page links the guide, and machine interface 1.4.0 adds `discovery.agent_setup`. The README Quick Start uses `python3` and gives the checksum and attestation commands. Toolkit behavior is unchanged.
- Lead the landing page with "Govern AI before it acts." and state that the person accountable keeps the final decision.
- Show current product releases on the landing and connect pages: Verified Vulnerability Governance v0.2.0, Containment Ledger v1.0.0, and stable, released, or available labels for the rest.
- Pin the README, site, `llms.txt`, and machine interface to v2.7.2, including the `global_ai_governance-2.7.2-py3-none-any.whl` install path and the v2.7.2 tag commit for the GitHub Action. The machine interface version stays 1.2.0.
- Point the connect page, landing product map, and `llms.txt` to AI Governance MCP v0.3.2, which bundles toolkit v2.7.2.
- Refine the landing, connect, and maturity introductions. Behavior is unchanged.
- Add design tokens v2 shared with Peace OS and Containment Ledger: a hairline grid field and a luminous rule on the landing, connect, and maturity introductions, wider label tracking, and quiet hover glow. The rule draws once and stays still under reduced motion. Behavior is unchanged.
- The landing page reads as one page: a single introduction with four facts (open and local-first, any MCP agent, framework crosswalks, attested releases), the starting paths, the suite with a one-line value for each product and an anchor named after its repository, then the browser Toolkit at `#toolkit` without a second header. The non-authorizing scope and non-affiliation note move to a Scope section near the end. The product map on the Connect page shows the same suite and lists Verified Vulnerability Governance v0.1.4 and AI Governance Foundations v1.1.1. Toolkit behavior is unchanged.
- Show current releases on the landing page, connect page, `llms.txt`, and machine interface: Toolkit v2.8.0 (wheel `global_ai_governance-2.8.0-py3-none-any.whl` and the v2.8.0 tag commit for the GitHub Action), AI Governance MCP v0.4.0 with its passport and Action Level check before each tool call, Agentic AI Governance v0.1.0-alpha.4 schemas and Agent Fleet Controls, and Verified Vulnerability Governance v0.3.0. Unchanged schemas keep their v2.7.2 URLs. Machine interface 1.3.0 adds `release`, `profiles.independent_assurance` (contract 0.2.0 shutdown evidence for autonomous agents), and pins the profile registry to v2.8.0. Toolkit behavior is unchanged.

## [2.8.0] - 2026-10-24 - Autonomous Agent Shutdown Evidence

- Independent assurance contract 0.2.0 (profile id unchanged, `independent-assurance-v0.1`). A case with `autonomous_agent: true` fails with a CRITICAL finding unless it carries `agent_passport_ref` (`passport_id`, `sha256:` `passport_digest`) and `shutdown_evidence` with `shutdown_tested_at`, `result: PASSED`, and at least one evidence reference, tested no more than 90 days before the evaluation time. `max_shutdown_test_age_days` can only shorten the bound. A future test date or a missing evaluation time fails closed. New rule IDs: `AGENT_PASSPORT_MISSING`, `SHUTDOWN_TEST_MISSING`, `SHUTDOWN_TEST_NOT_PASSED`, `SHUTDOWN_TEST_EVIDENCE_REFS`, `SHUTDOWN_TEST_STALE`, `SHUTDOWN_TEST_IN_FUTURE`, `SHUTDOWN_TEST_AGE_UNKNOWN`.
- Results add `details.shutdown_test` (state, tested time, age in days, bound) when shutdown evidence is evaluated.
- The shutdown hint no longer asks for "verified" evidence. It names the fields and states that the profile checks the submitted record and does not establish that the test occurred.
- Current structured `shutdown_evidence` satisfies the existing high-consequence shutdown check. The legacy `shutdown_evidence_present` boolean still does for non-autonomous cases.
- Six synthetic fixtures and tests for the new rules. Existing fixtures and results are unchanged.
- Pin the README to v2.8.0. Unchanged schemas keep their v2.7.2 `$id`.
- Status: TESTED. No capability, authority, certification, or external reproducibility claim is strengthened. `authority_effect` remains NONE.

## [2.7.2] - 2026-10-24 - Resolvable Schema Identifiers

- Every schema `$id` now resolves. Identifiers use the release-pinned form `https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.7.2/<path>`, which returns the exact schema published in this release. Earlier identifiers named `github.com` paths that did not resolve. Schema content, required fields, types, and validation results are unchanged; only `$id` values differ. Consumers that match on the old identifier strings should update them.
- CI checks that every absolute schema `$id` names the file's own path at a release tag listed in this changelog, and the Release Assets workflow fetches every `$id` from the tag and requires the identical document before it attaches assets.
- The site root at ai-governance.solutions is the Global AI Governance landing page: what it is and who it is for, three starting paths (browser, command line, agent), the product map, and a GitHub link, followed by the unchanged browser Toolkit at `#toolkit`. Pages gain an absolute canonical link, a link-preview image, and an Apple touch icon. On narrow screens the site links sit on their own row.
- Pin the README, site, `llms.txt`, and machine interface to v2.7.1. The machine interface version stays 1.2.0.
- The Connect page and `llms.txt` add Claude Code and Grok CLI setup, the full Anthropic MCP connector shape, and an Action Level guard section linking to AI Governance MCP examples. The product map gains the `#products` anchor.
- Pin AI Governance MCP references on the Connect page and in `llms.txt` to v0.3.1, which ships the Action Level guard and bundles toolkit v2.7.1.
- Links that open a page at a section, such as `connect.html#guard`, land on the section at once instead of animating the scroll on load. Smooth scrolling for in-page links and the reduced-motion setting are unchanged.
- Packaging: the distribution name is `global-ai-governance`, so future wheel and sdist files are named `global_ai_governance-<version>`. The command `gaig` and the import package `gaig_toolkit` are unchanged, and assets of existing releases keep their names. The package is not on PyPI.
- The wheel installs only `gaig_toolkit` at the top level: the reference tooling ships under `gaig_toolkit/_bundled/automation` instead of a top-level `automation` package, and `automation/tests` is no longer in the wheel. Repository scripts, CI paths, and the GitHub Action are unchanged.
- Package metadata: SPDX license `MIT` with license files, classifiers, and project links. README links are absolute and pinned to the release tag so they resolve on package indexes.
- The Release Assets workflow includes PyPI and TestPyPI trusted-publishing jobs that would upload only the wheel and sdist. They are inactive, and nothing is published to PyPI or TestPyPI.

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
