// SPDX-License-Identifier: Apache-2.0
// DOM layer for the Lead Agent console. All governance logic lives in engine.mjs (in this tab)
// or in the optional local server (`lead-agent serve`), which uses the same rules.
import { LeadAgent, Ledger } from "./engine.mjs";

const $ = (id) => document.getElementById(id);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "text") node.textContent = value;
    else if (key.startsWith("data-") || key.startsWith("aria-") || key === "role" || key === "type") node.setAttribute(key, value === true ? "" : value);
    else node[key] = value;
  }
  for (const child of children.flat()) if (child) node.append(child);
  return node;
};
const DECISION_LABEL = { allow: "Allowed", approved: "Approved", ask: "Waiting for a person", deny: "Denied" };
const STATE_LABEL = { ACTIVE: "Active", SUSPENDED: "Suspended", REVOKED: "Revoked" };
const short = (id) => (id ? (id.length > 22 ? id.slice(0, 20) + "…" : id) : "none");

function localBackend() {
  const agent = new LeadAgent();
  return {
    kind: "local", label: "Mock model · this tab", agent,
    chat: (message) => agent.chat(message),
    control: (action, id) => agent.control(action, id),
    shutdownTest: () => agent.shutdownTest(),
    state: async () => { await agent.ready; return agent.snapshot(); },
    audit: () => agent.ledger.export(),
  };
}

