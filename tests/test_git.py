# pylint: disable=R0801

"""
Tests against the problem of git not being found on the path.
"""
import os
import subprocess
import unittest
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment.api import IsolatedEnvironment

HERE = Path(__file__).parent.absolute()


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
                warnings.warn("git had some sort of a problem, dumping out the system")
                print(cp.stdout)
                print(cp.stderr)
                # print environment variables
                path = activated_env["PATH"]
                warnings.warn(f"dumping out the path: {path}")
                for p in path.split(os.pathsep):
                    warnings.warn(f"Path: {p}")
                activated_env.pop("PATH")
                warnings.warn("dumping out the environment variables")
                for k, v in activated_env.items():
                    warnings.warn(f"{k}: {v}")
                self.fail("git test had some sort of failure")


if __name__ == "__main__":
    unittest.main()
