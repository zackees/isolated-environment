"""
Unit test file.
"""

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from isolated_environment.api import IsolatedEnvironment

HERE = Path(__file__).parent
TEST_DIR = HERE / "test"


def pretty(data: Any) -> str:
    """Make JSON beautiful."""
    return json.dumps(data, indent=4, sort_keys=True)


class IsolatedEnvironmentTest(unittest.TestCase):
    """Main tester class."""

    def test_isolated_environment(self) -> None:
        """Test command line interface (CLI)."""
        with TemporaryDirectory() as tmp_dir:
            iso_env = IsolatedEnvironment(Path(tmp_dir) / "venv")
            print("pip_list_json before install")
            pip_list_json = pretty(iso_env.pip_list())
            print(pip_list_json)
            with iso_env.lock():
                if not iso_env.installed():
                    iso_env.install_environment()
                    iso_env.pip_install("static-ffmpeg")
                    pip_list_json = pretty(iso_env.pip_list())
                    print("pip_list_json after install")
                    print(pip_list_json)
            self.assertTrue(iso_env.installed())
            env = iso_env.environment()
            subprocess.check_output(["static_ffmpeg", "--help"], env=env, shell=True)
            iso_env.clean()
            self.assertFalse(iso_env.installed())


if __name__ == "__main__":
    unittest.main()
