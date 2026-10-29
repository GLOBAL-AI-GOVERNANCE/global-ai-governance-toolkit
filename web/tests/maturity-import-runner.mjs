import { pathToFileURL } from "node:url";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { evaluateMaturity, validateMaturityAssessment } = await import(
  pathToFileURL(path.join(root, "maturity/maturity-engine.mjs")).href
);

const base = {
  framework_id: "unesco-ai-maturity-2025",
  framework_version: "2025",
  assessment_id: "t",
  assessment_scope: "scope",
  assessment_coverage: "PARTIAL",
  accountable_owner: "owner",
  authority_effect: "NONE",
};

const goodCat = {
  pillar_id: "ai-governance-ethics-risk",
  category_id: "ai-governance-ethics-risk.ai-governance-framework",
  claimed_level: "READY",
  target_level: "DYNAMIC",
  human_determination: {
    level: "READY",
    status: "ACCEPTED",
    accountable_role: "assurance-function",
    determined_at: "2026-09-01T00:00:00Z",
  },
  evidence: [{ reference: "synthetic://ok", evidence_class: "OPERATING", scope: "scope", is_representative: true }],
};

const failures = [];
const cases = [
  ["evidence_object", { ...base, categories: [{ ...goodCat, evidence: { reference: "x", evidence_class: "OPERATING" } }] }, "evidence must be an array"],
  ["evidence_nested_array", { ...base, categories: [{ ...goodCat, evidence: [[{ reference: "x", evidence_class: "OPERATING" }]] }] }, "plain object"],
  ["pillar_mismatch", { ...base, categories: [{ ...goodCat, pillar_id: "ai-capacity-building" }] }, "does not belong to pillar_id"],
  ["human_string", { ...base, categories: [{ ...goodCat, human_determination: "READY" }] }, "human_determination must be an object"],
  ["conditions_object", { ...base, categories: [{ ...goodCat, human_determination: { ...goodCat.human_determination, status: "ACCEPTED_WITH_CONDITIONS", conditions: { a: 1 } } }] }, "conditions must be an array"],
  ["contradictions_object", { ...base, categories: [{ ...goodCat, contradictions: { x: 1 } }] }, "contradictions must be an array"],
  ["gaps_object", { ...base, categories: [{ ...goodCat, gaps: { x: 1 } }] }, "gaps must be an array"],
  ["corrective_object", { ...base, categories: [{ ...goodCat, corrective_actions: { action: "x" } }] }, "corrective_actions must be an array"],
];

for (const [name, payload, needle] of cases) {
  const problem = validateMaturityAssessment(payload);
  if (!problem) failures.push(`${name}: expected rejection, got null`);
  else if (!problem.toLowerCase().includes(needle.toLowerCase()) && !problem.includes(needle)) {
    failures.push(`${name}: expected message containing ${JSON.stringify(needle)}, got ${JSON.stringify(problem)}`);
  }
  try {
    evaluateMaturity(payload, "2026-10-29T12:00:00Z");
  } catch (error) {
    failures.push(`${name}: engine threw ${error.name}: ${error.message}`);
  }
}

const ok = validateMaturityAssessment({ ...base, categories: [goodCat] });
if (ok) failures.push(`valid sample rejected: ${ok}`);

if (failures.length) {
  console.error(JSON.stringify({ ok: false, failures }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, cases: cases.length }));
