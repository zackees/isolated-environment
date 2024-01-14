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

    def test_single_package_with_version(self) -> None:
        """Tests single package with version."""
        requirements = Requirements(["package==1.0.0", "package2>=1.0.0"])
        parsed_requirements = requirements.parse()

        self.assertEqual(len(parsed_requirements), 2)
        self.assertEqual(parsed_requirements[0].package_name, "package")
        self.assertEqual(parsed_requirements[0].enum_operator, "==")
        self.assertEqual(parsed_requirements[0].semversion, "1.0.0")


if __name__ == "__main__":
    unittest.main()
