# GAIG rename migration plan (gag to gaig)

**Status:** PROPOSED. This document is an inventory and plan, not a change. Nothing listed here has been renamed yet.

**Goal:** the abbreviation for Global AI Governance is always `gaig`, never `gag`, in every public repository of the `GLOBAL-AI-GOVERNANCE` account.

**What already shipped (non-breaking):** the "Rename gag to gaig (non-breaking changes)" pull requests rename only things that have no behavior or interface:

- the README section markers `<!-- gag:nav -->`, `<!-- /gag:nav -->`, `<!-- gag:footer -->`, `<!-- /gag:footer -->` become `gaig:` in eight repositories. No script, workflow, or sync tool in any repository matches on these markers.
- the toolkit site's internal CSS classes `gag-bar`, `gag-brand`, `gag-links`, `gag-cta`, `gag-footer`, `gag-footer-ctas` become `gaig-*`. They are renamed consistently in `web/index.html`, `web/connect.html`, and `web/styles.css`. No JavaScript or test references them.

Everything below is **breaking or not yet safe** and is intentionally unchanged. The working rule was: when unsure, treat it as breaking.

## Open decision: alias period or clean break

This is **not decided**. Maintainers must choose one before any step in the rollout below.

| Option | What it means | Cost | Benefit |
| --- | --- | --- | --- |
| A. Alias period | Ship `gaig` names and keep the `gag` names working for a stated period. That means a second console script, a `gag_toolkit` / `gag_mcp` shim package re-exporting the new module, env-var fallback reading `GAIG_*` then `GAG_*` with a deprecation warning, and a `GagInputError = GaigInputError` alias. Remove them in a later major/minor release. | Old names stay visible for a while, more code and tests. | No existing user, script, CI job, or MCP client config breaks on upgrade. |
| B. Clean break | Rename everything in one coordinated release per repository and document it as breaking. | Every existing install, script, client config, and deployment must be updated at once. Security env vars silently stop applying if not renamed (see below). | `gag` disappears immediately. |

Security note for either option: `GAG_MCP_ALLOWED_HOSTS` and `GAG_MCP_BEARER_TOKEN` gate network exposure of the MCP server (`src/gag_mcp/server.py`, `build_http_app`). A clean break does **not** reliably fail closed:

- **Non-loopback bind** (for example `--host 0.0.0.0` in a container): with the old names ignored, the allow-list is empty and the server refuses to start. This fails closed.
- **Loopback bind behind a reverse proxy or tunnel** (for example `cloudflared` to `127.0.0.1:8000`): today the public hostname in `GAG_MCP_ALLOWED_HOSTS` is what forces the bearer token. If the new code ignores the old names, the allow-list is empty and the bind is loopback. The server would then start **without a token and without DNS-rebinding protection** while still reachable through the tunnel. **This fails open.**

The rename must therefore not silently drop the old names. The minimum is to detect any `GAG_MCP_*` variable and refuse to start with a message naming its `GAIG_MCP_*` replacement. The alias option instead honors the old names with a warning. Either way, the server must refuse to start when old and new names are both set to different values. Tests must cover the loopback-plus-tunnel case.

## Inventory of remaining occurrences

Kinds: **CLI** (command name or output), **PKG** (distribution, entry point, or import package), **API** (public Python name), **ENV** (environment variable), **WIRE** (value visible to MCP clients or HTTP callers), **CFG** (client configuration users copy), **MI** (machine interface consumed by agents), **CI**, **TEST**, **DOC** (documents a real command, package, or setting), **CHK** (file covered by release checksums), **HIST** (history: leave as-is).

### global-ai-governance-toolkit

