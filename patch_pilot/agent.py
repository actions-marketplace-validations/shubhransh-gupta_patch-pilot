"""
Autonomous test-driven code healing and bug fixing orchestrator.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config import PatchConfig
from .git_ops import GitRepo
from .runner import TestRunner, TestResult
from .llm import UnifiedLLM

logger = logging.getLogger(__name__)


class PatchPilotAgent:
    """Agent that diagnoses bugs, modifies code, and self-heals iteratively until tests pass."""

    def __init__(self, config: Optional[PatchConfig] = None):
        self.config = config or PatchConfig()
        self.config.validate()

        self.repo_dir = self.config.target_repo_dir.resolve()
        self.git = GitRepo(self.repo_dir)
        self.runner = TestRunner(
            repo_dir=self.repo_dir,
            custom_cmd=self.config.test_command,
            timeout=self.config.timeout_per_run
        )
        self.llm = UnifiedLLM(
            provider=self.config.provider,
            model=self.config.model,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout_per_run * 2,
        )

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.llm.generate(prompt, system_instruction=system_prompt)

    def _collect_repo_files(self) -> List[str]:
        """Lists files in the repository excluding common ignore paths."""
        ignored = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
        files = []
        for root, dirs, filenames in os.walk(self.repo_dir):
            dirs[:] = [d for d in dirs if d not in ignored]
            for f in filenames:
                rel = os.path.relpath(os.path.join(root, f), self.repo_dir)
                if not rel.startswith("."):
                    files.append(rel)
        return files[:150]

    def solve_issue(self, issue_text: str, on_step=None) -> Dict[str, Any]:
        """Orchestrates the entire bug diagnosis, patch application, test healing, and git commit."""
        def log(msg: str):
            if on_step:
                on_step(msg)
            else:
                print(f"[*] {msg}")

        log(f"Starting Patch Pilot in: {self.repo_dir}")
        log(f"Issue description: '{issue_text[:80]}...'")

        # 1. Repo inspection
        files = self._collect_repo_files()
        log(f"Scanned repository tree ({len(files)} files discovered).")

        # 2. Detect test runner
        test_cmd = self.runner.detect_test_command()
        log(f"Target test command: `{test_cmd}`")

        # 3. Create branch if git repo
        branch_name = None
        if self.git.is_git_repo() and self.config.create_branch:
            clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "-", issue_text.lower())[:30].strip("-")
            branch_name = f"{self.config.branch_prefix}/{clean_slug}"
            self.git.create_and_checkout_branch(branch_name)
            log(f"Created working git branch: {branch_name}")

        # 4. Ask Gemini to locate target file and read its contents
        log("Diagnosing relevant files for the bug...")
        locate_prompt = f"""
Given the repository file list:
{json.dumps(files, indent=2)}

And the reported issue:
"{issue_text}"

Which file is most likely causing this bug or needs to be modified?
Return ONLY a JSON list of 1 to 3 relative file paths. Example:
["src/auth.py", "tests/test_auth.py"]
"""
        target_files_resp = self._call_llm(locate_prompt)
        try:
            match = re.search(r"\[.*\]", target_files_resp, re.DOTALL)
            target_files = json.loads(match.group(0)) if match else [files[0]]
        except Exception:
            target_files = [files[0]] if files else []

        log(f"Identified candidate files: {target_files}")

        # Read contents of candidate files
        context_files = {}
        for tf in target_files:
            fp = self.repo_dir / tf
            if fp.is_file():
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        context_files[tf] = f.read()
                except Exception:
                    pass

        # 5. Iterative Self-Healing Loop
        attempt = 0
        tests_passed = False
        last_test_output = ""
        patched_files = []

        while attempt < self.config.max_healing_attempts and not tests_passed:
            attempt += 1
            log(f"Healing iteration {attempt}/{self.config.max_healing_attempts}...")

            patch_prompt = f"""
Issue to resolve:
"{issue_text}"

Candidate file contents:
{json.dumps(context_files, indent=2)}

Previous test run result / traceback:
{last_test_output or 'Initial run - no previous traceback.'}

TASK:
Provide the complete replacement code for the file that needs fixing.
Respond with a JSON object where each key is the relative file path and each value is the complete, valid file content.
Example:
{{
  "src/module.py": "...full code..."
}}
"""
            system_prompt = (
                "You are an elite principal software engineer. "
                "Fix bugs cleanly while maintaining backward compatibility and adhering to project style. "
                "Return ONLY the requested JSON object."
            )

            raw_patch = self._call_llm(patch_prompt, system_prompt=system_prompt)
            try:
                match = re.search(r"\{.*\}", raw_patch, re.DOTALL)
                patch_dict = json.loads(match.group(0)) if match else {}
            except Exception as e:
                log(f"Failed to parse patch JSON: {e}")
                patch_dict = {}

            if not patch_dict:
                log("No files modified in this attempt.")
                break

            # Apply patch to disk
            for rel_path, new_content in patch_dict.items():
                target_path = self.repo_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                context_files[rel_path] = new_content
                if rel_path not in patched_files:
                    patched_files.append(rel_path)
                log(f"Applied patch to: {rel_path}")

            # Run test suite
            log(f"Executing tests (`{test_cmd}`)...")
            test_res = self.runner.run_tests(test_cmd)

            if test_res.passed:
                log("✅ All tests passed successfully!")
                tests_passed = True
                break
            else:
                log(f"❌ Tests failed (exit code {test_res.exit_code}). Capturing stack trace for self-healing...")
                last_test_output = test_res.output_summary

        # 6. Commit if tests passed and git repo
        commit_message = ""
        if self.git.is_git_repo():
            status = self.git.get_status()
            if status:
                commit_message = f"fix: resolve {issue_text[:50]}"
                self.git.stage_all_and_commit(commit_message)
                log(f"Committed changes with message: '{commit_message}'")

        diff = self.git.get_diff() if self.git.is_git_repo() else ""

        return {
            "success": tests_passed,
            "attempts": attempt,
            "patched_files": patched_files,
            "branch": branch_name,
            "commit_message": commit_message,
            "diff": diff,
            "test_command": test_cmd,
        }
