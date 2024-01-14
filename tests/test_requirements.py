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

    def test_package_with_greater_less_not_equal_operators(self) -> None:
        """Tests package with greater than, less than, and not equal to operators."""
        requirements = Requirements(
            ["package1>1.0.0", "package2<2.0.0", "package3!=3.0.0"]
        )
        parsed_requirements = requirements.parse()

        self.assertEqual(len(parsed_requirements), 3)
        self.assertEqual(parsed_requirements[0].package_name, "package1")
        self.assertEqual(parsed_requirements[0].enum_operator, ">")
        self.assertEqual(parsed_requirements[0].semversion, "1.0.0")
        self.assertEqual(parsed_requirements[1].package_name, "package2")
        self.assertEqual(parsed_requirements[1].enum_operator, "<")
        self.assertEqual(parsed_requirements[1].semversion, "2.0.0")
        self.assertEqual(parsed_requirements[2].package_name, "package3")
        self.assertEqual(parsed_requirements[2].enum_operator, "!=")
        self.assertEqual(parsed_requirements[2].semversion, "3.0.0")

    def test_package_with_greater_less_equal_operators(self) -> None:
        """Tests package with greater than or equal to, and less than or equal to operators."""
        requirements = Requirements(
            ["package1>=1.0.0", "package2<=2.0.0"]
        )
        parsed_requirements = requirements.parse()

        self.assertEqual(len(parsed_requirements), 2)
        self.assertEqual(parsed_requirements[0].package_name, "package1")
        self.assertEqual(parsed_requirements[0].enum_operator, ">=")
        self.assertEqual(parsed_requirements[0].semversion, "1.0.0")
        self.assertEqual(parsed_requirements[1].package_name, "package2")
        self.assertEqual(parsed_requirements[1].enum_operator, "<=")
        self.assertEqual(parsed_requirements[1].semversion, "2.0.0")


if __name__ == "__main__":
    unittest.main()
