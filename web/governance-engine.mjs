import { contracts } from "./contracts.generated.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATOR_VERSION = "1.0.0";
const NORMALIZATION_VERSION = "1.0.0";
const TIME_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;

export class GovernanceInputError extends Error {
  constructor(code, sourceColumn, suppliedValue, expected, remediation) {
    super(remediation);
    this.name = "GovernanceInputError";
    this.issue = { code, source_column: sourceColumn, supplied_value: suppliedValue, expected, remediation };
  }
}

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') { cell += '"'; index += 1; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"') quoted = true;
    else if (char === ",") { row.push(cell); cell = ""; }
    else if (char === "\n") { row.push(cell.replace(/\r$/, "")); rows.push(row); row = []; cell = ""; }
    else cell += char;
  }
  if (quoted) throw new GovernanceInputError("MALFORMED_CSV", null, null, [], "Close every quoted CSV field.");
  if (cell || row.length) { row.push(cell.replace(/\r$/, "")); rows.push(row); }
  return rows.filter((item) => item.some((value) => value.trim()));
}

function headerKey(value) { return value.trim().toLowerCase().replaceAll("_", " ").split(/\s+/).join(" "); }
function canonicalFields() { return Object.keys(contracts.canonicalSchema.properties).filter((field) => field !== "schema_version"); }
function aliases() {
  const result = new Map([["schema version", "schema_version"]]);
  for (const [field, definition] of Object.entries(contracts.mapping.fields)) {
    for (const name of [field, definition.human_label, ...(definition.aliases || [])]) result.set(headerKey(name), field);
  }
  return result;
}
function normalizeEnum(field, value) {
  const definition = contracts.canonicalSchema.properties[field];
  const allowed = definition.enum;
  const stripped = value.trim();
  if (!allowed) return stripped;
  if (allowed.length === 2 && allowed.includes("Yes") && allowed.includes("No")) {
    const folded = stripped.toLowerCase();
    for (const [canonical, variants] of Object.entries(contracts.mapping.boolean_aliases)) {
      if (variants.includes(folded)) return canonical;
    }
  }
  const matches = allowed.filter((item) => item.toLowerCase() === stripped.toLowerCase());
  if (matches.length === 1) return matches[0];
  throw new GovernanceInputError("INVALID_ENUM_VALUE", field, value, allowed, "Use one of the declared canonical values.");
}
function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}
async function sha256(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
}
function pretty(value) { return `${JSON.stringify(value, null, 2)}\n`; }

export async function normalizeCsv(text, sourceName = "inventory.csv") {
  const rawRows = parseCsv(text.replace(/^\uFEFF/, ""));
  if (rawRows.length < 2) throw new GovernanceInputError("EMPTY_INPUT", null, null, [], "Provide a header and at least one inventory record.");
  const headers = rawRows[0];
  if (new Set(headers).size !== headers.length) throw new GovernanceInputError("DUPLICATE_HEADER", null, null, [], "Make every source header unique.");
  const aliasMap = aliases();
  const ignored = new Set(contracts.mapping.legacy_ignored_columns.map(headerKey));
  const mapped = [], mappings = [], ignoredHeaders = [], unknown = [];
  for (const header of headers) {
    const target = aliasMap.get(headerKey(header));
    if (!target) {
      if (ignored.has(headerKey(header))) { mapped.push(null); ignoredHeaders.push(header); mappings.push(`${header}->IGNORED_LEGACY_NONCANONICAL`); }
      else unknown.push(header);
    } else { mapped.push(target); if (header !== target) mappings.push(`${header}->${target}`); }
  }
  if (unknown.length) throw new GovernanceInputError("UNKNOWN_COLUMN", unknown[0], null, canonicalFields(), "Remove the column or add an explicit reviewed alias to inventory-mapping.json.");
  const canonicalHeaders = mapped.filter(Boolean);
  if (new Set(canonicalHeaders).size !== canonicalHeaders.length) throw new GovernanceInputError("DUPLICATE_CANONICAL_COLUMN", null, null, [], "Remove source columns that map to the same canonical field.");
  const versionIndex = mapped.indexOf("schema_version");
  if (versionIndex >= 0) {
    const versions = [...new Set(rawRows.slice(1).map((row) => (row[versionIndex] || "").trim()))];
    if (versions.length !== 1 || versions[0] !== SCHEMA_VERSION) throw new GovernanceInputError("UNSUPPORTED_SCHEMA_VERSION", headers[versionIndex], versions.join(","), [SCHEMA_VERSION], "Use a supported canonical inventory schema version.");
  }
  const required = contracts.canonicalSchema.required.filter((field) => field !== "schema_version");
  const missing = required.filter((field) => !canonicalHeaders.includes(field));
  if (missing.length) throw new GovernanceInputError("MISSING_REQUIRED_COLUMN", null, null, missing, "Add every required canonical field or use the generated human template.");
  const records = rawRows.slice(1).map((values, rowOffset) => {
    if (values.length !== headers.length) throw new GovernanceInputError("ROW_WIDTH_MISMATCH", null, String(rowOffset + 2), headers, "Provide exactly one value for every header.");
    const source = Object.fromEntries(mapped.map((field, index) => [field, values[index]]).filter(([field]) => field));
    const record = { schema_version: SCHEMA_VERSION };
    for (const field of required) {
      const value = normalizeEnum(field, source[field]);
      if ((contracts.canonicalSchema.properties[field].minLength || 0) > 0 && !value) throw new GovernanceInputError("EMPTY_REQUIRED_VALUE", field, source[field], [], "Supply a non-empty value.");
      record[field] = value;
    }
    return record;
  }).sort((a, b) => a.system_id.localeCompare(b.system_id) || a.system_name.localeCompare(b.system_name));
  if (new Set(records.map((record) => record.system_id)).size !== records.length) throw new GovernanceInputError("DUPLICATE_SYSTEM_ID", "system_id", null, [], "Use one stable, unique system_id per record.");
  const humanLabels = new Set(Object.values(contracts.mapping.fields).map((definition) => definition.human_label));
  const format = headers.length === humanLabels.size && headers.every((header) => humanLabels.has(header)) ? "generated_human_csv" : (versionIndex >= 0 || headers.join("|") === canonicalFields().join("|")) ? "canonical_csv" : "legacy_csv";
  const warnings = versionIndex < 0 ? ["Source CSV did not declare schema_version; canonical v1 compatibility was applied."] : [];
  warnings.push(...ignoredHeaders.map((header) => `Known legacy column was not part of canonical governance meaning and was ignored: ${header}`));
  return { schema_version: SCHEMA_VERSION, normalization_version: NORMALIZATION_VERSION, source: { name: sourceName, sha256: await sha256(text), format }, mappings_applied: [...new Set(mappings)].sort(), warnings, records };
}

