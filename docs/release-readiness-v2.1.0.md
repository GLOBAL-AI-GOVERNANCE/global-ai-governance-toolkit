# v2.1.0 Release Readiness

## Release Identity

- Product: Global AI Governance Toolkit
- Release: v2.1.0
- Release theme: Decision-Ready Governance
- Maturity: Working public reference toolkit
- License: MIT

## Finished Outcome

The verified workflow converts an AI system inventory CSV into:

1. Schema validation evidence
2. Preliminary risk classification
3. Policy-driven governance findings with stable rule identifiers
4. An executive governance report
5. A deterministic AI Governance Decision Pack
6. A pending human decision record

## Automated Release Gates

The release workflow requires:

- Repository integrity validation
- Python syntax validation
- JSON and policy parsing
- Local Markdown link validation
- Immutable GitHub Actions pins
- Decision Pack manifest verification
- Full runtime-alignment and Decision Pack tests
- Checked-in Decision Pack regeneration with no drift
- Documented quick-start execution
- Valid default-path execution
- Critical fail-closed execution
- Explicit report-only execution
- No tracked or generated Python bytecode

## Exit Codes

- `0`: the selected automated gate permits continuation
- `1`: governance findings meet the selected blocking threshold
- `2`: schema, policy, input, configuration, or required-artifact failure

An exit code of `0` is not human approval, certification, compliance confirmation, or risk acceptance.

## Human Authority

Humans remain responsible for:

- Evidence quality
- Context and applicability
- Final risk interpretation
- Deployment or expansion approval
- Conditions and restrictions
- Risk acceptance
- Restriction, suspension, rollback, or shutdown authority

## Verification Commands

```bash
python -B automation/scripts/validate_repository.py

python -B -m unittest discover \
  -s automation/tests \
  -p "test_*.py" \
  -v

python -B automation/scripts/build_decision_pack_example.py --check

python -B automation/scripts/run_governance_checks.py \
  automation/sample-data/sample-ai-inventory.csv \
  --outdir automation/reports \
  --fail-on none
```

The bundled sample intentionally contains critical governance gaps. This command verifies that report-only mode produces a visible blocked-state Decision Pack. The release gate separately verifies that the default mode exits `1` and stops before pack generation.

## Evidence Boundary

This release is a tested public reference toolkit. It is not a legal opinion, regulatory determination, certification, proof of compliance, guarantee of production readiness, or substitute for legal, security, privacy, procurement, compliance, executive, or board review.
