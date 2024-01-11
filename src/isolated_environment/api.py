"""
Module to create an isolated environment. Like Pipx but allows
the ability to create an environment in a specific directory and
then populate it with packages incrementally. Also allows the
ability to run commands in the environment.
"""

import subprocess
import sys
import venv
from pathlib import Path


def _create_virtual_env(env_path: Path) -> Path:
    """Creates an empty virtual environment in the current directory using venv."""

    # Create parent directories
    env_path.parent.mkdir(parents=True, exist_ok=True)
    # Create the virtual environment
    venv.create(env_path, with_pip=True)
    env_name = env_path.name
    print(f"Virtual environment '{env_name}' created at {env_path}")
    return env_path


def _pip_install(env_path: Path, package: str, extra_index: str | None = None) -> None:
    """Installs a package in the virtual environment."""
    # Activate the environment and install packages
    cmd_list = []
    if sys.platform == "win32":
        cmd_list += [str(env_path / "Scripts" / "activate.bat")]
    else:
        cmd_list += ["/bin/bash", str(env_path / "bin" / "activate")]
    cmd_list += ["&&", "pip", "install", package]
    if extra_index:
        cmd_list.extend(["--extra-index-url", extra_index])
    cmd = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


class IsolatedEnvironment:
    """An isolated environment."""

    def __init__(self, env_path: Path, verbose: bool = False) -> None:
        self.env_path = env_path
        self.verbose = verbose

    def install_environment(self) -> None:
        """Installs the environment."""
        self.env_path = _create_virtual_env(self.env_path)

    def pip_install(self, package: str, extra_index: str | None = None) -> None:
        """Installs a package in the virtual environment."""
        assert (
            self.env_path.exists()
        ), f"The environment {self.env_path} doesn't exist, install it first."
        _pip_install(self.env_path, package, extra_index)

    def make_cmd_list(self, cmd_list: list[str]) -> list[str]:
        """Makes a command to run in the environment."""
        activate_bin = self.env_path / "bin" / "activate"
        if sys.platform == "win32":
            activate_bin = self.env_path / "Scripts" / "activate.bat"
        return [str(activate_bin), "&&", *cmd_list]

    def run(self, cmd_list: list[str]) -> int:
        """Runs a command in the environment."""
        cmd_list = self.make_cmd_list(cmd_list)
        cmd = subprocess.list2cmdline(cmd_list)
        if self.verbose:
            print(f"Running: {cmd}")
        return subprocess.run(cmd, shell=True, check=True).returncode
