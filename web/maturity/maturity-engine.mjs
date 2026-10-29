import { MATURITY_CATALOG } from "./catalog.generated.mjs";

const PROFILE_ID = "organizational-ai-maturity-v0.1";
const VERSION = "0.1.0";
const LEVELS = ["BASIC", "READY", "DYNAMIC", "ADVANCED"];
const CARRY = ["ACCEPTED", "ACCEPTED_WITH_CONDITIONS"];
const OPEN = ["PENDING", "REJECTED", "RETURNED_FOR_REASSESSMENT"];
const MEANING = "evidence_supported_level repeats a human-determined level only when submitted evidence passes bounded checks. It is not an independent maturity determination.";

function parseTime(value) {
  if (!value || typeof value !== "string") return null;
  const text = value.endsWith("Z") ? `${value.slice(0, -1)}+00:00` : value;
  const parsed = Date.parse(text);
  return Number.isNaN(parsed) ? null : parsed;
}

function finding(code, severity, message, action) {
  return { id: `${PROFILE_ID}:${code}`, severity, message, action };
}

function catalogIndex() {
  const pillars = {};
  const categories = {};
  const ids = [];
  for (const pillar of MATURITY_CATALOG.pillars) {
    pillars[pillar.id] = pillar;
    for (const category of pillar.categories) {
      categories[category.id] = { ...category, pillar_id: pillar.id };
      ids.push(category.id);
    }
  }
  return { pillars, categories, ids };
}


function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asStringArray(value) {
  return Array.isArray(value) ? value : [];
}

/** Reject malformed assessments before import mutates UI state. Returns problem string or null. */
export function validateMaturityAssessment(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return "Import must be a JSON object exported from this page or a matching assessment.";
  }
  if (value.framework_id !== "unesco-ai-maturity-2025") {
    return "Import rejected: framework_id must be unesco-ai-maturity-2025.";
  }
  if (value.framework_version !== "2025") {
    return "Import rejected: framework_version must be 2025.";
  }
  if (value.authority_effect !== "NONE") {
    return "Import rejected: authority_effect must be NONE.";
  }
  if (!Array.isArray(value.categories)) {
    return "Import rejected: categories must be an array.";
  }
  const catalog = catalogIndex();
  const known = new Set(Object.keys(catalog.categories));
  for (const category of value.categories) {
    if (!isPlainObject(category)) return "Import rejected: each category must be an object.";
    if (!known.has(category.category_id)) return `Import rejected: unknown category_id ${category.category_id}.`;
    if (!category.pillar_id || typeof category.pillar_id !== "string") {
      return "Import rejected: each category needs pillar_id.";
    }
    if (catalog.categories[category.category_id].pillar_id !== category.pillar_id) {
      return `Import rejected: category_id ${category.category_id} does not belong to pillar_id ${category.pillar_id}.`;
    }
    if (category.evidence !== undefined) {
      if (!Array.isArray(category.evidence)) {
        return "Import rejected: evidence must be an array of evidence objects.";
      }
      for (const item of category.evidence) {
        if (!isPlainObject(item)) {
          return "Import rejected: each evidence entry must be a plain object (nested arrays are not allowed).";
        }
      }
    }
    if (category.human_determination !== undefined && category.human_determination !== null) {
      if (!isPlainObject(category.human_determination)) {
        return "Import rejected: human_determination must be an object when present.";
      }
      const conditions = category.human_determination.conditions;
      if (conditions !== undefined && !Array.isArray(conditions)) {
        return "Import rejected: human_determination.conditions must be an array when present.";
      }
    }
    for (const key of ["contradictions", "gaps", "corrective_actions", "reassessment_triggers", "material_change_events"]) {
      if (category[key] !== undefined && !Array.isArray(category[key])) {
        return `Import rejected: ${key} must be an array when present.`;
      }
    }
  }
  return null;
}

