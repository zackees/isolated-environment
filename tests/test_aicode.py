# pylint: disable=R0801

"""
Tests against a bug in aicode which uses isolated-environment.
"""

import subprocess
import unittest
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
                requirements="advanced-aicode",
                full_isolation=True,
            )
            # now create an inner environment without the static-ffmpeg
            cmd_list = ["aicode", "--help"]
            cp: subprocess.CompletedProcess = iso_env.run(
                cmd_list, shell=False, capture_output=True
            )
            stdout = cp.stdout
            stderr = cp.stderr
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            self.assertEqual(0, cp.returncode)


if __name__ == "__main__":
    unittest.main()