function riskTier(row) {
  const yes = (field) => row[field]?.trim().toLowerCase() === "yes";
  const impacts = ["impact_people", "impact_money", "impact_security", "impact_rights", "impact_safety"].map(yes);
  if (row.autonomy_level === "Full" && (yes("public_facing") || ["Regulated", "Critical"].includes(row.data_sensitivity) || impacts.some(Boolean))) return "Frontier";
  if (row.autonomy_level === "Full") return "Critical";
  if (yes("impact_safety") || yes("impact_security") || row.data_sensitivity === "Critical") return "Critical";
  if (impacts.some(Boolean) || ["Personal", "Regulated"].includes(row.data_sensitivity) || yes("public_facing")) return "High";
  if (row.autonomy_level === "Partial" || row.data_sensitivity === "Internal") return "Moderate";
  return "Low";
}
function conditionMatches(row, condition) {
  const value = String(row[condition.field] || "").trim();
  if (condition.operator === "blank") return value === "";
  if (condition.operator === "equals") return value === condition.value;
  if (condition.operator === "in") return condition.values.includes(value);
  if (condition.operator === "not_in") return !condition.values.includes(value);
  throw new Error(`Unsupported policy operator: ${condition.operator}`);
}
async function finding(rule, row) {
  const identity = { rule_id: rule.id, system_id: row.system_id, severity: rule.severity.toUpperCase(), message: rule.message };
  return { finding_id: `sha256:${await sha256(stable(identity))}`, rule_id: rule.id, system_id: row.system_id, system_name: row.system_name, severity: rule.severity.toUpperCase(), message: rule.message };
}
function gate(findings) {
  if (findings.some((item) => item.severity === "CRITICAL")) return "BLOCKED";
  if (findings.length) return "REVIEW_REQUIRED";
  return "PASSED_CURRENT_AUTOMATED_CHECKS";
}
function markdownDocuments(records, findings, tiers, result) {
  const list = findings.length ? findings.map((item) => `- [${item.rule_id}] ${item.system_name}: ${item.severity} — ${item.message}`).join("\n") : "No governance gaps found.";
  return {
    "executive-summary.md": `# AI Governance Decision Pack\n\nAutomated gate: **${result.governance_gate_state}**\n\nHuman decision: **PENDING**\n\nThis reference output is not approval, certification, or risk acceptance.\n`,
    "system-profile.md": `# System Profile\n\n${records.map((item) => `- ${item.system_name} (${item.system_id}) — preliminary risk: ${tiers[item.system_id]}`).join("\n")}\n`,
    "risk-and-findings.md": `# Risk and Findings\n\n${list}\n`,
    "action-plan.md": "# Action Plan\n\nA human reviewer must assess findings, evidence, ownership, monitoring, and shutdown readiness before any decision.\n",
    "decision-record.md": "# Decision Record\n\nDecision status: **PENDING HUMAN DECISION**\n\nNo automated result grants operational authority.\n",
    "evidence-and-ownership.md": `# Evidence and Ownership\n\n${records.map((item) => `- ${item.system_id}: owner ${item.owner || "MISSING"}; evidence ${item.evidence_complete}`).join("\n")}\n`,
  };
}

