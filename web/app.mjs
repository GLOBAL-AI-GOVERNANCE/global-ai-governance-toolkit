import { contracts, evaluateCsv, GovernanceInputError, pretty } from "./governance-engine.mjs";

const state = { csv: "", sourceName: "", output: null, selectedOutput: "normalized" };
const byId = (id) => document.getElementById(id);

function showPanel(id) {
  document.querySelectorAll(".tab").forEach((button) => button.classList.toggle("active", button.dataset.panel === id));
  document.querySelectorAll(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === id));
}
function download(name, content, type = "application/json") {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([content], { type }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}
function summary(label, value) { return `<article><span>${label}</span><strong>${value}</strong></article>`; }
function renderPreview() {
  const normalized = state.output.normalized;
  byId("normalization-summary").innerHTML = [summary("Schema", normalized.schema_version), summary("Source format", normalized.source.format), summary("Records", normalized.records.length), summary("Mappings", normalized.mappings_applied.length)].join("");
  const fields = ["system_id", "system_name", "owner", "use_case", "data_sensitivity", "autonomy_level"];
  byId("preview-head").innerHTML = `<tr>${fields.map((field) => `<th>${field.replaceAll("_", " ")}</th>`).join("")}</tr>`;
  byId("preview-body").innerHTML = normalized.records.map((record) => `<tr>${fields.map((field) => `<td>${escapeHtml(record[field])}</td>`).join("")}</tr>`).join("");
}
function escapeHtml(value) { const span = document.createElement("span"); span.textContent = String(value); return span.innerHTML; }
function renderResults() {
  const { result, findings, tiers } = state.output;
  byId("gate").className = `gate ${result.governance_gate_state.toLowerCase()}`;
  byId("gate").innerHTML = `<p>Automated gate</p><h3>${result.governance_gate_state.replaceAll("_", " ")}</h3><span>Human decision: ${result.human_decision_state.replaceAll("_", " ")}</span>`;
  const tierCards = Object.entries(tiers).map(([id, tier]) => `<article class="finding"><span class="severity tier">${tier} risk</span><h3>${escapeHtml(id)}</h3><p>Preliminary risk tier from the Wave A calculator.</p></article>`);
  const findingCards = findings.findings.map((item) => `<article class="finding"><span class="severity ${item.severity.toLowerCase()}">${item.severity}</span><h3>${escapeHtml(item.rule_id)} · ${escapeHtml(item.system_name)}</h3><p>${escapeHtml(item.message)}</p></article>`);
  byId("finding-list").innerHTML = [...tierCards, ...(findingCards.length ? findingCards : ['<article class="finding clear"><span class="severity">No gaps</span><h3>Passed current automated checks</h3><p>A human decision is still required.</p></article>'])].join("");
}
function renderMachine() {
  const value = state.output[state.selectedOutput];
  byId("machine-json").textContent = pretty(value);
  document.querySelectorAll("[data-output]").forEach((button) => button.classList.toggle("active", button.dataset.output === state.selectedOutput));
}
function renderDownloads() {
  const files = {
    "normalized-inventory.json": pretty(state.output.normalized), "governance-findings.json": pretty(state.output.findings), "governance-result.json": pretty(state.output.result), "manifest.json": pretty(state.output.manifest), "governance-handoff.json": pretty(state.output.handoff), ...state.output.documents,
  };
  byId("download-grid").innerHTML = "";
  for (const [name, content] of Object.entries(files)) {
    const button = document.createElement("button"); button.className = "download"; button.innerHTML = `<span>${name.endsWith(".md") ? "HUMAN" : "MACHINE"}</span>${name}`;
    button.addEventListener("click", () => download(name, content, name.endsWith(".md") ? "text/markdown" : "application/json"));
    byId("download-grid").append(button);
  }
}
async function run() {
  byId("error").hidden = true;
  try {
    state.output = await evaluateCsv(state.csv, { sourceName: state.sourceName, evaluationTime: byId("evaluation-time").value.trim() || null });
    renderPreview(); renderResults(); renderMachine(); renderDownloads();
  } catch (error) {
    const issue = error instanceof GovernanceInputError ? error.issue : { code: "BROWSER_RUNTIME_ERROR", remediation: error.message };
    byId("error").textContent = `${issue.code}: ${issue.remediation}`; byId("error").hidden = false;
  }
}
async function loadCsv(text, name) {
  state.csv = text; state.sourceName = name; byId("source-name").textContent = name; byId("workspace").hidden = false; await run(); byId("workspace").scrollIntoView({ behavior: "smooth" });
}

byId("try-sample").addEventListener("click", () => loadCsv(contracts.sampleCsv, "safe-sample.csv"));
byId("csv-file").addEventListener("change", async (event) => { const [file] = event.target.files; if (file) await loadCsv(await file.text(), file.name); });
byId("run-checks").addEventListener("click", run);
document.querySelectorAll(".tab").forEach((button) => button.addEventListener("click", () => showPanel(button.dataset.panel)));
document.querySelectorAll("[data-output]").forEach((button) => button.addEventListener("click", () => { state.selectedOutput = button.dataset.output; renderMachine(); }));
