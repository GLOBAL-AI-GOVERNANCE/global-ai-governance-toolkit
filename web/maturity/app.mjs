import { MATURITY_CATALOG, evaluateMaturity, buildProfileResult, LEVEL_LABELS } from "./maturity-engine.mjs";
import { renderResult, gapRegister, reviewMarkdown } from "./maturity-viewer.mjs";

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

const pillarNav = document.querySelector("#pillar-nav");
const editor = document.querySelector("#editor");
const result = document.querySelector("#result");
const count = document.querySelector("#count");

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
  pillarNav.innerHTML = MATURITY_CATALOG.pillars.map((pillar) => {
    const items = pillar.categories.filter((category) => category.label.toLowerCase().includes(query)).map((category) => {
      const present = current(category.id);
      return `<button class="category" type="button" data-pillar="${pillar.id}" data-category="${category.id}" aria-current="${selected === category.id}">${category.label}${present ? " · assessed" : ""}</button>`;
    }).join("");
    return items ? `<section><h2>${pillar.label}</h2>${items}</section>` : "";
  }).join("");
  const missing = MATURITY_CATALOG.pillars.flatMap((pillar) => pillar.categories).filter((category) => !current(category.id));
  count.textContent = `${state.categories.length} assessed / ${MATURITY_CATALOG.pillars.reduce((sum, pillar) => sum + pillar.categories.length, 0)}. ${state.assessment_coverage === "FULL_FRAMEWORK" && missing.length ? `Full-framework coverage is incomplete: ${missing.length} categories remain.` : `Unassessed categories: ${missing.length}. Partial coverage is not framework completion.`}`;
}

function field(label, html) {
  return `<label>${label}${html}</label>`;
}

function renderEditor() {
  const category = MATURITY_CATALOG.pillars.flatMap((pillar) => pillar.categories.map((item) => ({ ...item, pillar }))).find((item) => item.id === selected);
  if (!category) {
    editor.innerHTML = "<p>Select a category.</p>";
    return;
  }
  const record = current(category.id) || blankCategory(category.pillar.id, category.id);
  const evidence = record.evidence[0] || {};
  const human = record.human_determination || {};
  const options = LEVEL_LABELS.map((level) => `<option ${record.claimed_level === level ? "selected" : ""}>${level}</option>`).join("");
  const targets = LEVEL_LABELS.map((level) => `<option ${record.target_level === level ? "selected" : ""}>${level}</option>`).join("");
  const humanLevels = ["", ...LEVEL_LABELS].map((level) => `<option value="${level}" ${human.level === level ? "selected" : ""}>${level || "None"}</option>`).join("");
  const statuses = ["", "PENDING", "ACCEPTED", "ACCEPTED_WITH_CONDITIONS", "REJECTED", "RETURNED_FOR_REASSESSMENT"].map((status) => `<option value="${status}" ${human.status === status ? "selected" : ""}>${status || "None"}</option>`).join("");
  editor.innerHTML = `<h2>${category.label}</h2><p>${category.pillar.label}</p>
    ${field("Claimed level", `<select id="claimed">${options}</select>`)}
    ${field("Target level", `<select id="target">${targets}</select>`)}
    ${field("Human-determined level", `<select id="human-level">${humanLevels}</select>`)}
    ${field("Determination status", `<select id="human-status">${statuses}</select>`)}
    ${field("Accountable role", `<input id="role" value="${human.accountable_role || ""}">`)}
    ${field("Determined at", `<input id="determined" value="${human.determined_at || ""}" placeholder="YYYY-MM-DDTHH:MM:SSZ">`)}
    ${field("Conditions", `<input id="conditions" value="${(human.conditions || []).join("; ")}">`)}
    ${field("Evidence reference", `<input id="reference" value="${evidence.reference || ""}">`)}
    ${field("Evidence class", `<select id="class">${["OPERATING", "POLICY", "PILOT", "SYNTHETIC", "OTHER"].map((item) => `<option ${evidence.evidence_class === item ? "selected" : ""}>${item}</option>`).join("")}</select>`)}
    ${field("Evidence scope", `<input id="evidence-scope" value="${evidence.scope || state.assessment_scope}">`)}
    ${field("Representative", `<select id="representative"><option value="false">No</option><option value="true" ${evidence.is_representative ? "selected" : ""}>Yes</option></select>`)}
    ${field("Valid through", `<input id="valid" value="${evidence.valid_through || ""}">`)}
    ${field("Integrity digest", `<input id="digest" value="${evidence.sha256 || ""}">`)}
    ${field("Contradictions", `<textarea id="contradictions">${(record.contradictions || []).join("\n")}</textarea>`)}
    ${field("Material-change events", `<textarea id="changes">${(record.material_change_events || []).join("\n")}</textarea>`)}
    ${field("Gaps", `<textarea id="gaps">${(record.gaps || []).join("\n")}</textarea>`)}
    ${field("Corrective action", `<input id="action" value="${(record.corrective_actions[0] || {}).action || ""}">`)}
    <button id="save-category" type="button">Save category</button>`;
  document.querySelector("#save-category").addEventListener("click", () => {
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

async function evaluate() {
  readSetup();
  const evaluated = evaluateMaturity(state, "2026-10-23T00:00:00Z");
  result.innerHTML = renderResult(evaluated.details);
  document.querySelector("#live").textContent = `Evaluated ${evaluated.details.assessed_category_count} categories. ${evaluated.details.coverage_status}.`;
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
  readSetup();
  const output = await buildProfileResult(state, "2026-10-23T00:00:00Z");
  delete output.canonical_details;
  download("profile-result.json", `${JSON.stringify(output, null, 2)}\n`, "application/json");
});
document.querySelector("#export-gaps").addEventListener("click", () => {
  download("maturity-gap-register.json", `${JSON.stringify(gapRegister(evaluateMaturity(state, "2026-10-23T00:00:00Z").details), null, 2)}\n`, "application/json");
});
document.querySelector("#export-review").addEventListener("click", () => {
  download("maturity-review.md", reviewMarkdown(evaluateMaturity(state, "2026-10-23T00:00:00Z").details), "text/markdown");
});
document.querySelector("#import-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const imported = JSON.parse(await file.text());
  Object.assign(state, imported);
  document.querySelector("#assessment-id").value = state.assessment_id || "";
  document.querySelector("#scope").value = state.assessment_scope || "";
  document.querySelector("#owner").value = state.accountable_owner || "";
  document.querySelector("#coverage").value = state.assessment_coverage || "PARTIAL";
  renderNav();
  evaluate();
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
renderEditor();
