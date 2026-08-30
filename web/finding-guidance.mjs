export const findingGuidance = Object.freeze({
  "GAI-AUTO-001": Object.freeze({
    title: "Named owner missing",
    meaning: "No accountable human owner has been supplied for this AI system.",
    next: "Name a human owner who can answer for the system before operation is approved.",
  }),
  "GAI-AUTO-002": Object.freeze({
    title: "Active monitoring missing",
    meaning: "The inventory says this AI system is not being actively monitored.",
    next: "Define and activate monitoring before an accountable human approves operation.",
  }),
  "GAI-AUTO-003": Object.freeze({
    title: "Shutdown path missing",
    meaning: "No documented way to stop this AI system has been supplied.",
    next: "Document and test a shutdown method before an accountable human approves operation.",
  }),
  "GAI-AUTO-004": Object.freeze({
    title: "High-impact evidence incomplete",
    meaning: "The inventory marks this as a high-impact system but does not show complete supporting evidence.",
    next: "Complete and review the evidence package before an accountable human makes a decision.",
  }),
  "GAI-AUTO-005": Object.freeze({
    title: "Full autonomy needs higher review",
    meaning: "The system is marked fully autonomous without the Critical or Frontier review level required by this policy.",
    next: "Escalate the review classification and keep the system under human control until review is complete.",
  }),
});

export function guidanceFor(ruleId) {
  return findingGuidance[ruleId] || Object.freeze({
    title: "Governance finding",
    meaning: "The current policy identified a condition that needs human review.",
    next: "Review the technical finding and resolve it before an accountable human makes a decision.",
  });
}
