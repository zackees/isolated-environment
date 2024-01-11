# isolated-environment

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)
[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

```bash
pip install isolated-environment
```

This is a package isolation library designed specifically for AI developers to solve the problems
of AI dependency conflicts introduced by the various `pytorch` incompatibilities within and between AI apps.

In plain words, this package allows you to install your AI apps globally without having to worry about `pytorch`
dependency conflicts.

# Example:


```python
from pathlib import Path
import subprocess

CUDA_VERSION = "cu121"
EXTRA_INDEX_URL = f"https://download.pytorch.org/whl/{CUDA_VERSION}"

HERE = Path(os.path.abspath(os.path.dirname(__file__)))
from isolated_environment import IsolatedEnvironment

iso_env = IsolatedEnvironment(HERE / 'whisper_env')
iso_env.install_environment()
iso_env.pip_install('torch==2.1.2', EXTRA_INDEX_URL)
iso_env.pip_install('openai-whisper')
venv = iso_env.environment()
subprocess.run(['whisper', '--help'], env=venv, shell=True, check=True)
```


# Background

After making my first major AI project `transcribe-anything` I quickly learned that `pytorch` has a lot of different versions of
its library and globally installing the package is an absolute nightmare, especially on Windows. The major problem is that out
of the box in Windows, pytorch does not support `cuda` acceleration, you have to use `pip` with an `--extra-index-url` parameter. If this isn't
done right the first time, you will get a cpu-only version of pytorch which is tricky to remove from the `site-packages` directory, requiring
the developer to `pip uninstall` all packages using `pytorch` and then purge the `pip` cache.

This is a real world example of how I was able to purge the cpu-pytorch from Windows, which took me a lot of trial and error to figure out.

*Without this library, you would have to do something like this to purge cpu-pytorch from the global `site-packages`*

```python
    uninstall = [
        "torch",
        "torchtext",
        "torchdata",
        "torchaudio",
        "torchvision",
        "torch-directml"
    ]
    for package in uninstall:
        subprocess.run(["pip", "uninstall", "-y", package], check=True)
    subprocess.run(["pip", "cache", "purge"], check=True)
```
...yuck

This means that if I install one tool and force the correct dependencies in, another tool relying on those dependencies will **BREAK**.

## `isolated-environment` vs `pipx`

`pipx` seems like a great solution but has major downsides. One downside is that `pipx` is pretty global, it's wants to install a tool
in a global directory and link it to your local bin, which requires a restart or manually adding the path. Also, if you are depending on
two different versions of a tool, then there are going to be conflicts. Additionally, the tool in the `pipx` directory becomes independent
of the package that installed it and requires its own uninstall step, which must be performed manually. And one last final issue with `pipx`
is that creating a virtual environment requires at least one package, before injecting other packages into it. Working around this issue
would require someone to create a dummy package just to get the initial virtual environment constructed, before injecting packages into it. This is a big issue with
`whisper` for example, which requires that cuda-pytorch be installed first, to skip the cpu-pytorch it installs by default.

So given all of these limitations of `pipx`, I created this `isolated-environment` library which solves all of these problems, specifically:

  1. The virtual environment name and path can be specified by our code, and is initially empty, as God intended it.
  2. The virtual environment can live within your `site-packages` directory, so if you uninstall your package then the isolated environment will be removed as well.

This solves the problem for `transcribe-anything` and now all AI dependencies can be installed during runtime in a private environment only accessible
to its package that will be uninstalled if the tool is uninstalled. This means no conflicts with other libs due to `pytorch` cpu vs gpu installs.

The result was pure bliss. You can now install `transcribe-anything` in your global `python`/`pip` directory without having to be concerned
about global conflicts with `pytorch`. As far as I know, no other AI tool does this.

I hope that `isolated-environment` will help you write great AI software without all of the conflicts that currently plague the python ecosystem that every other AI python tool seems to suffer from.

# The downsides

The downside is that it gets a bit trickier to access the tool installed in an `isolated-environment`. For example, installing `transcribe-anything` no longer globally installs
`whisper`, which means to test out `whisper` I have to `cd` to the correct private environment and activate it before invoking the tool.

Another downside, but this also exists within `pipx` is that you can't directly call into Python code within the `isolated-environment`. The only interface that can be used
at this point are command-based apis (anything that `subprocess.run` can invoke). But this is typical of all code that is isolated in its own environment.

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

  * All changes to `isolated-environment` **MUST** be put into a github fork, linked to this project.
    * That means clicking on the fork button on this repo, and then putting your changes into that fork.

This agreement means that `isolated-environment` can receive additional features from those that benefit from this package, so that others can benefit as well.

This supplemental licensing supersedes any language in the generic license attached. If you merely use `isolated-environment` as is, without modification,
none of this supplemental license applies to you.
