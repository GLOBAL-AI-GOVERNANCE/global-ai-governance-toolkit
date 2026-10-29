# Agent setup

This guide is for an AI agent, or a lead agent / orchestrator, that has been asked to set up Global AI Governance from <https://ai-governance.solutions/>. Each step gives the exact command and the result to expect. No account, API key, or sign-up is needed, and every install comes from a tagged GitHub release.

Live copy: <https://ai-governance.solutions/AGENT_SETUP.md>. Source: [`docs/AGENT_SETUP.md`](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/blob/main/docs/AGENT_SETUP.md).

Status: TESTED end to end in a clean Linux environment (Python 3.13, uv) by running the commands below in order. It is not independently verified, and it has not been run inside Claude Code, Claude Desktop, Cursor, VS Code, the Grok CLI, or the Gemini CLI; the client configs are launch-tested only.

Every step runs unattended. Nothing in this guide waits for a person. Two kinds of item are not steps:

| Runs unattended | Operator safety setting (default: a person) | External gates (not run here, not claimed) |
|---|---|---|
| Install the CLI, the MCP server, and the guards | Level 4 tool calls: ask a person by default, or go to the operator's automated approver for the tools its policy lists (step 6) | Independent review of the AI Cyber Resilience Framework (G7) |
| Run checks and build a Decision Pack | Risk acceptance (`approved_exception`) and `manual_review` closure proofs | Independent verification of Agentic AI Governance |
| Issue, validate, revoke, and refresh passports from a policy file (step 7) | Level 5 tool calls: always denied, with no setting to change that | Independent audit of Governed Systems Administration |
| Guard every tool call by passport and Action Level | | Human validation of Peace OS |
| Run the reference lead agent / orchestrator and its shutdown tests (step 7) | | |
| Close a vulnerability when a fresh rescan no longer reports it (step 8) | | |

Every output carries `authority_effect: NONE`. A passing check means no check stopped the work; it is not an approval.

## Fastest path: one command

```text
curl -fsSLO https://ai-governance.solutions/bootstrap.sh && bash bootstrap.sh
```

