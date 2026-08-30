# Machine Interfaces

## Optional profile result

The additive [`profile-result.schema.json`](../automation/contracts/v1/profile-result.schema.json) is shared by every registered profile. Discovery is available through [`registry.json`](../automation/profiles/registry.json) and the browser machine interface. The local browser renders this result; it does not evaluate profiles. A Decision Pack handoff may include a profile-result path/digest string in `evidence_refs`, while both artifacts preserve `authority_effect: NONE`.

Wave A provides a local contract spine without changing the five existing governance rules or built-in risk semantics.

The static browser publishes `web/machine-interface.json` as its versioned machine front door. It points to the generated browser template and sample, canonical repository contracts, CLI commands, outputs, Decision Pack manifest, governance handoff, and the non-authorizing boundary.

## Commands

```text
gag normalize INPUT --output-json FILE [--output-csv FILE]
gag check INPUT --outdir DIRECTORY [--fail-on none|high|critical]
          [--evaluation-time YYYY-MM-DDTHH:MM:SSZ]
          [--target-repository NAME]
gag verify OUTPUT_DIRECTORY
```

Exit codes remain:

- `0`: successful execution, including explicit report-only operation;
- `1`: governance findings meet the selected blocking threshold;
- `2`: invalid input, schema, policy, configuration, contract, or integrity state.

## Canonical input

`automation/contracts/v1/canonical-inventory-record.schema.json` is the source of truth. `inventory-mapping.json` defines friendly labels and reviewed aliases. The human CSV and Markdown field table are generated from these files and checked for drift.

Normalization accepts the current canonical CSV and the generated human CSV. Known legacy headers are mapped only where their meaning is unambiguous. The older v2 spreadsheet lacks several required canonical governance fields and therefore fails closed until those fields are supplied; no risk or impact meaning is guessed.

## Machine outputs

- `normalized-inventory.json`: source digest, mappings, warnings, and canonical records.
- `governance-findings.json`: stable finding IDs, rule IDs, severity, policy identity, and systems.
- `governance-result.json`: validation state, automated gate state, threshold, and `PENDING_HUMAN_DECISION`.
- `decision-pack/manifest.json`: source and generated digests plus generator, policy, normalization, schema, canonical-input, and evaluation-time metadata.
- `governance-handoff.json`: a Decision Pack reference with `authority_effect: NONE`.

The runtime never converts an automated result into human approval, certification, authorization, compliance, or risk acceptance.

## Determinism

No wall-clock time is inserted automatically. Supply `--evaluation-time` when a reproducible evaluation instant is needed. Identical input bytes, policy, versions, target repository, threshold, and evaluation time produce byte-identical outputs.
