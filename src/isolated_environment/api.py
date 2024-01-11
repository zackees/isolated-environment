"""
Module to create an isolated environment. Like Pipx but allows
the ability to create an environment in a specific directory and
then populate it with packages incrementally. Also allows the
ability to run commands in the environment.
"""


import sys
import subprocess
from pathlib import Path
import venv


def _create_virtual_env(env_path: Path) -> Path:
    """Creates an empty virtual environment in the current directory using venv."""

    # Create the virtual environment
    venv.create(env_path, with_pip=True)
    env_name = env_path.name
    print(f"Virtual environment '{env_name}' created at {env_path}")
    return env_path


def _pip_install(env_path: Path, package: str, extra_index: str | None = None) -> None:
    """Installs a package in the virtual environment."""
    # Activate the environment and install packages
    activate_bin = env_path / "bin" / "activate"
    if sys.platform == "win32":
        activate_bin = env_path / "Scripts" / "activate.bat"
    cmd_list = [
        activate_bin,
        "&&",
        'pip',
        'install',
        package
    ]
    if extra_index:
        cmd_list.extend(['--extra-index-url', extra_index])
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
        assert self.env_path.exists(), f"The environment {self.env_path} doesn't exist, install it first."
        _pip_install(self.env_path, package, extra_index)

    def run(self, cmd_list: list[str]) -> int:
        """Runs a command in the environment."""
        activate_bin = self.env_path / "bin" / "activate"
        if sys.platform == "win32":
            activate_bin = self.env_path / "Scripts" / "activate.bat"
        cmd = subprocess.list2cmdline(
            [
                activate_bin,
                "&&",
                *cmd_list
            ]
        )
        if self.verbose:
            print(f"Running: {cmd}")
        return subprocess.run(cmd, shell=True, check=True)