# isolated-environment

[![Linting](https://github.com/zackees/isolated-environment/actions/workflows/lint.yml/badge.svg)](https://github.com/zackees/isolated-environment/actions/workflows/lint.yml)
[![MacOS_Tests](https://github.com/zackees/isolated-environment/actions/workflows/push_macos.yml/badge.svg)](https://github.com/zackees/isolated-environment/actions/workflows/push_macos.yml)
[![Ubuntu_Tests](https://github.com/zackees/isolated-environment/actions/workflows/push_ubuntu.yml/badge.svg)](https://github.com/zackees/isolated-environment/actions/workflows/push_ubuntu.yml)
[![Win_Tests](https://github.com/zackees/isolated-environment/actions/workflows/push_win.yml/badge.svg)](https://github.com/zackees/isolated-environment/actions/workflows/push_win.yml)

![image](https://github.com/zackees/isolated-environment/assets/6856673/8dab37f1-0c6e-42ec-9680-2013287baa98)

# Summary

Got pinned dependencies in your python package that make it hard to install? Use isolated-environment to package those up in a runtime `venv` that only your package has access to.

This is a package isolation library designed originally for AI developers to solve the problems
of AI dependency conflicts introduced by the various `pytorch`/`tensorflow`/etc incompatibilities within and between AI apps.

*Install*
```bash
pip install isolated-environment
```

*Runtime*
```python
# Example of running "whisper --help" in an isolated-environment
from pathlib import Path
import subprocess
from isolated_environment import isolated_environment_run

TENSOR_VERSION = "2.1.2"
CUDA_VERSION = "cu121"
EXTRA_INDEX_URL = f"https://download.pytorch.org/whl/{CUDA_VERSION}"
HERE = Path(os.path.abspath(os.path.dirname(__file__)))

venv_path = Path(HERE) / "whisper-venv"
requirements = [
    "whisper-whisper",
    f"torch=={TENSOR_VERSION}+{CUDA_VERSION} --extra-index-url {EXTRA_INDEX_URL}"
]
cmd_list = ["whisper", "--help"]
# Note that shell=False, universal_newlines=True, capture=True
cp: subprocess.CompletedProcess = isolated_environment_run(
    env_path=venv_path,
    requirements=requirements,
    cmd_list=cmd_list)
print(cp.stdout)
```

Install cuda pytorch when nvidia-smi is found:

```python
# This generates an environment that should be passed to subprocess.run(...)
def get_environment() -> dict[str, Any]:
    """Returns the environment suitable for subprocess.run(..., env=env,...)"""
    venv_dir = HERE / "venv" / "whisper"
    deps = [
        "openai-whisper",
    ]
    if has_nvidia_smi():
        deps.append(  # This computer has nvidia cuda installed so install cuda torch.
            f"torch=={TENSOR_VERSION}+{CUDA_VERSION} --extra-index-url {EXTRA_INDEX_URL}"
        )
    else:
        # Install CPU version.
        deps.append(f"torch=={TENSOR_VERSION}")
    env = isolated_environment(venv_dir, deps)
    return env
```

Any changes to the pip requirements list between runs will invoke a call to `pip install`.

It moves the install of your chosen dependencies from **install time** to **runtime**. The benefit of this is that you can query the system
and make choices on what needs to be installed. For example in `pip` you can't conditionally install packages based on whether `nvidia-smi` has
been installed (indicating `cuda` acceleration), but with `isolated-environment` this is straightfoward.

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

# License

This software is free to use for personal and commercial products. However, if you make changes to `isolated-environment` code you must agree to the
following "good-samaritan" stipulations:

  * All changes to `isolated-environment` **MUST** be put into a github fork, linked to this github project (https://github.com/zackees/isolated-environment).
    * That means clicking on the fork button on this repo, and then putting your changes into that fork.

This agreement means that `isolated-environment` can receive additional features from those that benefit from this package, so that others can benefit as well.

This supplemental licensing supersedes any language in the generic license attached. If you merely use `isolated-environment` as is, without modification,
none of this supplemental license applies to you.

# Releases
  * 2.0.0 - Requirements internally is now just a text file. Sequantially installing requirements is now no longer
            possible. Any change to the requirements will cause a full rebuild. This fixes a number of problems
            with how requirements are handled. This should now be much more robust. However, the old api is slightly
            incompatible with the new one so a full api breaking version has been issued.
  * 1.3.4 - Isolation for pip too so that it doesn't bind to the parent pip.
  * 1.3.1 - New `full_isolation` mode to allow packages installed on other parts of the system from binding.
  * 1.3.1 - Update readme.
  * 1.3.0 - Marks a new interface.
  * 1.2.7 - Please use `isolated_environment_run()` instead of `isolated_environment`. The latter has
            footguns when using Linux when invoking `python` and `shell=True`
  * 1.2.6 - Update readme
  * 1.2.4 - Now support more build options, instead of just --extra-index-url.
  * 1.2.3 - All builds green with complex dependencies!
  * 1.2.2 - Tested and fixed complex semversion + build number for isolated_environment
  * 1.2.1 - Fixes `isolated_environment()` not installing deps correctly on first go
  * 1.2.0 - Now just use `isolated_environment()`, more simple.
  * 1.0.6 - `exists` -> `installed()`, adds `pip_list()`, adds `clean()`
  * 1.0.5 - Added `exists()`
  * 1.0.4 - Added `lock()`
  * 1.0.0 - Initial release
