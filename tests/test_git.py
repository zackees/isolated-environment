# pylint: disable=R0801

"""
Tests against the problem of git not being found on the path.
"""
import os
import shutil
import subprocess
import unittest
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment.api import IsolatedEnvironment, _remove_python_paths_from_env

HERE = Path(__file__).parent.absolute()
GIT_PATH = shutil.which("git")
PATH = os.environ["PATH"]


def which_all(name: str, paths: list[str]) -> str | None:
    """Finds the first path that contains the name."""
    for path in paths:
        out = shutil.which(name, path=path)
        if out is not None:
            return out
    return None


class AiderChatTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skipIf(GIT_PATH is None, "git is not installed")
    def test_git_is_not_sliced_out(self) -> None:
        env = os.environ.copy()
        env_modified = _remove_python_paths_from_env(env)
        paths = env_modified["PATH"].split(os.pathsep)
        path = which_all("git", paths=paths)
        self.assertIsNotNone(path)

    @unittest.skipIf(GIT_PATH is None, "git is not installed")
    def test_git_is_still_installed(self) -> None:
        """Tests that ensure_installed works."""
        with TemporaryDirectory() as tmp_dir:
            iso_env = IsolatedEnvironment(
                Path(tmp_dir) / "venv",
                requirements=None,
                full_isolation=True,
            )
            activated_env = iso_env.environment()
            # now create an inner environment without the static-ffmpeg
            cp: subprocess.CompletedProcess = iso_env.run(["git", "--help"], shell=True)
            if cp.returncode != 0:
                warning_message = [
                    "git had some sort of a problem, dumping out the system"
                ]
                warning_message.append(f"system git path: {GIT_PATH}")
                warning_message.append("system path:")
                for p in PATH.split(os.pathsep):
                    warning_message.append(f"  {p}")
                warning_message.append(f"stdout: {cp.stdout}")
                warning_message.append(f"stderr: {cp.stderr}")

                # print environment variables
                path = activated_env["PATH"]
                warning_message.append(f"dumping out the path: {path}")
                for p in path.split(os.pathsep):
                    warning_message.append(f"  {p}")

                activated_env.pop("PATH")
                warning_message.append("dumping out the environment variables")
                for k, v in activated_env.items():
                    warning_message.append(f"{k}: {v}")

                warnings.warn("\n".join(warning_message))
                self.fail("git test had some sort of failure")


if __name__ == "__main__":
    unittest.main()
