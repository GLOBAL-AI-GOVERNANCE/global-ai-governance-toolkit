# Autonomous Agent Policy

## Core Rule

No autonomous agent without least privilege.

## Requirements

Every autonomous agent must have:

- Named human owner
- Approved use case
- Defined scope
- Time-bound permissions
- Least-privilege access
- Human escalation path
- Logging and audit trail
- Monitoring
- Incident response path
- Shutdown path

## Prohibited Agent Capabilities Without Explicit Approval

An agent may not:

- Self-modify
- Self-replicate
- Escalate privileges
- Access sensitive systems
- Execute financial transactions
- Send external communications at scale
- Alter production systems
- Disable logging
- Bypass human review

## Violation Response

Violation triggers immediate restriction, incident review, and possible shutdown.
