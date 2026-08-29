// Generated from Wave A contracts. Do not edit.
export const contracts = {
  "canonicalSchema": {
    "$id": "https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit/automation/contracts/v1/canonical-inventory-record.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "additionalProperties": false,
    "properties": {
      "autonomy_level": {
        "enum": [
          "None",
          "Partial",
          "Full"
        ],
        "type": "string"
      },
      "business_unit": {
        "minLength": 1,
        "type": "string"
      },
      "data_sensitivity": {
        "enum": [
          "None",
          "Internal",
          "Personal",
          "Regulated",
          "Critical"
        ],
        "type": "string"
      },
      "evidence_complete": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "impact_money": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "impact_people": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "impact_rights": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "impact_safety": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "impact_security": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "monitoring_active": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "owner": {
        "type": "string"
      },
      "public_facing": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "schema_version": {
        "const": "1.0.0",
        "type": "string"
      },
      "shutdown_path_exists": {
        "enum": [
          "Yes",
          "No"
        ],
        "type": "string"
      },
      "system_id": {
        "minLength": 1,
        "type": "string"
      },
      "system_name": {
        "minLength": 1,
        "type": "string"
      },
      "use_case": {
        "minLength": 1,
        "type": "string"
      },
      "vendor_internal": {
        "enum": [
          "Vendor",
          "Internal",
          "Hybrid"
        ],
        "type": "string"
      }
    },
    "required": [
      "schema_version",
      "system_id",
      "system_name",
      "owner",
      "business_unit",
      "vendor_internal",
      "use_case",
      "data_sensitivity",
      "impact_people",
      "impact_money",
      "impact_security",
      "impact_rights",
      "impact_safety",
      "autonomy_level",
      "public_facing",
      "monitoring_active",
      "shutdown_path_exists",
      "evidence_complete"
    ],
    "title": "Canonical AI System Inventory Record v1",
    "type": "object"
  },
  "mapping": {
    "boolean_aliases": {
      "No": [
        "no",
        "n",
        "false",
        "0"
      ],
      "Yes": [
        "yes",
        "y",
        "true",
        "1"
      ]
    },
    "canonical_schema_version": "1.0.0",
    "contract_version": "1.0.0",
    "fields": {
      "autonomy_level": {
        "aliases": [
          "autonomy level"
        ],
        "human_label": "Autonomy Level"
      },
      "business_unit": {
        "aliases": [
          "business unit",
          "office"
        ],
        "human_label": "Business Unit"
      },
      "data_sensitivity": {
        "aliases": [
          "data sensitivity"
        ],
        "human_label": "Data Sensitivity"
      },
      "evidence_complete": {
        "aliases": [
          "evidence complete",
          "evidence complete?"
        ],
        "human_label": "Evidence Complete?"
      },
      "impact_money": {
        "aliases": [
          "impact money",
          "impacts money?"
        ],
        "human_label": "Impacts Money?"
      },
      "impact_people": {
        "aliases": [
          "impact people",
          "impacts people?"
        ],
        "human_label": "Impacts People?"
      },
      "impact_rights": {
        "aliases": [
          "impact rights",
          "impacts rights?"
        ],
        "human_label": "Impacts Rights?"
      },
      "impact_safety": {
        "aliases": [
          "impact safety",
          "impacts safety?"
        ],
        "human_label": "Impacts Safety?"
      },
      "impact_security": {
        "aliases": [
          "impact security",
          "impacts security?"
        ],
        "human_label": "Impacts Security?"
      },
      "monitoring_active": {
        "aliases": [
          "monitoring active",
          "monitoring active?"
        ],
        "human_label": "Monitoring Active?"
      },
      "owner": {
        "aliases": [],
        "human_label": "Owner"
      },
      "public_facing": {
        "aliases": [
          "public facing",
          "public facing?"
        ],
        "human_label": "Public Facing?"
      },
      "schema_version": {
        "aliases": [
          "schema version"
        ],
        "human_label": "Schema Version"
      },
      "shutdown_path_exists": {
        "aliases": [
          "shutdown path exists",
          "shutdown path exists?"
        ],
        "human_label": "Shutdown Path Exists?"
      },
      "system_id": {
        "aliases": [
          "system id"
        ],
        "human_label": "System ID"
      },
      "system_name": {
        "aliases": [
          "system name"
        ],
        "human_label": "System Name"
      },
      "use_case": {
        "aliases": [
          "use case",
          "purpose",
          "description"
        ],
        "human_label": "Use Case"
      },
      "vendor_internal": {
        "aliases": [
          "vendor/internal",
          "vendor / internal"
        ],
        "human_label": "Vendor / Internal"
      }
    },
    "legacy_ignored_columns": [
      "Risk Tier",
      "Status",
      "Data Used",
      "Impact Area",
      "Human Owner",
      "Technical Owner",
      "Executive Owner",
      "Last Review Date",
      "Next Review Date",
      "Notes"
    ]
  },
  "policy": {
    "policy_id": "global-ai-governance-toolkit.default-governance-rules",
    "policy_version": "1.0.0",
    "rules": [
      {
        "all": [
          {
            "field": "owner",
            "operator": "blank"
          }
        ],
        "description": "Every AI system must have a named human owner.",
        "id": "GAI-AUTO-001",
        "message": "Missing named owner. No owner, no deployment.",
        "name": "Owner Required",
        "severity": "critical"
      },
      {
        "all": [
          {
            "field": "monitoring_active",
            "operator": "equals",
            "value": "No"
          }
        ],
        "description": "Every deployed AI system must have active monitoring.",
        "id": "GAI-AUTO-002",
        "message": "Monitoring is not active.",
        "name": "Monitoring Required",
        "severity": "high"
      },
      {
        "all": [
          {
            "field": "shutdown_path_exists",
            "operator": "equals",
            "value": "No"
          }
        ],
        "description": "No AI system may deploy without a shutdown path.",
        "id": "GAI-AUTO-003",
        "message": "Shutdown path is missing.",
        "name": "Shutdown Path Required",
        "severity": "critical"
      },
      {
        "all": [
          {
            "field": "evidence_complete",
            "operator": "equals",
            "value": "No"
          },
          {
            "field": "calculated_risk_tier",
            "operator": "in",
            "values": [
              "High",
              "Critical",
              "Frontier"
            ]
          }
        ],
        "description": "High, Critical, and Frontier systems require complete evidence.",
        "id": "GAI-AUTO-004",
        "message": "Evidence is incomplete for a high-impact system.",
        "name": "Evidence Required for High Impact",
        "severity": "high"
      },
      {
        "all": [
          {
            "field": "autonomy_level",
            "operator": "equals",
            "value": "Full"
          },
          {
            "field": "calculated_risk_tier",
            "operator": "not_in",
            "values": [
              "Critical",
              "Frontier"
            ]
          }
        ],
        "description": "Full autonomy requires Critical or Frontier review.",
        "id": "GAI-AUTO-005",
        "message": "Full autonomy requires Critical or Frontier review.",
        "name": "Full Autonomy Escalates Risk",
        "severity": "high"
      }
    ],
    "schema_version": "1.0"
  },
  "sampleCsv": "system_id,system_name,owner,business_unit,vendor_internal,use_case,data_sensitivity,impact_people,impact_money,impact_security,impact_rights,impact_safety,autonomy_level,public_facing,monitoring_active,shutdown_path_exists,evidence_complete\nTEST-VALID-001,Read-Only Knowledge Assistant,Jordan Owner,Operations,Internal,Approved document retrieval,Internal,No,No,No,No,No,None,No,Yes,Yes,Yes\n"
};
