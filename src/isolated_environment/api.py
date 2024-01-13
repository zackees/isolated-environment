"""
Module to create an isolated environment. Like Pipx but allows
the ability to create an environment in a specific directory and
then populate it with packages incrementally. Also allows the
ability to run commands in the environment.
"""

import json
import os
import subprocess
import sys
import venv
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from filelock import FileLock


def _create_virtual_env(env_path: Path) -> Path:
    """Creates an empty virtual environment in the current directory using venv."""

    # Create parent directories
    env_path.parent.mkdir(parents=True, exist_ok=True)
    # Create the virtual environment
    venv.create(env_path, with_pip=True)
    env_name = env_path.name
    print(f"Virtual environment '{env_name}' created at {env_path}")
    return env_path


def _get_activated_environment(env_path: Path) -> dict[str, str]:
    """Gets the activate environment for the environment."""
    out_env = os.environ.copy()
    if sys.platform == "win32":
        out_env["PATH"] = str(env_path / "Scripts") + ";" + out_env["PATH"]
    else:
        out_env["PATH"] = str(env_path / "bin") + ":" + out_env["PATH"]
    return out_env


def _pip_install(env_path: Path, package: str, extra_index: str | None = None) -> None:
    """Installs a package in the virtual environment."""
    # Activate the environment and install packages
    env = _get_activated_environment(env_path)
    cmd_list = ["pip", "install", package]
    if extra_index:
        cmd_list.extend(["--extra-index-url", extra_index])
    cmd = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cmd}")
    subprocess.run(cmd, env=env, shell=True, check=True)


class IsolatedEnvironment:
    """An isolated environment."""

    def __init__(self, env_path: Path, verbose: bool = False) -> None:
        self.env_path = env_path
        self.env_path.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        # file_lock is side-by-side with the environment.
        self.file_lock = FileLock(str(env_path) + ".lock")

    def install_environment(self) -> None:
        """Installs the environment."""
        self.env_path = _create_virtual_env(self.env_path)

    def installed(self) -> bool:
        """Returns True if the environment is installed."""
        if not self.env_path.exists():
            return False
        if sys.platform == "win32":
            return self.env_path.exists() and (self.env_path / "Scripts").exists()
        return self.env_path.exists() and (self.env_path / "bin").exists()

    def clean(self) -> None:
        """Cleans the environment."""
        if self.env_path.exists():
            if sys.platform == "win32":
                (self.env_path / "Scripts").rmdir()
            else:
                (self.env_path / "bin").rmdir()
            self.env_path.rmdir()

    @contextmanager
    def lock(self) -> Iterator[None]:
        """Locks the environment to prevent it from being used."""
        self.file_lock.acquire()
        try:
            yield
        finally:
            self.file_lock.release()

    def pip_install(self, package: str, extra_index: str | None = None) -> None:
        """Installs a package in the virtual environment."""
        assert (
            self.env_path.exists()
        ), f"The environment {self.env_path} doesn't exist, install it first."
        _pip_install(self.env_path, package, extra_index)

    def environment(self) -> dict[str, str]:
        """Gets the activated environment, which should be applied to subprocess environments."""
        return _get_activated_environment(self.env_path)

    def run(self, cmd_list: list[str]) -> int:
        """Runs a command in the environment."""
        env = self.environment()
        cmd = subprocess.list2cmdline(cmd_list)
        if self.verbose:
            print(f"Running: {cmd}")
        return subprocess.run(cmd, env=env, shell=True, check=True).returncode

    def pip_list(self) -> dict[str, Any]:
        """Returns a dictionary of installed packages."""
        if not self.installed():
            return {}
        env = self.environment()
        cmd_list = ["pip", "list", "--format", "json"]
        cmd = subprocess.list2cmdline(cmd_list)
        completed = subprocess.run(
            cmd,
            env=env,
            shell=True,
            check=True,
            capture_output=True,
            universal_newlines=True,
        )
        stdout = completed.stdout
        out = json.loads(stdout)
        return out  # type: ignore
