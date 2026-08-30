# ZDR Vendor Review Gate

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Purpose

Before any S2+ workload sends data to an external model provider, the organization confirms zero-data-retention (ZDR) protection or routes the workload to structural assurance instead. This gate is pass/fail. A workload that fails the gate does not launch; it is redesigned, re-routed, or its data class is downgraded.

## Definition

ZDR, for the purposes of this gate, means the provider retains none of the organization's prompts, outputs, or telemetry beyond the ephemeral processing needed to serve the request, such that:

1. Content is not persisted to storage.
2. Content is not used to train or improve models.
3. Content is not available for routine human review.

## Why contractual language alone is not the gate

A promise not to misuse retained data is weaker than never retaining the data. Retained interactions can be swept into legal discovery, exposed in a breach, or affected by future policy changes; data that was never stored cannot. The gate therefore distinguishes *structural* protection (data never retained, or workload isolated on owned/attested compute) from *contractual* protection (retained-data promises), and requires the strongest protection the workload's tier demands.

## The Gate — all items must pass

| # | Check | Pass condition |
|---|---|---|
| 1 | Agreement exists | A written ZDR (or equivalent no-retention) agreement is in force with THIS provider — per provider, not assumed across vendors. |
| 2 | Content scope | Prompts, outputs, and uploaded content are all covered. |
| 3 | Derived metadata scope | Retention of derived metadata — safety-classifier outputs, monitoring logs, usage telemetry — is reviewed and bounded, not just "customer content." |
| 4 | Training prohibition | Training on institutional and customer data is prohibited in writing. |
| 5 | Human review | No routine human access to the organization's interactions or provider-side logs. |
| 6 | Subprocessors | The commitments bind subprocessors and infrastructure partners. |
| 7 | Change control | The provider cannot silently weaken retention terms; changes require notice and re-review. |
| 8 | Exit leverage | The organization retains a credible switch path (model liquidity) so the agreement is enforceable in practice, not only on paper. |

## Failure handling

- Any failed check on an S2+ workload: **do not deploy.** Options: negotiate the gap closed, route to owned or attested compute, or reduce the data class sent.
- Record every review in `templates/ai-vendor-zdr-review-record.md`.
- Re-review on provider terms changes, annually, and on any incident.

## Extraction-Risk Posture

Default zero-trust posture: any external frontier model used **without** confirmed ZDR is treated as extraction-risk — assume institutional signal sent to it may end up improving someone else's system. The burden of proof sits with the integration, never with the objector.