export function evaluateMaturity(data, evaluationTime) {
  const findings = [];
  const evidence = [];
  const catalog = catalogIndex();
  const evalDt = parseTime(evaluationTime);
  const details = {
    categories: [],
    overall_synthesis: "PENDING_HUMAN_SYNTHESIS",
    human_determination: "PENDING",
    authority_effect: "NONE",
    evidence_supported_level_meaning: MEANING,
    assessment_coverage: data.assessment_coverage,
    coverage_status: "INCOMPLETE",
    assessed_category_count: 0,
    framework_category_count: catalog.ids.length,
    missing_category_ids: catalog.ids.slice(),
  };
  if (data.authority_effect != null && data.authority_effect !== "NONE") {
    findings.push(finding("AUTHORITY_EFFECT", "CRITICAL", "Authority effect must remain NONE.", "Set authority_effect to NONE."));
  }
  if (data.framework_version !== "2025") {
    findings.push(finding("FRAMEWORK_VERSION", "CRITICAL", "Only framework version 2025 is supported by this adapter.", "Use the 2025 adapter."));
  }
  const coverage = data.assessment_coverage;
  if (coverage !== "PARTIAL" && coverage !== "FULL_FRAMEWORK") {
    findings.push(finding("ASSESSMENT_COVERAGE", "CRITICAL", "Assessment coverage must be PARTIAL or FULL_FRAMEWORK.", "Declare coverage. Partial coverage is not framework completion."));
  }
  const categories = Array.isArray(data.categories) ? data.categories : [];
  if (!categories.length) {
    findings.push(finding("CATEGORIES_MISSING", "CRITICAL", "At least one category assessment is required.", "Supply category records."));
    return { findings, evidence, details };
  }
  const seen = new Set();
  for (const cat of categories) {
    if (!cat || typeof cat !== "object" || Array.isArray(cat)) {
      findings.push(finding("CATEGORY_SHAPE", "CRITICAL", "Each category assessment must be an object.", "Supply a category object."));
      continue;
    }
    const result = evaluateCategory(cat, data, catalog, evalDt, findings, evidence, seen);
    if (result) details.categories.push(result);
  }
  const unique = [];
  for (const item of details.categories) {
    if (item.known && !unique.includes(item.category_id)) unique.push(item.category_id);
  }
  const missing = catalog.ids.filter((id) => !unique.includes(id));
  details.assessed_category_count = unique.length;
  details.missing_category_ids = missing;
  if (coverage === "FULL_FRAMEWORK" && missing.length) {
    details.coverage_status = "INCOMPLETE";
    findings.push(finding("COVERAGE_INCOMPLETE", "CRITICAL", "Full-framework coverage is missing one or more official categories.", "Submit every official category once, or declare PARTIAL coverage."));
  } else if (coverage === "FULL_FRAMEWORK") details.coverage_status = "COMPLETE";
  else if (coverage === "PARTIAL") details.coverage_status = "PARTIAL";
  return { findings, evidence, details };
}

