# Releasing

Release tags in this repository are the source of truth for the Toolkit pin. After you publish a release (or after MCP / Peace OS / Agentic publish theirs):

1. The profile repo job **Sync suite versions** regenerates `suite-manifest.json` from GitHub releases and auto-merges when checks are green.
2. This repo's job **Sync site versions** pulls that manifest and refreshes `automation/suite-pins.json`, `docs/AGENT_SETUP.md`, `docs/JOURNEYS.md`, `web/bootstrap.sh`, connect/index/start pages, `web/llms.txt`, and `web/machine-interface.json`, then auto-merges.
3. Do not hand-edit those version strings. Run `python3 automation/scripts/sync_site_from_manifest.py --check` locally if you need to confirm drift.
4. Social preview PNGs under `/workspace/brand/social` render from the same suite-manifest; uploading the PNGs stays a browser step for the operator.

Cross-repo triggers use a scheduled pull or `workflow_dispatch` so no extra secrets are required (`GITHUB_TOKEN` cannot start workflows in other repositories).
