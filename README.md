# 🤖 Patch Pilot

[![Documentation](https://img.shields.io/badge/Documentation-Apple%20HIG%20Style-blue?style=for-the-badge&logo=vercel)](https://agent-docs-coral.vercel.app#patch-pilot)
[![GitHub Stars](https://img.shields.io/github/stars/shubhransh-gupta/patch-pilot?style=for-the-badge&color=30d158)](https://github.com/shubhransh-gupta/patch-pilot/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **📖 Live Documentation & Interactive FAQs:** [https://agent-docs-coral.vercel.app#patch-pilot](https://agent-docs-coral.vercel.app#patch-pilot)

<p align="center">
  <img src="assets/demo.svg" alt="Patch Pilot Live Terminal Demo" width="100%" />
</p>

An autonomous test-driven code healing and bug patching agent with **universal model support**.

Patch Pilot inspects your local repository, analyzes bug descriptions, pinpoints root-cause files, iteratively applies patches, executes your test suite, and feeds back error stack traces until tests pass and changes are committed cleanly to Git.

## 🌐 Universal Model Support (Bring Your Own Key)

Patch Pilot works with all major AI providers or entirely local setups:

| Provider | Supported Models | Environment Variable |
| :--- | :--- | :--- |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022`, `claude-3-7-sonnet` | `export ANTHROPIC_API_KEY="..."` |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini` | `export OPENAI_API_KEY="..."` |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro` | `export GEMINI_API_KEY="..."` |
| **DeepSeek** | `deepseek-chat`, `deepseek-reasoner` | `export DEEPSEEK_API_KEY="..."` |
| **NVIDIA Nemotron** | `nvidia/nemotron-4-340b-instruct` | `export NVIDIA_API_KEY="..."` |
| **OpenRouter** | 200+ models across all frontier labs | `export OPENROUTER_API_KEY="..."` |
| **Local / Self-Hosted** | Ollama (`qwen2.5-coder`, `llama3.2`, `deepseek-r1`), vLLM | `--base-url http://localhost:11434/v1` |

## 🌟 Key Capabilities

- **Multi-Model Intelligence**: Fix code using Claude 3.5 Sonnet, GPT-4o, Gemini 2.5, DeepSeek-Coder, or local Ollama.
- **Automatic Test Runner Detection**: Supports `pytest`, `unittest`, `npm test`, `cargo test`, and `go test` with zero configuration.
- **Iterative Self-Healing Loop**: If a patch fails the test suite, Patch Pilot captures the exact error tracebacks and re-prompts the model to refine the fix.
- **Git Branch & Commit Automation**: Automatically isolates changes in a dedicated Git feature branch and writes conventional commit messages upon test verification.

## 🚀 Quick Start

### 1. Installation

Install directly from PyPI:

```bash
pip install patch-pilot-ai
```

Or install from source:

```bash
git clone https://github.com/shubhransh-gupta/patch-pilot.git
cd patch-pilot
pip install -e .
```

### ⚡ Use as a GitHub Action in Your CI/CD

You can drop Patch Pilot directly into any repository's CI pipeline to automatically self-heal failing builds:

```yaml
- name: Run Patch Pilot Self-Healing
  uses: shubhransh-gupta/patch-pilot@v1
  with:
    api-key: ${{ secrets.GEMINI_API_KEY }}
    provider: 'gemini'
    issue: 'Fix failing unit tests in CI build'
```

### 2. Set Your Preferred API Key

Choose any provider:
```bash
# Option A: Anthropic Claude (Great for complex reasoning)
export ANTHROPIC_API_KEY="sk-ant-..."

# Option B: OpenAI
export OPENAI_API_KEY="sk-proj-..."

# Option C: Google Gemini
export GEMINI_API_KEY="AIzaSy..."

# Option D: DeepSeek
export DEEPSEEK_API_KEY="sk-..."
```

### 3. Run Patch Pilot Inside Any Repo

```bash
cd my-project/

# Auto-detects provider from your exported environment variable
patch-pilot "Fix KeyError when parsing optional config headers in client.py"

# Or explicitly choose provider and model
patch-pilot "Fix race condition in token refresher" --provider anthropic --model claude-3-5-sonnet-20241022

# Or run with local Ollama
patch-pilot "Fix off-by-one error in pagination" --base-url http://localhost:11434/v1 --model qwen2.5-coder
```

## ⚙️ Options

```bash
patch-pilot [ISSUE] [OPTIONS]

Options:
  --provider, -p TEXT     LLM provider: gemini, openai, anthropic, deepseek, nvidia, ollama, openrouter
  --model, -m TEXT        Specific model identifier
  --base-url TEXT         Custom API base URL (for Ollama, vLLM, etc.)
  --repo, -r PATH         Path to local repository (default: .)
  --test-cmd, -t TEXT     Custom test command (e.g. 'pytest tests/test_auth.py')
  --max-attempts INT      Max self-healing iterations (default: 4)
  --api-key, -k TEXT      Explicit API key override
  --no-branch             Skip automatic git branch creation
```

## 📦 Project Structure

```
patch-pilot/
├── patch_pilot/
│   ├── agent.py       # Core self-healing loop and diagnosis orchestrator
│   ├── llm.py         # Universal multi-provider LLM interface (Claude/GPT/Gemini/Ollama)
│   ├── runner.py      # Subprocess test executor and framework detector
│   ├── git_ops.py     # Git branch and commit wrapper
│   ├── config.py      # Configuration and model settings
│   └── cli.py         # Rich terminal interface
└── pyproject.toml     # Packaging and entry points
```

## 📄 License

MIT License. Copyright (c) 2026 Shubhransh Gupta.