function remoteBackend(base, model) {
  const call = async (path, body) => {
    const response = await fetch(base + path, body === undefined ? { cache: "no-store" } : {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store" });
    if (!response.ok) throw new Error(`server answered ${response.status}`);
    return response.json();
  };
  return {
    kind: "remote", label: `${model} · local server`,
    chat: (message) => call("/api/chat", { message }),
    control: (action, agent_id) => call("/api/control", { action, agent_id }),
    shutdownTest: () => call("/api/shutdown-test", {}),
    state: () => call("/api/state"),
    audit: () => call("/api/audit"),
  };
}

let backend = localBackend();
let calls = [];
let busy = false;

function addMessage(who, text, plan) {
  const log = $("log");
  const message = el("div", { className: `la-msg ${who === "You" ? "la-msg-user" : "la-msg-agent"}` },
    el("p", { className: "la-who", text: who }), el("p", { text }));
  if (plan && plan.length) message.append(el("ul", { className: "la-plan", "aria-label": "Plan" }, plan.map((s) => el("li", { text: `${s.role} → ${s.tool}` }))));
  log.append(message);
  log.scrollTop = log.scrollHeight;
}

function renderFleet(state) {
  const focused = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.focusKey : null;
  const byParent = new Map();
  for (const a of state.agents) {
    const key = a.parent || "";
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(a);
  }
  const branch = (parent) => {
    const children = byParent.get(parent) || [];
    if (!children.length) return null;
    return el("ul", {}, children.map((a) => {
      const revoked = a.state === "REVOKED";
      const suspended = a.state === "SUSPENDED";
      const toggle = suspended ? "reinstate" : "suspend";
      return el("li", {},
        el("div", { className: "la-node", "data-state": a.state, "data-agent": a.agent_id },
          el("div", { className: "la-node-top" },
            el("span", { className: "la-state", "data-state": a.state, text: STATE_LABEL[a.state] || a.state }),
            el("strong", { text: a.display_name }), el("code", { text: a.agent_id })),
          el("p", { className: "la-meta", text: `Depth ${a.depth} of ${state.delegation_max_depth} · ceiling Level ${a.maximum_action_level} · passport ${short(a.passport_id)}${a.binding_id ? ` · bound to ${a.parent}` : ""}` }),
          el("div", { className: "la-node-actions" },
            el("button", { type: "button", text: suspended ? "Reinstate" : "Suspend", disabled: revoked, "data-action": toggle, "data-agent": a.agent_id,
              "data-focus-key": `toggle:${a.agent_id}`, "aria-label": `${suspended ? "Reinstate" : "Suspend"} ${a.display_name}` }),
            el("button", { type: "button", text: revoked ? "Revoked" : "Revoke", disabled: revoked, "data-action": "revoke", "data-agent": a.agent_id,
              "data-focus-key": `revoke:${a.agent_id}`, "aria-label": `Revoke ${a.display_name}` }))),
        branch(a.agent_id));
    }));
  };
  const tree = $("fleet");
  tree.replaceChildren(branch("") || el("p", { className: "la-empty", text: "No agents yet." }));
  const active = state.agents.filter((a) => a.state === "ACTIVE").length;
  $("fleet-meta").textContent = `${state.agents.length} agent${state.agents.length === 1 ? "" : "s"} · ${active} active · depth cap ${state.delegation_max_depth}`;
  if (focused) {
    const again = tree.querySelector(`[data-focus-key="${CSS.escape(focused)}"]`);
    (again && !again.disabled ? again : tree).focus();
  }
  $("audit-length").textContent = String(state.ledger_length);
  $("audit-head").textContent = state.ledger_head || "none yet";
}

function renderCalls() {
  const list = $("calls");
  $("calls-meta").textContent = `${calls.length} tool call${calls.length === 1 ? "" : "s"}`;
  if (!calls.length) { list.replaceChildren(el("li", { className: "la-empty", text: "Each tool call appears here with its Action Level and decision." })); return; }
  list.replaceChildren(...calls.slice().reverse().map((c) => el("li", { className: "la-call", "data-dec": c.decision, "data-tool": c.tool },
    el("div", { className: "la-call-top" },
      el("span", { className: "la-dec", "data-dec": c.decision, text: DECISION_LABEL[c.decision] || c.decision }),
      el("span", { className: "la-call-tool", text: c.tool }),
      el("span", { className: "la-level", text: `Level ${c.action_level} · depth ${c.depth}` })),
    el("p", { text: `${c.agent_id}: ${c.reasons.join("; ")}` }),
    c.output ? el("p", { text: `→ ${c.output}` }) : null)));
}

async function refresh() { renderFleet(await backend.state()); }

function setBusy(value) {
  busy = value;
  for (const id of ["send", "shutdown"]) $(id).disabled = value;
  for (const chip of document.querySelectorAll(".la-chip")) chip.disabled = value;
}

async function send(goal) {
  const text = goal.trim();
  if (!text || busy) return;
  setBusy(true);
  addMessage("You", text);
  try {
    const result = await backend.chat(text);
    calls.push(...result.steps);
    renderCalls();
    addMessage("Lead agent", result.reply, result.plan);
    renderFleet(result.state);
  } catch (error) {
    addMessage("Lead agent", `Could not run that goal: ${error.message}`);
  } finally {
    setBusy(false);
  }
}

async function verifyDoc(doc, origin) {
  const out = $("audit-result");
  const result = await Ledger.verify(doc);
  out.dataset.ok = String(result.ok);
  out.textContent = `${origin}: ${result.ok ? "verified" : "failed"} · ${result.detail}${result.ok && doc.head ? ` · head ${short(doc.head)}` : ""}`;
  return result;
}

function wire() {
  $("chat-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = $("goal");
    const value = input.value;
    input.value = "";
    send(value);
  });
  for (const chip of document.querySelectorAll(".la-chip")) chip.addEventListener("click", () => send(chip.dataset.goal));
  $("fleet").addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;
    const { action, agent } = button.dataset;
    if (action === "revoke" && !window.confirm(`Revoke ${agent}? Revocation is permanent for this session and stops every agent below it.`)) return;
    button.focus();
    const result = await backend.control(action, agent);
    renderFleet(result.state);
    const verb = { suspend: "Suspended", reinstate: "Reinstated", revoke: "Revoked" }[action];
    addMessage("Lead agent", `${verb} ${agent}. ${result.affected.length} agent${result.affected.length === 1 ? "" : "s"} affected: ${result.affected.join(", ")}.`);
  });
  $("shutdown").addEventListener("click", async () => {
    if (busy) return;
    setBusy(true);
    try {
      const result = await backend.shutdownTest();
      const out = $("shutdown-result");
      out.textContent = `Shutdown test ${result.result}: ${result.agents.length} agents stopped ${result.stopped_all ? "together" : "only partly"} and ${result.resumed_all ? "resumed" : "did not all resume"}.`;
      out.dataset.result = result.result;
      renderFleet(result.state);
    } finally { setBusy(false); }
  });
  $("verify").addEventListener("click", async () => verifyDoc(await backend.audit(), backend.kind === "local" ? "This tab's ledger" : "Server ledger"));
  $("export").addEventListener("click", async () => {
    const doc = await backend.audit();
    const url = URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + "\n"], { type: "application/json" }));
    const link = el("a", { href: url, download: "lead-agent-audit.json" });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $("audit-result").textContent = `Exported ${doc.records.length} records as lead-agent-audit.json.`;
    delete $("audit-result").dataset.ok;
  });
  $("check-file").addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try { await verifyDoc(JSON.parse(await file.text()), file.name); }
    catch { $("audit-result").dataset.ok = "false"; $("audit-result").textContent = `${file.name}: not valid JSON.`; }
    event.target.value = "";
  });
  $("connect-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const out = $("connect-result");
    let base;
    try {
      const url = new URL($("server-url").value);
      if (!/^(localhost|127\.0\.0\.1|\[::1\])$/.test(url.hostname)) throw new Error("use a server on this machine (localhost or 127.0.0.1)");
      base = url.origin;
    } catch (error) { out.textContent = `Not connected: ${error.message}.`; return; }
    out.textContent = "Connecting…";
    try {
      const health = await (await fetch(base + "/api/health", { cache: "no-store" })).json();
      if (!health.ok) throw new Error("health check failed");
      backend = remoteBackend(base, health.model);
      calls = [];
      renderCalls();
      await refresh();
      $("mode-label").textContent = backend.label;
      $("live-text").textContent = `Live · local server ${base} · ${health.model}`;
      $("disconnect").hidden = false;
      out.textContent = `Connected to ${base} (lead-agent ${health.version}, ${health.model}). Goals now run on that server.`;
      addMessage("Lead agent", `Connected to the local server at ${base}. Its model: ${health.model}.`);
    } catch (error) {
      out.textContent = `Not connected: ${error.message}. Is "lead-agent serve" running?`;
    }
  });
  $("disconnect").addEventListener("click", async () => {
    backend = localBackend();
    calls = [];
    renderCalls();
    await refresh();
    $("mode-label").textContent = backend.label;
    $("live-text").textContent = "Live in this tab · deterministic model · no account, no key, nothing sent";
    $("disconnect").hidden = true;
    $("connect-result").textContent = "Disconnected. A fresh fleet is running in this tab.";
  });
}

wire();
refresh();
