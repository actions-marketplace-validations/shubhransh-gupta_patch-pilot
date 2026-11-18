"""
Git operations wrapper for Patch Pilot.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple


class GitRepo:
    """Helper for git repository manipulation."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def _run(self, args: list) -> Tuple[int, str, str]:
        res = subprocess.run(
            ["git"] + args,
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
        )
        return res.returncode, res.stdout, res.stderr

    def is_git_repo(self) -> bool:
        code, out, _ = self._run(["rev-parse", "--is-inside-work-tree"])
        return code == 0 and "true" in out

    def get_diff(self) -> str:
        code, out, _ = self._run(["diff"])
        return out

    def create_and_checkout_branch(self, branch_name: str) -> bool:
        code, _, _ = self._run(["checkout", "-b", branch_name])
        if code != 0:
            # Try switching to it if it already exists
            code, _, _ = self._run(["checkout", branch_name])
        return code == 0

    def stage_all_and_commit(self, message: str) -> bool:
        self._run(["add", "-A"])
        code, out, err = self._run(["commit", "-m", message])
        return code == 0

    def get_status(self) -> str:
        _, out, _ = self._run(["status", "--short"])
        return out
