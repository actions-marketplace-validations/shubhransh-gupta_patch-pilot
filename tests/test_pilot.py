import pytest
from patch_pilot.config import PatchConfig
from patch_pilot.runner import TestRunner


def test_config_defaults():
    cfg = PatchConfig()
    assert cfg.provider in ("gemini", "openai", "anthropic", None)
    assert cfg.max_healing_attempts > 0


def test_runner_detection(tmp_path):
    runner = TestRunner(repo_dir=tmp_path)
    assert runner.detect_test_command() == "pytest"
