# Machine-Interface Compatibility Policy

The canonical inventory, machine results, Decision Pack manifest, handoff, and installed CLI are public reference interfaces.

- Versions use `MAJOR.MINOR.PATCH`.
- Patch changes clarify behavior or add compatible validation without changing accepted meaning.
- Minor changes may add optional fields or commands while preserving existing valid inputs and outputs.
- Breaking field, state, command, exit-code, or authority-semantic changes require a new major interface version.
- Unsupported canonical schema versions fail closed.
- Unknown input columns and machine fields are not silently discarded.
- Existing repository-relative commands remain compatibility entry points during the v1 contract line.
- The existing handoff v1 contract remains reference-only and requires `authority_effect: NONE`.

Repository tags remain the release authority. Presence on `main` does not itself create a public release.
