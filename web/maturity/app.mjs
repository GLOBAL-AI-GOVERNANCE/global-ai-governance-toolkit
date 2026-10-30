import { MATURITY_CATALOG, evaluateMaturity, buildProfileResult, LEVEL_LABELS, validateMaturityAssessment } from "./maturity-engine.mjs";
import { renderResult, gapRegister, reviewMarkdown, escapeHtml } from "./maturity-viewer.mjs";

const TIME_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;

function isStrictUtcTimestamp(value) {
  if (!TIME_PATTERN.test(value)) return false;
  const [datePart, timePart] = value.slice(0, -1).split("T");
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);
  const instant = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
  return instant.getUTCFullYear() === year
    && instant.getUTCMonth() === month - 1
    && instant.getUTCDate() === day
    && instant.getUTCHours() === hour
    && instant.getUTCMinutes() === minute
    && instant.getUTCSeconds() === second;
}

function nowUtc() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}


const state = {
  framework_id: "unesco-ai-maturity-2025",
  framework_version: "2025",
  assessment_id: "",
  assessment_scope: "",
  assessment_coverage: "PARTIAL",
  accountable_owner: "",
  authority_effect: "NONE",
  categories: [],
};
let selected = null;
let hasEvaluatedResult = false;

const pillarNav = document.querySelector("#pillar-nav");
const editor = document.querySelector("#editor");
const result = document.querySelector("#result");
const count = document.querySelector("#count");
const evaluationTimeInput = document.querySelector("#evaluation-time");
if (evaluationTimeInput && !evaluationTimeInput.value) evaluationTimeInput.value = nowUtc();


function setExportsEnabled(enabled) {
  for (const id of ["export-result", "export-gaps", "export-review"]) {
    const node = document.querySelector("#" + id);
    if (node) node.disabled = !enabled;
  }
}

function blankCategory(pillarId, categoryId) {
  return {
    pillar_id: pillarId,
    category_id: categoryId,
    claimed_level: "BASIC",
    target_level: "BASIC",
    evidence: [{ reference: "", evidence_class: "OPERATING", scope: "", is_representative: false }],
    contradictions: [],
    gaps: [],
    corrective_actions: [],
    material_change_events: [],
  };
}

function current(categoryId) {
  return state.categories.find((item) => item.category_id === categoryId);
}

function renderNav() {
  const query = document.querySelector("#filter").value.trim().toLowerCase();
  pillarNav.replaceChildren();
  for (const pillar of MATURITY_CATALOG.pillars) {
    const items = pillar.categories.filter((category) => category.label.toLowerCase().includes(query));
    if (!items.length) continue;
    const section = document.createElement("section");
    const heading = document.createElement("h2");
    heading.textContent = pillar.label;
    section.append(heading);
    for (const category of items) {
      const present = current(category.id);
      const button = document.createElement("button");
      button.className = "category";
      button.type = "button";
      button.dataset.pillar = pillar.id;
      button.dataset.category = category.id;
      button.setAttribute("aria-current", String(selected === category.id));
      button.textContent = `${category.label}${present ? " · assessed" : ""}`;
      section.append(button);
    }
    pillarNav.append(section);
  }
  const missing = MATURITY_CATALOG.pillars.flatMap((pillar) => pillar.categories).filter((category) => !current(category.id));
  if (!pillarNav.children.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.setAttribute("role", "status");
    empty.textContent = query ? `No categories match “${document.querySelector("#filter").value.trim()}”.` : "No categories available.";
    pillarNav.append(empty);
  }
  count.textContent = `${state.categories.length} assessed / ${MATURITY_CATALOG.pillars.reduce((sum, pillar) => sum + pillar.categories.length, 0)}. ${state.assessment_coverage === "FULL_FRAMEWORK" && missing.length ? `Full-framework coverage is incomplete: ${missing.length} categories remain.` : `Unassessed categories: ${missing.length}. Partial coverage is not framework completion.`}`;
}

function field(label, control) {
  const wrap = document.createElement("label");
  wrap.append(label);
  wrap.append(control);
  return wrap;
}

function inputControl(id, value, multiline = false) {
  const node = document.createElement(multiline ? "textarea" : "input");
  node.id = id;
  if (multiline) node.value = value ?? "";
  else {
    node.type = "text";
    node.value = value ?? "";
  }
  return node;
}

