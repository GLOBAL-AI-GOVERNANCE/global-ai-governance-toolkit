import fs from "node:fs";
import { evaluateCsv } from "../governance-engine.mjs";

const [path, evaluationTime = ""] = process.argv.slice(2);
const output = await evaluateCsv(fs.readFileSync(path, "utf8"), { sourceName: path.split(/[\\/]/).pop(), evaluationTime: evaluationTime || null });
process.stdout.write(JSON.stringify(output));
