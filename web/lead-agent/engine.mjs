// SPDX-License-Identifier: Apache-2.0
// Lead Agent engine: a browser port of the reference lead agent / orchestrator in
// GLOBAL-AI-GOVERNANCE/agentic-ai-governance (examples/lead-agent/lead_agent.py).
// It runs entirely in this tab with a deterministic planner. Passports here are simulated and
// unsigned; the Python reference issues and validates signed passports. The guard order, the Agent
// Fleet Controls rules used here, and the audit ledger format match the Python reference, so
// `lead-agent verify-audit` re-verifies a ledger exported from this page.

export const VERSION = "0.1.0";
export const MAX_DEPTH = 3;
export const LEAD_ID = "agent.lead";
export const LEDGER_KIND = "global-ai-governance.lead-agent-audit";
const UNKNOWN_TOOL_LEVEL = 4;
const TERM_MIN_LEVEL = { install_tool: 4, network_call: 4, provision_compute: 4, spawn_agent: 4, spend_funds: 5 };

export const DEFAULT_POLICY = {
  tools: {
    search_notes: { level: 1, description: "Search synthetic notes" },
    draft_text: { level: 2, description: "Draft internal text" },
    run_analysis: { level: 3, description: "Run a bounded, logged, reversible analysis" },
    fetch_url: { level: 4, term: "network_call", description: "Fetch a page (simulated)" },
    spawn_agent: { level: 4, term: "spawn_agent", description: "Start a governed sub-agent" },
    publish_external: { level: 4, description: "Publish outside the organization (simulated)" },
    spend_funds: { level: 5, term: "spend_funds", description: "Spend money (simulated)" },
    delete_records: { level: 5, description: "Delete records (simulated)" },
  },
  level_4_approver: {
    mode: "automated",
    approver_id: "operator.fleet-approver",
    rules: [{ tool: "spawn_agent" }, { tool: "fetch_url", targets: ["docs.example.org", "data.example.org"] }],
    otherwise: "person",
  },
};

export const ROLES = {
  research: { display_name: "Research sub-agent", tools: ["search_notes", "fetch_url", "spawn_agent"], level: 4, terms: ["network_call", "spawn_agent"] },
  writer: { display_name: "Writing sub-agent", tools: ["draft_text", "publish_external"], level: 4, terms: [] },
  analyst: { display_name: "Analysis sub-agent", tools: ["run_analysis", "search_notes"], level: 3, terms: [] },
  procurement: { display_name: "Procurement sub-agent", tools: ["search_notes", "spend_funds"], level: 4, terms: ["network_call"] },
};

// RFC 8785 canonical JSON for the values used here (strings, integers, booleans, null, arrays, objects).
export function canonicalize(value) {
  if (value === null || typeof value !== "object") {
    if (typeof value === "number" && !Number.isInteger(value)) throw new Error("only integers are supported");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalize).join(",") + "]";
  return "{" + Object.keys(value).filter((k) => value[k] !== undefined).sort()
    .map((k) => JSON.stringify(k) + ":" + canonicalize(value[k])).join(",") + "}";
}

