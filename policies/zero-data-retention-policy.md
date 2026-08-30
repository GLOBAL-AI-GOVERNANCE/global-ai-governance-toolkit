# Zero Data Retention Policy

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Policy Statement

No sensitive institutional data (tier S2 or above) may be sent to an external AI model provider unless one of the following holds:

1. A confirmed zero-data-retention (ZDR) agreement is in force with that provider, verified through the ZDR Vendor Review Gate; or
2. The workload runs under structural assurance (owned or attested compute) such that the provider cannot retain the data.

## Requirements

1. **Per-provider verification.** ZDR is negotiated and verified per provider. A ZDR agreement with one vendor confers nothing about another.
2. **Full-scope coverage.** Protection must cover prompts, outputs, uploaded content, and — explicitly reviewed — derived metadata such as classifier outputs, monitoring logs, and telemetry. Content-only language is an open gap until the metadata question is answered in writing.
3. **No training.** Training or model improvement using institutional or customer data must be contractually prohibited.
4. **No routine human review.** Provider personnel must not have routine access to the organization's interactions.
5. **Change control.** Provider retention terms may not be weakened without notice; any change triggers re-review.
6. **Leverage preservation.** The organization maintains model liquidity (see Model Liquidity Policy) so that ZDR commitments remain enforceable in practice: a provider that degrades terms can credibly be replaced.
7. **Personal accounts prohibited.** Employees must not process S1+ institutional data through personal or unmanaged AI accounts, which carry no organizational protections at all.

## Default Posture

Any external model used without confirmed ZDR is treated as extraction-risk. The organization assumes data sent to it may be retained, reviewed, or used in training, and classifies the workload accordingly (S0–S1 data only).

## Enforcement

- Gate `G03` (sovereignty check) blocks S2+ deployments without ZDR or structural assurance.
- Gate `G04` blocks S2+ deployments without a written training prohibition.
- Advisory `A01` flags unreviewed metadata retention as sovereignty debt.
- Every review recorded in `templates/ai-vendor-zdr-review-record.md`.

## Review Cycle

Annually per provider; immediately on provider terms changes, incidents, or material workload changes.
