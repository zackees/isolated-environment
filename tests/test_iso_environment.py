"""
Unit test file.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment.api import IsolatedEnvironment

HERE = Path(__file__).parent
TEST_DIR = HERE / "test"


class IsolatedEnvironmentTest(unittest.TestCase):
    """Main tester class."""

    def test_isolated_environment(self) -> None:
        """Test command line interface (CLI)."""
        with TemporaryDirectory() as tmp_dir:
            iso_env = IsolatedEnvironment(Path(tmp_dir) / "venv")
            iso_env.install_environment()
            iso_env.pip_install("static-ffmpeg")
            rtn = iso_env.run(["static_ffmpeg", "--help"])
            self.assertEqual(0, rtn)


if __name__ == "__main__":
    unittest.main()