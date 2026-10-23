# Local AI & Device Assurance — Device Capability & Trust Record (DCTR)

**Record ID:** GAIG-LOCAL-AI-ASSURANCE-2026-10-19-001  
**Status:** Engineering proposal / not yet implemented  
**Proposed path:** `enterprise/sovereignty/local-ai-device-assurance.md`  
**Review boundary:** Reference design only. `authority_effect: NONE`.  
**Simulation package:** GAIG-SIM-LOCAL-AI-2026-10-19-001 (48/48 synthetic tests PASS; IMPLEMENTATION WAIT; RELEASE NOT VERIFIED)

## 1. Executive decision

Extend the existing Global AI Governance sovereignty and assurance architecture to assess local, private-server, and cloud AI deployments against six separately reported dimensions:

1. Capability  
2. Efficiency  
3. Reliability  
4. Privacy  
5. Authority  
6. Economics  

Do not create a new repository or duplicate the existing model-routing, compute-assurance, Decision Pack, or mission-assurance systems. Do not create a composite "intelligence score." Preserve each dimension's evidence, limits, and disposition independently.

The first implementation should be an optional, non-authorizing toolkit profile. It must not be advertised as part of a published release until its schema, evaluator, fixtures, tests, interface, and release notes have been reviewed and validated.

## 2. Why this belongs in the existing portfolio

The current portfolio already provides the principal architecture:

- **Global AI Governance Toolkit:** inventory normalization, policy-driven findings, Decision Packs, sovereignty assessment, and optional profiles.
- **AI Governance Foundations (`ai-governance-os`):** reusable doctrine and reference structures.
- **Agentic AI Governance:** experimental Agent Trust Passport, authority, evidence, expiry, and revocation artifacts.
- **AI Governance MCP:** read-only, non-authorizing integration surface for released reference tooling.
- **Global AI Assurance Envelope:** reference-only cross-repository evidence handoff.
- **Mission-assurance profile on toolkit `main`:** experimental staged review with configuration binding, evidence references, blocking unknowns, material-change handling, and human-decision requirements.

The existing sovereignty decision tree already routes workloads according to sensitivity, capability, cost, and control; favors deterministic software when inference is unnecessary; and requires structural assurance for S4 workloads. This proposal should operationalize those principles for real device and model deployments, not restate them as a competing policy engine.

### Repository boundary

This proposal does not make AgentReady a dependency of Global AI Governance. A future AgentReady-generated device record may be consumed as an external evidence reference, but the governance toolkit must remain independently understandable and testable.

The device record is not an Agent Trust Passport. A device assessment describes a machine and a specific configuration; an agent passport describes an agent's bounded authority semantics. These subjects, issuers, and meanings must not be conflated.

## 3. Refreshed preflight note (2026-10-23)

At the time of this documentation PR the live `main` HEAD was `faaf491efa804eab6b42550c26933af3132659c3` ("Publish Global AI Governance Toolkit v2.5.3"). The original simulation package was built against an earlier snapshot (`7d3ee4ecb8c44875372f7a3079bf152d3943e054`). All claims remain bounded to the simulation; no production profile exists yet.

## 4. Proposed capability: Local AI & Device Assurance

### 4.1 Assessment question

How much verified, task-relevant work can this deployment deliver under its actual hardware, energy, time, cost, privacy, reliability, and risk constraints?

The assessment should help an accountable human choose among:

- deterministic software without model inference;
- a local model on the endpoint;
- a model hosted on owned or private infrastructure;
- attested compute where appropriate;
- an external model route permitted by the workload's data class and verified provider controls; or
- no deployment until blocking gaps are resolved.

A model fitting in memory is not evidence that it performs acceptably. A benchmark score is not evidence of general intelligence. A successful test is not deployment authorization.

### 4.2 Six independent dimensions

| Dimension    | Required evidence examples                                      | Key limitations |
|--------------|-----------------------------------------------------------------|-----------------|
| **Capability** | Named task suite and version; representative inputs; expected outputs; task-level success criteria; evaluator identity/method | Selected benchmark performance does not prove general capability or future performance. |
| **Efficiency** | Latency distribution; throughput where relevant; peak memory; CPU/GPU utilization; energy measurement when available; context size; test hardware | Nominal weight size or successful model loading does not establish useful speed, energy efficiency, or total memory fit. |
| **Reliability** | Repeated-run results; failure classes; deterministic checks where applicable; recovery and rollback evidence; known failure modes | A finite test set cannot establish universal reliability. |
| **Privacy** | Data class; local/private/cloud route; network and egress evidence; retention/training terms where applicable; encryption and access-control evidence | A provider statement or a local-only design claim is not by itself proof of all runtime behavior. |
| **Authority** | Principal and accountable owner; exact tool allow-list; read/write scope; approval gates; credential boundary; action logs; revocation and shutdown path | Model capability never grants authority. Read-only tools remain read-only; reference results never become permission. |
| **Economics** | Hardware acquisition/depreciation; inference and hosting cost; energy; maintenance; human review time; cost per successful task | Report assumptions and uncertainty. Do not imply that local execution is always cheaper. |

Do not collapse these dimensions into one weighted score. A high capability or low cost must not compensate for a critical privacy, authority, recovery, or reliability failure.

### 4.3 Proposed Device Capability & Trust Record

Use **Device Capability & Trust Record (DCTR)** as the working name. Avoid "passport" until reviewed because Agentic AI Governance already uses Agent Trust Passport for a different semantic object.

A DCTR is a versioned, configuration-bound, non-authorizing evidence record. It is not a credential, certification, proof of safety, or grant of permission.

## 5. Simulation results (bounded)

A deterministic, standard-library-only Python simulation of the candidate rules was exercised:

- 48/48 unit tests PASS
- 8 named end-to-end scenarios exercised (baseline PASS, S4-to-cloud-ZDR SAFE STOP, stale efficiency WAIT, authority elevation SAFE STOP, deterministic path PASS, material change WAIT, revoked agent SAFE STOP, low capability WAIT)
- Every output carries `authority_effect: NONE`
- No GitHub mutations were performed by the simulation
- No physical device, real model, or provider was tested

**Disposition:** SIMULATION PASS · IMPLEMENTATION WAIT · RELEASE NOT VERIFIED

## 6. Required boundaries

- No new repository.
- No direct write to `main`.
- No release-interface changes in the first documentation-only PR.
- No MCP exposure until a reviewed implementation is pinned to a verified release/commit and deliberately added to the MCP contract.
- No modification of Agent Trust Passport semantics.
- No claim that a device record is a credential, certification, authorization, or proof of safety.
- Keep all cross-repository handoffs reference-only with `authority_effect: NONE`.

## 7. Recommended next steps

1. Review this design.
2. After review, implement the candidate profile on a separately scoped branch using the existing Profile Result, registry, validator, Decision Pack, and test patterns.
3. Run the real repository validator, profile tests, full regression suite, CLI tests, and relevant workflow CI.
4. Keep the profile out of published machine-interface discovery and MCP until release review and human authorization.

---

*This document is a reference design only. It does not authorize any deployment, certify any device, or alter the authority boundary of the toolkit.*
