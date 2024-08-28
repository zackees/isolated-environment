"""
Module to create an isolated environment. Like Pipx but allows
the ability to create an environment in a specific directory and
then populate it with packages incrementally. Also allows the
ability to run commands in the environment.
"""

import json
import os
import shutil
import subprocess
import sys
import venv
import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Any, Iterator

from filelock import FileLock

WARNED_ONCE = int(os.environ.get("SILENCE_FULL_ISOLATION_WARNING", "0")) == 1


@dataclass
class ActivatedEnvironment:
    """An activated environment."""

    env: dict[str, str]
    python: Path
    pip: Path


def _create_virtual_env(env_path: Path) -> Path:
    """Creates an empty virtual environment in the current directory using venv."""

    # Create parent directories
    env_path.parent.mkdir(parents=True, exist_ok=True)
    # Create the virtual environment
    venv.create(env_path, with_pip=True)
    env_name = env_path.name
    print(f"Virtual environment '{env_name}' created at {env_path}")
    return env_path


def has_python_or_pip(path: str) -> bool:
    """Returns True if python or pip is in the path."""
    python = which("python", path=path) or which("python3", path=path)
    pip = which("pip", path=path) or which("pip3", path=path)
    return (python is not None) or (pip is not None)


def _get_activated_environment(
    env_path: Path, full_isolation: bool
) -> ActivatedEnvironment:
    """Gets the activate environment for the environment."""
    global WARNED_ONCE  # pylint: disable=global-statement
    if full_isolation:
        if not WARNED_ONCE:
            warnings.warn("Warning: full_isolation is deprecated and now ignored.")
            WARNED_ONCE = True
    out_env = os.environ.copy()
    # set VIRTUAL_ENV to make sure Python finds the correct packages
    out_env["VIRTUAL_ENV"] = str(env_path)
    scripts = "Scripts" if sys.platform == "win32" else "bin"
    python_name = "python.exe" if sys.platform == "win32" else "python"
    python = env_path / scripts / python_name
    pip = env_path / scripts / "pip"
    activate_environment: ActivatedEnvironment = ActivatedEnvironment(
        env=out_env, python=python, pip=pip
    )
    return activate_environment


def _pip_install_all(
    env_path: Path, requiresments: str, full_isolation: bool, args: list[str] | None
) -> None:
    """Installs all the packages"""
    act_env = _get_activated_environment(env_path, full_isolation)
    # write out requirements file
    req_file = env_path / "requirements.txt"
    req_file.write_text(requiresments)
    cmd_list = [str(act_env.pip), "install"]
    if args:
        cmd_list += args
    cmd_list += ["-r"]
    cmd_list += [str(req_file)]
    cmd = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cmd}")
    subprocess.run(cmd, env=act_env.env, shell=True, check=True)


class IsolatedEnvironment:
    """An isolated environment."""

    def __init__(
        self,
        env_path: Path,
        requirements: str | None = None,
        full_isolation: bool = False,  # For absolute isolation, set to False
    ) -> None:
        self.env_path = env_path
        self.full_isolation = full_isolation
        self.env_path.mkdir(parents=True, exist_ok=True)
        # file_lock is side-by-side with the environment.
        self.file_lock = FileLock(str(env_path) + ".lock")
        self.requirements = env_path / "requirements.txt"
        self.ensure_installed(requirements)

    def install_environment(self) -> None:
        """Installs the environment."""
        assert (
            not self.installed()
        ), f"The environment {self.env_path} is already installed."
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
            shutil.rmtree(self.env_path, ignore_errors=True)

    def _read_reqs(self) -> str | None:
        """Reads the packages.json file."""
        data = self.requirements.read_text()
        if data == "None":
            return None
        return data

    @contextmanager
    def lock(self) -> Iterator[None]:
        """Locks the environment to prevent it from being used."""
        self.file_lock.acquire()
        try:
            yield
        finally:
            self.file_lock.release()

    def environment(self) -> dict[str, str]:
        """Gets the activated environment, which should be applied to subprocess environments."""
        return _get_activated_environment(self.env_path, self.full_isolation).env

    def run(self, cmd_list: list[str], **kwargs) -> subprocess.CompletedProcess:
        """Runs a command in the environment."""
        act_env = _get_activated_environment(self.env_path, self.full_isolation)
        env = act_env.env
        capture_output = kwargs.get("capture_output", False)
        if "capture_output" in kwargs:
            del kwargs["capture_output"]
        check = kwargs.get("check", False)
        if "check" in kwargs:
            del kwargs["check"]

        universal_newlines = kwargs.get("universal_newlines", True)
        if "universal_newlines" in kwargs:
            del kwargs["universal_newlines"]
        text = kwargs.get("text", universal_newlines)
        if "text" in kwargs:
            del kwargs["text"]
        shell = kwargs.get("shell", False)
        cmd_or_cmd_list = subprocess.list2cmdline(cmd_list) if shell else cmd_list
        cp = subprocess.run(
            cmd_or_cmd_list,
            env=env,
            check=check,
            text=text,
            capture_output=capture_output,
            universal_newlines=universal_newlines,
            **kwargs,
        )
        return cp

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

    def pip_has(self, packages: list[str]) -> bool:
        """Returns True if the packages are installed."""
        pip_list = self.pip_list()
        pip_list_names = [p["name"] for p in pip_list]  # type: ignore
        for package in packages:
            if package not in pip_list_names:
                return False
        return True

    # Returns an environment dictionary
    def ensure_installed(
        self, reqs: str | None, args: list[str] | None = None
    ) -> dict[str, Any]:
        """Ensures that the packages are installed."""
        with self.lock():
            prev_reqs: str | None = (
                self.requirements.read_text() if self.requirements.exists() else None
            )
            if prev_reqs == "None":
                prev_reqs = None
            if reqs != prev_reqs:
                self.clean()
            if not self.installed():
                self.install_environment()
            if prev_reqs == reqs:
                return self.environment()
            if reqs:
                # write the requirements
                self.requirements.write_text(reqs)
                # install the requirements
                _pip_install_all(self.env_path, reqs, self.full_isolation, args)
            return self.environment()

    def installed_requirements(self) -> str | None:
        """Returns a list of installed requirements."""
        return self._read_reqs()
