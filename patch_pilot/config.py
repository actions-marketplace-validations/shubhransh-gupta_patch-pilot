"""
Configuration for Patch Pilot agent supporting multiple LLM providers.
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
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_healing_attempts: int = 4
    test_command: Optional[str] = None
    timeout_per_run: int = 45
    target_repo_dir: Path = field(default_factory=Path.cwd)
    create_branch: bool = True
    branch_prefix: str = "fix/patch-pilot"

    def validate(self):
        available_keys = [
            self.api_key,
            os.getenv("GEMINI_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENROUTER_API_KEY"),
            os.getenv("DEEPSEEK_API_KEY"),
            os.getenv("NVIDIA_API_KEY"),
            self.base_url,
        ]
        if not any(available_keys):
            raise ValueError(
                "No API Key found.\n"
                "Please set one of the following environment variables:\n"
                "  • export GEMINI_API_KEY='...'\n"
                "  • export OPENAI_API_KEY='...'\n"
                "  • export ANTHROPIC_API_KEY='...'\n"
                "  • export DEEPSEEK_API_KEY='...'\n"
                "  • export NVIDIA_API_KEY='...'\n"
                "Or pass --api-key / --base-url."
            )
