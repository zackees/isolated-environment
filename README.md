# isolated-environment

Like Pipx, but allows creation of an explicit virtual environment and incrementally building it.

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

# Example:

```python
from pathlib import Path

CUDA_VERSION = "cu121"
EXTRA_INDEX_URL = f"https://download.pytorch.org/whl/{CUDA_VERSION}"

HERE = Path(os.path.abspath(os.path.dirname(__file__)))
from isolated_environment import IsolatedEnvironment

iso_env = IsolatedEnvironment(HERE / 'myenvironment')
iso_env.install_environment()
iso_env.pip_install('torch==2.1.2', EXTRA_INDEX_URL)
iso_env.pip_install('openai-whisper')
iso_env.run(['whisper', '--help'])
```

# Development

## Install

  * First time setup
    * clone the repo
    * run `./install`
  * To develop software, run `. ./activate.sh`

# Windows

This environment requires you to use `git-bash`.

# Linting

Run `./lint.sh` to find linting errors using `ruff`, `flake8` and `mypy`.
