# AI Model Routing Record

> Template — Global AI Governance Toolkit v2.2.0. One record per workload; update on any re-route trigger.

| Field | Entry |
|---|---|
| Record ID | ROUTE-____ |
| Workload name | |
| Owner | |
| Date | |
| Sensitivity tier | S0 / S1 / S2 / S3 / S4 |

## Routing decision

| Question | Answer |
|---|---|
| Does this workflow need model inference at all? If deterministic software suffices, route to an owned tool. | |
| Control layer criteria met (agnostic routing, permissions, audit, rollback, owned context)? | |
| Assurance level selected | tier1_owned / tier2_attested / tier3_zdr_cloud / tier4_standard |
| Model path selected | air-gapped sovereign / self-hosted open / fine-tuned open / owned ontology + external / attested compute / ZDR cloud / enterprise privacy mode / standard swappable |
| Primary model(s) / provider(s) | |
| Documented fallback (liquidity) | |
| ZDR review record(s) linked | |

## Justification

Why this route, in 3–5 sentences: capability requirement vs. sovereignty requirement, cost, and what was rejected.

## Re-route triggers acknowledged

New provider · new data class · new agent capability · new autonomy level · provider policy change · incident.

> Rule: Route every workload deliberately. Undocumented routing is advisory finding A03.
