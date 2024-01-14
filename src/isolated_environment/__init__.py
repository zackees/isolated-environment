from pathlib import Path
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
