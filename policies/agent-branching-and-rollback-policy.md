# Agent Branching and Rollback Policy

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Policy Statement

No AI agent may take autonomous action against production systems, production data, or the organization's live digital-twin/ontology unless the action is reversible. Reversibility is achieved through branching: forking state, acting inside the isolated branch, validating, and only then promoting or discarding.

## Rationale

Without reversibility, an organization faces a false choice: forbid agents from touching anything real (losing the value of automation) or accept unbounded risk (losing control). Branching removes the dilemma. Reversible actions can be granted a wider action surface precisely because the cost of a mistake is bounded. Control, implemented this way, increases freedom rather than restricting it.

## Requirements

1. **Branch before commit.** Agent actions on production-relevant state execute in an isolated branch or sandbox. Production remains untouched until validation passes.
2. **Validation gate.** Every branch is validated — automated checks, and human review at the thresholds defined by the workload's sensitivity tier — before promotion.
3. **Two safe outcomes.** Promote or discard. Both must leave production consistent. A branch that cannot be cleanly discarded is a design defect and blocks deployment.
4. **Rollback for the promoted path.** Even promoted changes retain a rollback path for a defined window.
5. **Scope binding.** The branch inherits the agent's granular permissions; branching is not a permission bypass.
6. **Logging.** Fork, actions-in-branch, validation results, and promote/discard decisions are written to the append-only audit log.
7. **Organizational branching (advanced).** Where the organization maintains a digital twin, entire candidate workflows or operating models may be trialed in a branched twin and compared against the status quo before adoption.

## Enforcement

- Gate `G07` (sovereignty check) blocks any system with autonomous actions and no rollback/branching path.
- Gate `G05` blocks agent tool access without granular permissions.
- Gate `G06` blocks S2+ production agents without audit logging.

## Operating Rule

> No rollback path, no autonomous action.