export async function evaluateCsv(text, { sourceName = "inventory.csv", evaluationTime = null, failOn = "none", targetRepository = "agentic-ai-governance" } = {}) {
  if (evaluationTime && !TIME_PATTERN.test(evaluationTime)) throw new GovernanceInputError("INVALID_EVALUATION_TIME", "evaluation_time", evaluationTime, ["YYYY-MM-DDTHH:MM:SSZ"], "Use a UTC timestamp such as 2026-08-29T12:00:00Z.");
  const normalized = await normalizeCsv(text, sourceName);
  const tiered = normalized.records.map((record) => ({ ...record, calculated_risk_tier: riskTier(record) }));
  const tiers = Object.fromEntries(tiered.map((record) => [record.system_id, record.calculated_risk_tier]));
  const findingsList = [];
  for (const row of tiered) for (const rule of contracts.policy.rules) if (rule.all.every((condition) => conditionMatches(row, condition))) findingsList.push(await finding(rule, row));
  findingsList.sort((a, b) => a.severity.localeCompare(b.severity) || a.system_id.localeCompare(b.system_id) || a.rule_id.localeCompare(b.rule_id));
  const findings = { schema_version: SCHEMA_VERSION, generator_version: GENERATOR_VERSION, policy_id: contracts.policy.policy_id, policy_version: contracts.policy.policy_version, input_digest: `sha256:${normalized.source.sha256}`, findings: findingsList };
  const result = { schema_version: SCHEMA_VERSION, generator_version: GENERATOR_VERSION, normalization_version: NORMALIZATION_VERSION, policy_id: contracts.policy.policy_id, policy_version: contracts.policy.policy_version, evaluation_time: evaluationTime, input_digest: `sha256:${normalized.source.sha256}`, validation_state: "VALID", governance_gate_state: gate(findingsList), human_decision_state: "PENDING_HUMAN_DECISION", blocking_threshold: failOn, finding_count: findingsList.length, system_ids: normalized.records.map((item) => item.system_id).sort() };
  const documents = markdownDocuments(normalized.records, findingsList, tiers, result);
  const generated_files = await Promise.all(Object.keys(documents).sort().map(async (path) => ({ path, sha256: await sha256(documents[path]) })));
  const machineSources = { "normalized-inventory.json": pretty(normalized), "governance-findings.json": pretty(findings), "governance-result.json": pretty(result) };
  const source_artifacts = await Promise.all(Object.keys(machineSources).map(async (path) => ({ path, role: path.replaceAll("-", " ").replace(".json", ""), sha256: await sha256(machineSources[path]) })));
  const canonicalDigest = `sha256:${await sha256(stable(normalized.records))}`;
  const manifest = { canonical_inventory_digest: canonicalDigest, decision_status: "pending_human_decision", evaluation_time: evaluationTime, generated_files, generator: "web/governance-engine.mjs", generator_version: GENERATOR_VERSION, governance_gate_result: result.governance_gate_state === "BLOCKED" ? "BLOCKED BY CRITICAL FINDINGS" : result.governance_gate_state === "REVIEW_REQUIRED" ? "HUMAN REVIEW REQUIRED" : "PASSED CURRENT AUTOMATED CHECKS", hash_mode: "sha256-text-lf", manifest_schema_version: SCHEMA_VERSION, normalization_version: NORMALIZATION_VERSION, policy_id: contracts.policy.policy_id, policy_version: contracts.policy.policy_version, schema_version: "1.0", source_artifacts, system_count: normalized.records.length, system_ids: result.system_ids };
  const manifestText = pretty(manifest);
  const decisionPackId = `sha256:${await sha256(pretty({ canonical_inventory_digest: canonicalDigest, evaluation_time: evaluationTime, policy_id: result.policy_id, policy_version: result.policy_version }))}`;
  const handoffId = `sha256:${await sha256(pretty({ decision_pack_id: decisionPackId, target_repository: targetRepository }))}`;
  const handoff = { schema_version: SCHEMA_VERSION, handoff_id: handoffId, source_repository: "global-ai-governance-toolkit", source_artifact_type: "AI_GOVERNANCE_DECISION_PACK_REFERENCE", decision_pack_id: decisionPackId, system_id: result.system_ids.length === 1 ? result.system_ids[0] : "multiple-systems", target_repository: targetRepository, artifact_digest: `sha256:${await sha256(manifestText)}`, evidence_refs: findingsList.map((item) => item.finding_id), authority_refs: [], authority_effect: "NONE", review_boundary: "Pending human review; this handoff grants no approval, authority, certification, or risk acceptance.", configuration_ref: null };
  return { normalized, tiers, findings, result, documents, manifest, handoff };
}

export { contracts, pretty };