function evaluateCategory(cat, data, catalog, evalDt, findings, evidence, seen) {
  const pillar = catalog.pillars[cat.pillar_id];
  const category = catalog.categories[cat.category_id];
  if (!pillar) {
    findings.push(finding("UNKNOWN_PILLAR", "CRITICAL", "Pillar is not in the framework catalog.", "Use a pillar identifier from the adapter catalog."));
    return null;
  }
  if (!category) {
    findings.push(finding("UNKNOWN_CATEGORY", "CRITICAL", "Category is not in the framework catalog.", "Use a category identifier from the adapter catalog."));
    return null;
  }
  if (category.pillar_id !== cat.pillar_id) {
    findings.push(finding("CATEGORY_PILLAR_MISMATCH", "CRITICAL", "Category does not belong to the submitted pillar.", "Submit the category under its catalog pillar."));
    return null;
  }
  if (seen.has(cat.category_id)) {
    findings.push(finding("DUPLICATE_CATEGORY", "CRITICAL", "Category is repeated in this assessment.", "Submit each official category at most once."));
    return null;
  }
  seen.add(cat.category_id);
  const human = isPlainObject(cat.human_determination) ? cat.human_determination : null;
  const humanStatus = human ? human.status : null;
  const humanLevel = human ? human.level : null;
  const established = CARRY.includes(humanStatus) && LEVELS.includes(humanLevel);
  const conditionList = human && Array.isArray(human.conditions) ? [...human.conditions] : [];
  const result = {
    known: true,
    pillar_id: cat.pillar_id,
    pillar: pillar.label,
    category_id: cat.category_id,
    category: category.label,
    claimed_level: cat.claimed_level,
    target_level: cat.target_level,
    human_determination_status: humanStatus,
    human_determined_level: established ? humanLevel : null,
    conditions: humanStatus === "ACCEPTED_WITH_CONDITIONS" ? conditionList : [],
    evidence_supported_level: null,
    level_support_state: "NOT_DETERMINED",
    support_status: "UNSUPPORTED",
    freshness_status: "CURRENT",
    assessment_state: "CURRENT",
    confidence: "LOW",
    contradictions: asStringArray(cat.contradictions),
    gaps: asStringArray(cat.gaps),
    corrective_actions: asStringArray(cat.corrective_actions),
    reassessment_triggers: asStringArray(cat.reassessment_triggers),
    material_change_events: asStringArray(cat.material_change_events),
  };
  if (!LEVELS.includes(cat.claimed_level)) {
    findings.push(finding("INVALID_LEVEL", "CRITICAL", "Claimed level must be BASIC, READY, DYNAMIC, or ADVANCED.", "Use only the four source vocabulary levels."));
  }
  if (human) {
    if (![...CARRY, ...OPEN].includes(humanStatus)) {
      findings.push(finding("HUMAN_DETERMINATION", "CRITICAL", "Human determination status is not recognized.", "Use a defined determination status."));
    }
    if (parseTime(human.determined_at) == null) {
      findings.push(finding("HUMAN_DETERMINATION", "CRITICAL", "Human determination time must be an RFC3339 timestamp.", "Supply a timestamp with Z or an explicit offset."));
    }
    if (!human.accountable_role) {
      findings.push(finding("HUMAN_DETERMINATION", "CRITICAL", "Human determination requires an accountable role.", "Name the accountable function, not a person."));
    }
  }
  if (cat.evidence != null && !Array.isArray(cat.evidence)) {
    findings.push(finding("EVIDENCE_SHAPE", "CRITICAL", "Evidence must be an array of evidence objects.", "Submit evidence as a JSON array."));
  }
  const evs = Array.isArray(cat.evidence) ? cat.evidence : [];
  let hasOperating = false;
  let hasRepresentative = false;
  let hasPolicy = false;
  let hasPilot = false;
  let syntheticOnly = evs.length > 0;
  let scopeMismatch = false;
  let stale = false;
  let integrityFail = false;
  for (const ev of evs) {
    if (!isPlainObject(ev)) continue;
    if (ev.reference) evidence.push({ type: "URI", reference: ev.reference, sha256: ev.sha256 });
    if (ev.evidence_class !== "SYNTHETIC") syntheticOnly = false;
    if (ev.evidence_class === "OPERATING") {
      hasOperating = true;
      if (ev.is_representative === true) hasRepresentative = true;
    } else if (ev.evidence_class === "POLICY") hasPolicy = true;
    else if (ev.evidence_class === "PILOT") hasPilot = true;
    else if (ev.evidence_class === "SYNTHETIC") {
      findings.push(finding("SYNTHETIC_MISUSE", "HIGH", "Synthetic evidence cannot prove operating practice.", "Label synthetic evidence and do not treat it as operational proof."));
    }
    if (ev.scope && ev.scope !== data.assessment_scope) {
      scopeMismatch = true;
      findings.push(finding("SCOPE_MISMATCH", "HIGH", "Evidence scope does not match the assessment scope.", "Evidence must cover the submitted scope."));
    }
    const validThrough = parseTime(ev.valid_through);
    if (validThrough != null && evalDt != null && validThrough < evalDt) {
      stale = true;
      findings.push(finding("STALE", "HIGH", "Evidence is past its validity time.", "Reassess. Stale evidence is not current."));
    } else if (ev.valid_through && validThrough == null) {
      findings.push(finding("INVALID_TIME", "CRITICAL", "Evidence validity time is not a usable timestamp.", "Use RFC3339 with Z or an explicit offset."));
    }
    if (ev.integrity_asserted && !ev.sha256) {
      integrityFail = true;
      findings.push(finding("INTEGRITY_FAIL", "HIGH", "Integrity was asserted without a digest.", "Supply sha256 or remove the integrity assertion."));
    }
  }
  if (result.contradictions.length) {
    result.support_status = "CONTRADICTED";
    findings.push(finding("CONTRADICTED", "HIGH", "Contradictory evidence is present and is not averaged away.", "Resolve contradictions before treating the determination as supported."));
  } else if (!evs.length) {
    result.support_status = "UNSUPPORTED";
    findings.push(finding("MISSING_EVIDENCE", "HIGH", "No evidence was submitted for this category.", "Supply evidence before carrying a maturity determination."));
  } else if (scopeMismatch || integrityFail || syntheticOnly) result.support_status = "UNSUPPORTED";
  else if (hasPolicy && !hasOperating && ["DYNAMIC", "ADVANCED"].includes(cat.claimed_level)) {
    result.support_status = "PARTIAL";
    findings.push(finding("POLICY_ONLY_OVERCLAIM", "HIGH", "A policy record alone does not support a Dynamic or Advanced position.", "Supply representative operating evidence."));
  } else if (hasPilot && !hasRepresentative) {
    result.support_status = "PARTIAL";
    findings.push(finding("PILOT_AS_ENTERPRISE", "HIGH", "Pilot evidence does not establish organization-wide practice.", "Supply representative operating evidence for that scope."));
  } else if (hasOperating && !hasRepresentative) {
    result.support_status = "PARTIAL";
    findings.push(finding("NON_REPRESENTATIVE", "MEDIUM", "Operating evidence is not marked representative.", "State whether the evidence represents typical practice."));
  } else if (hasOperating && hasRepresentative && !scopeMismatch && !integrityFail) {
    result.support_status = "SUPPORTED";
    result.confidence = "MEDIUM";
  } else result.support_status = "UNSUPPORTED";
  if (stale) {
    result.freshness_status = "STALE";
    result.assessment_state = "REASSESSMENT_REQUIRED";
  }
  if (result.material_change_events.length) {
    result.assessment_state = "REASSESSMENT_REQUIRED";
    findings.push(finding("REASSESSMENT_REQUIRED", "MEDIUM", "An observed material-change event requires reassessment.", "Reassess before treating the prior determination as current."));
  }
  if (cat.organization_defined_critical && !cat.critical_rationale) {
    findings.push(finding("CRITICAL_RATIONALE", "MEDIUM", "An organization-defined critical category needs a rationale.", "Record the organization's own reason."));
  }
  const blocked = result.support_status !== "SUPPORTED" || result.freshness_status !== "CURRENT" || result.assessment_state !== "CURRENT" || result.contradictions.length > 0;
  if (result.contradictions.length) result.level_support_state = "EVIDENCE_CONTRADICTED";
  else if (stale) result.level_support_state = "EVIDENCE_STALE";
  else if (blocked || OPEN.includes(humanStatus) || human == null) result.level_support_state = OPEN.includes(humanStatus) || human == null ? "NOT_DETERMINED" : "EVIDENCE_INSUFFICIENT";
  else if (established && !blocked) {
    result.level_support_state = "HUMAN_DETERMINATION_SUPPORTED";
    result.evidence_supported_level = humanLevel;
  } else result.level_support_state = "EVIDENCE_INSUFFICIENT";
  result.authority_effect = "NONE";
  return result;
}

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