function selectControl(id, options, selectedValue) {
  const node = document.createElement("select");
  node.id = id;
  for (const option of options) {
    const opt = document.createElement("option");
    if (typeof option === "string") {
      opt.value = option;
      opt.textContent = option || "None";
      if (selectedValue === option) opt.selected = true;
    } else {
      opt.value = option.value;
      opt.textContent = option.label;
      if (selectedValue === option.value) opt.selected = true;
    }
    node.append(opt);
  }
  return node;
}

function renderEditor() {
  const category = MATURITY_CATALOG.pillars.flatMap((pillar) => pillar.categories.map((item) => ({ ...item, pillar }))).find((item) => item.id === selected);
  editor.replaceChildren();
  if (!category) {
    const p = document.createElement("p");
    p.textContent = "Select a category.";
    editor.append(p);
    return;
  }
  const record = current(category.id) || blankCategory(category.pillar.id, category.id);
  const evidence = record.evidence[0] || {};
  const human = record.human_determination || {};

  const title = document.createElement("h2");
  title.textContent = category.label;
  const pillar = document.createElement("p");
  pillar.textContent = category.pillar.label;
  editor.append(title, pillar);

  editor.append(
    field("Claimed level", selectControl("claimed", LEVEL_LABELS, record.claimed_level)),
    field("Target level", selectControl("target", LEVEL_LABELS, record.target_level)),
    field("Human-determined level", selectControl("human-level", ["", ...LEVEL_LABELS], human.level || "")),
    field("Determination status", selectControl("human-status", ["", "PENDING", "ACCEPTED", "ACCEPTED_WITH_CONDITIONS", "REJECTED", "RETURNED_FOR_REASSESSMENT"], human.status || "")),
    field("Accountable role", inputControl("role", human.accountable_role || "")),
    field("Determined at", (() => { const n = inputControl("determined", human.determined_at || ""); n.placeholder = "YYYY-MM-DDTHH:MM:SSZ"; return n; })()),
    field("Conditions", inputControl("conditions", (human.conditions || []).join("; "))),
    field("Evidence reference", inputControl("reference", evidence.reference || "")),
    field("Evidence class", selectControl("class", ["OPERATING", "POLICY", "PILOT", "SYNTHETIC", "OTHER"], evidence.evidence_class || "OPERATING")),
    field("Evidence scope", inputControl("evidence-scope", evidence.scope || state.assessment_scope)),
    field("Representative", selectControl("representative", [{ value: "false", label: "No" }, { value: "true", label: "Yes" }], evidence.is_representative ? "true" : "false")),
    field("Valid through", inputControl("valid", evidence.valid_through || "")),
    field("Integrity digest", inputControl("digest", evidence.sha256 || "")),
    field("Contradictions", inputControl("contradictions", (record.contradictions || []).join("\n"), true)),
    field("Material-change events", inputControl("changes", (record.material_change_events || []).join("\n"), true)),
    field("Gaps", inputControl("gaps", (record.gaps || []).join("\n"), true)),
    field("Corrective action", inputControl("action", (record.corrective_actions[0] || {}).action || "")),
  );
  const save = document.createElement("button");
  save.id = "save-category";
  save.type = "button";
  save.textContent = "Save category";
  editor.append(save);
  save.addEventListener("click", () => {
    const lines = (id) => document.querySelector(id).value.split("\n").map((item) => item.trim()).filter(Boolean);
    const saved = {
      pillar_id: category.pillar.id,
      category_id: category.id,
      claimed_level: document.querySelector("#claimed").value,
      target_level: document.querySelector("#target").value,
      evidence: [{
        reference: document.querySelector("#reference").value,
        evidence_class: document.querySelector("#class").value,
        scope: document.querySelector("#evidence-scope").value,
        is_representative: document.querySelector("#representative").value === "true",
        valid_through: document.querySelector("#valid").value || undefined,
        sha256: document.querySelector("#digest").value || undefined,
      }].filter((item) => item.reference),
      contradictions: lines("#contradictions"),
      material_change_events: lines("#changes"),
      gaps: lines("#gaps"),
      corrective_actions: document.querySelector("#action").value ? [{ action: document.querySelector("#action").value }] : [],
    };
    const level = document.querySelector("#human-level").value;
    const status = document.querySelector("#human-status").value;
    if (level && status) {
      saved.human_determination = {
        level, status,
        accountable_role: document.querySelector("#role").value,
        determined_at: document.querySelector("#determined").value,
        conditions: document.querySelector("#conditions").value.split(";").map((item) => item.trim()).filter(Boolean),
      };
    }
    state.categories = state.categories.filter((item) => item.category_id !== category.id).concat(saved);
    renderNav();
    evaluate();
  });
}

