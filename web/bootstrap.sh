#!/usr/bin/env bash
# Global AI Governance one-command setup. authority_effect: NONE.
# Runs AGENT_SETUP.md steps 0-8 unattended into ./gaig-setup.
# Read https://ai-governance.solutions/AGENT_SETUP.md before you run this.
set -euo pipefail

SITE="${GAIG_SITE:-https://ai-governance.solutions}"
TOOLKIT_TAG=v2.8.2
MCP_TAG=v0.5.1
AGENTIC_TAG=v0.1.0-alpha.6
VVG_TAG=v0.4.0
ROOT="$(pwd)/gaig-setup"
PY="${ROOT}/.venv/bin/python"
PIP="${ROOT}/.venv/bin/pip"

need() { command -v "$1" >/dev/null || { echo "need $1" >&2; exit 1; }; }
need python3
need curl
need git
if ! command -v uvx >/dev/null; then
  need uv || { echo "need uv (https://docs.astral.sh/uv/) for uvx" >&2; exit 1; }
fi

mkdir -p "$ROOT"
cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "== 0. machine front door =="
curl -fsSL "$SITE/llms.txt" | head -n 1 | grep -q 'Global AI Governance Toolkit'
curl -fsSL "$SITE/machine-interface.json" \
  | python -c "import json,sys; d=json.load(sys.stdin); assert d['machine_interface_version']>='1.6.0' and d['release']=='v2.8.2'; print(d['machine_interface_version'], d['release'])"

echo "== 1. toolkit =="
WHL="global_ai_governance-2.8.2-py3-none-any.whl"
curl -fsSLO "https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/releases/download/${TOOLKIT_TAG}/${WHL}"
curl -fsSLO "https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/releases/download/${TOOLKIT_TAG}/SHA256SUMS"
grep " ${WHL}\$" SHA256SUMS | sha256sum -c -
"$PIP" install --quiet "./${WHL}"
gaig --version | grep -qx '2.8.2'

echo "== 2. inventory check =="
curl -fsSLO "$SITE/sample-ai-inventory.csv"
gaig check sample-ai-inventory.csv --outdir out >/dev/null
gaig verify out >/dev/null

echo "== 3-4. MCP server =="
"$PIP" install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@${MCP_TAG}"
export GAIG_MCP_FROM="git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@${MCP_TAG}"
cat > mcp_check.py <<'PY'
import asyncio, json, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params = StdioServerParameters(command="uvx", args=["--from", os.environ["GAIG_MCP_FROM"], "gaig-mcp"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            tools = await s.list_tools()
            print(f"server {init.server_info.name} {init.server_info.version}")
            print("tools", ", ".join(sorted(t.name for t in tools.tools)))
asyncio.run(main())
PY
"$PIP" install --quiet "mcp>=1.0"
python mcp_check.py | tee mcp_out.txt
grep -q 'server gaig-mcp 0.5.1' mcp_out.txt

echo "== 6. Action Level guard + automated Level 4 approver =="
HOOKS=.claude/hooks
mkdir -p "$HOOKS"
STACKS="https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/${MCP_TAG}/examples/agent-stacks"
for f in tool_call_hook.py passport_tool_call_hook.py action_level_guard.py; do
  curl -fsSL -o "$HOOKS/$f" "$STACKS/$f"
done
cat > "$HOOKS/action-levels.json" <<'JSON'
{"send_external_email": 4, "delete_records": 5, "open_pull_request": 4}
JSON
curl -fsSL -o "$HOOKS/action-levels.approver.json" \
  "https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/${MCP_TAG}/examples/policies/action-levels.automated-approver.json"
printf '{"tool_name": "x__delete_records"}' | python "$HOOKS/tool_call_hook.py" --policy "$HOOKS/action-levels.json" | grep -q deny
printf '{"tool_name": "x__open_pull_request"}' | python "$HOOKS/tool_call_hook.py" --policy "$HOOKS/action-levels.approver.json" | grep -q allow

echo "== 7. passports, fleet controls, lead agent =="
"$PIP" install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance@${AGENTIC_TAG}"
validate-passport --example signed-unrevoked >/dev/null
git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$AGENTIC_TAG" \
  https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance agentic
python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json >/dev/null
issue-passports issue agentic/examples/fleet-issuance/fleet-policy.json --out fleet/ >/dev/null
python -c "import json,sys; agents=json.load(open('fleet/fleet.json'))['agents']; assert all(a['verification_primary_status']=='VALID' for a in agents); print(len(agents),'VALID')"
lead-agent demo > lead-agent-demo.json
python -c "import json; d=json.load(open('lead-agent-demo.json')); assert d['passed']; print('passed', len(d['checks']), 'checks')"

echo "== 8. VVG rescan closure =="
"$PIP" install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance@${VVG_TAG}"
mkdir -p vvg-rescan && cd vvg-rescan
for f in before.sarif after-fixed.sarif rescan_closure.py; do
  curl -fsSLO "https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/${VVG_TAG}/examples/automated-closure/$f"
done
vvd init >/dev/null
vvd asset create --name demo-repo --owner-team appsec >/dev/null
ASSETS=$(vvd asset list)
ASSET_ID=$(python -c "import json,sys; print(json.loads(sys.argv[1].splitlines()[0])['asset_id'])" "$ASSETS")
IMPORTED=$(vvd finding import --sarif before.sarif --asset-id "$ASSET_ID")
FINDING_ID=${IMPORTED%%$'\n'*}
vvd evidence add --finding-id "$FINDING_ID" --type source_to_sink_trace --summary "Request parameter reaches the HTML response" >/dev/null
python rescan_closure.py --finding-id "$FINDING_ID" --rescan after-fixed.sarif >/dev/null
vvd audit verify
cd ..

echo "== done check =="
check() { if eval "$2" >/dev/null 2>&1; then echo "$1 ok"; else echo "$1 FAILED"; exit 1; fi; }
check "toolkit 2.8.2      " "gaig --version | grep -qx '2.8.2'"
check "decision pack      " "gaig verify out"
check "mcp server 0.5.1   " "grep -q 'server gaig-mcp 0.5.1' mcp_out.txt"
check "action level guard " "printf '{\"tool_name\": \"x__delete_records\"}' | python .claude/hooks/tool_call_hook.py --policy .claude/hooks/action-levels.json | grep -q deny"
check "passport validator " "validate-passport --example signed-unrevoked"
check "fleet controls     " "python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json"
check "fleet passports    " "python -c \"import json,sys; sys.exit(any(a['verification_primary_status']!='VALID' for a in json.load(open('fleet/fleet.json'))['agents']))\""
check "level 4 approver   " "printf '{\"tool_name\": \"x__open_pull_request\"}' | python .claude/hooks/tool_call_hook.py --policy .claude/hooks/action-levels.approver.json | grep -q allow"
check "lead agent demo    " "lead-agent demo"
check "rescan closure     " "cd vvg-rescan && vvd audit verify"
echo "bootstrap complete. authority_effect: NONE"
