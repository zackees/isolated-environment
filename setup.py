"""
Setup file.
"""

import os
import re

from setuptools import setup

URL = "https://github.com/zackees/isolated-environment"
KEYWORDS = "pipx isolated virtual environment"
HERE = os.path.dirname(os.path.abspath(__file__))



if __name__ == "__main__":
    setup(
        maintainer="Zachary Vorhies",
        keywords=KEYWORDS,
        url=URL,
        package_data={"": ["assets/example.txt"]},
        include_package_data=True)

