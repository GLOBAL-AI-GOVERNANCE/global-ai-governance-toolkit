# v2.4.0 Release Gate Record

## Gate definition

This record defines evidence for a later v2.4.0 tag. It is not a publication. The published release remains the v2.3.0 tag until a separate release action creates v2.4.0.

## Required before tag

- Package metadata and `gag --version` report `2.4.0`.
- README still identifies v2.3.0 as the published release until the tag exists.
- Changelog unreleased notes match current main and do not claim publication.
- `profiles.cli_supported` matches `automation/profiles/registry.json`.
- `profiles.browser_supported` matches registry entries with `browser_support: true`.
- `profiles.supported` equals `profiles.browser_supported`.
- Organizational maturity is absent from the registry, CLI module map, machine interface, and browser.
- `authority_effect` remains NONE.
- Repository integrity, history privacy, pull-request identity, automation tests, browser parity, and the static browser boundary pass.
- Contract v1 inventory, findings, and result schemas are unchanged by this stabilization.

## Not performed here

- No tag.
- No GitHub Release.
- No merge of unrelated profile work.
- No change to the published v2.3.0 release assets.
