# Quickstart

```bash
gag profile ciso-ai-risk-v0.1 automation/profiles/fixtures/ciso-pass.json \
  --outdir profile-output --evaluation-time 2026-08-29T12:00:00Z
```

Review `profile-output/profile-result.json` with the named accountable people. Exit `0` means PASS or CONDITIONAL, `1` means FAIL, and `2` means invalid input or configuration.