[`bootstrap.sh`](https://ai-governance.solutions/bootstrap.sh) runs steps 0 to 8 below without a prompt: it installs every component from its release tag into `gaig-setup/.venv`, issues passports for a sample fleet, guards three tool calls, runs the lead agent demo, closes a vulnerability from a rescan, and ends with a done check where every line ends in `ok`. Exit code 0 means every check passed. Read it before you run it; it is short. Run it again in the same folder and it repeats the checks. The steps below do the same thing one at a time.

## Current versions

| Component | Version | Install |
|---|---|---|
| Toolkit (`gaig` CLI) | v2.8.2 | release wheel |
| AI Governance MCP (`gaig-mcp`) | v0.5.1 | `uvx` from the tag |
| Agentic AI Governance (`validate-passport`) | v0.1.0-alpha.5 | `pip` from the tag |
| Verified Vulnerability Governance (`vvd`) | v0.4.0 | `pip` from the tag |

<!-- gaig:mcp-bundle -->
`gaig-mcp` v0.5.1 bundles the Toolkit at v2.8.1 (commit `0ab38c6a94a705e4423bfc9bb19ef2137f59f5c5`) and Agentic AI Governance at commit `58bdfb291df0de7c9437b4476e370a609c4b1d5f`. Its outputs report those commits in `source`. Bundle pins come from MCP `UPSTREAM_LOCK.json`, not from the Toolkit release tag.
<!-- /gaig:mcp-bundle -->

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

Expect the llms.txt title `# Global AI Governance Toolkit` and its `## Agent setup (start here)` section, then `1.6.0 v2.8.2`.

The schema URLs in llms.txt and machine-interface.json point at the `v2.7.2` tag on purpose: those schemas did not change in v2.8.2, and their `$id` values name v2.7.2.

## 2. Install the Toolkit CLI

```bash
REL=https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/releases/download/v2.8.2
curl -fsSLO "$REL/global_ai_governance-2.8.2-py3-none-any.whl"
curl -fsSLO "$REL/SHA256SUMS"
grep ' global_ai_governance-2.8.2-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
python -m pip install --quiet ./global_ai_governance-2.8.2-py3-none-any.whl
gaig --version
```

Expect: `global_ai_governance-2.8.2-py3-none-any.whl: OK`, then `2.8.2`. On macOS, use `shasum -a 256 -c -` in place of `sha256sum -c -`.

Optional build-provenance check, if the GitHub CLI is installed and signed in:

```text
gh attestation verify global_ai_governance-2.8.2-py3-none-any.whl --owner GLOBAL-AI-GOVERNANCE
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
curl -fsSL -o sample-with-gaps.csv https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.8.2/automation/sample-data/sample-ai-inventory.csv
gaig check sample-with-gaps.csv --outdir out-gaps --fail-on none >/dev/null
python -c "import json; r=json.load(open('out-gaps/governance-result.json')); print(r['governance_gate_state'], r['finding_count'])"
```

Expect `BLOCKED 5`: five findings to resolve. Without `--fail-on none`, `gaig check` exits nonzero when findings meet the threshold, which is how a pipeline stops for review.

To check your own systems, download the blank template from <https://ai-governance.solutions/ai-system-inventory-template.csv>, fill one row per AI system or agent, and run `gaig check` on it. `gaig verify` works on `gaig check` output folders only.

### Optional: assurance profiles

`gaig profile` reads a JSON case file, not the inventory CSV. These synthetic cases are from the v2.8.2 tag:

```bash
RAW=https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.8.2
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
uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1 gaig-mcp --version
```

The first run builds the package from the tag in a few seconds. Expect `0.5.1`. The server speaks stdio by default. Add `--http --port 8000` for Streamable HTTP at `/mcp`.

Check it the way an MCP client would. This script starts the server, lists its tools, and calls each read-only tool once:

```bash
cat > mcp_check.py <<'PY'
"""Start gaig-mcp over stdio, list its tools, and call each one once."""
import json, subprocess

CMD = ["uvx", "--from",
       "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1", "gaig-mcp"]
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
server gaig-mcp 0.5.1
tools ['build_decision_pack', 'check_inventory', 'validate_passport']
check_inventory VALID BLOCKED authority_effect NONE
validate_passport signed-unrevoked VALID exit 0
validate_passport signed-revoked REVOKED exit 1
```

The server's sample inventory is the one with gaps, so `BLOCKED` is the expected result: the check found missing owners, monitoring, or shutdown paths.

## 5. Register the server with your agent client

Use one of these. Each runs the same `uvx` command. If your client cannot find `uvx`, put the absolute path from `command -v uvx` in `command`.

Claude Code:

```text
claude mcp add gaig --scope project -- \
  uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1 gaig-mcp
```

Grok CLI:

```text
grok mcp add gaig -- uvx --from git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1 gaig-mcp
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.gaig]
command = "uvx"
args = ["--from", "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1", "gaig-mcp"]
```

Claude Desktop, Cursor (`.cursor/mcp.json`), or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "gaig": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1", "gaig-mcp"]
    }
  }
}
```

Gemini CLI (`.gemini/settings.json`): the same entry under `mcpServers`, as in [`gemini-cli.settings.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.5.1/examples/client-configs/gemini-cli.settings.json). Keep the server alias free of underscores; the Gemini CLI names its tools `mcp_gaig_check_inventory`.

VS Code uses the same entry under `servers` in `.vscode/mcp.json`. Ready-made files for each client are in [`examples/client-configs/`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/tree/v0.5.1/examples/client-configs). After a restart, the client should list `check_inventory`, `build_decision_pack`, and `validate_passport`. Remote platforms (ChatGPT, the OpenAI, Anthropic, and xAI APIs, grok.com) cannot reach stdio or localhost; they need an HTTPS server you host, as described in the [MCP README](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.5.1/README.md).

## 6. Guard tool calls with Action Levels

The Action Level guard is a `PreToolUse` hook for Claude Code and the Grok CLI, and a `BeforeTool` hook for the Gemini CLI. Levels 0 to 3 run, and Level 5 is denied. Level 4 is an operator safety setting: by default it asks a person (Claude Code) or is denied (the Grok and Gemini CLIs, whose hooks cannot ask); the operator can instead route listed Level 4 tools to an automated approver, below. A tool without a level counts as Level 4. The hook files are not in the package, so fetch them from the tag:

