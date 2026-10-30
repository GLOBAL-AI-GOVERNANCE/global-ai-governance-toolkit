// Evaluation session state for the static browser workspace.
// Every new input gets a monotonically increasing token. Only the newest token may
// publish an output, so a slower earlier evaluation can never render or be downloaded
// after a newer input (valid, invalid, empty, or unreadable) has arrived.

export function createEvaluationSession() {
  let token = 0;
  let snapshot = { token: 0, sourceName: "", status: "empty", output: null, issue: null };
  return {
    begin(sourceName) {
      token += 1;
      snapshot = { token, sourceName: String(sourceName ?? ""), status: "pending", output: null, issue: null };
      return token;
    },
    isCurrent(candidate) { return candidate === token; },
    resolve(candidate, output) {
      if (candidate !== token) return false;
      snapshot = { ...snapshot, status: "ready", output, issue: null };
      return true;
    },
    reject(candidate, issue) {
      if (candidate !== token) return false;
      snapshot = { ...snapshot, status: "error", output: null, issue };
      return true;
    },
    canDownload(candidate) { return candidate === token && snapshot.status === "ready" && snapshot.output !== null; },
    get current() { return snapshot; },
  };
}

const MAX_LISTED = 6;

function listExpected(expected) {
  if (!Array.isArray(expected) || !expected.length) return "";
  const shown = expected.slice(0, MAX_LISTED).join(", ");
  return expected.length > MAX_LISTED ? `${shown}, and ${expected.length - MAX_LISTED} more` : shown;
}

// Field-specific guidance. Names the column and row when known. Never echoes cell
// content: supplied values are omitted except a row number for width mismatches.
export function describeInputError(issue) {
  if (!issue || typeof issue !== "object") return "BROWSER_RUNTIME_ERROR: The input could not be evaluated.";
  const where = [];
  if (issue.source_column) where.push(`column "${issue.source_column}"`);
  const row = issue.row ?? (issue.code === "ROW_WIDTH_MISMATCH" ? issue.supplied_value : null);
  if (row) where.push(`row ${row} (the header is row 1)`);
  const expected = listExpected(issue.expected);
  const expectedText = !expected ? "" :
    issue.code === "BINARY_INPUT" ? "" :
    issue.code === "UNKNOWN_COLUMN" ? ` Accepted columns include: ${expected}.` :
    issue.code === "MISSING_REQUIRED_COLUMN" ? ` Missing: ${expected}.` :
    issue.code === "ROW_WIDTH_MISMATCH" ? ` Expected ${issue.expected.length} values, one per header.` :
    ` Allowed values: ${expected}.`;
  return `${issue.code}${where.length ? ` in ${where.join(", ")}` : ""}: ${issue.remediation || "Check the input."}${expectedText}`;
}
