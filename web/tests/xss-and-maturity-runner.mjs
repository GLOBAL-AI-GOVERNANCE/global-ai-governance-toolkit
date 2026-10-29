import { pathToFileURL } from "node:url";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readFile } from "node:fs/promises";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const payload = `<img src=x onerror=alert(1)>`;
const failures = [];

const { renderResult, escapeHtml } = await import(pathToFileURL(path.join(root, "maturity/maturity-viewer.mjs")).href);
const html = renderResult({
  assessed_category_count: 1,
  framework_category_count: 1,
  coverage_status: "PARTIAL",
  evidence_supported_level_meaning: payload,
  categories: [{
    category: payload,
    pillar: payload,
    claimed_level: "BASIC",
    evidence_supported_level: "BASIC",
    target_level: "BASIC",
    human_determined_level: "BASIC",
    human_determination_status: payload,
    level_support_state: payload,
    support_status: payload,
    freshness_status: payload,
    assessment_state: payload,
    confidence: payload,
    contradictions: [payload],
    conditions: [payload],
    gaps: [payload],
    corrective_actions: [{ action: payload }],
  }],
});
if (html.includes("<img")) failures.push("maturity renderResult leaked raw <img tag");
if (!html.includes("&lt;img")) failures.push("maturity renderResult did not escape <img payload");

const { evaluateMaturity, buildProfileResult } = await import(pathToFileURL(path.join(root, "maturity/maturity-engine.mjs")).href);
const sample = {
  framework_id: "unesco-ai-maturity-2025",
  framework_version: "2025",
  assessment_coverage: "PARTIAL",
  authority_effect: "NONE",
  categories: [{
    pillar_id: "ai-governance-ethics-risk",
    category_id: "ai-governance-ethics-risk.ai-governance-framework",
    claimed_level: "BASIC",
    target_level: "BASIC",
    evidence: [],
  }],
};
const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
const built = await buildProfileResult(sample, now);
if (built.evaluation_time !== now) failures.push(`export evaluation_time expected ${now}, got ${built.evaluation_time}`);
if (built.evaluation_time === "2026-10-23T00:00:00Z") failures.push("export still pinned to 2026-10-23");

const appSource = await readFile(path.join(root, "maturity/app.mjs"), "utf8");
if (appSource.includes('"2026-10-23T00:00:00Z"')) failures.push("maturity app still hardcodes 2026-10-23");
if (!appSource.includes("isStrictUtcTimestamp") || !appSource.includes("nowUtc")) failures.push("maturity app missing UTC validation/default");
if (appSource.includes("value=\"${") || appSource.includes("innerHTML = `<h2>${category")) {
  failures.push("maturity app still interpolates unsanitized values into HTML");
}

const { evaluateCsv } = await import(pathToFileURL(path.join(root, "governance-engine.mjs")).href);
const csv = [
  "system_id,system_name,owner,business_unit,vendor_internal,use_case,data_sensitivity,impact_people,impact_money,impact_security,impact_rights,impact_safety,autonomy_level,public_facing,monitoring_active,shutdown_path_exists,evidence_complete",
  `XSS-1,${payload},Owner,Ops,Internal,Demo,None,No,No,No,No,No,None,No,Yes,Yes,Yes`,
  `FULL-1,Full Agent,Owner,Ops,Internal,Demo,Internal,No,No,No,No,No,Full,No,Yes,Yes,Yes`,
].join("\n");
const output = await evaluateCsv(csv, { sourceName: "xss.csv", evaluationTime: "2026-08-29T12:00:00Z" });
const previewHtml = `<td>${escapeHtml(payload)}</td>`;
if (previewHtml.includes("<img") || !previewHtml.includes("&lt;img")) failures.push("CSV preview escape failed");
const ruleIds = output.findings.findings.map((item) => item.rule_id);
if (!ruleIds.includes("GAI-AUTO-005")) failures.push(`GAI-AUTO-005 did not fire for Full autonomy; got ${ruleIds.join(",")}`);

if (failures.length) {
  console.error(JSON.stringify({ ok: false, failures }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, evaluation_time: built.evaluation_time, auto005: true, xss_escaped: true, rules: ruleIds }));
