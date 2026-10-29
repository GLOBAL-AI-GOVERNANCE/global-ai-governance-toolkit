# Interoperability

How Global AI Governance works with the public agent stacks and protocols we tested against. Statuses are TESTED (we ran the path), AVAILABLE (config or adapter ships), or DOCUMENTED (research only). Never VERIFIED by an independent party. No endorsement or affiliation is implied.

Live matrix: [ai-governance.solutions/interoperability.html](https://ai-governance.solutions/interoperability.html).

## How to read a row

- **Works with**: what you connect today.
- **How tested**: offline against the published open-source SDK or config, usually with a mock model. Client-inside runs are called out when they exist.
- **Status**: TESTED / AVAILABLE / DOCUMENTED.

## Matrix

| Stack | Works with | How tested | Status |
| --- | --- | --- | --- |
| Model Context Protocol | `gaig-mcp` server; Claude Code / Claude Desktop / Cursor / VS Code / Codex / Gemini CLI / LangGraph recipes | stdio ClientSession; tools list; authority_effect NONE | TESTED |
| MCP registry | `server.json` on ai-governance-mcp | schema fields present; launch args pin v0.5.0 | AVAILABLE |
| OpenAI Agents SDK | Guardrails adapter + hooks pattern in MCP examples | Offline mock; deny Level 5, approve Level 4 via automated operator | AVAILABLE |
| OpenAI Codex CLI | `~/.codex/config.toml` recipe | One recorded local stdio run (Codex CLI 0.151.0) | TESTED |
| OpenAI AGENTS.md | Toolkit / MCP / Agentic / VVG AGENTS.md | Machine front door + suite path | AVAILABLE |
| Anthropic MCP | Spec-shaped server; Claude Code PreToolUse hooks | Hook dry-run offline; not inside Claude Code | TESTED (launch) / AVAILABLE (hooks) |
| Anthropic Claude Agent SDK | Passport + Action Level hook pattern | Offline against published hook contract | AVAILABLE |
| Anthropic SKILL.md | Agent skill files in MCP and Agentic | File present; not run inside Claude | AVAILABLE |
| Google A2A | A2A passport extension + agent card notes | Schema + docs; offline | AVAILABLE |
| Google ADK / Gemini CLI | Gemini CLI MCP recipe; ADK tool-wrapper notes | Launch command; not inside Gemini | AVAILABLE |
| Microsoft Agent Framework / AutoGen / Semantic Kernel | MCP stdio client pattern | Documented; VS Code mcp.json launch tested | AVAILABLE |
| VS Code MCP | `.vscode/mcp.json` | Launch command tested; not inside VS Code | AVAILABLE |
| LangGraph | MCP tool node example | Offline graph with mock model | AVAILABLE |
| CrewAI / LlamaIndex / smolagents | Tool-call guard wrapper | Offline mock | AVAILABLE |
| AWS Strands / AgentCore | MCP client notes | Documented only | DOCUMENTED |
| OpenTelemetry GenAI | Span attributes for check calls | Example exporter; offline | AVAILABLE |
| AAIF / AGNTCY | Alignment notes | Research only | DOCUMENTED |
| xAI | OpenAI-compatible local Lead Agent serve; Grok CLI MCP recipe | Launch + mock; not inside Grok | AVAILABLE |
| SpaceX | No public agent SDK found | Honest gap | DOCUMENTED (gap) |

## Lead Agent

The browser Lead Agent at [/lead-agent/](https://ai-governance.solutions/lead-agent/) runs a deterministic mock model with no account or key. Optional local serve (`lead-agent serve` from Agentic AI Governance) talks to OpenAI-, Anthropic-, or xAI-compatible endpoints when keys sit in the local environment. Keys never enter the browser.

## Limitations

- Product use does not depend on external reviews. Evidence gates that wait on outside parties stay unchanged and are not required for the paths above.
- Client-inside runs (Claude Code, Cursor, VS Code, Gemini CLI, Grok CLI) are mostly launch-tested, not session-tested.
- Adapters wrap Action Levels and passports; they do not authorize any action. Every MCP result carries `authority_effect: NONE`.
