# Agent setup

This guide is for an AI agent, or a lead agent / orchestrator, that has been asked to set up Global AI Governance from <https://ai-governance.solutions/>. Each step gives the exact command and the result to expect. No account, API key, or sign-up is needed, and every install comes from a tagged GitHub release.

Live copy: <https://ai-governance.solutions/AGENT_SETUP.md>. Source: [`docs/AGENT_SETUP.md`](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/blob/main/docs/AGENT_SETUP.md).

Status: TESTED end to end in a clean Linux environment (Python 3.13, uv) by running the commands below in order. It is not independently verified, and it has not been run inside Claude Code, Claude Desktop, Cursor, VS Code, or the Grok CLI; the client configs are launch-tested only.

What an agent can set up alone, and what stays with people:

| An agent can do this unattended | This stays with an accountable person |
|---|---|
| Install the CLI, the MCP server, and the guards | Approve, deploy, accept risk, or shut down a system |
| Run checks and build a Decision Pack | Decide on the Decision Pack |
| Validate an Agent Trust Passport | Issue a passport and hold its signing key |
| Record vulnerability evidence | Approve a closure proof |

Every output carries `authority_effect: NONE`. A passing check means no check stopped the work; it is not an approval.

## Current versions

| Component | Version | Install |
|---|---|---|
| Toolkit (`gaig` CLI) | v2.8.0 | release wheel |
| AI Governance MCP (`gaig-mcp`) | v0.4.0 | `uvx` from the tag |
| Agentic AI Governance (`validate-passport`) | v0.1.0-alpha.4 | `pip` from the tag |
| Verified Vulnerability Governance (`vvd`) | v0.3.0 | `pip` from the tag |

`gaig-mcp` v0.4.0 bundles the Toolkit at v2.7.2 (commit `cc5f599`) and Agentic AI Governance at commit `58bdfb2`. Its outputs report those commits in `source`.

## 0. Requirements

