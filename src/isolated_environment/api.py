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
from pathlib import Path
from typing import Any, Iterator

from filelock import FileLock

from isolated_environment.requirements import Requirements

WARN_OPERATOR = [  # _todo: implement operator support
    "==",
    ">=",
    "<=",
    ">",
    "<",
    "~=",
    "!=",
]


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

    # set PYTHONPATH to make sure Python finds installed packages
    if sys.platform == "win32":
        out_env["PYTHONPATH"] = str(env_path / "Lib" / "site-packages")
    else:
        out_env["PYTHONPATH"] = str(env_path / "lib" / "site-packages")
    return out_env


def _pip_install(
    env_path: Path, package: str, build_options: str | None = None
) -> None:
    """Installs a package in the virtual environment."""
    # Activate the environment and install packages
    env = _get_activated_environment(env_path)
    cmd_list = ["pip", "install", package]
    if build_options:
        cmd_list.extend(build_options.split(" "))
    cmd = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cmd}")
    subprocess.run(cmd, env=env, shell=True, check=True)


def _package_name(package: str) -> str:
    """Splits a package into name and version."""
    for f in WARN_OPERATOR:
        if f in package:
            return package.split(f)[0]
    return package


class IsolatedEnvironment:
    """An isolated environment."""

    def __init__(
        self, env_path: Path, requirements: Requirements | None = None
    ) -> None:
        self.env_path = env_path
        self.env_path.mkdir(parents=True, exist_ok=True)
        # file_lock is side-by-side with the environment.
        self.file_lock = FileLock(str(env_path) + ".lock")
        self.packages_json = env_path / "packages.json"
        if requirements is not None:
            self.ensure_installed(requirements)

    def install_environment(self) -> None:
        """Installs the environment."""
        assert (
            not self.installed()
        ), f"The environment {self.env_path} is already installed."
        self.env_path = _create_virtual_env(self.env_path)
        # write the packages.json file
        empty_reqs = Requirements([])
        self._write_reqs(empty_reqs)

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

    def _read_reqs(self) -> Requirements:
        """Reads the packages.json file."""
        if not self.packages_json.exists():
            return Requirements([])
        out = self.packages_json.read_text()
        data = Requirements.from_json(out)
        return data

    def _write_reqs(self, reqs: Requirements) -> None:
        """Writes the packages.json file."""
        out = reqs.to_json()
        self.packages_json.write_text(out)

    @contextmanager
    def lock(self) -> Iterator[None]:
        """Locks the environment to prevent it from being used."""
        self.file_lock.acquire()
        try:
            yield
        finally:
            self.file_lock.release()

    def pip_install(
        self, package: str | list[str], build_options: str | None = None
    ) -> None:
        """Installs a package in the virtual environment."""
        assert (
            self.env_path.exists()
        ), f"The environment {self.env_path} doesn't exist, install it first."
        reqs = self._read_reqs()
        if isinstance(package, list):
            for p in package:
                _pip_install(self.env_path, p, build_options)
                reqs.add(package)
        elif isinstance(package, str):
            _pip_install(self.env_path, package, build_options)
            reqs.add(package)
        else:
            raise TypeError(f"Unknown type for package: {type(package)}")
        self._write_reqs(reqs)

    def environment(self) -> dict[str, str]:
        """Gets the activated environment, which should be applied to subprocess environments."""
        return _get_activated_environment(self.env_path)

    def run(self, cmd_list: list[str]) -> subprocess.CompletedProcess:
        """Runs a command in the environment."""
        env = self.environment()
        cmd = subprocess.list2cmdline(cmd_list)
        cp = subprocess.run(cmd, env=env, shell=True, check=True)
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
        for p in packages:
            for f in WARN_OPERATOR:
                if f in p:
                    warnings.warn(
                        f"Warning: The package {p} has an operator {f} in "
                        + "it and we don't support version matching yet."
                    )
        for package in packages:
            package_name = _package_name(package)
            if package_name not in pip_list_names:
                return False
        return True

    # Returns an environment dictionary
    def ensure_installed(self, reqs: Requirements) -> dict[str, Any]:
        """Ensures that the packages are installed."""
        with self.lock():
            if not self.installed():
                self.install_environment()
            prev_reqs = self._read_reqs()
            if reqs == prev_reqs:
                return self.environment()
            list_reqs = list(reqs)
            for req in list_reqs:
                if req not in prev_reqs:
                    package_str = req.get_package_str()
                    build_options = req.build_options
                    self.pip_install(package=package_str, build_options=build_options)
            self._write_reqs(reqs)
            return self.environment()

    def installed_requirements(self) -> Requirements:
        """Returns a list of installed requirements."""
        return self._read_reqs()
