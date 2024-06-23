"""
Unit test file.
"""

import os
import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment.api import IsolatedEnvironment

HERE = Path(__file__).parent.absolute()
TEST_DATA = HERE / "test_data"
INNER_PY = TEST_DATA / "inner.py"

assert INNER_PY.exists(), f"Missing: {INNER_PY}"


class FullIoslationTester(unittest.TestCase):
    """Main tester class."""

    def test_ensure_installed(self) -> None:
        """Tests that ensure_installed works."""
        with TemporaryDirectory() as tmp_dir:
            prev_dir = os.getcwd()
            os.chdir(tmp_dir)
            shutil.copy(INNER_PY, tmp_dir)
            try:
                iso_env = IsolatedEnvironment(
                    Path(tmp_dir) / "venv",
                    requirements="static-ffmpeg",
                    full_isolation=True,
                )
                # now create an inner environment without the static-ffmpeg
                cp: subprocess.CompletedProcess = iso_env.run(["python", "inner.py"])
                cp = iso_env.run(["python", "inner.py"])
                self.assertEqual(0, cp.returncode)
            finally:
                os.chdir(prev_dir)


if __name__ == "__main__":
    unittest.main()