Python 3.11 or later, `git`, and `curl`. The MCP server also needs [uv](https://docs.astral.sh/uv/); step 4 installs it into the virtual environment if it is missing. Commands are for bash on Linux or macOS. On Windows, use Git Bash and activate with `. .venv/Scripts/activate`.

```bash
mkdir gaig-setup && cd gaig-setup
python3 -m venv .venv && . .venv/bin/activate
python -c "import sys; assert sys.version_info >= (3, 11), sys.version; print('python ok')"
```

Expect: `python ok`.

## 1. Read the machine-readable entry points

```bash
curl -fsSL https://ai-governance.solutions/llms.txt | head -20
curl -fsSL https://ai-governance.solutions/machine-interface.json \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d['machine_interface_version'], d['release'])"
```

Expect the llms.txt title `# Global AI Governance Toolkit` and its `## Agent setup (start here)` section, then `1.4.0 v2.8.0`.

The schema URLs in llms.txt and machine-interface.json point at the `v2.7.2` tag on purpose: those schemas did not change in v2.8.0, and their `$id` values name v2.7.2.

## 2. Install the Toolkit CLI

```bash
REL=https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/releases/download/v2.8.0
curl -fsSLO "$REL/global_ai_governance-2.8.0-py3-none-any.whl"
curl -fsSLO "$REL/SHA256SUMS"
grep ' global_ai_governance-2.8.0-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
python -m pip install --quiet ./global_ai_governance-2.8.0-py3-none-any.whl
gaig --version
```

Expect: `global_ai_governance-2.8.0-py3-none-any.whl: OK`, then `2.8.0`. On macOS, use `shasum -a 256 -c -` in place of `sha256sum -c -`.

Optional build-provenance check, if the GitHub CLI is installed and signed in:

```text
gh attestation verify global_ai_governance-2.8.0-py3-none-any.whl --owner GLOBAL-AI-GOVERNANCE
```

Expect exit code 0.

## 3. Run a check and build a Decision Pack

```bash
curl -fsSLO https://ai-governance.solutions/sample-ai-inventory.csv
gaig check sample-ai-inventory.csv --outdir out
gaig verify out
python -c "import json; r=json.load(open('out/governance-result.json')); print(r['validation_state'], r['governance_gate_state'], r['human_decision_state'])"
```

Expect `Governance automation complete.` with a list of outputs, then `Output contracts and Decision Pack integrity verified.`, then `VALID PASSED_CURRENT_AUTOMATED_CHECKS PENDING_HUMAN_DECISION`. The Decision Pack is in `out/decision-pack/` for the person accountable.

The site's sample is the clean inventory. To see what a check finds, run the example with gaps:

```bash
curl -fsSL -o sample-with-gaps.csv https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.8.0/automation/sample-data/sample-ai-inventory.csv
gaig check sample-with-gaps.csv --outdir out-gaps --fail-on none >/dev/null
python -c "import json; r=json.load(open('out-gaps/governance-result.json')); print(r['governance_gate_state'], r['finding_count'])"
```

Expect `BLOCKED 5`: five findings for a person to review. Without `--fail-on none`, `gaig check` exits nonzero when findings meet the threshold, which is how a pipeline stops for review.

To check your own systems, download the blank template from <https://ai-governance.solutions/ai-system-inventory-template.csv>, fill one row per AI system or agent, and run `gaig check` on it. `gaig verify` works on `gaig check` output folders only.

### Optional: assurance profiles

`gaig profile` reads a JSON case file, not the inventory CSV. These synthetic cases are from the v2.8.0 tag:

```bash
RAW=https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.8.0
curl -fsSL -o auditable.json "$RAW/automation/assurance/auditable-ai/fixtures/pass.json"
curl -fsSL -o maturity.json "$RAW/automation/profiles/fixtures/maturity-supported.json"
curl -fsSL -o assurance.json "$RAW/automation/assurance/independent-assurance/fixtures/agent_pass.json"
gaig profile auditable-ai-v1 auditable.json --outdir p-auditable
gaig profile organizational-ai-maturity-v0.1 maturity.json --outdir p-maturity
gaig profile independent-assurance-v0.1 assurance.json --outdir p-assurance --evaluation-time 2026-10-15T00:00:00Z
for d in p-auditable p-maturity p-assurance; do python -c "import json,sys; r=json.load(open(sys.argv[1]+'/profile-result.json')); print(r['profile_id'], r['status'])" "$d"; done
```

Expect each command to exit 0, then `auditable-ai-v1 PASS`, `organizational-ai-maturity-v0.1 PASS`, and `independent-assurance-v0.1 PASS`.

The independent assurance case is dated. Without `--evaluation-time` it is judged at a default time outside its qualification window, and it fails closed with exit 1 and `status: FAIL`. That is the intended behavior. For your own case, pass the time you want it judged at.

## 4. Run the MCP server

```bash
command -v uvx >/dev/null || python -m pip install --quiet uv
uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0 gaig-mcp --version
```

The first run builds the package from the tag in a few seconds. Expect `0.4.0`. The server speaks stdio by default. Add `--http --port 8000` for Streamable HTTP at `/mcp`.

Check it the way an MCP client would. This script starts the server, lists its tools, and calls each read-only tool once:

```bash
cat > mcp_check.py <<'PY'
"""Start gaig-mcp over stdio, list its tools, and call each one once."""
import json, subprocess

CMD = ["uvx", "--from",
       "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0", "gaig-mcp"]
proc = subprocess.Popen(CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, text=True)
next_id = 0

def rpc(method, params=None, notify=False):
    global next_id
    msg = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    if not notify:
        next_id += 1
        msg["id"] = next_id
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    while not notify:
        reply = json.loads(proc.stdout.readline())
        if reply.get("id") == next_id:
            return reply["result"]

def call(name, args):
    result = rpc("tools/call", {"name": name, "arguments": args})
    return json.loads(result["content"][0]["text"])

info = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                          "clientInfo": {"name": "setup-check", "version": "1"}})
rpc("notifications/initialized", notify=True)
print("server", info["serverInfo"]["name"], info["serverInfo"]["version"])
print("tools", sorted(t["name"] for t in rpc("tools/list")["tools"]))
inv = call("check_inventory", {"use_sample": True})
print("check_inventory", inv["result"]["validation_state"], inv["result"]["governance_gate_state"],
      "authority_effect", inv["authority_effect"])
for example in ("signed-unrevoked", "signed-revoked"):
    out = call("validate_passport", {"example": example})
    print("validate_passport", example, out["result"]["verification"]["verification_primary_status"],
          "exit", out["result"]["validator_exit_code"])
proc.stdin.close()
proc.wait(timeout=10)
PY
python mcp_check.py
```

Expect:

```text
server gaig-mcp 0.4.0
tools ['build_decision_pack', 'check_inventory', 'validate_passport']
check_inventory VALID BLOCKED authority_effect NONE
validate_passport signed-unrevoked VALID exit 0
validate_passport signed-revoked REVOKED exit 1
```

The server's sample inventory is the one with gaps, so `BLOCKED` is the expected result: the check found missing owners, monitoring, or shutdown paths for a person to review.

## 5. Register the server with your agent client

Use one of these. Each runs the same `uvx` command. If your client cannot find `uvx`, put the absolute path from `command -v uvx` in `command`.

Claude Code:

```text
claude mcp add gaig --scope project -- \
  uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0 gaig-mcp
```

Grok CLI:

```text
grok mcp add gaig -- uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0 gaig-mcp
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.gaig]
command = "uvx"
args = ["--from", "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0", "gaig-mcp"]
```

Claude Desktop, Cursor (`.cursor/mcp.json`), or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "gaig": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0", "gaig-mcp"]
    }
  }
}
```

VS Code uses the same entry under `servers` in `.vscode/mcp.json`. Ready-made files for each client are in [`examples/client-configs/`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/tree/v0.4.0/examples/client-configs). After a restart, the client should list `check_inventory`, `build_decision_pack`, and `validate_passport`. Remote platforms (ChatGPT, the OpenAI, Anthropic, and xAI APIs, grok.com) cannot reach stdio or localhost; they need an HTTPS server you host, as described in the [MCP README](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.4.0/README.md).

## 6. Guard tool calls with Action Levels

The Action Level guard is a `PreToolUse` hook for Claude Code and the Grok CLI. Levels 0 to 3 run, Level 4 asks an accountable person (Claude Code) or is denied (the Grok CLI, whose hooks cannot ask), and Level 5 is denied. A tool without a level counts as Level 4. The hook files are not in the package, so fetch them from the tag:

```bash
HOOKS=.claude/hooks   # for the Grok CLI, use .grok/hooks
mkdir -p "$HOOKS"
STACKS=https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/v0.4.0/examples/agent-stacks
for f in tool_call_hook.py action_level_guard.py passport_tool_call_hook.py; do
  curl -fsSL -o "$HOOKS/$f" "$STACKS/$f"