function readSetup() {
  state.assessment_id = document.querySelector("#assessment-id").value;
  state.assessment_scope = document.querySelector("#scope").value;
  state.accountable_owner = document.querySelector("#owner").value;
  state.assessment_coverage = document.querySelector("#coverage").value;
}

function fixedTimeEnabled() {
  return Boolean(document.querySelector("#fixed-evaluation-time")?.checked);
}

/** One UTC instant per Evaluate/export action. Refresh to now unless fixed-time mode is on. */
function captureEvaluationInstant({ refresh }) {
  let raw;
  if (fixedTimeEnabled() || !refresh) {
    raw = (evaluationTimeInput?.value || "").trim() || nowUtc();
  } else {
    raw = nowUtc();
  }
  if (evaluationTimeInput) evaluationTimeInput.value = raw;
  if (!isStrictUtcTimestamp(raw)) {
    throw new Error("Evaluation time must be a real UTC timestamp such as 2026-08-29T12:00:00Z.");
  }
  return raw;
}

async function evaluate() {
  readSetup();
  let evaluationTime;
  try {
    evaluationTime = captureEvaluationInstant({ refresh: true });
  } catch (error) {
    result.replaceChildren();
    const p = document.createElement("p");
    p.className = "error";
    p.setAttribute("role", "alert");
    p.textContent = error.message;
    result.append(p);
    document.querySelector("#live").textContent = error.message;
    return null;
  }
  const evaluated = evaluateMaturity(state, evaluationTime);
  result.innerHTML = renderResult(evaluated.details);
  hasEvaluatedResult = true;
  setExportsEnabled(true);
  document.querySelector("#live").textContent = `Evaluated ${evaluated.details.assessed_category_count} categories at ${evaluationTime}. ${evaluated.details.coverage_status}.`;
  return evaluated;
}

function download(name, text, type) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type }));
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

document.querySelector("#filter").addEventListener("input", renderNav);
document.querySelector("#coverage").addEventListener("change", () => { readSetup(); renderNav(); });
pillarNav.addEventListener("click", (event) => {
  const button = event.target.closest("button.category");
  if (!button) return;
  selected = button.dataset.category;
  renderNav();
  renderEditor();
});
document.querySelector("#evaluate").addEventListener("click", evaluate);
document.querySelector("#export-result").addEventListener("click", async () => {
  if (!hasEvaluatedResult) { showImportStatus("Evaluate locally before exporting.", true); return; }
  readSetup();
  let evaluationTime;
  try {
    evaluationTime = captureEvaluationInstant({ refresh: false });
  } catch (error) {
    showImportStatus(error.message, true);
    return;
  }
  const output = await buildProfileResult(state, evaluationTime);
  delete output.canonical_details;
  download("profile-result.json", `${JSON.stringify(output, null, 2)}\n`, "application/json");
});
document.querySelector("#export-gaps").addEventListener("click", () => {
  if (!hasEvaluatedResult) { showImportStatus("Evaluate locally before exporting.", true); return; }
  let evaluationTime;
  try {
    evaluationTime = captureEvaluationInstant({ refresh: false });
  } catch (error) {
    showImportStatus(error.message, true);
    return;
  }
  download("maturity-gap-register.json", `${JSON.stringify(gapRegister(evaluateMaturity(state, evaluationTime).details), null, 2)}\n`, "application/json");
});
document.querySelector("#export-review").addEventListener("click", () => {
  if (!hasEvaluatedResult) { showImportStatus("Evaluate locally before exporting.", true); return; }
  let evaluationTime;
  try {
    evaluationTime = captureEvaluationInstant({ refresh: false });
  } catch (error) {
    showImportStatus(error.message, true);
    return;
  }
  download("maturity-review.md", reviewMarkdown(evaluateMaturity(state, evaluationTime).details), "text/markdown");
});

