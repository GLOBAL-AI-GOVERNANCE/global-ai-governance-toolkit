export function profileViewModel(result) {
  if (!result || result.schema_version !== "1.0.0" || result.authority_effect !== "NONE") throw new Error("Unsupported profile-result contract");
  return {
    profile: `${result.profile_id} · ${result.profile_version}`,
    status: result.status,
    summary: result.summary,
    findings: result.findings.map(({ id, severity, message, action }) => ({ id, severity, message, action })),
    evidenceReferences: result.evidence_references,
    details: result.details,
    authorityEffect: result.authority_effect,
  };
}

export function renderProfileResult(result, document) {
  const view = profileViewModel(result);
  const target = document.getElementById("profile-result");
  if (!target) throw new Error("Missing #profile-result target");
  const escape = (value) => String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  target.innerHTML = `<h2>${escape(view.profile)}</h2><p class="profile-status">${escape(view.status)}</p><p>${escape(view.summary)}</p>`
    + `<h3>Findings and actions</h3>${view.findings.map(item => `<article><strong>${escape(item.severity)} · ${escape(item.id)}</strong><p>${escape(item.message)}</p><p>Action: ${escape(item.action)}</p></article>`).join("") || "<p>No findings.</p>"}`
    + `<h3>Evidence references</h3><pre>${escape(JSON.stringify(view.evidenceReferences, null, 2))}</pre>`
    + `<h3>Profile details</h3><pre>${escape(JSON.stringify(view.details, null, 2))}</pre><p>Authority effect: ${view.authorityEffect}</p>`;
  return view;
}