| File | Kind | Occurrence | What breaks, for whom | Proposed replacement | Alias option |
| --- | --- | --- | --- | --- | --- |
| `pyproject.toml:15` | PKG/CLI | `gag = "gag_toolkit.cli:main"` | Every user, script, and CI job that runs `gag` | `gaig = "gaig_toolkit.cli:main"` | Yes: keep `gag` as a second console script during the alias period |
| `pyproject.toml:19` | PKG | `include = ["gag_toolkit*", ...]` | Packaging; must match the folder name | `gaig_toolkit*` (plus `gag_toolkit*` if a shim is kept) | Yes |
| `gag_toolkit/` (folder) | PKG | import package `gag_toolkit` | Anyone running `python -m gag_toolkit.cli` or importing it | `gaig_toolkit/` | Yes: a `gag_toolkit` shim that re-exports `gaig_toolkit` |
| `gag_toolkit/cli.py:1,19` | CLI | docstring, `prog="gag"` (help/usage text) | Users reading `--help`; tests or scripts matching usage text | `prog="gaig"` | Not needed: follows the command |
| `gag_toolkit/cli.py:87` | CLI | stderr prefix `gag: ` | Scripts that grep error output | `gaig: ` | Not applicable (cosmetic, but user-visible output) |
| `automation/scripts/run_profile.py:99` | CLI | error prefix `gag profile: ` | Scripts that grep error output | `gaig profile: ` | Not applicable |
| `automation/scripts/validate_repository.py:64` | CI | required-file entry `gag_toolkit/cli.py` | The repository validator fails if the folder moves without this change | `gaig_toolkit/cli.py` | Not applicable |
| `automation/tests/test_contract_spine.py:191` | TEST | `-m gag_toolkit.cli` | Test fails after the folder rename | `-m gaig_toolkit.cli` | Not applicable |
| `.github/workflows/ai-governance-checks.yml:40` | CI | `gag --version` | CI fails after the command rename | `gaig --version` (plus `gag --version` while the alias exists) | Not applicable |
| `web/machine-interface.json:4-7` | MI | `gag check/normalize/profile/verify` command strings | Agents and integrations that read the published machine interface and execute those commands | `gaig ...` | Not applicable. Publish only once the `gaig` command exists in a release |
| `web/llms.txt:13-16` | MI | `gag check/normalize/profile/verify` | Same as above, for LLM agents | `gaig ...` | Not applicable. Same timing |
| `web/llms.txt:35` | MI/DOC | `gag-mcp`, `gag_mcp`, `GAG_MCP_ALLOWED_HOSTS`, `GAG_MCP_BEARER_TOKEN` | Agents that follow these setup instructions | Update in the same release as the MCP rename | Not applicable |
| `web/connect.html:39-44` | CFG/DOC | `gag-mcp` commands; MCP client configs with server name/label `"gag"` (Claude Desktop, Anthropic API, OpenAI API, xAI API) | Users who copy these configs. Prompts that say "use gag" are tied to the server label | `gaig-mcp`; server name/label `"gaig"` | Server label is client-side: existing configs keep working with any label, but docs and prompts must agree |
| `web/connect.html` (other lines) | DOC | `GAG_MCP_*`, `gag_mcp` mentions | Users following setup docs | Update with the MCP rename | Not applicable |
| `README.md:54-57` | DOC | `gag check ... --outdir /tmp/gag-output`, `gag verify /tmp/gag-output` | Readers copying the quick start | `gaig check ... /tmp/gaig-output` | Not applicable. Kept with the command it documents |
| `README.md:322` (footer) | DOC | "command `gag-mcp`" | Readers | `gaig-mcp` | Not applicable |
| `docs/MACHINE_INTERFACES.md:18-22` | DOC/MI | command list | Integrators | `gaig ...` | Not applicable |
| `docs/automation-layer.md:46` | DOC | `gag check ...` | Readers | `gaig check ...` | Not applicable |
| `automation/README.md:5,18,73` | DOC | `gag profile`, `gag check`, `gag normalize`, `gag verify` | Readers | `gaig ...` | Not applicable |
| `automation/PROFILE_DEVELOPMENT_KIT.md:5` | DOC | `gag profile` | Profile authors | `gaig profile` | Not applicable |
| `automation/assurance/auditable-ai/README.md:7` | DOC | `gag profile auditable-ai-v1 ...` | Readers | `gaig profile ...` | Not applicable |
| `enterprise/ciso-ai-risk/QUICKSTART.md:4` | DOC | `gag profile ciso-ai-risk-v0.1 ...` | Readers | `gaig profile ...` | Not applicable |
| `CHANGELOG.md:37` | HIST | past entry "`gag profile` CLI" | Nobody. It is a historical record | **Leave as-is.** Add a new changelog entry at rename time | Not applicable |
| `release-notes/v2.3.0-assurance-accountability-profiles.md:5` | HIST | `gag profile` | Nobody | **Leave as-is** | Not applicable |
| `docs/release-readiness-v2.4.0.md:9` | HIST | `gag --version` | Nobody | **Leave as-is** | Not applicable |
| GitHub release notes v2.3.0 (not a file) | HIST | `gag profile` | Nobody | **Leave as-is** | Not applicable |