async function sha256(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return `sha256:${[...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("")}`;
}

export async function buildProfileResult(data, evaluationTime) {
  const evaluated = evaluateMaturity(data, evaluationTime);
  const ordered = [...new Map(evaluated.findings.map((item) => [item.id, item])).values()].sort((a, b) => a.id.localeCompare(b.id));
  const status = ordered.some((item) => item.severity === "CRITICAL") ? "FAIL" : ordered.length ? "CONDITIONAL" : "PASS";
  const summaries = {
    PASS: "Submitted profile passed its bounded structural and integrity checks.",
    CONDITIONAL: "Submitted profile requires the listed accountable follow-up actions.",
    FAIL: "Submitted profile failed one or more fail-closed checks.",
  };
  const raw = `${JSON.stringify(data)}\n`;
  return {
    schema_version: "1.0.0",
    profile_id: PROFILE_ID,
    profile_version: VERSION,
    source_artifact_sha256: await sha256(raw),
    decision_pack_manifest: null,
    authority_effect: "NONE",
    evaluation_time: evaluationTime,
    status,
    summary: summaries[status],
    findings: ordered,
    evidence_references: evaluated.evidence.filter((item) => item.reference).sort((a, b) => `${a.type}${a.reference}`.localeCompare(`${b.type}${b.reference}`)),
    details: evaluated.details,
    canonical_details: canonical(evaluated.details),
  };
}

export const LEVEL_LABELS = LEVELS;
export { MATURITY_CATALOG };
