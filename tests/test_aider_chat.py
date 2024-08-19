"""
Aider chat was presenting some problems so we have a test to fix this
use case and hopefully fixes a bunch of other installation issues.
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
                requirements="aider-chat",
                full_isolation=True,
            )
            # now create an inner environment without the static-ffmpeg
            cp: subprocess.CompletedProcess = iso_env.run(
                ["aider", "--version"], shell=True
            )
            self.assertEqual(0, cp.returncode)


if __name__ == "__main__":
    unittest.main()
