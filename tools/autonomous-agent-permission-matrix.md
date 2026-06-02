# Autonomous Agent Permission Matrix

No autonomous agent without least privilege.

| Permission Type | Default | Requires Approval? | Notes |
|---|---|---:|---|
| Read public web | Allowed with logging | No | Limit domains if needed |
| Read internal non-sensitive docs | Restricted | Yes | Owner approval required |
| Read sensitive data | Prohibited by default | Yes, executive/data owner | High control requirement |
| Send external email | Prohibited by default | Yes | Human approval strongly preferred |
| Modify files | Restricted | Yes | Versioning required |
| Modify production systems | Prohibited by default | Yes, executive/security | Critical control |
| Execute code | Restricted | Yes | Sandbox required |
| Purchase goods/services | Prohibited by default | Yes | Financial control |
| Create accounts/API keys | Prohibited by default | Yes | Security approval |
| Change permissions | Prohibited | Yes, security executive | Highest risk |
| Self-modify | Prohibited | No routine approval | Frontier review |
| Self-replicate | Prohibited | No routine approval | Frontier review |

## Required Controls

- Named owner
- Approved tool list
- Least-privilege access
- Time-bound permissions
- Full logging
- Monitoring
- Escalation path
- Shutdown path
