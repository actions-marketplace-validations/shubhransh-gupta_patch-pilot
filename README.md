# 🤖 Patch Pilot

An autonomous test-driven code healing and bug patching agent powered by Google Gemini.

Patch Pilot inspects your local repository, analyzes bug descriptions, pinpoints root-cause files, iteratively applies patches, executes your test suite, and feeds back error stack traces until tests pass and changes are committed cleanly to Git.

## 🌟 Key Capabilities

- **Automatic Test Runner Detection**: Supports `pytest`, `unittest`, `npm test`, `cargo test`, and `go test` with zero configuration.
- **Iterative Self-Healing Loop**: If a patch fails the test suite, Patch Pilot captures the exact error tracebacks and re-prompts Gemini to refine the fix.
- **Git Branch & Commit Automation**: Automatically isolates changes in a dedicated Git feature branch and writes conventional commit messages upon test verification.
- **Powered by Gemini**: Fast inference, high reasoning quality, and support for large codebases.

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/shubhransh-gupta/patch-pilot.git
cd patch-pilot
pip install -e .
```

### 2. Configure Gemini API Key

```bash
export GEMINI_API_KEY="AIzaSy..."
```

### 3. Run Patch Pilot Inside Any Repo

```bash
cd my-project/
patch-pilot "Fix KeyError when parsing optional config headers in client.py"
```

Or target a specific test command:

```bash
patch-pilot "Resolve edge-case in user session expiration" --test-cmd "pytest tests/test_session.py"
```

## ⚙️ Options

```bash
patch-pilot [ISSUE] [OPTIONS]

Options:
  --repo, -r PATH         Path to local repository (default: .)
  --test-cmd, -t TEXT     Custom test command (e.g. 'pytest tests/test_auth.py')
  --max-attempts, -m INT  Max self-healing iterations (default: 4)
  --model TEXT            Gemini model identifier (default: gemini-2.5-flash)
  --api-key, -k TEXT      Explicit Gemini API key override
  --no-branch             Skip automatic git branch creation
```

## 📦 Project Structure

```
patch-pilot/
├── patch_pilot/
│   ├── agent.py       # Core self-healing loop and diagnosis orchestrator
│   ├── runner.py      # Subprocess test executor and framework detector
│   ├── git_ops.py     # Git branch and commit wrapper
│   ├── config.py      # Configuration and model settings
│   └── cli.py         # Rich terminal interface
└── pyproject.toml     # Packaging and entry points
```

## 📄 License

MIT License. Copyright (c) 2026 Shubhransh Gupta.
