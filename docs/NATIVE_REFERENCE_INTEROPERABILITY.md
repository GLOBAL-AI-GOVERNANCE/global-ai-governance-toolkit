# Native Reference Interoperability

The Toolkit may compose references to governance artifacts owned by other GLOBAL-AI-GOVERNANCE repositories without copying or redefining their native semantics.

The reference object is intentionally small: source repository, native artifact type and identifier, schema version, subject identifier, exact artifact digest, reference-generation time, and `authority_effect: NONE`.

Supported native owners in this candidate are:

- Agentic AI Governance: Agent Trust Passport;
- Verified Vulnerability Governance: Governed Closure Receipt;
- AI Cyber Resilience Framework: Change Impact and Operating Disposition.

The adapter validates reference ownership, digest form, subject binding, duplicate references, and the non-authorizing boundary. It does **not** parse or reinterpret native status vocabularies, rerun native validation, claim current trust, convert closure into authorization, or convert resilience disposition into deployment approval.

Native repositories remain authoritative for their own schemas, validation logic, validity, revocation, closure, recovery, and operating-state semantics. Portfolio composition references those artifacts by digest and leaves consequential judgment to accountable human authority.

The included envelope fixture is synthetic and reference-only. It demonstrates deterministic composition, not real remediation, real deployment readiness, certification, compliance, or independent external validation.
