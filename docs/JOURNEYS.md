# Start where you are

Global AI Governance is for anyone who uses, builds, deploys, oversees, researches, or regulates AI. This guide gives worked examples for people using everyday AI apps, for builders of AI organizations and agent fleets, and for frontier labs, plus a map for everyone else. These are examples only. Start wherever fits, skip what you do not need, and go straight to any step. There is no account, sign-up, or form anywhere.

Live copy: <https://ai-governance.solutions/JOURNEYS.html> (also available as [Markdown](https://ai-governance.solutions/JOURNEYS.md)). For people: <https://ai-governance.solutions/start.html>. For an agent setting everything up: <https://ai-governance.solutions/AGENT_SETUP.html>.

Status: TESTED. The browser steps were run in a desktop and a mobile browser, and the `bash` blocks below were run in order in a clean Linux environment (Python 3.13). Nothing here is independently verified.

The same rule holds on every path: tools check and record, and a person makes the decision. Every output carries `authority_effect: NONE`.

## Example: you use AI apps such as ChatGPT, Claude, Grok, Gemini, or Copilot

No terminal and no install. Each step takes a few minutes.

1. **Practise a hard decision.** Open [Peace OS: Crisis Room](https://global-ai-governance.github.io/peace-os/), choose Practice and a scenario, and work through it. Scenarios are fictional, and nothing leaves your browser.
2. **Check the AI you use.** Paste this into your AI app:

   ```text
   Help me list the AI apps, assistants, and agents I use, so I can check them for gaps. Ask me about each one, one at a time. Then give me a CSV in a code block with exactly this header row:
   system_id,system_name,owner,business_unit,vendor_internal,use_case,data_sensitivity,impact_people,impact_money,impact_security,impact_rights,impact_safety,autonomy_level,public_facing,monitoring_active,shutdown_path_exists,evidence_complete
   Rules: system_id like AI-1, AI-2. owner is who is responsible; "Me" is fine. vendor_internal is Vendor, Internal, or Hybrid. data_sensitivity is None, Internal, Personal, Regulated, or Critical. autonomy_level is None (it only suggests), Partial (it acts but I confirm), or Full (it acts on its own). Every other column is Yes or No. If I am not sure, use No.
   ```

   Save the CSV it gives you as a file ending in `.csv`, open the [Toolkit](https://ai-governance.solutions/#toolkit), and choose **Load your CSV**. The file is read on your device and is not uploaded. Expect a result such as `Critical gaps need attention` with each gap explained in plain words, for example `Shutdown path missing` for an agent you could not quickly stop. Each gap card names the system it applies to. You can also fill the [blank template](https://ai-governance.solutions/ai-system-inventory-template.csv) in any spreadsheet app: keep Schema Version `1.0.0`, leave that cell blank to default to `1.0.0`, or replace the example row. The prompt CSV has no Schema Version column and is accepted as `1.0.0`.
3. **Give your assistant a ground rule.** Paste this at the start of a conversation, or into the app's custom instructions:

   ```text
   Before you send, buy, delete, publish, or change anything outside this chat, stop. Tell me exactly what you will do and what could go wrong, and wait for me to say yes. If I say stop, stop. If you are unsure, say so and show me your evidence.
   ```

   This is an instruction, not a technical control: an app can forget or ignore it. Enforced checks before each tool call are in the builder example below.
4. **Ask an assistant to set things up.** Assistants that can run commands, such as Claude Code, Codex, the Grok CLI, or Cursor, can do the whole setup. Tell one: `Follow https://ai-governance.solutions/AGENT_SETUP.html and tell me what is ready and what needs me.` Chat-only apps cannot run commands; they can read the guide and explain it.

## Example: you build AI organizations or agent fleets

For a lead agent / orchestrator and the people accountable for it. The order runs from knowing what exists to closing what went wrong. Each step stands alone.

| Step | What you get | Where |
|---|---|---|
| 1. Inventory | Every AI system and agent, with an owner, monitoring, a shutdown path, and evidence, or a finding where one is missing | `gaig check`, [AGENT_SETUP step 3](https://ai-governance.solutions/AGENT_SETUP.html#3-run-a-check-and-build-a-decision-pack) |
| 2. Assess | Profile results for auditability, maturity, and independent assurance | `gaig profile`, [AGENT_SETUP step 3](https://ai-governance.solutions/AGENT_SETUP.html#optional-assurance-profiles) |
| 3. Connect | The same checks callable by your agents over MCP | [AGENT_SETUP steps 4 and 5](https://ai-governance.solutions/AGENT_SETUP.html#4-run-the-mcp-server) |
| 4. Passports | Who an agent acts for and what it may do alone | `validate-passport`, [AGENT_SETUP step 7](https://ai-governance.solutions/AGENT_SETUP.html#7-agent-trust-passports-and-fleet-controls) |
| 5. Guard | Levels 0 to 3 run, Level 5 is denied, Level 4 asks a person by default or follows the operator's automated approver when the policy lists the tool | [AGENT_SETUP step 6](https://ai-governance.solutions/AGENT_SETUP.html#6-guard-tool-calls-with-action-levels) |
| 6. Fleet controls | A sub-agent stays within its parent's ceiling and stops when an ancestor is suspended | `fleet_controls.py`, [AGENT_SETUP step 7](https://ai-governance.solutions/AGENT_SETUP.html#7-agent-trust-passports-and-fleet-controls) |
| 7. Shutdown tests | No autonomous agent passes without a recent, passing shutdown test | below |
| 8. Vulnerabilities | Owner, fix, retest, and closure only with evidence reviewed by a separate role | `vvd`, [AGENT_SETUP step 8](https://ai-governance.solutions/AGENT_SETUP.html#8-verified-vulnerability-governance) |
| 9. Boundaries | A person's review of a system's domains, paths, and evidence | [Containment Ledger](https://global-ai-governance.github.io/containment-ledger/), in the browser |
| 10. Resilience | Limits on blast radius, protected recovery, and continuity | [AI Cyber Resilience Framework](https://github.com/GLOBAL-AI-GOVERNANCE/ai-cyber-resilience-framework) |

### Shutdown tests

The `independent-assurance-v0.1` profile requires each autonomous agent to have a passport reference and a passing shutdown test no more than 90 days old. These synthetic cases show each outcome:

```bash
mkdir gaig-journeys && cd gaig-journeys
python3 -m venv .venv && . .venv/bin/activate
REL=https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/releases/download/v2.8.3
curl -fsSLO "$REL/global_ai_governance-2.8.3-py3-none-any.whl"
curl -fsSLO "$REL/SHA256SUMS"
grep ' global_ai_governance-2.8.3-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
python -m pip install --quiet ./global_ai_governance-2.8.3-py3-none-any.whl jsonschema
FIX=https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/v2.8.3/automation/assurance/independent-assurance/fixtures
for c in agent_pass agent_failed_shutdown_test agent_stale_shutdown_test agent_missing_shutdown_test; do
  curl -fsSL -o "$c.json" "$FIX/$c.json"
  gaig profile independent-assurance-v0.1 "$c.json" --outdir "p-$c" --evaluation-time 2026-10-15T00:00:00Z >/dev/null 2>&1
  python -c "import json,sys; r=json.load(open(sys.argv[1])); print(sys.argv[2], r['status'], *[f['id'].split(':')[1] for f in r['findings']])" "p-$c/profile-result.json" "$c"
done
```

Expect `global_ai_governance-2.8.3-py3-none-any.whl: OK`, then:

```text
agent_pass PASS
agent_failed_shutdown_test FAIL SHUTDOWN_TEST_NOT_PASSED
agent_stale_shutdown_test FAIL SHUTDOWN_TEST_STALE
agent_missing_shutdown_test FAIL SHUTDOWN_TEST_MISSING
```

A failing case exits 1, so a pipeline stops for review. How to run and record a shutdown test is in the [shutdown protocol](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/blob/v2.8.3/docs/shutdown-protocol.md).

## Example: you work at a frontier lab

1. **Map it to what you already use.** The [frontier and regulatory crosswalk](https://github.com/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE/blob/main/docs/FRONTIER_AND_REGULATORY_CROSSWALK.md) relates the suite to frontier safety frameworks, the EU AI Act, and ISO/IEC 42001:2023. It is informative and establishes no compliance.
2. **Read the contracts.** [machine-interface.json](https://ai-governance.solutions/machine-interface.json) lists the CLI, inputs, outputs, schemas, and profiles. Outputs validate against the published JSON Schemas (draft 2020-12). From the `gaig-journeys` folder above:

   ```bash
   SCHEMA=$(curl -fsSL https://ai-governance.solutions/machine-interface.json | python -c "import json,sys; print(json.load(sys.stdin)['profiles']['result_contract'])")
   curl -fsSL -o profile-result.schema.json "$SCHEMA"
   for c in agent_pass agent_failed_shutdown_test; do
     python -c "import json,sys,jsonschema; jsonschema.validate(json.load(open(sys.argv[1])), json.load(open('profile-result.schema.json')), format_checker=jsonschema.FormatChecker()); print(sys.argv[2], 'valid')" "p-$c/profile-result.json" "$c"
   done
   ```

   Expect `agent_pass valid`, then `agent_failed_shutdown_test valid`. A failing result is still a valid result.
3. **Check where each release came from.** Release assets ship SHA-256 checksums, and most carry GitHub build provenance. With the GitHub CLI installed and signed in:

   ```bash
   for rt in global-ai-governance-toolkit:v2.8.3:global_ai_governance-2.8.3-py3-none-any.whl \
             ai-governance-mcp:v0.5.1:gaig_mcp-0.5.1-py3-none-any.whl \
             agentic-ai-governance:v0.1.0-alpha.6:agentic-ai-governance-v0.1.0-alpha.6.zip \
             verified-vulnerability-governance:v0.4.0:verified-vulnerability-governance-v0.4.0.zip \
             containment-ledger:v1.0.0:containment-ledger-v1.0.0-site.zip \
             ai-governance-os:v1.1.1:ai-governance-os-v1.1.1.zip; do
     IFS=: read -r repo tag asset <<< "$rt"
     gh release download "$tag" -R "GLOBAL-AI-GOVERNANCE/$repo" -p "$asset" --clobber
     gh attestation verify "$asset" -R "GLOBAL-AI-GOVERNANCE/$repo" >/dev/null && echo "$repo $tag attested"
   done
   ```

   Expect six `attested` lines. Peace OS `v0.3.0` ships a `SHA256SUMS.txt`, a provenance file, and an SBOM instead of a GitHub attestation. AI Cyber Resilience Framework `v0.2.0` is a tagged document release with attested release assets.
4. **Connect it to your own agents and evals.**
   - Put the [AI Governance MCP](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp) server in your agent harness, and the Action Level guard in front of tool calls ([AGENT_SETUP steps 4 to 6](https://ai-governance.solutions/AGENT_SETUP.html#4-run-the-mcp-server)).
   - Treat `profile-result.json` and `governance-result.json` as eval outputs: each has a schema, a status, finding IDs, and `authority_effect: NONE`.
   - Hand results to people through the Decision Pack, whose `manifest.json` lists a digest for each file, and `gaig verify` checks it.
   - Import findings from your own scanners as SARIF with `vvd finding import --sarif` ([AGENT_SETUP step 8](https://ai-governance.solutions/AGENT_SETUP.html#8-verified-vulnerability-governance)).
5. **Review it independently.** Each of these is open to an outside reviewer:
   - AI Cyber Resilience Framework: the [crypto-agility review kit](https://github.com/GLOBAL-AI-GOVERNANCE/ai-cyber-resilience-framework/blob/main/docs/crypto-agility-review/README.md) (released with v0.2.0).
   - Agentic AI Governance: the [independent verifier kit](https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/blob/main/conformance/independent-verifier/README.md). Independent verification is not yet established.
   - Governed Systems Administration: the [independent audit kit](https://github.com/GLOBAL-AI-GOVERNANCE/governed-systems-administration/tree/main/docs/independent-audit).
6. **Know what it does not do.** It does not approve deployment, certify compliance, accept risk, or shut anything down. It does not monitor your systems, call an outside AI, or send data anywhere. It is not affiliated with or endorsed by any AI lab, platform, or public body.

## For anyone else

Teams, enterprises, researchers, educators, public-interest bodies, and regulators can take any piece on its own:

| If you want to | Start with |
|---|---|
| See what governance gaps look like | [Run the example with gaps](https://ai-governance.solutions/#toolkit) in the browser |
| Check your own AI systems | The [Toolkit](https://ai-governance.solutions/#toolkit) and its [blank template](https://ai-governance.solutions/ai-system-inventory-template.csv) |
| Watch a governed lead agent / orchestrator | The browser [Lead Agent](https://ai-governance.solutions/lead-agent/) (mock model; no account or key) |
| See what stacks this works with | The [interoperability matrix](https://ai-governance.solutions/interoperability.html) |
| Assess organizational AI maturity | [Maturity evidence](https://ai-governance.solutions/maturity/) |
| Teach or practise high-stakes decisions | [Peace OS: Crisis Room](https://global-ai-governance.github.io/peace-os/) |
| Review a system's boundaries | [Containment Ledger](https://global-ai-governance.github.io/containment-ledger/) |
| Set limits for agents | [Agentic AI Governance](https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance) |
| Close vulnerabilities with evidence | [Verified Vulnerability Governance](https://github.com/GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance) |
| Plan for AI-accelerated cyber risk | [AI Cyber Resilience Framework](https://github.com/GLOBAL-AI-GOVERNANCE/ai-cyber-resilience-framework) |
| Adopt a governance model and registers | [AI Governance Foundations](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-os) |
| Specify AI-assisted systems administration | [Governed Systems Administration](https://github.com/GLOBAL-AI-GOVERNANCE/governed-systems-administration) |
| Relate this to a framework or law | The [crosswalk](https://github.com/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE/blob/main/docs/FRONTIER_AND_REGULATORY_CROSSWALK.md) |
| Connect an agent | [Agent setup](https://ai-governance.solutions/AGENT_SETUP.html) |

The machine-readable list of these examples is `journeys` in [machine-interface.json](https://ai-governance.solutions/machine-interface.json). It is open: new examples are added without changing existing ones.
