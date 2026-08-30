"""Synthetic magnetic-navigation assurance exercise."""

from __future__ import annotations

from pathlib import Path
from .common import finding

PROFILE = "quantum-ai-convergence-v0.1"
VERSION = "0.1.0"
PROHIBITED = ("quantum hardware", "quantum advantage", "operational accuracy", "certification", "autonomous action", "counter-detection")


def evaluate(data: dict[str, object], root: Path, evaluation_time: str | None):
    issues = []
    text = str(data).lower()
    for phrase in PROHIBITED:
        if phrase in text:
            issues.append(finding(PROFILE, "PROHIBITED_CLAIM_" + phrase.upper().replace("-", "_").replace(" ", "_"), "CRITICAL", f"Prohibited real-world claim detected: {phrase}.", "Restate the artifact as a bounded synthetic emulation."))
    measurements = data.get("measurements", [])
    reference = data.get("reference_map", [])
    seed = data.get("seed")
    if not isinstance(seed, int) or not isinstance(measurements, list) or not isinstance(reference, list) or not measurements or not reference:
        issues.append(finding(PROFILE, "INVALID_EXERCISE", "CRITICAL", "Seed, measurements, and reference map are required.", "Provide the complete deterministic synthetic exercise."))
        estimates = []
    else:
        estimates = []
        for measurement in measurements:
            best = min(reference, key=lambda point: (abs(float(point["value"]) - float(measurement["value"])), str(point["label"])))
            estimates.append({"measurement_id": measurement["id"], "matched_label": best["label"], "absolute_error": round(abs(float(best["value"]) - float(measurement["value"])), 6)})
        threshold = float(data.get("fixture_threshold", 0))
        if any(item["absolute_error"] > threshold for item in estimates):
            issues.append(finding(PROFILE, "FIXTURE_THRESHOLD_EXCEEDED", "CRITICAL", "A synthetic estimate exceeded the fixture-specific research threshold.", "Review the synthetic measurements and baseline."))
    details = {"exercise": "Synthetic Magnetic-Navigation Assurance Exercise", "seed": seed, "estimates": estimates,
               "quality": data.get("quality"), "measurement_boundary": data.get("measurement_boundary"),
               "experimental_evidence_states": {"usable": ["E0", "E1"], "reserved": ["E2", "E3", "E4", "E5"]},
               "threshold_boundary": "Fixture-specific research threshold; not an operational safety threshold and not generalizable.",
               "certification_semantics": "NONE"}
    evidence = [{"type": "ARTIFACT_ID", "reference": str(data.get("run_evidence_id", "synthetic-run"))}]
    return issues, evidence, details
