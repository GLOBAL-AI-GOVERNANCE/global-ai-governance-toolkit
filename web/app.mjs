import { contracts, evaluateCsv, GovernanceInputError, pretty } from "./governance-engine.mjs";
import { guidanceFor } from "./finding-guidance.mjs";
import { renderProfileResult, SYNTHETIC_CISO_PROFILE_RESULT } from "./profile-viewer.mjs";
import { createEvaluationSession, describeInputError } from "./evaluation-session.mjs";

const session = createEvaluationSession();
const state = { csv: "", sourceName: "", selectedOutput: "normalized" };
const byId = (id) => document.getElementById(id);

function showPanel(id, focus = false) {
  document.querySelectorAll(".tabs [role=tab]").forEach((tab) => {
    const selected = tab.dataset.panel === id;
    tab.classList.toggle("active", selected);
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  document.querySelectorAll(".panel").forEach((panel) => { const active = panel.id === id; panel.classList.toggle("active", active); panel.hidden = !active; });
}
function download(name, content, type = "application/json") {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([content], { type }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}
function summary(label, value) { return `<article><span>${label}</span><strong>${value}</strong></article>`; }
function escapeHtml(value) { const span = document.createElement("span"); span.textContent = String(value); return span.innerHTML; }
function clearEvaluation(statusText) {
  for (const id of ["normalization-summary", "preview-head", "preview-body", "result-explanation", "finding-list", "download-grid"]) byId(id).innerHTML = "";
  byId("gate").className = "gate"; byId("gate").innerHTML = "";
  byId("machine-json").textContent = "";
  byId("evaluation-status").textContent = statusText;
}
function renderPreview(output) {
  const normalized = output.normalized;
  byId("normalization-summary").innerHTML = [summary("Schema", normalized.schema_version), summary("Source format", normalized.source.format), summary("Records", normalized.records.length), summary("Mappings", normalized.mappings_applied.length)].join("");
  const fields = ["system_id", "system_name", "owner", "use_case", "data_sensitivity", "autonomy_level"];
  byId("preview-head").innerHTML = `<tr>${fields.map((field) => `<th>${field.replaceAll("_", " ")}</th>`).join("")}</tr>`;
  byId("preview-body").innerHTML = normalized.records.map((record) => `<tr>${fields.map((field) => `<td>${escapeHtml(record[field])}</td>`).join("")}</tr>`).join("");
}
function renderResults(output) {
  const { result, findings, tiers } = output;
  byId("gate").className = `gate ${result.governance_gate_state.toLowerCase()}`;
  const resultCopy = result.governance_gate_state === "BLOCKED"
    ? { result: "Critical gaps need attention", meaning: "The current automated checks found at least one critical governance gap.", next: "Resolve the critical gaps, rerun the review, and keep the final decision with an accountable human." }
    : result.governance_gate_state === "REVIEW_REQUIRED"
      ? { result: "Human review is required", meaning: "The current automated checks found governance gaps that need review.", next: "Review each gap, add the missing controls or evidence, and document the accountable human decision." }
      : { result: "Current automated checks passed", meaning: "No gap was found by the five bounded rules in this toolkit.", next: "Review the evidence and Decision Pack. An accountable human must still make the decision." };
  byId("gate").innerHTML = `<p>Result</p><h3>${resultCopy.result}</h3><span>Human decision remains pending</span>`;
  byId("result-explanation").innerHTML = `<article><h3>What this means</h3><p>${resultCopy.meaning}</p></article><article><h3>What to do next</h3><p>${resultCopy.next}</p></article>`;
  const tierCards = Object.entries(tiers).map(([id, tier]) => `<article class="finding"><span class="severity tier">${tier} risk</span><h3>${escapeHtml(id)}</h3><p>Preliminary risk tier from the built-in calculator.</p></article>`);
  const findingCards = findings.findings.map((item) => {
    const guidance = guidanceFor(item.rule_id);
    return `<article class="finding"><span class="severity ${item.severity.toLowerCase()}">${item.severity} · ${escapeHtml(item.rule_id)}</span><h3>${guidance.title}</h3><h4>What this means</h4><p>${guidance.meaning}</p><h4>What to do next</h4><p>${guidance.next}</p><details><summary>Technical detail</summary><p>System: ${escapeHtml(item.system_name)} (${escapeHtml(item.system_id)})</p><p>Policy message: ${escapeHtml(item.message)}</p><p>Finding ID: <code>${escapeHtml(item.finding_id)}</code></p></details></article>`;
  });
  byId("finding-list").innerHTML = [...tierCards, ...(findingCards.length ? findingCards : ['<article class="finding clear"><span class="severity">No gaps</span><h3>Passed current automated checks</h3><p>A human decision is still required.</p></article>'])].join("");
}
function renderMachine() {
  const output = session.current.output;
  byId("machine-json").textContent = output ? pretty(output[state.selectedOutput]) : "";
  document.querySelectorAll("[data-output]").forEach((button) => {
    const selected = button.dataset.output === state.selectedOutput;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}
function renderDownloads(output, token) {
  const files = {
    "normalized-inventory.json": pretty(output.normalized), "governance-findings.json": pretty(output.findings), "governance-result.json": pretty(output.result), "manifest.json": pretty(output.manifest), "governance-handoff.json": pretty(output.handoff), ...output.documents,
  };
  byId("download-grid").innerHTML = "";
  for (const [name, content] of Object.entries(files)) {
    const button = document.createElement("button"); button.type = "button"; button.className = "download"; button.innerHTML = `<span>${name.endsWith(".md") ? "HUMAN" : "MACHINE"}</span>${name}`;
    button.addEventListener("click", () => { if (session.canDownload(token)) download(name, content, name.endsWith(".md") ? "text/markdown" : "application/json"); });
    byId("download-grid").append(button);
  }
}
// Invalidate everything from the previous evaluation before any new input is read or evaluated.
function beginInput(sourceName) {
  const token = session.begin(sourceName);
  state.sourceName = sourceName;
  byId("source-name").textContent = sourceName;
  byId("error").hidden = true; byId("error").textContent = "";
  byId("workspace").hidden = false;
  clearEvaluation(`Evaluating ${sourceName}…`);
  return token;
}
function fail(token, issue) {
  if (!session.reject(token, issue)) return;
  clearEvaluation(`No valid evaluation for ${state.sourceName}. Previous results were cleared.`);
  byId("error").textContent = describeInputError(issue); byId("error").hidden = false;
}
async function evaluate(token) {
  try {
    const output = await evaluateCsv(state.csv, { sourceName: state.sourceName, evaluationTime: byId("evaluation-time").value.trim() || null });
    if (!session.resolve(token, output)) return;
    renderPreview(output); renderResults(output); renderMachine(); renderDownloads(output, token);
    byId("evaluation-status").textContent = `Evaluation ready for ${state.sourceName}.`;
  } catch (error) {
    fail(token, error instanceof GovernanceInputError ? error.issue : { code: "BROWSER_RUNTIME_ERROR", remediation: error.message });
  }
}
async function loadCsv(textOrPromise, name) {
  const token = beginInput(name);
  byId("workspace").scrollIntoView();
  let text;
  try { text = await textOrPromise; }
  catch { return fail(token, { code: "FILE_READ_ERROR", remediation: "The file could not be read. Choose the file again." }); }
  if (!session.isCurrent(token)) return;
  state.csv = text;
  await evaluate(token);
}

byId("run-sample").addEventListener("click", () => loadCsv(contracts.sampleCsv, "safe-sample.csv"));
byId("run-gaps-sample").addEventListener("click", () => loadCsv(contracts.gapsSampleCsv, "synthetic-sample-with-gaps.csv"));
byId("csv-file").addEventListener("change", (event) => { const [file] = event.target.files; if (file) loadCsv(file.text(), file.name); });
byId("run-checks").addEventListener("click", () => evaluate(beginInput(state.sourceName)));
const tabs = [...document.querySelectorAll(".tabs [role=tab]")];
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => showPanel(tab.dataset.panel));
  tab.addEventListener("keydown", (event) => {
    const moves = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: tabs.length - 1 };
    if (!(event.key in moves)) return;
    event.preventDefault();
    showPanel(tabs[(moves[event.key] + tabs.length) % tabs.length].dataset.panel, true);
  });
});
showPanel("preview");
document.querySelectorAll("[data-output]").forEach((button) => button.addEventListener("click", () => { state.selectedOutput = button.dataset.output; renderMachine(); }));
byId("profile-file").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  byId("profile-error").hidden = true;
  try { renderProfileResult(JSON.parse(await file.text()), document); }
  catch (error) { byId("profile-error").textContent = error.message; byId("profile-error").hidden = false; }
});
byId("run-profile-sample").addEventListener("click", () => renderProfileResult(SYNTHETIC_CISO_PROFILE_RESULT, document));
