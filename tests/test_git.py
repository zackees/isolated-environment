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

from isolated_environment.api import IsolatedEnvironment

HERE = Path(__file__).parent.absolute()
GIT_PATH = shutil.which("git")


class AiderChatTester(unittest.TestCase):
    """Main tester class."""

    def test_ensure_installed(self) -> None:
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
                warning_message.append(f"stdout: {cp.stdout}")
                warning_message.append(f"stderr: {cp.stderr}")

                # print environment variables
                path = activated_env["PATH"]
                warning_message.append(f"dumping out the path: {path}")
                for p in path.split(os.pathsep):
                    warning_message.append(f"Path: {p}")

                activated_env.pop("PATH")
                warning_message.append("dumping out the environment variables")
                for k, v in activated_env.items():
                    warning_message.append(f"{k}: {v}")

                warnings.warn("\n".join(warning_message))
                self.fail("git test had some sort of failure")


if __name__ == "__main__":
    unittest.main()
