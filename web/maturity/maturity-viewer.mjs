const LEVEL_TEXT = { BASIC: "Basic", READY: "Ready", DYNAMIC: "Dynamic", ADVANCED: "Advanced" };

function text(value) {
  return value ? LEVEL_TEXT[value] || value : "Not established";
}

export function renderResult(details) {
  const cards = (details.categories || []).map((cat) => `
    <article class="result-card">
      <h3>${cat.category}</h3>
      <p class="meta">${cat.pillar}</p>
      <div class="triad">
        <p><span>Where we say we are</span><strong>${text(cat.claimed_level)}</strong></p>
        <p><span>What the evidence can carry</span><strong>${text(cat.evidence_supported_level)}</strong></p>
        <p><span>Where we need to be</span><strong>${text(cat.target_level)}</strong></p>
      </div>
      <ul>
        <li>Human determination: ${text(cat.human_determined_level)} (${cat.human_determination_status || "none"})</li>
        <li>Evidence support: ${cat.level_support_state}</li>
        <li>Evidence state: ${cat.support_status}</li>
        <li>Freshness: ${cat.freshness_status}</li>
        <li>Assessment: ${cat.assessment_state}</li>
        <li>Confidence: ${cat.confidence}</li>
        <li>Contradictions: ${(cat.contradictions || []).join("; ") || "None recorded"}</li>
        <li>Conditions: ${(cat.conditions || []).join("; ") || "None"}</li>
        <li>Gaps: ${(cat.gaps || []).join("; ") || "None recorded"}</li>
        <li>Corrective actions: ${(cat.corrective_actions || []).map((item) => item.action || item).join("; ") || "None recorded"}</li>
      </ul>
    </article>`).join("");
  return `
    <p class="status-line">Coverage ${details.assessed_category_count} of ${details.framework_category_count}. Status ${details.coverage_status}. Overall synthesis remains pending human review. Authority effect NONE.</p>
    ${cards || "<p>No category result yet.</p>"}
    <p>${details.evidence_supported_level_meaning}</p>`;
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