### ai-governance-mcp

| File | Kind | Occurrence | What breaks, for whom | Proposed replacement | Alias option |
| --- | --- | --- | --- | --- | --- |
| `pyproject.toml:6` | PKG | distribution `name = "gag-mcp"` | `pip` installs, upgrade paths, dependency pins | `gaig-mcp` | Partial: old installs must be uninstalled; a `gag-mcp` meta-package is possible but not recommended |
| `pyproject.toml:26` | PKG/CLI | `gag-mcp = "gag_mcp.server:main"` | Every client config and Dockerfile that runs `gag-mcp` | `gaig-mcp = "gaig_mcp.server:main"` | Yes: keep a second `gag-mcp` console script |
| `src/gag_mcp/` (`__init__.py`, `core.py`, `server.py`) | PKG | import package `gag_mcp`; `python -m gag_mcp.server` | Users and the bundle manifest that run `-m gag_mcp.server` or import `gag_mcp.core` | `src/gaig_mcp/` | Yes: a `gag_mcp` shim package |
| `src/gag_mcp/core.py:48` | API | `class GagInputError(ValueError)` (documented in README lines 68/80) | Callers that catch `GagInputError` | `GaigInputError` | Yes: `GagInputError = GaigInputError` |
| `src/gag_mcp/server.py:37`, `core.py:114` | WIRE | MCP server name `gag-mcp` in `initialize` and in result envelopes | Clients or tests that match server name | `gaig-mcp` | Not applicable (value change; announce) |
| `src/gag_mcp/server.py:140` | WIRE | `/health` returns `"server": "gag-mcp"` | Health checks or monitors that match the body | `gaig-mcp` | Not applicable (announce) |
| `src/gag_mcp/server.py:213` | CLI | `prog="gag-mcp"` | Help text | `gaig-mcp` | Not applicable |
| `src/gag_mcp/server.py:159,183,191-201` | ENV (security) | `GAG_MCP_ALLOWED_HOSTS`, `GAG_MCP_BEARER_TOKEN` | **Every remote deployment.** Ignoring the old names makes non-loopback binds refuse to start, but a loopback bind behind a tunnel/proxy would start **without token or Host protection** (fails open) | `GAIG_MCP_ALLOWED_HOSTS`, `GAIG_MCP_BEARER_TOKEN` | Yes: read new name, fall back to old with a deprecation warning, refuse on conflicting values |
| `src/gag_mcp/server.py:184` | ENV | `GAG_MCP_CORS_ORIGINS` | Browser-client deployments lose CORS | `GAIG_MCP_CORS_ORIGINS` | Yes: same fallback |
| `src/gag_mcp/core.py:76-85` | ENV | `GAG_TOOLKIT_PATH`, `GAG_AGENTIC_PATH` | Users with custom checkouts. The bundle `manifest.json` sets them | `GAIG_TOOLKIT_PATH`, `GAIG_AGENTIC_PATH` | Yes: same fallback |
| `src/gag_mcp/core.py:136,145,269` | WIRE (minor) | temp prefixes `gag-mcp-in-`, `gag-mcp-out-`, `gag-mcp-pp-` | Anything that cleans up or allow-lists temp paths by prefix (unlikely) | `gaig-mcp-*` | Not applicable |
| `src/gag_mcp/core.py:238-240` | WIRE/CLI | `reproduce_locally` hints `gag check ...`, `gag verify ...` returned to MCP clients | Agents that run the hint after the toolkit rename | `gaig check`, `gaig verify` | Ship only after the toolkit `gaig` command is released and pinned |
| `src/gag_mcp/core.py:309`, `__init__.py:1`, module docstrings | DOC/WIRE | "issued by gag-mcp" text in results | Cosmetic. It is in result text | `gaig-mcp` | Not applicable |
| `manifest.json:3,13,16,19-20` | PKG/ENV | bundle name `gag-mcp`, entry point `src/gag_mcp/server.py`, `-m gag_mcp.server`, `GAG_TOOLKIT_PATH`, `GAG_AGENTIC_PATH` | Desktop-extension bundle installs | Rename with the package and env vars | Follows the alias decision |
| `deploy/Dockerfile:1,11-13,16` | ENV/CLI | `GAG_MCP_*` docs and `CMD gag-mcp --http ...` | Container deployments (Render, Cloud Run, etc.) | `gaig-mcp`, `GAIG_MCP_*` | Follows the alias decision |
| `README.md` (lines 5, 7, 38-39, 51, 68, 80, 97-100, 112-178, 185-204) | DOC/CFG | commands, package, env vars, `GagInputError`, MCP client configs with server name/label `"gag"`, prompts "Use gag to ..." | Users copying configs and commands | `gaig` equivalents. Rewrite the line 7 sentence "Names that did not change" | Follows the alias decision |
| `docs/llms-txt-mcp-addendum.md:4-5` | MI | `gag-mcp` | Agents | `gaig-mcp` | Not applicable |
| `docs/verification-transcript.md:1,138,275` | HIST/DOC | recorded transcript output | Nobody (recorded evidence) | Regenerate with `scripts/smoke_test.py` after rename; do not hand-edit | Not applicable |
| `scripts/smoke_test.py:2,106,109,112` | TEST | `-m gag_mcp.server`, transcript header | Smoke test fails after folder rename | `gaig_mcp` | Not applicable |
| `tests/conftest.py`, `test_compat.py` (asserts `eps.get("gag-mcp") == "gag_mcp.server:main"`), `test_core.py`, `test_security.py`, `test_transports.py` | TEST | imports, env vars, entry-point assertion | Tests fail after rename | Update together. Add tests for env fallback if aliasing | Not applicable |
| `scripts/fetch_upstreams.sh:9-10`, `README.md:13-15` | PIN | toolkit pinned at `cf906ef62c114a16b017a073c30f74933b8399e5`, agentic at `2124aeaadf236303c584ac150a5ea61ca787d3f0` | The MCP imports `automation.scripts.*` (not `gag_toolkit`), so the toolkit folder rename does not break imports. But the `reproduce_locally` hints must match the pinned toolkit's command | Bump the toolkit pin to the first toolkit commit/release that ships `gaig`, in the same MCP change that updates the hints | Not applicable |

