"""
Subprocess test runner and automatic framework detector.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    command: str
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    output_summary: str


class TestRunner:
    """Detects and runs project tests."""
    __test__ = False

    def __init__(self, repo_dir: Path, custom_cmd: Optional[str] = None, timeout: int = 45):
        self.repo_dir = repo_dir
        self.custom_cmd = custom_cmd
        self.timeout = timeout

    def detect_test_command(self) -> str:
        """Auto-detect test command based on repo markers."""
        if self.custom_cmd:
            return self.custom_cmd

        # Python
        if (self.repo_dir / "pytest.ini").is_file() or (self.repo_dir / "pyproject.toml").is_file() or (self.repo_dir / "tests").is_dir():
            return "pytest"
        if (self.repo_dir / "setup.py").is_file():
            return "python -m unittest discover"

        # Node / JS
        if (self.repo_dir / "package.json").is_file():
            return "npm test"

        # Rust
        if (self.repo_dir / "Cargo.toml").is_file():
            return "cargo test"

        # Go
        if (self.repo_dir / "go.mod").is_file():
            return "go test ./..."

        return "pytest"

    def run_tests(self, command: Optional[str] = None) -> TestResult:
        """Executes test suite and captures output."""
        cmd_str = command or self.detect_test_command()
        env = os.environ.copy()
        py_bin_dir = str(Path(sys.executable).parent)
        if py_bin_dir not in env.get("PATH", ""):
            env["PATH"] = f"{py_bin_dir}:{env.get('PATH', '')}"

        try:
            res = subprocess.run(
                cmd_str,
                cwd=str(self.repo_dir),
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )
            passed = (res.returncode == 0)
            combined_output = (res.stdout + "\n" + res.stderr).strip()
            summary = "\n".join(combined_output.splitlines()[-25:]) if combined_output else "No output"
            return TestResult(
                command=cmd_str,
                passed=passed,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                output_summary=summary,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                command=cmd_str,
                passed=False,
                exit_code=-1,
                stdout="",
                stderr="Execution timed out",
                output_summary=f"Test timed out after {self.timeout}s",
            )
        except Exception as e:
            return TestResult(
                command=cmd_str,
                passed=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                output_summary=f"Failed to run test command: {e}",
            )