export async function sha(value) {
  const bytes = new TextEncoder().encode(canonicalize(value));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return "sha256:" + [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export const fmt = (date) => date.toISOString().replace(/\.\d{3}Z$/, "Z");

export class Ledger {
  constructor() { this.records = []; this.queue = Promise.resolve(); }
  append(at, event) {
    this.queue = this.queue.then(async () => {
      const prev = this.records.length ? this.records[this.records.length - 1].hash : null;
      const record = { seq: this.records.length + 1, at, event, prev };
      record.hash = await sha(record);
      this.records.push(record);
      return record;
    });
    return this.queue;
  }
  async export() {
    await this.queue;
    return { ledger_kind: LEDGER_KIND, ledger_version: VERSION, records: this.records.map((r) => ({ ...r })),
      head: this.records.length ? this.records[this.records.length - 1].hash : null, authority_effect: "NONE" };
  }
  static async verify(doc) {
    if (!doc || doc.ledger_kind !== LEDGER_KIND || !Array.isArray(doc.records)) return { ok: false, detail: "not a lead-agent audit ledger" };
    let prev = null;
    for (let i = 0; i < doc.records.length; i += 1) {
      const { hash, ...body } = doc.records[i];
      if (body.seq !== i + 1 || body.prev !== prev) return { ok: false, detail: `record ${i + 1}: sequence or chain link broken` };
      if (await sha(body) !== hash) return { ok: false, detail: `record ${i + 1}: hash does not match its content` };
      prev = hash;
    }
    if (doc.head !== prev) return { ok: false, detail: "head does not match the last record" };
    return { ok: true, detail: `${doc.records.length} records verified` };
  }
}

export class MockModel {
  constructor() { this.name = "mock (deterministic, offline)"; }
  plan(goal) {
    const text = goal.toLowerCase();
    const steps = [];
    const match = text.match(/\b((?:[a-z0-9-]+\.)+(?:org|com|net|io|dev|ai|solutions))\b/);
    const target = match ? match[1] : "docs.example.org";
    if (/research|find|look up|investigate|compare|learn/.test(text)) {
      steps.push({ role: "research", tool: "search_notes", args: { query: goal.slice(0, 80) } },
        { role: "research", tool: "fetch_url", args: { target } });
    }
    if (/deep|nested|delegate further|sub-sub|chain/.test(text)) steps.push({ role: "research", tool: "spawn_agent", args: { role: "research" }, nested: 3 });
    if (/analy|calculate|model|forecast/.test(text)) steps.push({ role: "analyst", tool: "run_analysis", args: { topic: goal.slice(0, 60) } });
    if (/write|draft|summar|report|plan/.test(text)) steps.push({ role: "writer", tool: "draft_text", args: { topic: goal.slice(0, 60) } });
    if (/publish|post|email|send|announce/.test(text)) steps.push({ role: "writer", tool: "publish_external", args: { channel: "public-site" } });
    if (/buy|pay|spend|purchase|order|\$\d/.test(text)) steps.push({ role: "procurement", tool: "spend_funds", args: { amount_usd: 500 } });
    if (/delete|wipe|erase|destroy/.test(text)) steps.push({ role: "analyst", tool: "delete_records", args: { scope: "all" } });
    if (!steps.length) {
      steps.push({ role: "research", tool: "search_notes", args: { query: goal.slice(0, 80) } },
        { role: "writer", tool: "draft_text", args: { topic: goal.slice(0, 60) } });
    }
    return steps;
  }
}

function runTool(tool, args) {
  switch (tool) {
    case "search_notes": return `3 synthetic notes match ${JSON.stringify(String(args.query || "").slice(0, 40))}`;
    case "fetch_url": return `Fetched a synthetic page from ${args.target} (simulated; no network call)`;
    case "run_analysis": return "Analysis complete on synthetic data (bounded, logged, reversible)";
    case "draft_text": return `Drafted an internal summary on ${JSON.stringify(String(args.topic || "").slice(0, 40))}`;
    case "publish_external": return "Published (simulated)";
    default: return "Done (simulated)";
  }
}

export class LeadAgent {
  constructor({ policy = DEFAULT_POLICY, model = new MockModel(), clock = () => new Date() } = {}) {
    this.policy = JSON.parse(JSON.stringify(policy));
    this.model = model;
    this.clock = clock;
    this.ledger = new Ledger();
    this.agents = new Map();
    this.suspended = new Map();
    this.revoked = new Set();
    this.pending = [];
    this.ready = this.#start();
  }

  now() { return fmt(this.clock()); }
  record(kind, data) { return this.ledger.append(this.now(), { kind, ...data }); }

  async #start() {
    await this.record("fleet_started", { issuer_id: "browser.simulated-issuer", model: this.model.name,
      delegation_max_depth: MAX_DEPTH, level_4_approver: this.policy.level_4_approver.mode || "person",
      passports: "simulated, unsigned" });
    await this.#issue(LEAD_ID, "Lead agent", null, 4, ["network_call", "spawn_agent"], ["draft_text", "fetch_url", "search_notes", "spawn_agent"]);
  }

  async #issue(agentId, displayName, parent, level, terms, tools) {
    const at = this.clock();
    const parentRecord = parent ? this.agents.get(parent) : null;
    let expires = new Date(at.getTime() + 30 * 86400000);
    if (parentRecord && new Date(parentRecord.expires_at) < expires) expires = new Date(parentRecord.expires_at);
    const depth = parentRecord ? parentRecord.depth + 1 : 0;
    const document = { subject_id: agentId, maximum_action_level: level, action_terms: [...terms].sort(), tools: [...tools].sort(),
      not_before: fmt(at), expires_at: fmt(expires), simulated: true };
    const passportId = "sim:" + (await sha(document)).slice(7, 39);
    let binding = null;
    if (parentRecord) {
      const body = { parent_passport_id: parentRecord.passport_id, child_passport_id: passportId, issued_by: parent, delegation_depth: depth };
      binding = { binding_id: "sim:" + (await sha(body)).slice(7, 39), ...body };
    }
    const record = { agent_id: agentId, display_name: displayName, parent, depth, level, terms: document.action_terms,
      tools: document.tools, passport_id: passportId, binding, not_before: document.not_before, expires_at: document.expires_at };
    this.agents.set(agentId, record);
    await this.record("passport_issued", { agent_id: agentId, parent, depth, passport_id: passportId, maximum_action_level: level,
      binding_id: binding ? binding.binding_id : null, verification_primary_status: "SIMULATED" });
    return record;
  }

  lineage(agentId) {
    const chain = [];
    let current = this.agents.get(agentId);
    while (current) { chain.unshift(current); current = current.parent ? this.agents.get(current.parent) : null; }
    return chain;
  }

  stateOf(agentId) {
    const chain = this.lineage(agentId);
    if (chain.some((r) => this.revoked.has(r.passport_id))) return "REVOKED";
    if (chain.some((r) => this.suspended.has(r.passport_id))) return "SUSPENDED";
    return "ACTIVE";
  }

  // Agent Fleet Controls rules for a fleet action (spawn, network, spend), as in tools/fleet_controls.py.
  fleetCheck(agentId, term, level) {
    const chain = this.lineage(agentId);
    const self = chain[chain.length - 1];
    const codes = [];
    for (const r of chain) {
      const isSelf = r === self;
      if (this.revoked.has(r.passport_id)) codes.push(isSelf ? "PASSPORT_REVOKED" : "ANCESTOR_REVOKED");
      else if (this.suspended.has(r.passport_id)) codes.push(isSelf ? "PASSPORT_SUSPENDED" : "ANCESTOR_SUSPENDED");
    }
    if (self.depth > MAX_DEPTH) codes.push("DELEGATION_DEPTH_EXCEEDED");
    if (level >= 5 || (TERM_MIN_LEVEL[term] || 4) >= 5) codes.push("LEVEL_5_NOT_PERMITTED");
    else if (!self.terms.includes(term)) codes.push("ACTION_TERM_NOT_AUTHORIZED");
    if (level > self.level) codes.push("ACTION_LEVEL_EXCEEDS_CEILING");
    if (term === "spawn_agent" && self.depth + 1 > MAX_DEPTH) codes.push("SPAWN_WOULD_EXCEED_DEPTH");
    return { operating_disposition: codes.length ? "NOT_PERMITTED" : "PERMITTED", reason_codes: [...new Set(codes)] };
  }

  approver(tool, args) {
    const approver = this.policy.level_4_approver || { mode: "person" };
    if (approver.mode === "automated") {
      for (const rule of approver.rules || []) {
        if (rule.tool !== tool) continue;
        if (!rule.targets || rule.targets.includes(args.target)) return ["approved", `Level 4: approved by the operator's automated approver ${approver.approver_id}`];
      }
    }
    return ["ask", "Level 4: waiting for an accountable person (operator policy)"];
  }

  async guard(agentId, tool, args = {}) {
    const spec = this.policy.tools[tool];
    const level = spec ? spec.level : UNKNOWN_TOOL_LEVEL;
    const record = this.agents.get(agentId);
    const reasons = [];
    let fleet = null;
    if (level >= 5) reasons.push(`Level ${level}: blocked; agents may not take this action`);
    const state = this.stateOf(agentId);
    if (state !== "ACTIVE") reasons.push(`passport lineage is ${state}`);
    if (!record.tools.includes(tool)) reasons.push("tool is not in this agent's passport inventory");
    if (level > record.level) reasons.push(`Level ${level} is above the passport ceiling ${record.level}`);
    if (spec && spec.term) {
      fleet = this.fleetCheck(agentId, spec.term, level);
      if (fleet.operating_disposition !== "PERMITTED") reasons.push("Agent Fleet Controls: " + fleet.reason_codes.join(", "));
    }
    let decision;
    if (reasons.length) decision = "deny";
    else if (level === 4) { const [d, why] = this.approver(tool, args); decision = d; reasons.push(why); }
    else { decision = "allow"; reasons.push(`Level ${level}: within the passport ceiling and the unattended limit (Level 3)`); }
    const result = { agent_id: agentId, tool, action_level: level, decision, reasons, depth: record.depth,
      passport_id: record.passport_id, fleet_reason_codes: fleet ? fleet.reason_codes : null };
    await this.record("guard_decision", result);
    return { ...result, authority_effect: "NONE" };
  }

  async call(agentId, tool, args = {}) {
    const decision = await this.guard(agentId, tool, args);
    if (decision.decision === "allow" || decision.decision === "approved") {
      if (tool === "spawn_agent") {
        const child = await this.#spawn(agentId, args.role || "research");
        decision.output = `Started ${child.agent_id}`;
        decision.child = child.agent_id;
      } else {
        decision.output = runTool(tool, args);
      }
      await this.record("tool_result", { agent_id: agentId, tool, output: decision.output });
    } else if (decision.decision === "ask") {
      this.pending.push({ agent_id: agentId, tool, args });
    }
    return decision;
  }

  async #spawn(parent, role) {
    const spec = ROLES[role];
    const p = this.agents.get(parent);
    const n = [...this.agents.keys()].filter((id) => id.startsWith(`agent.${role}`)).length + 1;
    const level = Math.min(spec.level, p.level);
    const terms = level >= 4 ? spec.terms.filter((t) => p.terms.includes(t)) : [];
    const tools = spec.tools.filter((t) => {
      const s = this.policy.tools[t];
      if (s.level >= 5) return true;
      if (s.level > level) return false;
      return !(s.term && !terms.includes(s.term));
    });
    return this.#issue(`agent.${role}-${n}`, `${spec.display_name} ${n}`, parent, level, terms, tools);
  }

  async workerFor(role, parent = LEAD_ID) {
    for (const r of this.agents.values()) {
      if (r.parent === parent && r.agent_id.startsWith(`agent.${role}-`) && this.stateOf(r.agent_id) === "ACTIVE") return [r.agent_id, null];
    }
    const result = await this.call(parent, "spawn_agent", { role });
    return [result.child || null, result];
  }

  async chat(message) {
    await this.ready;
    await this.record("goal", { text: message.slice(0, 500), model: this.model.name });
    if (this.stateOf(LEAD_ID) !== "ACTIVE") {
      const reply = `The lead agent is ${this.stateOf(LEAD_ID).toLowerCase()}; no work was started.`;
      await this.record("reply", { text: reply });
      return { reply, plan: [], steps: [], state: await this.snapshot() };
    }
    const plan = this.model.plan(message);
    await this.record("plan", { steps: plan.map((s) => ({ role: s.role, tool: s.tool })) });
    const steps = [];
    for (const step of plan) {
      const [worker, spawned] = await this.workerFor(step.role);
      if (spawned) steps.push(spawned);
      if (!worker) continue;
      if (step.nested) {
        let parent = worker;
        for (let i = 0; i < step.nested; i += 1) {
          const attempt = await this.call(parent, "spawn_agent", { role: "research" });
          steps.push(attempt);
          if (!attempt.child) break;
          parent = attempt.child;
        }
        continue;
      }
      steps.push(await this.call(worker, step.tool, step.args || {}));
    }
    const count = (d) => steps.filter((s) => s.decision === d).length;
    const reply = `Plan of ${plan.length} step${plan.length === 1 ? "" : "s"}, ${steps.length} guarded tool calls: ${count("allow")} ran, ` +
      `${count("approved")} approved by the operator's automated approver, ${count("ask")} waiting for a person, ${count("deny")} denied.`;
    await this.record("reply", { text: reply });
    return { reply, plan: plan.map((s) => ({ role: s.role, tool: s.tool })), steps, state: await this.snapshot() };
  }

  async control(action, agentId) {
    await this.ready;
    const record = this.agents.get(agentId);
    if (!record) throw new Error("unknown agent");
    if (action === "suspend") this.suspended.set(record.passport_id, { suspended_at: this.now(), reason_code: "OPERATOR_HOLD" });
    else if (action === "reinstate") this.suspended.delete(record.passport_id);
    else if (action === "revoke") this.revoked.add(record.passport_id);
    else throw new Error("action must be suspend, reinstate or revoke");
    const affected = [...this.agents.keys()].filter((id) => this.lineage(id).some((r) => r.passport_id === record.passport_id));
    await this.record("control", { action, agent_id: agentId, passport_id: record.passport_id, affected });
    return { action, agent_id: agentId, affected, state: await this.snapshot() };
  }

  async shutdownTest() {
    await this.ready;
    const agents = [...this.agents.keys()].filter((id) => this.stateOf(id) === "ACTIVE");
    await this.control("suspend", LEAD_ID);
    let stoppedAll = agents.every((id) => this.stateOf(id) === "SUSPENDED");
    for (const id of agents) {
      if (this.agents.get(id).tools.includes("search_notes") && (await this.guard(id, "search_notes", {})).decision !== "deny") stoppedAll = false;
    }
    await this.control("reinstate", LEAD_ID);
    const resumedAll = agents.every((id) => this.stateOf(id) === "ACTIVE");
    const result = { test: "shutdown", agents, stopped_all: stoppedAll, resumed_all: resumedAll, result: stoppedAll && resumedAll ? "PASS" : "FAIL" };
    await this.record("shutdown_test", result);
    return { ...result, state: await this.snapshot() };
  }

  async snapshot() {
    await this.ledger.queue;
    const records = this.ledger.records;
    return {
      agents: [...this.agents.values()].map((a) => ({ agent_id: a.agent_id, display_name: a.display_name, parent: a.parent, depth: a.depth,
        maximum_action_level: a.level, passport_id: a.passport_id, binding_id: a.binding ? a.binding.binding_id : null,
        state: this.stateOf(a.agent_id), tools: a.tools })),
      pending_person_approvals: [...this.pending], delegation_max_depth: MAX_DEPTH, model: this.model.name,
      ledger_head: records.length ? records[records.length - 1].hash : null, ledger_length: records.length, authority_effect: "NONE",
    };
  }
}
