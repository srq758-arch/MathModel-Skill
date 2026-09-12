from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path.cwd()
PROFILE_FILE = BASE_DIR / "paper_output" / "context" / "workflow_profile.json"


PROFILE_TEMPLATES: dict[str, dict[str, Any]] = {
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
        "stage_brief": {
            "enabled": True,
            "max_lines": 8,
            "fields": ["what_was_done", "why", "artifacts", "what_to_watch_next"],
        },
        "model_upgrade_gate": {
            "enabled": True,
            "require_baseline_run": True,
            "trigger_any": [
                "baseline error or objective value is materially inadequate for the task",
                "residuals or diagnostics show a systematic pattern the baseline cannot explain",
                "hard constraints are violated or feasibility is unstable",
                "results are unstable under reasonable parameter or data perturbations",
                "an enhanced model has a clear expected gain that justifies its extra complexity",
            ],
            "no_trigger_action": "keep the baseline as the active model and document why added complexity is unnecessary",
        },
        "comparison_dimensions": ["accuracy", "stability", "interpretability", "implementation_cost"],
        "stage_requirements": {
            "S1": [
                "explain each question in plain language",
                "identify knowns, unknowns, constraints, and the main difficulty",
            ],
            "S2": [
                "declare one runnable baseline before enhanced candidates",
                "state inputs, outputs, evaluation criteria, and upgrade triggers",
            ],
            "S3": [
                "prepare the data and diagnostics needed to judge the baseline fairly",
                "define metrics before seeing the final result",
            ],
            "S4": [
                "implement the baseline path first",
                "keep enhanced-model hooks separate so they can be activated only after diagnosis",
            ],
            "S5": [
                "run and diagnose the baseline before any upgrade",
                "upgrade only when at least one recorded trigger is satisfied",
                "compare candidate models on accuracy, stability, interpretability, and implementation cost",
            ],
        },
        "preserve_formal_gates": ["S6", "S7", "S8"],
    },
}


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def build_profile(name: str, *, implicit: bool = False) -> dict[str, Any]:
    payload = deepcopy(PROFILE_TEMPLATES[name])
    return {
        "schema_version": "1.0",
        "profile": name,
        "implicit": implicit,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_by": "paper-workflow-orchestrator/scripts/workflow_profile.py",
        **payload,
    }


def load_profile() -> dict[str, Any]:
    if not PROFILE_FILE.exists():
        return build_profile("standard", implicit=True)
    try:
        payload = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Invalid workflow profile JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("workflow_profile.json must contain a JSON object")
    name = str(payload.get("profile") or "").strip()
    if name not in PROFILE_TEMPLATES:
        raise RuntimeError(f"Unsupported workflow profile: {name or '<missing>'}")
    return payload


def write_profile(name: str) -> dict[str, Any]:
    payload = build_profile(name)
    PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Select or inspect the optional Standard workflow execution profile.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--set", dest="profile_name", choices=sorted(PROFILE_TEMPLATES))
    group.add_argument("--reset", action="store_true", help="Remove the explicit profile and return to implicit Standard behavior.")
    group.add_argument("--show", action="store_true", help="Print the active profile as JSON. This is the default action.")
    args = parser.parse_args()

    if args.reset:
        if PROFILE_FILE.exists():
            PROFILE_FILE.unlink()
        print(json.dumps(build_profile("standard", implicit=True), ensure_ascii=False, indent=2))
        return 0

    if args.profile_name:
        payload = write_profile(args.profile_name)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    try:
        payload = load_profile()
    except RuntimeError as exc:
        print(f"[PROFILE FAIL] {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
