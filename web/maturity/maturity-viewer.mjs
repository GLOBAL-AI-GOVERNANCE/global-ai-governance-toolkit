const LEVEL_TEXT = { BASIC: "Basic", READY: "Ready", DYNAMIC: "Dynamic", ADVANCED: "Advanced" };

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[character]));
}

function text(value) {
  return value ? LEVEL_TEXT[value] || value : "Not established";
}

export function renderResult(details) {
  const cards = (details.categories || []).map((cat) => `
    <article class="result-card">
      <h3>${escapeHtml(cat.category)}</h3>
      <p class="meta">${escapeHtml(cat.pillar)}</p>
      <div class="triad">
        <p><span>Where we say we are</span><strong>${escapeHtml(text(cat.claimed_level))}</strong></p>
        <p><span>What the evidence can carry</span><strong>${escapeHtml(text(cat.evidence_supported_level))}</strong></p>
        <p><span>Where we need to be</span><strong>${escapeHtml(text(cat.target_level))}</strong></p>
      </div>
      <ul>
        <li>Human determination: ${escapeHtml(text(cat.human_determined_level))} (${escapeHtml(cat.human_determination_status || "none")})</li>
        <li>Evidence support: ${escapeHtml(cat.level_support_state)}</li>
        <li>Evidence state: ${escapeHtml(cat.support_status)}</li>
        <li>Freshness: ${escapeHtml(cat.freshness_status)}</li>
        <li>Assessment: ${escapeHtml(cat.assessment_state)}</li>
        <li>Confidence: ${escapeHtml(cat.confidence)}</li>
        <li>Contradictions: ${escapeHtml((cat.contradictions || []).join("; ") || "None recorded")}</li>
        <li>Conditions: ${escapeHtml((cat.conditions || []).join("; ") || "None")}</li>
        <li>Gaps: ${escapeHtml((cat.gaps || []).join("; ") || "None recorded")}</li>
        <li>Corrective actions: ${escapeHtml((cat.corrective_actions || []).map((item) => item.action || item).join("; ") || "None recorded")}</li>
      </ul>
    </article>`).join("");
  return `
    <p class="status-line">Coverage ${escapeHtml(details.assessed_category_count)} of ${escapeHtml(details.framework_category_count)}. Status ${escapeHtml(details.coverage_status)}. Overall synthesis remains pending human review. Authority effect NONE.</p>
    ${cards || "<p>No category result yet.</p>"}
    <p>${escapeHtml(details.evidence_supported_level_meaning)}</p>`;
}

export function gapRegister(details) {
  return {
    authority_effect: "NONE",
    categories: (details.categories || []).filter((cat) => cat.evidence_supported_level !== cat.target_level || cat.assessment_state !== "CURRENT").map((cat) => ({
      category_id: cat.category_id,
      claimed_level: cat.claimed_level,
      evidence_supported_level: cat.evidence_supported_level,
      target_level: cat.target_level,
      gaps: cat.gaps,
      corrective_actions: cat.corrective_actions,
    })),
  };
}

export function reviewMarkdown(details) {
  const lines = ["# Maturity evidence review", "", "Overall synthesis: pending human review.", "authority_effect: NONE", ""];
  for (const cat of details.categories || []) {
    lines.push(`## ${cat.category}`, "", `- Claimed: ${text(cat.claimed_level)}`, `- Evidence can carry: ${text(cat.evidence_supported_level)}`, `- Target: ${text(cat.target_level)}`, `- Support: ${cat.level_support_state}`, "");
  }
  return lines.join("\n");
}

export { escapeHtml };
