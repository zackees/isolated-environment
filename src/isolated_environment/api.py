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


def _remove_python_paths_from_env(env: dict[str, str]) -> dict[str, str]:
    """Removes PYTHONPATH from the environment."""
    out_env = env.copy()
    if "PYTHONPATH" in out_env:
        del out_env["PYTHONPATH"]
    path_list = out_env["PATH"].split(os.pathsep)

    exported_path_list: list[str] = []
    for p in path_list:
        if not has_python_or_pip(p):
            exported_path_list.append(p)
    exported_path_list = [os.path.basename(sys.executable)] + exported_path_list
    out_env["PATH"] = os.pathsep.join(exported_path_list)
    return out_env


def _get_activated_environment(
    env_path: Path, full_isolation: bool
) -> ActivatedEnvironment:
    """Gets the activate environment for the environment."""
    out_env = os.environ.copy()
    if full_isolation:
        out_env = _remove_python_paths_from_env(out_env)
    if sys.platform == "win32":
        out_env["PATH"] = str(env_path / "Scripts") + ";" + out_env["PATH"]
    else:
        out_env["PATH"] = str(env_path / "bin") + ":" + out_env["PATH"]

    # set PYTHONPATH to make sure Python finds installed packages
    if sys.platform == "win32":
        out_env["PYTHONPATH"] = str(env_path / "Lib" / "site-packages")
    else:
        out_env["PYTHONPATH"] = str(env_path / "lib" / "site-packages")

    scripts = "Scripts" if sys.platform == "win32" else "bin"
    python_name = "python.exe" if sys.platform == "win32" else "python"
    python = env_path / scripts / python_name
    pip = env_path / scripts / "pip"
    activate_environment: ActivatedEnvironment = ActivatedEnvironment(
        env=out_env, python=python, pip=pip
    )
    return activate_environment


def _pip_install(
    env_path: Path, package: str, build_options: str | None, full_isolation: bool
) -> None:
    """Installs a package in the virtual environment."""
    # Activate the environment and install packages
    act_env: ActivatedEnvironment = _get_activated_environment(env_path, full_isolation)
    cmd_list = [str(act_env.pip), "install", package]
    if build_options:
        cmd_list.extend(build_options.split(" "))
    cmd = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cmd}")
    subprocess.run(cmd, env=act_env.env, shell=True, check=True)


def _package_name(package: str) -> str:
    """Splits a package into name and version."""
    for f in WARN_OPERATOR:
        if f in package:
            return package.split(f)[0]
    return package


class IsolatedEnvironment:
    """An isolated environment."""

    def __init__(
        self,
        env_path: Path,
        requirements: Requirements | None = None,
        full_isolation: bool = False,  # For absolute isolation, set to False
    ) -> None:
        self.env_path = env_path
        self.full_isolation = full_isolation
        self.env_path.mkdir(parents=True, exist_ok=True)
        # file_lock is side-by-side with the environment.
        self.file_lock = FileLock(str(env_path) + ".lock")
        self.packages_json = env_path / "packages.json"
        self.ensure_installed(requirements or Requirements([]))

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
        self,
        package: str | list[str],
        build_options: str | None,
        full_isolation: bool,
    ) -> None:
        """Installs a package in the virtual environment."""
        assert (
            self.env_path.exists()
        ), f"The environment {self.env_path} doesn't exist, install it first."
        reqs = self._read_reqs()
        if isinstance(package, list):
            for p in package:
                _pip_install(self.env_path, p, build_options, full_isolation)
                reqs.add(package)
        elif isinstance(package, str):
            _pip_install(self.env_path, package, build_options, full_isolation)
            reqs.add(package)
        else:
            raise TypeError(f"Unknown type for package: {type(package)}")
        self._write_reqs(reqs)

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
        assert "shell" not in kwargs, "shell passed in, we only support shell=False."
        if "shell" in kwargs and kwargs["shell"]:
            if "python" in cmd_list[0]:
                raise ValueError(
                    f"shell=True and python in {cmd_list}, this will drop you into "
                    + "the python interpreter in linux and you will not be able to exit."
                )

        universal_newlines = kwargs.get("universal_newlines", True)
        if "universal_newlines" in kwargs:
            del kwargs["universal_newlines"]
        text = kwargs.get("text", universal_newlines)
        if "text" in kwargs:
            del kwargs["text"]
        if cmd_list and (
            cmd_list[0] == "python"
            or cmd_list[0] == "python.exe"
            or cmd_list[0] == "python3"
        ):
            cmd_list[0] = str(act_env.python)
        if cmd_list and (
            cmd_list[0] == "pip" or cmd_list[0] == "pip.exe" or cmd_list[0] == "pip3"
        ):
            cmd_list[0] = str(act_env.pip)
        cp = subprocess.run(
            cmd_list,
            env=env,
            shell=False,
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
                    self.pip_install(
                        package=package_str,
                        build_options=build_options,
                        full_isolation=self.full_isolation,
                    )
            self._write_reqs(reqs)
            return self.environment()

    def installed_requirements(self) -> Requirements:
        """Returns a list of installed requirements."""
        return self._read_reqs()
