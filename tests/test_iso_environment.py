"""
Unit test file.
"""

import json
import subprocess
import sys
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


def get_deps() -> str:
    """Gets the dependencies."""
    out: list[str] = ["static_ffmpeg"]
    if sys.platform != "darwin":
        out.append("--extra-index-url https://download.pytorch.org/whl/cpu")
        out.append("torch==2.1.2")
    return "\n".join(out)


class IsolatedEnvironmentTest(unittest.TestCase):
    """Main tester class."""

    def test_ensure_installed(self) -> None:
        """Tests that ensure_installed works."""
        reqs = get_deps()
        with TemporaryDirectory() as tmp_dir:
            iso_env = IsolatedEnvironment(Path(tmp_dir) / "venv")
            env = iso_env.ensure_installed(reqs, args=["--use-pep517"])
            self.assertTrue(iso_env.installed())
            installed_reqs = iso_env.installed_requirements()
            self.assertEqual(installed_reqs, reqs)
            try:
                subprocess.check_output(
                    ["static_ffmpeg", "--help"],
                    env=env,
                    shell=True,  # shell=True is allowed only when NOT running python.
                )
            except subprocess.CalledProcessError as exc:
                # doesn't fail on Windows, but it does on other platforms
                if sys.platform == "win32":
                    raise exc
            # Second time should be a no-op.
            iso_env.ensure_installed(reqs)
            iso_env.clean()
            self.assertFalse(iso_env.installed())


if __name__ == "__main__":
    unittest.main()
