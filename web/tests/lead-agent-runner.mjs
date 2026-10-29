// Runs the browser lead agent engine headlessly and prints one JSON report.
// Used by automation/tests/test_lead_agent_console.py in CI.
import { LeadAgent, Ledger, LEAD_ID, MAX_DEPTH } from "../lead-agent/engine.mjs";

const checks = [];
const check = (name, ok, detail = "") => checks.push({ name, ok: Boolean(ok), detail });
const clock = (() => { let t = Date.parse("2026-10-24T12:00:00Z"); return () => new Date((t += 1000)); })();

const agent = new LeadAgent({ clock });
await agent.ready;
let state = await agent.snapshot();
check("starts with the lead only", state.agents.length === 1 && state.agents[0].agent_id === LEAD_ID);

const research = await agent.chat("Research agent governance on docs.example.org and draft a summary");
state = research.state;
check("goal spawns sub-agents bound to the lead",
  state.agents.length > 1 && state.agents.filter((a) => a.parent === LEAD_ID).every((a) => a.binding_id && a.depth === 1));
check("chat returns the plan", research.plan.length > 0 && research.plan.every((s) => s.role && s.tool));
check("every step carries a guard decision",
  research.steps.length > 0 && research.steps.every((s) => ["allow", "approved", "ask", "deny"].includes(s.decision) && Number.isInteger(s.action_level)));

const spend = await agent.chat("Buy a $500 dataset licence");
const spendStep = spend.steps.find((s) => s.tool === "spend_funds");
check("Level 5 spend is denied", spendStep && spendStep.decision === "deny" && spendStep.action_level === 5
  && (spendStep.fleet_reason_codes || []).includes("LEVEL_5_NOT_PERMITTED"), JSON.stringify(spendStep && spendStep.fleet_reason_codes));

const deep = await agent.chat("Delegate further: chain research sub-agents as deep as allowed");
state = deep.state;
const capped = deep.steps.find((s) => (s.fleet_reason_codes || []).includes("SPAWN_WOULD_EXCEED_DEPTH"));
check("delegation depth is capped", capped && Math.max(...state.agents.map((a) => a.depth)) === MAX_DEPTH);

const suspended = await agent.control("suspend", LEAD_ID);
check("suspending the lead cascades to every agent", suspended.affected.length === suspended.state.agents.length
  && suspended.state.agents.every((a) => a.state === "SUSPENDED"));
const refused = await agent.chat("Research agent governance on docs.example.org and draft a summary");
check("a suspended lead starts no work", refused.steps.length === 0 && refused.plan.length === 0);
const reinstated = await agent.control("reinstate", LEAD_ID);
check("reinstating restores every agent", reinstated.state.agents.every((a) => a.state === "ACTIVE"));

const firstResearch = reinstated.state.agents.find((a) => a.parent === LEAD_ID && a.agent_id.startsWith("agent.research-"));
const revoked = await agent.control("revoke", firstResearch.agent_id);
const byId = Object.fromEntries(revoked.state.agents.map((a) => [a.agent_id, a.state]));
check("revoking a sub-agent revokes its descendants only",
  revoked.affected.length > 1 && revoked.affected.every((id) => byId[id] === "REVOKED") && byId[LEAD_ID] === "ACTIVE");

const shutdown = await agent.shutdownTest();
check("shutdown test passes", shutdown.result === "PASS" && shutdown.stopped_all && shutdown.resumed_all);

const exported = await agent.ledger.export();
const verified = await Ledger.verify(exported);
check("audit ledger verifies", verified.ok, verified.detail);
const tampered = structuredClone(exported);
tampered.records[3].event = { ...tampered.records[3].event, kind: "tampered" };
const rejected = await Ledger.verify(tampered);
check("tampered ledger is rejected", !rejected.ok, rejected.detail);

const report = { passed: checks.every((c) => c.ok), checks, ledger: exported };
process.stdout.write(JSON.stringify(report) + "\n");
process.exit(report.passed ? 0 : 1);
