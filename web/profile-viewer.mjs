export const SYNTHETIC_CISO_PROFILE_RESULT = Object.freeze({
  schema_version: "1.0.0", profile_id: "ciso-ai-risk-v0.1", profile_version: "0.1.0",
  source_artifact_sha256: `sha256:${"0".repeat(64)}`, decision_pack_manifest: null,
  authority_effect: "NONE", evaluation_time: "2026-08-29T12:00:00Z", status: "PASS",
  summary: "Submitted profile passed its bounded structural and integrity checks.", findings: [],
  evidence_references: [{ type: "ARTIFACT_ID", reference: "SYNTHETIC-CISO-EVIDENCE-001" }],
  details: { current_decision: "conditionally_authorized", top_condition: "Keep human review on every proposed customer action.", stop_condition: "Stop use if monitoring fails or an action bypasses human review.", review_expiration: "2027-01-31T00:00:00Z", dependency_state: [{ id: "agentic-stateful-revocation", state: "NOT_YET_ESTABLISHED" }], governed_system_reference: "SYSTEM-SYNTH-CS-001" },
});

export function profileViewModel(result) {
  if (!result || result.schema_version !== "1.0.0" || result.authority_effect !== "NONE" || !Array.isArray(result.findings) || !Array.isArray(result.evidence_references)) throw new Error("Unsupported profile-result contract");
  const details = result.details || {};
  const findings = result.findings.map(({ id, severity, message, action }) => ({ id, severity, message, action }));
  return {
    profile: `${result.profile_id} — ${result.profile_version}`, status: result.status,
    decision: details.current_decision || details.bounded_decision || result.status, consequence: result.summary,
    remainingRisk: findings.length ? findings.map(item => item.message).join(" ") : (details.stop_condition || "No machine finding; bounded human review remains required."),
    nextAction: findings.length ? findings.map(item => item.action).join(" ") : (details.top_condition || "Review the evidence and record an accountable human decision."),
    timeline: details.review_expiration || result.evaluation_time || "Not supplied",
    findings, evidenceReferences: result.evidence_references, details, authorityEffect: result.authority_effect,
  };
}

export function renderProfileResult(result, document) {
  const view = profileViewModel(result);
  const target = document.getElementById("profile-result");
  if (!target) throw new Error("Missing #profile-result target");
  const escape = (value) => String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  target.setAttribute("role", "region"); target.setAttribute("aria-labelledby", "profile-decision-heading"); target.setAttribute("tabindex", "-1");
  target.innerHTML = `<header><p>${escape(view.profile)}</p><h2 id="profile-decision-heading">Decision: ${escape(view.decision)}</h2><p class="profile-status" role="status" aria-live="polite">Machine status: ${escape(view.status)}</p></header>`
    + `<ol class="decision-surface" aria-label="Decision review sequence"><li><h3>Consequence</h3><p>${escape(view.consequence)}</p></li><li><h3>Remaining risk</h3><p>${escape(view.remainingRisk)}</p></li><li><h3>Next action</h3><p>${escape(view.nextAction)}</p></li><li><h3>Timeline</h3><p><time>${escape(view.timeline)}</time></p></li></ol>`
    + `<details><summary>Technical evidence</summary><h3>Findings</h3>${view.findings.map(item => `<article><strong>${escape(item.severity)} — ${escape(item.id)}</strong><p>${escape(item.message)}</p><p>Action: ${escape(item.action)}</p></article>`).join("") || "<p>No machine findings.</p>"}<h3>Evidence references</h3><pre>${escape(JSON.stringify(view.evidenceReferences, null, 2))}</pre><h3>Profile details</h3><pre>${escape(JSON.stringify(view.details, null, 2))}</pre></details>`
    + `<p class="authority-boundary"><strong>Authority effect: ${escape(view.authorityEffect)}</strong>. This machine view does not approve deployment, accept risk, certify, or attest.</p>`;
  if (typeof target.focus === "function") target.focus();
  return view;
}
