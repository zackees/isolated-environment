"""
Unit test file.
"""
import unittest

from isolated_environment.requirements import Requirements


class RequirementsTesting(unittest.TestCase):
    """Main tester class."""

    def test_simple_requirements(self) -> None:
        """Tests simple requirements."""
        requirements = Requirements(["package1", "package2", "package3"])
        parsed_requirements = requirements.parse()

        for req in parsed_requirements:
            self.assertIn(req.package_name, ["package1", "package2", "package3"])
            self.assertIsNone(req.enum_operator)
            self.assertIsNone(req.semversion)


if __name__ == "__main__":
    unittest.main()
