from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

from .api import IsolatedEnvironment  # noqa: F401
from .requirements import Requirements  # noqa: F401

__all__ = ["isolated_environment"]


def isolated_environment(
    env_path: Path, requirements: list[str] | None = None
) -> dict[str, Any]:
    """Creates an isolated environment."""
    requirements = requirements or []
    reqs = Requirements(requirements)
    iso_env = IsolatedEnvironment(env_path, reqs)
    env = iso_env.environment()
    return env


def isolated_environment_cmd(
    env_path: Path,
    cmd_list: list[str],
    requirements: list[str] | None,
) -> CompletedProcess:
    """Creates an isolated environment."""
    requirements = requirements or []
    reqs = Requirements(requirements)
    iso_env = IsolatedEnvironment(env_path, reqs)
    iso_env.ensure_installed(reqs)
    cp = iso_env.run(cmd_list)
    return cp
