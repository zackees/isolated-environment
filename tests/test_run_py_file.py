"""
Unit test file.
"""

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from isolated_environment import isolated_environment, isolated_environment_run

HERE = Path(__file__).parent

RUN_PY = HERE / "run.py"


class MainTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skip("DO NOT USE shell=True for python!!!")
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

    def test_isolated_environment_run(self) -> None:
        """Test command line interface (CLI)."""
        with TemporaryDirectory() as tmp_dir:
            venv_path = Path(tmp_dir) / "venv"
            cp = isolated_environment_run(
                env_path=venv_path,
                requirements=[],
                cmd_list=["python", str(RUN_PY)],
                capture_output=True,
            )
            self.assertEqual(0, cp.returncode)
            self.assertEqual("Hello World!\n", cp.stdout)


if __name__ == "__main__":
    unittest.main()