### GLOBAL-AI-GOVERNANCE (profile repository)

| File | Kind | Occurrence | What breaks, for whom | Proposed replacement | Alias option |
| --- | --- | --- | --- | --- | --- |
| `README.md:27` | DOC | "The `gag-mcp` command, `gag_mcp` Python package, and `GAG_MCP_*` variables are unchanged since the repository rename." | Readers. The sentence becomes false after the rename | Rewrite to name `gaig-mcp`, `gaig_mcp`, `GAIG_MCP_*` (and the alias period, if any) | Not applicable |
| `README.md:31` | DOC (security) | `GAG_MCP_ALLOWED_HOSTS` remote-use guidance | Operators | `GAIG_MCP_ALLOWED_HOSTS` | Not applicable |
| `portfolio.json:188` | MI | "Command gag-mcp and package gag_mcp." | Agents reading the portfolio | `gaig-mcp`, `gaig_mcp` | Not applicable |

### peace-os (all checksum-covered)

`SHA256SUMS.txt` covers `README.md` (line 11), `web/index.html` (line 153), and `web/styles.css` (line 158). `scripts/verify_release_artifacts.py` fails if any of them change without new sums. All items below therefore wait for the **next release candidate**, which gets freshly generated checksums.

| File | Kind | Occurrence | Proposed replacement |
| --- | --- | --- | --- |
| `README.md:3,7,106,115` | CHK | `gag:nav` / `gag:footer` markers | `gaig:` |
| `README.md:111` | CHK/DOC | "command `gag-mcp`" | `gaig-mcp` (after the MCP rename) |
| `web/index.html:19-22,59-60` | CHK | classes `gag-bar`, `gag-brand`, `gag-links`, `gag-cta`, `gag-footer-ctas`, `gag-footer-note` | `gaig-*` |
| `web/styles.css:122-130` | CHK | the same classes | `gaig-*` |

