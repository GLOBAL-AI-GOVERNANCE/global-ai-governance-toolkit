// Unit-level checks of the browser evaluation state logic (no DOM). Emits JSON for automation/tests.
import fs from "node:fs";
import { createEvaluationSession, describeInputError } from "../evaluation-session.mjs";
import { evaluateCsv, GovernanceInputError } from "../governance-engine.mjs";

const valid = fs.readFileSync(process.argv[2], "utf8");
const evaluationTime = process.argv[3];
const results = {};
const deferred = () => { let resolve; const promise = new Promise((r) => { resolve = r; }); return { promise, resolve }; };

// valid -> invalid -> valid
{
  const s = createEvaluationSession();
  const t1 = s.begin("first.csv");
  s.resolve(t1, await evaluateCsv(valid, { sourceName: "first.csv", evaluationTime }));
  const readyAfterValid = s.current.status === "ready" && s.canDownload(t1);
  const t2 = s.begin("bad.csv");
  const pendingClearsOutput = s.current.output === null && s.current.sourceName === "bad.csv" && !s.canDownload(t1);
  let issue = null; try { await evaluateCsv("foo,bar\n1,2\n", { sourceName: "bad.csv", evaluationTime }); } catch (e) { issue = e.issue; }
  s.reject(t2, issue);
  const errorState = s.current.status === "error" && s.current.output === null && !s.canDownload(t1) && !s.canDownload(t2);
  const t3 = s.begin("second.csv");
  s.resolve(t3, await evaluateCsv(valid, { sourceName: "second.csv", evaluationTime }));
  results.validInvalidValid = { readyAfterValid, pendingClearsOutput, errorState, recovered: s.current.status === "ready" && s.current.output.normalized.source.name === "second.csv" && s.canDownload(t3) && !s.canDownload(t1) };
}
// rapid changes: slow first result arrives after the newer input
{
  const s = createEvaluationSession();
  const slow = deferred(); const fast = deferred();
  const tA = s.begin("a.csv"); const pa = slow.promise.then((o) => s.resolve(tA, o));
  const tB = s.begin("b.csv"); const pb = fast.promise.then((o) => s.resolve(tB, o));
  fast.resolve({ marker: "b" }); await pb; slow.resolve({ marker: "a" }); const staleAccepted = await pa;
  const tC = s.begin("c.csv"); const staleError = s.reject(tB, { code: "X" });
  results.rapid = { staleAccepted, newestKept: s.current.sourceName === "c.csv" && s.current.status === "pending", staleErrorAccepted: staleError, oldTokenCanDownload: s.canDownload(tB) || s.canDownload(tA) };
}
// mismatched filename: output source always equals the session source
{
  const s = createEvaluationSession();
  const t = s.begin("named.csv"); s.resolve(t, await evaluateCsv(valid, { sourceName: "named.csv", evaluationTime }));
  results.filename = { session: s.current.sourceName, output: s.current.output.normalized.source.name };
}
// field-specific guidance; no cell content echoed
const errorFor = async (csv) => { try { await evaluateCsv(csv, { sourceName: "x.csv", evaluationTime }); return null; } catch (e) { return e instanceof GovernanceInputError ? e.issue : { code: "OTHER" }; } };
const header = valid.split(/\r?\n/)[0];
const firstRow = valid.split(/\r?\n/)[1].split(",");
const autonomyIndex = header.split(",").indexOf("autonomy_level");
const badEnumRow = [...firstRow]; badEnumRow[autonomyIndex] = "SECRET-CELL-VALUE";
const enumIssue = await errorFor(`${header}\n${firstRow.join(",")}\n${badEnumRow.join(",").replace(firstRow[0], "OTHER-ID")}\n`);
const unknownIssue = await errorFor(`${header},extra_col\n${firstRow.join(",")},1\n`);
const widthIssue = await errorFor(`${header}\n${firstRow.slice(0, 3).join(",")}\n`);
results.messages = {
  enum: describeInputError(enumIssue), enumRow: enumIssue?.row, unknown: describeInputError(unknownIssue), width: describeInputError(widthIssue),
  empty: describeInputError(await errorFor("")), runtime: describeInputError(null),
};
process.stdout.write(JSON.stringify(results));
