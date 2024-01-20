"""
Unit test file.
"""

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment import isolated_environment

HERE = Path(__file__).parent

RUN_PY = HERE / "run.py"


class MainTester(unittest.TestCase):
    """Main tester class."""

    def test_shell(self) -> None:
        """Test command line interface (CLI)."""
        with TemporaryDirectory() as tmp_dir:
            venv_path = Path(tmp_dir) / "venv"
            env = isolated_environment(venv_path, [])
            cmd_list = [
                "python",
                str(RUN_PY),
            ]
            stdout: str = subprocess.check_output(
                cmd_list, env=env, shell=True, universal_newlines=True
            )
            self.assertEqual("Hello World!\n", stdout)

    def test_no_shell(self) -> None:
        """Test command line interface (CLI)."""
        with TemporaryDirectory() as tmp_dir:
            venv_path = Path(tmp_dir) / "venv"
            env = isolated_environment(venv_path, [])
            cmd_list = [
                "python",
                str(RUN_PY),
            ]
            stdout: str = subprocess.check_output(
                cmd_list, env=env, shell=False, universal_newlines=True
            )
            self.assertEqual("Hello World!\n", stdout)


if __name__ == "__main__":
    unittest.main()
