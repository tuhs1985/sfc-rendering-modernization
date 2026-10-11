"""Bounded diagnostic adjudication; never equate mechanism evidence with visual uplift."""
import argparse
import json
from pathlib import Path

MAX_SUMMARY_BYTES = 256 * 1024


def analyze(summary):
    shading = summary["shading_off"]
    intervention = summary["visual_tint"]  # shared source-lease safety counters
    phases = shading["phases"]
    samples = shading["samples"]
    if len(phases) != 5 or len(samples) > 96:
        raise ValueError("Invalid fixed phase/sample bounds")
    if [p["phase"] for p in phases] != list(range(5)):
        raise ValueError("Invalid phase ordering")
    issues = []
    if not shading["enabled"] or intervention["enabled"] or summary["geometry_hook_enabled"]:
        issues.append("Wrong diagnostic configuration")
    if not summary["hooks_restored"] or not summary["gate_activated"]:
        issues.append("Gate/cleanup not confirmed")
    for key in ("thread_mismatch", "rejected", "restore_failed", "active_scopes"):
        if intervention[key]:
            issues.append(f"Source safety counter {key}={intervention[key]}")
    for key in ("rejected_semantics", "owner_overflow", "thread_overflow"):
        if summary[key]:
            issues.append(f"Semantic safety counter {key}={summary[key]}")
    if intervention["applied"] != intervention["restored"] + intervention["renderer_replaced"]:
        issues.append("Unreleased source substitutions")
    if not all(p["observed"] for p in phases):
        issues.append("Target not observed in every comparison phase")
    if not phases[1]["applied"] or phases[1]["applied"] != phases[1]["released"]:
        issues.append("Identification cue/release not demonstrated")
    if phases[3]["applied"] != phases[3]["released"]:
        issues.append("Lighting-off release incomplete")
    target = intervention["target_owner_id"]
    seen_phases = set()
    for sample in samples:
        phase = sample["phase"]
        if phase not in range(5):
            raise ValueError("Invalid sample phase")
        elapsed = sample["elapsed_ms"]
        expected = 0 if elapsed < 5000 else 1 if elapsed < 8000 else 2 if elapsed < 13000 else 3 if elapsed < 58000 else 4
        if phase != expected:
            issues.append("Sample outside declared phase timing")
        seen_phases.add(phase)
        if not target or sample["owner"] != target:
            issues.append("Sample cross-associated to another owner")
        if any(int(sample[key], 16) == 0 for key in ("ship", "visual", "model0", "source")):
            issues.append("Missing semantic identity")
        expected_flags = sample["flags"] & ~6 if phase == 3 and sample["applied"] else sample["flags"]
        if sample["effective_flags"] != expected_flags:
            issues.append("Unexpected source flag modification")
        if sample["applied"]:
            if phase not in (1, 3) or sample["restore"] not in (1, 2) or not int(sample["effective"], 16):
                issues.append("Invalid intervention/release sample")
            if phase == 3 and (not sample["lit_entries"] or sample["manager_mode"] == 3):
                issues.append("Ineligible lighting source substituted")
        elif sample["restore"] or int(sample["effective"], 16):
            issues.append("Baseline/no-op sample incorrectly substituted")
    if seen_phases != set(range(5)):
        issues.append("Bounded comparison samples incomplete")
    no_op = not phases[3]["eligible"] or not phases[3]["applied"]
    if not no_op and not any(s["phase"] == 3 and s["lit_entries"] > 0 and
                             s["applied"] for s in samples):
        issues.append("No lighting-eligible intervention sample")
    status = "ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED" if issues else (
        "NO_OP_LIGHTING_INELIGIBLE" if no_op else "MECHANISM_COHERENT_VISUAL_REVIEW_PENDING")
    return {"probe_id": "M1-C-RT-001", "status": status,
            "target_owner_id": target, "sample_count": len(samples), "phases": phases,
            "issues": sorted(set(issues)), "visual_confirmation": "SPONSOR_REQUIRED",
            "formal_m1": "CONTINUES", "downstream_fresh_correlation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    source = args.run_dir / "M1-A-summary.json"
    if source.stat().st_size > MAX_SUMMARY_BYTES:
        parser.error("Summary exceeds 256 KiB input safeguard")
    try:
        result = analyze(json.loads(source.read_text(encoding="utf-8-sig")))
    except (KeyError, TypeError, ValueError) as error:
        parser.error(f"Malformed diagnostic summary: {error}")
    output = args.run_dir / "M1-C-shading-analysis.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
