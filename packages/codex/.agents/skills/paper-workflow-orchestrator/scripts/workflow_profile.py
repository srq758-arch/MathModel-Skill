from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


PROFILE_FILE = Path.cwd() / "paper_output" / "context" / "workflow_profile.json"
PROFILES = {
    "standard": {
        "delivery_mode": "standard",
        "guidance_level": "standard",
        "baseline_first": False,
        "explain_decisions": False,
        "stage_brief": {"enabled": False, "max_lines": 0},
        "model_upgrade_gate": {"enabled": False},
        "comparison_dimensions": ["accuracy", "stability", "interpretability", "implementation_cost"],
        "preserve_formal_gates": ["S6", "S7", "S8"],
    },
    "beginner-guided": {
        "delivery_mode": "standard",
        "guidance_level": "beginner",
        "baseline_first": True,
        "explain_decisions": True,
        "stage_brief": {"enabled": True, "max_lines": 8},
        "model_upgrade_gate": {
            "enabled": True,
            "require_baseline_run": True,
            "trigger_any": [
                "baseline_inadequate",
                "systematic_residuals",
                "constraint_violation",
                "instability",
                "justified_gain",
            ],
            "no_trigger_action": "keep_baseline",
        },
        "comparison_dimensions": ["accuracy", "stability", "interpretability", "implementation_cost"],
        "stage_requirements": {
            "S1": ["plain_language_problem", "knowns_unknowns_constraints", "main_difficulty"],
            "S2": ["runnable_baseline", "inputs_outputs_metrics", "upgrade_triggers"],
            "S3": ["baseline_diagnostics", "predeclared_metrics"],
            "S4": ["baseline_first_implementation", "separate_upgrade_hooks"],
            "S5": ["run_baseline_first", "upgrade_only_on_trigger", "four_way_comparison"],
        },
        "preserve_formal_gates": ["S6", "S7", "S8"],
    },
}


def build(name: str, implicit: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "profile": name,
        "implicit": implicit,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_by": "paper-workflow-orchestrator/scripts/workflow_profile.py",
        **PROFILES[name],
    }


def show() -> dict:
    if not PROFILE_FILE.exists():
        return build("standard", True)
    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("profile") not in PROFILES:
        raise ValueError("invalid workflow_profile.json")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Select or inspect the Standard workflow execution profile.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--set", choices=sorted(PROFILES))
    group.add_argument("--reset", action="store_true")
    group.add_argument("--show", action="store_true")
    args = parser.parse_args()

    try:
        if args.reset:
            PROFILE_FILE.unlink(missing_ok=True)
            data = build("standard", True)
        elif args.set:
            data = build(args.set)
            PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
            PROFILE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            data = show()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[PROFILE FAIL] {exc}")
        return 2

    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
