from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Union

from .api import IsolatedEnvironment  # noqa: F401
from .requirements import Requirements  # noqa: F401


# Note: be very careful when using shell=True and executing
# the python interpreter.  On linux it will drop you into the
# python interpreter and you will not be able to exit.
def isolated_environment(
    env_path: Union[Path, str], requirements: list[str] | None = None
) -> dict[str, Any]:
    """Creates an isolated environment."""
    if isinstance(env_path, str):
        env_path = Path(env_path)  # type: ignore
    requirements = requirements or []
    reqs = Requirements(requirements)
    iso_env = IsolatedEnvironment(env_path, reqs)
    env = iso_env.environment()
    return env


def isolated_environment_run(
    env_path: Union[Path, str],
    requirements: list[str] | None,
    cmd_list: list[str],
    **kwargs: Any,
) -> CompletedProcess:
    """
    Creates an isolated environment. Note that by default:
      shell=False,
      capture_output=False,
      universal_newlines=True,
      text=universal_newlines,
    If "python" is in cmd_list[0], then shell=True will cause a ValueError
    """
    if isinstance(env_path, str):
        env_path = Path(env_path)  # type: ignore
    requirements = requirements or []
    reqs = Requirements(requirements)
    iso_env = IsolatedEnvironment(env_path, reqs)
    iso_env.ensure_installed(reqs)
    cp = iso_env.run(cmd_list, **kwargs)
    return cp


isolated_environment_cmd = isolated_environment_run  # backwards compatibility
