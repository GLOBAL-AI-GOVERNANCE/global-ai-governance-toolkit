# Compute Assurance Ladder

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Principle

Compute decisions are made on **assurance**: the mechanism that backs the guarantee that data will not be retained, exposed, or misused. Assurance is either **structural** (physical or technical isolation — the stronger form) or **contractual** (a promise). Match every workload to the strongest rung it needs; never assume one rung fits all workloads.

## The Ladder

| Level | Name | Assurance type | Description | Suitable workloads |
|---|---|---|---|---|
| `tier1_owned` | Owned Hardware | Structural | Air-gapped or self-hosted infrastructure on hardware the organization owns. The boundary is physical. | Classified-equivalent work, trade secrets, core institutional knowledge (S4). |
| `tier2_attested` | Attested Compute | Structural | Rented compute with confidential computing and hardware attestation: cryptographic proof the workload executed inside an isolated enclave the host cannot inspect. | Sensitive workflows where owning hardware is impractical (S3–S4). |
| `tier3_zdr_cloud` | ZDR Cloud | Contractual | Closed frontier model under a confirmed zero-data-retention agreement. Assurance rests on the contract, not isolation. | Day-to-day sensitive tasks needing frontier capability (S2–S3). |
| `tier4_standard` | Standard Third-Party | Contractual (weakest) | Consumer or default API access without ZDR. Treat everything sent as observed. | Public or low-signal information only (S0–S1). |

## Attestation flow (tier 2)

1. The organization encrypts the workload to the target enclave's public key and dispatches it.
2. The workload executes in silicon-isolated memory; the host OS, hypervisor, and operators cannot inspect it.
3. The hardware root of trust signs an attestation quote binding the measurement to this run.
4. The organization verifies the signature chain. Structural assurance achieved.

## Hardware adaptability rule

Owned compute should favor generally programmable architectures over chips narrowly optimized for one model architecture. Model architectures shift; hardware that only serves today's architecture becomes a stranded asset. Adaptability is itself a sovereignty control.

## Hard rule enforced by automation

Gate `G10`: any S4 workload on `tier3_zdr_cloud` or `tier4_standard` fails the sovereignty check. Sovereign workloads require structural assurance. Contracts are not isolation.