### Footer command mentions (documentation of a real command)

Each of these READMEs has one footer line saying "command `gag-mcp`". They change when the MCP command is renamed:

`agentic-ai-governance/README.md:189`, `ai-cyber-resilience-framework/README.md`, `ai-governance-os/README.md`, `containment-ledger/README.md`, `governed-systems-administration/README.md`, `verified-vulnerability-governance/README.md`, `.github/README.md`, `global-ai-governance-toolkit/README.md:322`, `peace-os/README.md:111` (checksum-covered).

### Occurrences added after the initial inventory

These arrived with the GitHub Action, the bundled MCP release, the client configurations, and the install table. They follow the same rules as the rows above. Line numbers in this document can drift as files change; search by occurrence.

| Repository | File | Kind | Occurrence | Rollout step |
| --- | --- | --- | --- | --- |
| global-ai-governance-toolkit | `action.yml` | CLI/ENV | runs `gag check`; exported step variables `GAG_CHECK_REPORT_DIR`, `GAG_CHECK_EXIT_CODE`, `GAG_CHECK_GATE_STATE` (public: later workflow steps read them); internal step variables `GAG_PYTHON`, `GAG_ACTION_PATH`, `GAG_ACTION_BIN`, `GAG_INVENTORY`, `GAG_OUTDIR`, `GAG_FAIL_ON`, `GAG_EVALUATION_TIME`, `GAG_STATUS` | Step 2. Exported variables follow the alias decision (export both names during an alias period) |
| global-ai-governance-toolkit | `README.md` (GitHub Action section) | DOC | `gag check`, `GAG_CHECK_*` | Step 2 |
| global-ai-governance-toolkit | `.github/workflows/ai-governance-checks.yml` | CI | `GAG_CHECK_EXIT_CODE`, `GAG_CHECK_GATE_STATE` assertions on the action | Step 2 |
| global-ai-governance-toolkit | `.github/workflows/release-assets.yml` | CI | `bin/gag --version` check on built release assets | Step 2 |
| ai-governance-mcp | `pyproject.toml`, `MANIFEST.in`, `scripts/bundle_upstreams.py`, `src/gag_mcp/_upstream/` | PKG | bundled upstream path `src/gag_mcp/_upstream`, package data keys `gag_mcp` | Step 4 |
| ai-governance-mcp | `.github/workflows/release-assets.yml` | CI | `bin/gag-mcp --version` check on built release assets | Step 4 |
| ai-governance-mcp | `examples/client-configs/` (`cursor.mcp.json`, `vscode.mcp.json`, `codex.config.toml`, `README.md`) | CFG | server key `gag`, command `gag-mcp` in the `uvx --from ...@v0.1.0` line | Step 4. Configs pinned to `@v0.1.0` keep working with that tag |
| ai-governance-mcp | `examples/agent-stacks/` and `tests/test_examples.py`, `tests/test_bundle.py` | CFG/TEST | `gag-mcp` command and `gag_mcp` imports in examples and their tests | Step 4 |
| GLOBAL-AI-GOVERNANCE | `README.md` (Install at a glance) | DOC | `uvx ... gag-mcp`, `docker build ... -t gag-mcp` | Step 5 |
| GLOBAL-AI-GOVERNANCE | `portfolio.json` (install entries) | MI | `uvx ... gag-mcp`, `docker build ... -t gag-mcp` | Step 5 |

