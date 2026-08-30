import fs from "node:fs";
import { evaluateCsv } from "../governance-engine.mjs";
import { findingGuidance } from "../finding-guidance.mjs";

const fixture = process.argv[2];
const evaluationTime = process.argv[3];
const output = await evaluateCsv(fs.readFileSync(fixture, "utf8"), {
  sourceName: fixture.split(/[\\/]/).pop(),
  evaluationTime,
  failOn: "none",
});
process.stdout.write(JSON.stringify({
  findingGuidance,
  findings: output.findings.findings,
  result: output.result,
  handoff: output.handoff,
  manifest: output.manifest,
}));
