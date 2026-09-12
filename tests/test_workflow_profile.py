from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SCRIPT = REPO_ROOT / "packages" / "claude" / ".claude" / "skills" / "paper-workflow-orchestrator" / "scripts" / "workflow_profile.py"
CODEX_SCRIPT = REPO_ROOT / "packages" / "codex" / ".agents" / "skills" / "paper-workflow-orchestrator" / "scripts" / "workflow_profile.py"
TRAE_SCRIPT = REPO_ROOT / "packages" / "trae" / ".trae" / "skills" / "paper-workflow-orchestrator" / "scripts" / "workflow_profile.py"


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


def main() -> int:
    check(CLAUDE_SCRIPT.is_file(), "Claude workflow_profile.py is missing")
    check(CODEX_SCRIPT.is_file(), "Codex workflow_profile.py is missing")
    check(TRAE_SCRIPT.is_file(), "Trae workflow_profile.py is missing")
    check(CODEX_SCRIPT.read_bytes() == CLAUDE_SCRIPT.read_bytes(), "Codex workflow profile script drift")
    check(TRAE_SCRIPT.read_bytes() == CLAUDE_SCRIPT.read_bytes(), "Trae workflow profile script drift")

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
