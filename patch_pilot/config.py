"""
Configuration for Patch Pilot agent.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List


def load_env():
    """Load nearby .env file if available."""
    for p in [Path.cwd() / ".env", Path.cwd() / ".env.local", Path.home() / ".config" / "patch-pilot" / ".env"]:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


load_env()


@dataclass
class PatchConfig:
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    model: str = "gemini-2.5-flash"
    fallback_models: List[str] = field(default_factory=lambda: [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-4-hydrogen"
    ])
    max_healing_attempts: int = 4
    test_command: Optional[str] = None
    timeout_per_run: int = 45
    target_repo_dir: Path = field(default_factory=Path.cwd)
    create_branch: bool = True
    branch_prefix: str = "fix/patch-pilot"

    def validate(self):
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set.\n"
                "Please set it via environment variable: export GEMINI_API_KEY='your-key'\n"
                "Get a free Gemini API key at: https://aistudio.google.com/"
            )
