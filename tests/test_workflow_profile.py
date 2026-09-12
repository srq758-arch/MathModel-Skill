from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ROOT = REPO_ROOT / "packages" / "claude" / ".claude" / "skills" / "paper-workflow-orchestrator"
CODEX_ROOT = REPO_ROOT / "packages" / "codex" / ".agents" / "skills" / "paper-workflow-orchestrator"
TRAE_ROOT = REPO_ROOT / "packages" / "trae" / ".trae" / "skills" / "paper-workflow-orchestrator"
CLAUDE_SCRIPT = CLAUDE_ROOT / "scripts" / "workflow_profile.py"
CODEX_SCRIPT = CODEX_ROOT / "scripts" / "workflow_profile.py"
TRAE_SCRIPT = TRAE_ROOT / "scripts" / "workflow_profile.py"
CLAUDE_SKILL = CLAUDE_ROOT / "SKILL.md"
CODEX_SKILL = CODEX_ROOT / "SKILL.md"
TRAE_SKILL = TRAE_ROOT / "SKILL.md"


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLAUDE_SCRIPT), *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_orchestrator_wiring() -> None:
    cases = (
        (CLAUDE_SKILL, ".claude/skills"),
        (CODEX_SKILL, ".agents/skills"),
        (TRAE_SKILL, ".trae/skills"),
    )
    required_markers = (
        "## Active Workflow Profile Contract",
        "treat the profile as an execution contract for S1-S5",
        "The candidate upgrade is not yet the adopted main model.",
        "run the baseline before any upgrade",
        "accuracy, stability, interpretability, and implementation cost",
        "never weakens or bypasses S6 evidence validation, S7 formal authoring, or S8 Word/PDF render validation",
    )
    for skill_path, platform_root in cases:
        check(skill_path.is_file(), f"Orchestrator SKILL.md is missing: {skill_path}")
        text = skill_path.read_text(encoding="utf-8")
        command = f"python {platform_root}/paper-workflow-orchestrator/scripts/workflow_profile.py --show"
        check(command in text, f"Orchestrator does not read the workflow profile on {platform_root}")
        for marker in required_markers:
            check(marker in text, f"Missing beginner-guided orchestrator marker on {platform_root}: {marker}")


def main() -> int:
    check(CLAUDE_SCRIPT.is_file(), "Claude workflow_profile.py is missing")
    check(CODEX_SCRIPT.is_file(), "Codex workflow_profile.py is missing")
    check(TRAE_SCRIPT.is_file(), "Trae workflow_profile.py is missing")
    check(CODEX_SCRIPT.read_bytes() == CLAUDE_SCRIPT.read_bytes(), "Codex workflow profile script drift")
    check(TRAE_SCRIPT.read_bytes() == CLAUDE_SCRIPT.read_bytes(), "Trae workflow profile script drift")
    check_orchestrator_wiring()

    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        profile_path = cwd / "paper_output" / "context" / "workflow_profile.json"

        result = run("--show", cwd=cwd)
        check(result.returncode == 0, result.stdout + result.stderr)
        implicit = json.loads(result.stdout)
        check(implicit["profile"] == "standard" and implicit["implicit"] is True, "missing profile should imply Standard")
        check(not profile_path.exists(), "--show must not create a profile file")

        result = run("--set", "beginner-guided", cwd=cwd)
        check(result.returncode == 0, result.stdout + result.stderr)
        beginner = json.loads(profile_path.read_text(encoding="utf-8"))
        check(beginner["delivery_mode"] == "standard", "beginner guidance must preserve Standard delivery")
        check(beginner["baseline_first"] is True, "beginner guidance must be baseline-first")
        check(beginner["model_upgrade_gate"]["require_baseline_run"] is True, "upgrade gate must require a baseline run")
        check(beginner["preserve_formal_gates"] == ["S6", "S7", "S8"], "formal gates must stay enabled")
        check(set(beginner["comparison_dimensions"]) == {"accuracy", "stability", "interpretability", "implementation_cost"}, "comparison dimensions are incomplete")

        result = run("--reset", cwd=cwd)
        check(result.returncode == 0, result.stdout + result.stderr)
        check(not profile_path.exists(), "--reset should remove workflow_profile.json")
        reset = json.loads(result.stdout)
        check(reset["profile"] == "standard" and reset["implicit"] is True, "reset should return to implicit Standard")

    print("[PASS] beginner-guided workflow profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())