The `ai-governance-mcp` upstream locks now point at newer toolkit and agentic commits than the ones named in the MCP table above. The rule is unchanged: bump the toolkit lock to the first commit or release that ships `gaig`, in the same MCP change that updates the hints.

### Repositories with no occurrences

`governance-continuity-assurance` (private) has none. The non-breaking PRs cleared every repository except `global-ai-governance-toolkit`, `ai-governance-mcp`, `GLOBAL-AI-GOVERNANCE`, and `peace-os` (plus the footer lines above).

## Items moved from "safe" to "breaking" during review

- `GagInputError`: an internal-looking name, but documented in the MCP README as something callers catch.
- `gag: ` / `gag profile: ` error prefixes: user-visible output that scripts may match.
- `/tmp/gag-output` in the toolkit quick start: part of a real command example; it changes with the command.
- peace-os markers and CSS classes: harmless in themselves, but covered by release checksums.
- `web/connect.html` command lines and MCP server name/label `"gag"`: user-copied configuration.
- Footer `gag-mcp` mentions: they document a real command.

## Suggested rollout order

Each step is its own reviewed PR and release. Under either option, do not publish a `gaig` command in machine interfaces before a release ships it.

1. **Decide alias period vs clean break** (open decision above). If aliasing, also decide the removal version.
2. **Toolkit release (`global-ai-governance-toolkit`).** Rename `gag_toolkit/` to `gaig_toolkit/` and the console script to `gaig`. Optionally keep the `gag` script and a `gag_toolkit` shim. Update `prog`, the error prefixes, `validate_repository.py`, `test_contract_spine.py`, CI (`gaig --version`), and all DOC rows. Add a new CHANGELOG entry describing the rename and the alias policy. Leave past CHANGELOG entries, `release-notes/`, and `docs/release-readiness-*` untouched. Tag a release.
3. **Toolkit machine interfaces.** Update `web/machine-interface.json`, `web/llms.txt` (commands), and `docs/MACHINE_INTERFACES.md` in the same release as step 2 or right after it. They must never advertise a command that is not yet installable.
4. **MCP release (`ai-governance-mcp`).** Rename the distribution to `gaig-mcp`, the package to `gaig_mcp`, `GagInputError` to `GaigInputError`, the server name, `/health`, temp prefixes, and `prog`. Rename the env vars to `GAIG_MCP_ALLOWED_HOSTS`, `GAIG_MCP_BEARER_TOKEN`, `GAIG_MCP_CORS_ORIGINS`, `GAIG_TOOLKIT_PATH`, `GAIG_AGENTIC_PATH`. Never silently ignore old `GAG_MCP_*` names. Either honor them with a warning (alias) or refuse to start naming the replacement (clean break). Refuse to start on conflicting old/new values. Test the loopback-plus-tunnel case. Add tests for both names. **Bump the toolkit pin** in `scripts/fetch_upstreams.sh` and the README to the step-2 release, and update the `reproduce_locally` hints to `gaig`. Update `manifest.json`, `deploy/Dockerfile`, README client configs (server name/label `"gaig"`), and the docs addendum. Regenerate `docs/verification-transcript.md` with `scripts/smoke_test.py`. Publish operator upgrade notes for remote deployments, covering how to rename secrets before upgrading.
5. **Site and portfolio surfaces.** Update the toolkit `web/connect.html` and `web/llms.txt` MCP lines, the `GLOBAL-AI-GOVERNANCE` README and `portfolio.json`, and the footer `gag-mcp` line in each repository README.
6. **peace-os next RC.** Rename the README markers, the footer command line, and the `web/` classes. Regenerate `SHA256SUMS.txt` and run `scripts/verify_release_artifacts.py` as part of the RC process.
7. **Alias removal (only if aliasing was chosen).** At the announced version, remove the `gag` script, the shims, `GagInputError`, and the env fallbacks. Add a changelog note.

History files (past CHANGELOG entries, `release-notes/`, `docs/release-readiness-*`, published GitHub release notes, recorded transcripts) stay as-is. Each repository's changelog gets a note at rename time instead.

Boundary: this plan is decision support only. It authorizes no change (`authority_effect: NONE`). Each step needs its own human review and approval.
