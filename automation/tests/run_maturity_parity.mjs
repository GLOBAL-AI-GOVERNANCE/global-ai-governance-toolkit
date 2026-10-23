import { readFileSync } from "node:fs";
import { evaluateMaturity } from "../../web/maturity/maturity-engine.mjs";

const [fixture, evaluationTime] = process.argv.slice(2);
const data = JSON.parse(readFileSync(fixture, "utf8"));
const evaluated = evaluateMaturity(data, evaluationTime || null);
process.stdout.write(JSON.stringify(evaluated.details));