function showImportStatus(message, isError) {
  let node = document.querySelector("#import-status");
  if (!node) {
    node = document.createElement("p");
    node.id = "import-status";
    node.setAttribute("role", "status");
    node.setAttribute("aria-live", "polite");
    const input = document.querySelector("#import-file");
    input.insertAdjacentElement("afterend", node);
  }
  node.textContent = message;
  node.dataset.state = isError ? "error" : "ok";
  node.setAttribute("role", isError ? "alert" : "status");
  node.setAttribute("aria-live", isError ? "assertive" : "polite");
}

function validateMaturityImport(value) {
  return validateMaturityAssessment(value);
}

document.querySelector("#import-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  let imported;
  try {
    imported = JSON.parse(await file.text());
  } catch {
    showImportStatus("Import failed: the file is not valid JSON. Your current assessment was left unchanged.", true);
    event.target.value = "";
    return;
  }
  const problem = validateMaturityImport(imported);
  if (problem) {
    showImportStatus(problem + " Your current assessment was left unchanged.", true);
    event.target.value = "";
    return;
  }
  state.assessment_id = imported.assessment_id || "";
  state.assessment_scope = imported.assessment_scope || "";
  state.accountable_owner = imported.accountable_owner || "";
  state.assessment_coverage = imported.assessment_coverage || "PARTIAL";
  state.authority_effect = "NONE";
  state.framework_id = imported.framework_id;
  state.framework_version = imported.framework_version;
  state.categories = imported.categories;
  document.querySelector("#assessment-id").value = state.assessment_id;
  document.querySelector("#scope").value = state.assessment_scope;
  document.querySelector("#owner").value = state.accountable_owner;
  document.querySelector("#coverage").value = state.assessment_coverage;
  if (imported.evaluation_time && isStrictUtcTimestamp(imported.evaluation_time) && evaluationTimeInput) {
    evaluationTimeInput.value = imported.evaluation_time;
  }
  renderNav();
  evaluate();
  showImportStatus(`Imported ${file.name}: ${state.categories.length} categor${state.categories.length === 1 ? "y" : "ies"}.`, false);
  event.target.value = "";
});
document.querySelector("#sample").addEventListener("click", () => {
  const sample = {
    framework_id: "unesco-ai-maturity-2025",
    framework_version: "2025",
    assessment_id: "synthetic-sample",
    assessment_scope: "synthetic enterprise",
    assessment_coverage: "PARTIAL",
    accountable_owner: "governance-function",
    authority_effect: "NONE",
    categories: [
      {
        pillar_id: "ai-governance-ethics-risk",
        category_id: "ai-governance-ethics-risk.ai-governance-framework",
        claimed_level: "READY",
        target_level: "DYNAMIC",
        human_determination: { level: "READY", status: "ACCEPTED", accountable_role: "assurance-function", determined_at: "2026-09-01T00:00:00Z" },
        evidence: [{ reference: "synthetic://operating-record", evidence_class: "OPERATING", scope: "synthetic enterprise", is_representative: true, valid_through: "2027-09-01T00:00:00Z" }],
      },
      {
        pillar_id: "people-culture",
        category_id: "people-culture.ai-literacy-awareness",
        claimed_level: "DYNAMIC",
        target_level: "DYNAMIC",
        human_determination: { level: "DYNAMIC", status: "ACCEPTED", accountable_role: "assurance-function", determined_at: "2026-09-01T00:00:00Z" },
        evidence: [{ reference: "synthetic://expired-record", evidence_class: "OPERATING", scope: "synthetic enterprise", is_representative: true, valid_through: "2025-01-01T00:00:00Z" }],
      },
      {
        pillar_id: "strategy-value",
        category_id: "strategy-value.ai-vision-ambition",
        claimed_level: "ADVANCED",
        target_level: "ADVANCED",
        contradictions: ["A second synthetic record disagrees with the claimed level."],
        evidence: [{ reference: "synthetic://disputed-record", evidence_class: "OPERATING", scope: "synthetic enterprise", is_representative: true, valid_through: "2027-01-01T00:00:00Z" }],
      },
    ],
  };
  Object.assign(state, sample);
  document.querySelector("#assessment-id").value = sample.assessment_id;
  document.querySelector("#scope").value = sample.assessment_scope;
  document.querySelector("#owner").value = sample.accountable_owner;
  document.querySelector("#coverage").value = sample.assessment_coverage;
  document.querySelector("#sample-note").hidden = false;
  renderNav();
  evaluate();
});

renderNav();
setExportsEnabled(false);
renderEditor();
