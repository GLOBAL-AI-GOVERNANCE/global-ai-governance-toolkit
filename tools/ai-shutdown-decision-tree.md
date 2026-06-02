# AI Shutdown Decision Tree

## Step 1: Has The AI System Caused Harm Or Material Risk?

If yes, proceed to Step 2.

Examples:

- Harmful output
- Data leakage
- Security exposure
- Bias or discriminatory outcome
- Unauthorized autonomy
- Scope violation
- Legal or compliance violation
- Monitoring failure

## Step 2: Can The System Be Immediately Contained?

If no, full shutdown is required.

Containment options:

- Disable access
- Restrict permissions
- Pause workflow
- Remove integration
- Suspend vendor access
- Roll back model/version

## Step 3: Is Root Cause Known?

If no, keep system paused or restricted while investigating.

## Step 4: Can Controls Prevent Recurrence?

If no, keep system shut down or retire permanently.

## Step 5: Is Evidence Updated?

Required before restart:

- Root cause analysis
- Corrective action
- Updated testing
- Control verification
- Owner sign-off
- Monitoring confirmation
- Shutdown path retest

## Final Decision

- Continue operation
- Restrict operation
- Pause operation
- Full shutdown
- Permanent retirement
