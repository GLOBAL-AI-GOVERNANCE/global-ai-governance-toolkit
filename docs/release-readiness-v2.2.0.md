# v2.2.0 Release Readiness

Status: release candidate pending protected PR, hosted CI, merge, and current-main verification.

## Scope

v2.2.0 packages the local-first browser and machine-interface improvements accumulated after v2.1.0 together with the additive AI Sovereignty Control Layer.

The reviewed pre-integration main baseline is `491da882461bdc99071a8c6cec6f10e052e0db5d`.

## Required Verification

The release candidate must pass the current Toolkit repository validator, generated-template checks, browser-contract checks, full automation test suite, Decision Pack drift check, sovereignty checker compile, passing sovereignty baseline, intentionally blocked sovereignty demo, add-on manifest verification, and `git diff --check`.

Hosted PR checks and current-main checks must complete successfully before the release is created.

## Public Boundary

The sovereignty checker is additive. It does not replace the primary Decision Pack runtime and does not promote legacy `governance-os.yaml` into runtime policy.

This release does not establish certification, compliance, provider attestation, production authorization, institutional approval, operational safety, or fitness for every environment.
