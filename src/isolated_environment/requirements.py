from dataclasses import dataclass
from enum import Enum

import semver


class Operator(Enum):
    """Enum for requirement operator"""

    EQ = "=="
    GE = ">="
    LE = "<="
    GT = ">"
    LT = "<"
    NE = "!="
    APPROX = "~="


@dataclass
class Req:
    """Parsed requirement"""

    package_name: str
    enum_operator: Operator | None = None
    semversion: semver.VersionInfo | None = None

    @staticmethod
    def parse(requirement: str) -> "Req":
        # Split the requirement string into package name and version
        operator = None
        semversion = None
        for op in Operator:
            if op.value in requirement:
                package_name, version = requirement.split(op.value)
                operator = op
                semversion = semver.VersionInfo.parse(version)
                break
        else:
            package_name = requirement
        # Return a new ParsedRequirement instance
        return Req(package_name, operator, semversion)

    def compare(self, other_package_name: str, other_semversion: semver.VersionInfo):
        if self.package_name != other_package_name:
            return False, False

        version_matched = False

        if self.enum_operator is None or self.semversion is None:
            # Handle the case where operator or semversion is None
            return True, version_matched

        if self.enum_operator == Operator.EQ:
            version_matched = self.semversion == other_semversion
        elif self.enum_operator == Operator.GE:
            version_matched = self.semversion >= other_semversion
        elif self.enum_operator == Operator.LE:
            version_matched = self.semversion <= other_semversion
        elif self.enum_operator == Operator.GT:
            version_matched = self.semversion > other_semversion
        elif self.enum_operator == Operator.LT:
            version_matched = self.semversion < other_semversion
        elif self.enum_operator == Operator.NE:
            version_matched = self.semversion != other_semversion
        elif self.enum_operator == Operator.APPROX:
            if self.semversion is not None and other_semversion is not None:
                version_matched = (
                    self.semversion.major == other_semversion.major
                    and self.semversion.minor == other_semversion.minor
                )

        return True, version_matched


@dataclass
class Requirements:
    """Requirements"""

    packages: list[str]

    def parse(self) -> list[Req]:
        return [Req.parse(package) for package in self.packages]
