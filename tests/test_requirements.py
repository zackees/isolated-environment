"""
Unit test file.
"""

import unittest

from isolated_environment.requirements import Requirements


class RequirementsTesting(unittest.TestCase):
    """Main tester class."""

    def test_simple_requirements(self) -> None:
        """Tests simple requirements."""
        reqs = Requirements(["package1", "package2", "package3"])

        for req in reqs:
            self.assertIn(req.package_name, ["package1", "package2", "package3"])
            self.assertIsNone(req.enum_operator)
            self.assertIsNone(req.semversion)

    def test_single_package_with_version(self) -> None:
        """Tests single package with version."""
        reqs = Requirements(["package==1.0.0", "package2>=1.0.0"])

        self.assertEqual(len(reqs), 2)
        self.assertEqual(reqs[0].package_name, "package")
        self.assertEqual(reqs[0].enum_operator, "==")
        self.assertEqual(reqs[0].semversion, "1.0.0")

    def test_package_with_greater_less_not_equal_operators(self) -> None:
        """Tests package with greater than, less than, and not equal to operators."""
        reqs = Requirements(["package1>1.0.0", "package2<2.0.0", "package3!=3.0.0"])

        self.assertEqual(len(reqs), 3)
        self.assertEqual(reqs[0].package_name, "package1")
        self.assertEqual(reqs[0].enum_operator, ">")
        self.assertEqual(reqs[0].semversion, "1.0.0")
        self.assertEqual(reqs[1].package_name, "package2")
        self.assertEqual(reqs[1].enum_operator, "<")
        self.assertEqual(reqs[1].semversion, "2.0.0")
        self.assertEqual(reqs[2].package_name, "package3")
        self.assertEqual(reqs[2].enum_operator, "!=")
        self.assertEqual(reqs[2].semversion, "3.0.0")

    def test_package_with_greater_less_equal_operators(self) -> None:
        """Tests package with greater than or equal to, and less than or equal to operators."""
        reqs = Requirements(["package1>=1.0.0", "package2<=2.0.0"])

        self.assertEqual(len(reqs), 2)
        self.assertEqual(reqs[0].package_name, "package1")
        self.assertEqual(reqs[0].enum_operator, ">=")
        self.assertEqual(reqs[0].semversion, "1.0.0")
        self.assertEqual(reqs[1].package_name, "package2")
        self.assertEqual(reqs[1].enum_operator, "<=")
        self.assertEqual(reqs[1].semversion, "2.0.0")

    def test_extra_index_url_mismatch(self) -> None:
        """Tests extra index url mismatch."""
        reqs = Requirements(
            [
                "package1==1.0.0 --extra-index-url https://pypi.org/simple",
                "package2>=1.0.0 --extra-index-url https://test.pypi.org/simple",
            ]
        )

        self.assertEqual(len(reqs), 2)
        self.assertEqual(reqs[0].package_name, "package1")
        self.assertEqual(reqs[0].enum_operator, "==")
        self.assertEqual(reqs[0].semversion, "1.0.0")
        self.assertEqual(
            reqs[0].build_options, "--extra-index-url https://pypi.org/simple"
        )
        self.assertEqual(reqs[1].package_name, "package2")
        self.assertEqual(reqs[1].enum_operator, ">=")
        self.assertEqual(reqs[1].semversion, "1.0.0")
        self.assertEqual(
            reqs[1].build_options, "--extra-index-url https://test.pypi.org/simple"
        )

    def test_extra_index_url_absence(self) -> None:
        """Tests absence of extra index url."""
        reqs = Requirements(
            [
                "package1==1.0.0 --extra-index-url https://pypi.org/simple",
                "package2>=1.0.0",
            ]
        )

        self.assertEqual(len(reqs), 2)
        self.assertEqual(reqs[0].package_name, "package1")
        self.assertEqual(reqs[0].enum_operator, "==")
        self.assertEqual(reqs[0].semversion, "1.0.0")
        self.assertEqual(
            reqs[0].build_options, "--extra-index-url https://pypi.org/simple"
        )
        self.assertEqual(reqs[1].package_name, "package2")
        self.assertEqual(reqs[1].enum_operator, ">=")
        self.assertEqual(reqs[1].semversion, "1.0.0")
        self.assertIsNone(reqs[1].build_options)

    def test_has(self) -> None:
        """Tests absence of extra index url."""
        deps = [
            "package1==1.0.0 --extra-index-url https://pypi.org/simple",
            "package2>=1.0.0",
        ]
        reqs = Requirements(deps)
        self.assertIn("package1==1.0.0 --extra-index-url https://pypi.org/simple", reqs)
        self.assertIn("package2>=1.0.0", reqs)
        self.assertIn(deps, reqs)


if __name__ == "__main__":
    unittest.main()