```bash
HOOKS=.claude/hooks   # for the Grok CLI, use .grok/hooks
mkdir -p "$HOOKS"
STACKS=https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/v0.5.1/examples/agent-stacks
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

To turn the hook on, merge [`claude-code.settings.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.5.1/examples/client-configs/claude-code.settings.json) into `.claude/settings.json`, and add `--policy "$CLAUDE_PROJECT_DIR/.claude/hooks/action-levels.json"` to its command. For the Grok CLI, put [`grok-cli.hooks.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.5.1/examples/client-configs/grok-cli.hooks.json) in `.grok/hooks/` and trust it with `/hooks-trust`. For the Gemini CLI, use [`gemini-cli.settings.json`](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/blob/v0.5.1/examples/client-configs/gemini-cli.settings.json) and put the hook files in `.gemini/hooks/`. These hook entries are TESTED with documented-format input, not inside any of the three clients.

### Run Level 4 unattended (operator safety setting)

A policy file can name an automated approver that the operator runs, and list the Level 4 tools it approves. Those calls then run with no person in the loop, and every decision records `approved_by`. Every other Level 4 call still asks; unknown tools are never auto-approved; Level 5 is always denied; and the approver can only list tools the same policy puts at Level 4.

```bash
curl -fsSL -o "$HOOKS/action-levels.approver.json" \
  https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/v0.5.1/examples/policies/action-levels.automated-approver.json
for t in mcp__gh__open_pull_request mcp__crm__send_external_email mcp__crm__delete_records; do
  printf '%s -> ' "$t"
  printf '{"tool_name": "%s"}' "$t" | python "$HOOKS/tool_call_hook.py" --policy "$HOOKS/action-levels.approver.json"
  echo
done
```

Expect `"permissionDecision": "allow"` with the reason `Level 4: approved by the operator's automated approver operator.ci-approver (listed in policy)` for `open_pull_request`, `"permissionDecision": "ask"` for `send_external_email`, and `"permissionDecision": "deny"` for `delete_records`. Point `--policy` at this file to use it. Edit `level_4_approver.approve` to choose which Level 4 tools run unattended; remove `level_4_approver` to send every Level 4 call to a person.

### Check the passport too

`check_tool_call` combines the passport check, the revocation check, and the Action Level, at the server's own clock. It is a Python function and a hook, not an MCP tool. The bundled example passports are dated, so at today's clock they are expired, and the check denies. That is the expected result:

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp@v0.5.1"
python -c "
from gaig_mcp.core import check_tool_call
r = check_tool_call('send_external_email', tool_level=4, example='signed-unrevoked')['result']
print(r['call_disposition']); print(r['reasons'][0])"
```

Expect `deny`, then `Passport did not verify at the server clock time (status EXPIRED).`

An `allow` needs a current passport, its trusted key, a current signed revocation list, and the evidence bundle. Step 7 issues all of them from a policy file, with no manual step, and runs this hook against them.

## 7. Agent Trust Passports and fleet controls

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance@v0.1.0-alpha.5"
validate-passport --example signed-unrevoked >/dev/null; echo "exit $?"
validate-passport --example signed-revoked >/dev/null; echo "exit $?"
```

Each run also prints, on stderr, that verification is not authorization. Expect `exit 0` (VALID), then `exit 1` (REVOKED).

The fleet controls reference tool runs from a checkout at the tag:

```bash
git -c advice.detachedHead=false clone --quiet --depth 1 --branch v0.1.0-alpha.5 https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance agentic
python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json >/dev/null; echo "exit $?"
python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/ancestor-suspended.json >/dev/null; echo "exit $?"
```

Expect `exit 0` (a sub-agent within its parent's ceiling: `PERMITTED`), then `exit 3` (an ancestor's passport is suspended: `NOT_PERMITTED`). Other cases are in `agentic/examples/fleet-controls/`.

### Issue passports from a policy file

`issue-passports` turns a fleet policy into signed passports, a trusted key, a signed revocation list, and an evidence bundle for each agent. It runs unattended, so CI or the operator's own provisioning can issue, revoke, and reissue with no manual step. The policy, not the agent, sets each agent's ceiling, and an agent cannot raise its own.

```bash
issue-passports issue agentic/examples/fleet-issuance/fleet-policy.json --out fleet/ >/dev/null
python -c "import json; [print(a['agent_id'], a['verification_primary_status']) for a in json.load(open('fleet/fleet.json'))['agents']]"
A=fleet/agents/agent.example.researcher
for t in mcp__gh__open_pull_request mcp__crm__send_external_email mcp__db__delete_records; do
  printf '%s -> ' "$t"
  printf '{"tool_name": "%s", "hook_event_name": "PreToolUse"}' "$t" | python "$HOOKS/passport_tool_call_hook.py" \
    --policy "$HOOKS/action-levels.approver.json" --passport "$A/passport.json" --trusted-key fleet/trusted-key.json \
    --revocation-list fleet/revocation-list.json --bundle-manifest "$A/bundle-manifest.json" --bundle-root "$A/bundle"
  echo
done
```

Expect three agents, each `VALID`. Then, for the researcher's passport: an empty decision (allow) for `open_pull_request`, `"permissionDecision": "ask"` for `send_external_email`, and `"permissionDecision": "deny"` for `delete_records`. `fleet/signing-key.json` is the issuer's private key: keep it out of version control and out of the agents' reach. `issue-passports --help` lists `revoke` and the other subcommands.

### Run the reference lead agent / orchestrator

The [lead agent](https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/tree/v0.1.0-alpha.5/examples/lead-agent) plans a task, hands parts to sub-agents, and checks every tool call against the passports and Action Levels above. Its demo uses an offline model, needs no API key, and runs its own shutdown tests:

```bash
lead-agent demo > lead-agent-demo.json; echo "exit $?"
python -c "import json; d=json.load(open('lead-agent-demo.json')); print('passed', d['passed'], len(d['checks']), 'checks')"
```

Expect `exit 0`, then `passed True` and the number of checks. A failed check exits 1. A browser version is at [ai-governance.solutions/lead-agent/](https://ai-governance.solutions/lead-agent/); it runs the same offline model on the page.

## 8. Verified Vulnerability Governance

```bash
python -m pip install --quiet "git+https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance@v0.4.0"
mkdir vvg && cd vvg
vvd init >/dev/null
vvd asset create --name demo-repo --owner-team appsec >/dev/null
ASSET_ID=$(vvd asset list | python -c "import json,sys; print(json.loads(sys.stdin.readline())['asset_id'])")
curl -fsSL -o sample.sarif https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/v0.4.0/examples/sarif/sample.sarif
vvd finding import --sarif sample.sarif --asset-id "$ASSET_ID"
vvd finding demo >/dev/null
vvd close-check --finding-id finding-demo-001; echo "exit $?"
vvd add-demo-closure-proof --finding-id finding-demo-001 >/dev/null
vvd close-check --finding-id finding-demo-001; echo "exit $?"
vvd audit verify
cd ..
```

Expect the new finding ID and `Imported 1 finding(s).`, then `Blocked: no approved closure proof exists.` with `exit 1`, then `Closure allowed using manual_review proof.` with `exit 0`, then `Audit chain intact: 7 event(s)` and the chain head.

### Close a finding from a rescan

When a fresh scan no longer reports a finding, that rescan is the proof, and closure needs no person. The finding stays open if the rescan still reports it.

```bash
mkdir vvg-rescan && cd vvg-rescan
for f in before.sarif after-fixed.sarif rescan_closure.py; do
  curl -fsSLO https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/v0.4.0/examples/automated-closure/$f
done
vvd init >/dev/null
vvd asset create --name demo-repo --owner-team appsec >/dev/null
ASSETS=$(vvd asset list)
ASSET_ID=$(python -c "import json,sys; print(json.loads(sys.argv[1].splitlines()[0])['asset_id'])" "$ASSETS")
IMPORTED=$(vvd finding import --sarif before.sarif --asset-id "$ASSET_ID")
FINDING_ID=${IMPORTED%%$'\n'*}
vvd evidence add --finding-id "$FINDING_ID" --type source_to_sink_trace --summary "Request parameter reaches the HTML response" >/dev/null
python rescan_closure.py --finding-id "$FINDING_ID" --rescan after-fixed.sarif
vvd audit verify
cd ..
```

Expect a JSON result with `"recorded": true` and `"close_check_exit": 0`, then `Audit chain intact`.

The demo proof in the first block is synthetic test data. For a real finding, a rescan proof (above) closes it unattended. A `manual_review` or `approved_exception` proof is an operator safety setting: it is recorded by a reviewer in a separate role with `vvd proof add --reviewer ... --decision approved`, and the agent that fixed the finding does not record it for itself.

## 9. Browser tools

[Containment Ledger](https://global-ai-governance.github.io/containment-ledger/) and [Peace OS: Crisis Room](https://global-ai-governance.github.io/peace-os/) run in a browser with no install. They are made for review and decision practice. Both are static sites, so an agent can open them in a headless browser; neither records a decision for anyone.

## Done check

Run this from the `gaig-setup` folder. Every line should end in `ok`:

```bash
check() { if eval "$2" >/dev/null 2>&1; then echo "$1 ok"; else echo "$1 FAILED"; fi; }
check "toolkit 2.8.2      " "gaig --version | grep -qx '2.8.2'"
check "decision pack      " "gaig verify out"
check "mcp server 0.5.1   " "python mcp_check.py | grep -q 'server gaig-mcp 0.5.1'"
check "action level guard " "printf '{\"tool_name\": \"x__delete_records\"}' | python .claude/hooks/tool_call_hook.py --policy .claude/hooks/action-levels.json | grep -q deny"
check "passport validator " "validate-passport --example signed-unrevoked"
check "fleet controls     " "python agentic/tools/fleet_controls.py agentic/examples/fleet-controls/sub-agent-spawn-permitted.json"
check "vulnerability audit" "cd vvg && vvd audit verify"
check "fleet passports    " "python -c \"import json,sys; sys.exit(any(a['verification_primary_status']!='VALID' for a in json.load(open('fleet/fleet.json'))['agents']))\""
check "level 4 approver   " "printf '{\"tool_name\": \"x__open_pull_request\"}' | python .claude/hooks/tool_call_hook.py --policy .claude/hooks/action-levels.approver.json | grep -q allow"
check "lead agent demo    " "lead-agent demo"
check "rescan closure     " "cd vvg-rescan && vvd audit verify"
```

Then report what ran and its outputs. Nothing above waits on a person. Level 4 tools the operator has not listed for the automated approver still ask a person, Level 5 is always denied, and the external gates in the first table are not run or claimed.

## If something differs

| You see | Why, and what to do |
|---|---|
| `input is not valid JSON` from `gaig profile` | Profiles read a JSON case file, not the CSV. Use the cases in step 3. |
| `independent-assurance-v0.1 ... FAIL`, exit 1 | The case is dated. Pass `--evaluation-time`. |
| `gaig verify` reports a missing `normalized-inventory.json` | `verify` reads `gaig check` output, not profile output. |
| `check_tool_call` returns `deny`, status `EXPIRED` | Expected for the bundled examples. Issue current passports from a policy file (step 7). |
| Every tool asks for approval | No level is set for it, so it counts as Level 4. Add it to `action-levels.json`, or list it under `level_4_approver.approve` if it is Level 4 and the operator wants it unattended. |
| `uvx: command not found` in a client | Use the absolute path from `command -v uvx` in the client config. |
| Schema URLs name `v2.7.2` | Intended. Those schemas did not change in v2.8.2. |

## More

- [llms.txt](https://ai-governance.solutions/llms.txt) and [machine-interface.json](https://ai-governance.solutions/machine-interface.json)
- [Start where you are](https://ai-governance.solutions/start.html) and its Markdown copy, [JOURNEYS.md](https://ai-governance.solutions/JOURNEYS.md)
- [Connect page](https://ai-governance.solutions/connect.html) and its [works-with matrix](https://ai-governance.solutions/connect.html#works-with)
- [Interoperability](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/blob/main/docs/INTEROP.md): which agent stacks are tested, and how
- [Lead agent console](https://ai-governance.solutions/lead-agent/) and the one-command [bootstrap.sh](https://ai-governance.solutions/bootstrap.sh)
- [Toolkit README](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit#quick-start)
- [AI Governance MCP](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp/tree/v0.5.1)
- [Agentic AI Governance](https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/tree/v0.1.0-alpha.5)
- [Verified Vulnerability Governance](https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance/tree/v0.4.0)
