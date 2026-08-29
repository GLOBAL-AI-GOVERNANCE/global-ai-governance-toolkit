# AI System Inventory Template

This template is generated from the canonical inventory contract. Use the CSV template for data entry; do not add columns without updating the versioned contract and mapping.

| Human label | Canonical field | Allowed values |
|---|---|---|
| Schema Version | `schema_version` | Text |
| System ID | `system_id` | Text |
| System Name | `system_name` | Text |
| Owner | `owner` | Text |
| Business Unit | `business_unit` | Text |
| Vendor / Internal | `vendor_internal` | Vendor / Internal / Hybrid |
| Use Case | `use_case` | Text |
| Data Sensitivity | `data_sensitivity` | None / Internal / Personal / Regulated / Critical |
| Impacts People? | `impact_people` | Yes / No |
| Impacts Money? | `impact_money` | Yes / No |
| Impacts Security? | `impact_security` | Yes / No |
| Impacts Rights? | `impact_rights` | Yes / No |
| Impacts Safety? | `impact_safety` | Yes / No |
| Autonomy Level | `autonomy_level` | None / Partial / Full |
| Public Facing? | `public_facing` | Yes / No |
| Monitoring Active? | `monitoring_active` | Yes / No |
| Shutdown Path Exists? | `shutdown_path_exists` | Yes / No |
| Evidence Complete? | `evidence_complete` | Yes / No |

Canonical schema version: `1.0.0`
