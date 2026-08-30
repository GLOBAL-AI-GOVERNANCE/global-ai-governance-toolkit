# Model Liquidity Policy

Part of Global AI Governance Toolkit — v2.2.0 AI Sovereignty Control Layer.

## Policy Statement

The organization must be able to switch AI models and providers with low friction. Dependency on a single provider converts ordinary vendor events — outages, retention-policy changes, refusal-policy changes, pricing changes, geopolitical restrictions — into existential workflow risk, and removes the leverage that makes contractual protections enforceable.

## Requirements

1. **Model-agnostic architecture.** No workload may hard-code a single model as its foundation. Model access goes through a routing layer that treats models as substitutable components.
2. **Documented exit path.** Every production AI workflow maintains a tested fallback: an alternative provider, an open-weight model, or a deterministic degradation mode.
3. **Continuous evaluation.** A shared evaluation suite scores candidate models on quality, cost, and latency so substitution decisions are evidence-based, not guesswork.
4. **Separation of knowledge and intelligence.** Institutional context, prompts-as-assets, ontology, and workflow logic live in the organization-owned control layer — never only inside one provider's ecosystem — so switching providers does not orphan accumulated know-how.
5. **Leverage discipline.** Concessions won from one provider (ZDR terms, pricing, capability access) are used as negotiating baselines with others. Consolidation pressure toward a single provider is resisted deliberately.
6. **Open-weight readiness.** For workloads where know-how must compound in-house, maintain the ability to fine-tune and self-host open-weight models on owned or attested compute, subject to license and terms-of-service review by counsel (including any restrictions on training against closed-model outputs).

## Enforcement

- Advisory `A02` flags single-provider dependency as sovereignty debt.
- Advisory `A03` requires a documented routing record per workload.
- Quarterly liquidity test: for each S2+ workflow, confirm the documented fallback still works.

## Operating Rule

> No model liquidity, no strategic dependency.
