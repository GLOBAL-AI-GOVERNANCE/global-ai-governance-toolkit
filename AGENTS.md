# AGENTS.md

Instructions for coding agents working in this repository.

## Setup and checks

```bash
python -m venv .venv && . .venv/bin/activate
python -m pip install -e ".[dev]"
python -m compileall -q automation web
python -m pytest automation/tests -q
```

Site and setup gates (from repo root):

```bash
python automation/scripts/generate_maturity_catalog.py --check
bash -n web/bootstrap.sh
```

Live end-to-end setup (clean directory; uses published release tags):

```bash
curl -fsSLO https://ai-governance.solutions/bootstrap.sh && bash bootstrap.sh
```

## Rules

- Every profile and evaluator result keeps `authority_effect: "NONE"`. Do not add a path that approves, certifies, or authorizes.
- Do not present proposals or design notes as shipped working features.
- Version pins on the public site come from `suite-manifest.json` / `suite-pins.json` via the sync workflows. Do not hand-edit version tables in AGENT_SETUP, JOURNEYS, bootstrap, or the site badges.
- Prefer squash-merge through green CI. Do not force-push `main`.
- Keep META CSP free of `frame-ancestors` (HTTP header only).