done
cat > "$HOOKS/action-levels.json" <<'JSON'
{"send_external_email": 4, "delete_records": 5}
JSON
for t in mcp__gaig__check_inventory mcp__crm__send_external_email mcp__crm__delete_records; do
  printf '%s -> ' "$t"
  printf '{"tool_name": "%s"}' "$t" | python "$HOOKS/tool_call_hook.py" --policy "$HOOKS/action-levels.json"
  echo
done
```

Expect an empty decision (allow) for `mcp__gaig__check_inventory`, `"permissionDecision": "ask"` for `send_external_email`, and `"permissionDecision": "deny"` for `delete_records`. List your own tools and levels in `action-levels.json`; one entry covers the plain name and its `mcp__server__` (Claude Code) or `server__` (Grok CLI) form.

To turn the hook on, merge [`claude-code.settings.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.4.0/examples/client-configs/claude-code.settings.json) into `.claude/settings.json`, and add `--policy "$CLAUDE_PROJECT_DIR/.claude/hooks/action-levels.json"` to its command. For the Grok CLI, put [`grok-cli.hooks.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.4.0/examples/client-configs/grok-cli.hooks.json) in `.grok/hooks/` and trust it with `/hooks-trust`. These hook entries are TESTED with recorded-format input, not inside either client.

### Check the passport too

`check_tool_call` combines the passport check, the revocation check, and the Action Level, at the server's own clock. It is a Python function and a hook, not an MCP tool. The bundled example passports are dated, so at today's clock they are expired, and the check denies. That is the expected result:

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.4.0"
python -c "
from gaig_mcp.core import check_tool_call
r = check_tool_call('send_external_email', tool_level=4, example='signed-unrevoked')['result']
print(r['call_disposition']); print(r['reasons'][0])"
```

Expect `deny`, then `Passport did not verify at the server clock time (status EXPIRED).`

An `allow` or `ask` needs a real passport, its trusted key, a current signed revocation list, and the evidence bundle. An accountable person issues the passport and holds the signing key; an agent cannot issue its own. With those files in place, run `passport_tool_call_hook.py` with `--passport`, `--trusted-key`, `--revocation-list`, `--bundle-manifest`, and `--bundle-root`, as described in the [MCP README](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.4.0/README.md#check-the-passport-and-the-action-level-before-each-tool-call).

## 7. Agent Trust Passports and fleet controls

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance@v0.1.0-alpha.4"
validate-passport --example signed-unrevoked >/dev/null; echo "exit $?"
validate-passport --example signed-revoked >/dev/null; echo "exit $?"
```

Each run also prints, on stderr, that verification is not authorization. Expect `exit 0` (VALID), then `exit 1` (REVOKED).

The fleet controls reference tool runs from a checkout at the tag:

```bash
git -c advice.detachedHead=false clone --quiet --depth 1 --branch v0.1.0-alpha.4 https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance agentic
python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json >/dev/null; echo "exit $?"
python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/ancestor-suspended.json >/dev/null; echo "exit $?"
```

Expect `exit 0` (a sub-agent within its parent's ceiling: `PERMITTED`), then `exit 3` (an ancestor's passport is suspended: `NOT_PERMITTED`). Other cases are in `agentic/examples/fleet-controls/`.

## 8. Verified Vulnerability Governance

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance@v0.3.0"
mkdir vvg && cd vvg
vvd init >/dev/null
vvd asset create --name demo-repo --owner-team appsec >/dev/null
ASSET_ID=$(vvd asset list | python -c "import json,sys; print(json.loads(sys.stdin.readline())['asset_id'])")
curl -fsSL -o sample.sarif https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/v0.3.0/examples/sarif/sample.sarif
vvd finding import --sarif sample.sarif --asset-id "$ASSET_ID"
vvd finding demo >/dev/null
vvd close-check --finding-id finding-demo-001; echo "exit $?"
vvd add-demo-closure-proof --finding-id finding-demo-001 >/dev/null
vvd close-check --finding-id finding-demo-001; echo "exit $?"
vvd audit verify
cd ..
```

Expect the new finding ID and `Imported 1 finding(s).`, then `Blocked: no approved closure proof exists.` with `exit 1`, then `Closure allowed using manual_review proof.` with `exit 0`, then `Audit chain intact: 7 event(s)` and the chain head.

The demo proof is synthetic test data. For a real finding, an agent records evidence with `vvd evidence add`; the closure proof is approved by a reviewer in a separate role, with `vvd proof add --reviewer ... --decision approved`. An agent should not record that approval for itself.

## 9. Browser-only tools

[Containment Ledger](https://global-ai-governance.github.io/containment-ledger/) and [Peace OS: Crisis Room](https://global-ai-governance.github.io/peace-os/) run in a browser with no install. They are made for a person to review and decide, so an agent's part is to point the right person to them.

## Done check

Run this from the `gaig-setup` folder. Every line should end in `ok`:

```bash
check() { if eval "$2" >/dev/null 2>&1; then echo "$1 ok"; else echo "$1 FAILED"; fi; }
check "toolkit 2.8.0      " "gaig --version | grep -qx '2.8.0'"
check "decision pack      " "gaig verify out"
check "mcp server 0.4.0   " "python mcp_check.py | grep -q 'server gaig-mcp 0.4.0'"
check "action level guard " "printf '{\"tool_name\": \"x__delete_records\"}' | python .claude/hooks/tool_call_hook.py --policy .claude/hooks/action-levels.json | grep -q deny"
check "passport validator " "validate-passport --example signed-unrevoked"
check "fleet controls     " "python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json"
check "vulnerability audit" "cd vvg && vvd audit verify"
```

Then tell the person you work for what is ready, and what is waiting on them: reviewing the Decision Pack, issuing a passport if they want pre-call passport checks, and approving any Level 4 action.

## If something differs

| You see | Why, and what to do |
|---|---|
| `input is not valid JSON` from `gaig profile` | Profiles read a JSON case file, not the CSV. Use the cases in step 3. |
| `independent-assurance-v0.1 ... FAIL`, exit 1 | The case is dated. Pass `--evaluation-time`. |
| `gaig verify` reports a missing `normalized-inventory.json` | `verify` reads `gaig check` output, not profile output. |
| `check_tool_call` returns `deny`, status `EXPIRED` | Expected for the bundled examples. A real decision needs a human-issued passport. |
| Every tool asks for approval | No level is set for it, so it counts as Level 4. Add it to `action-levels.json`. |
| `uvx: command not found` in a client | Use the absolute path from `command -v uvx` in the client config. |
| Schema URLs name `v2.7.2` | Intended. Those schemas did not change in v2.8.0. |

## More

- [llms.txt](https://ai-governance.solutions/llms.txt) and [machine-interface.json](https://ai-governance.solutions/machine-interface.json)
- [Connect page](https://ai-governance.solutions/connect.html)
- [Toolkit README](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit#quick-start)
- [AI Governance MCP](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/tree/v0.4.0)
- [Agentic AI Governance](https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/tree/v0.1.0-alpha.4)
- [Verified Vulnerability Governance](https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/tree/v0.3.0)
