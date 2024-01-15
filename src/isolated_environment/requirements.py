import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator, List, Tuple, Union

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

    # str representation of the enum
    def __str__(self) -> str:
        return self.value

    # equals operator
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Operator):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented


def comp(a: Any, b: Any) -> bool:
    """Compares two objects."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a == b


@dataclass
class VersionBuild:
    """Designed to handle version strings in pip, which can be like 2.1.2+build1"""

    semversion: semver.VersionInfo
    build: str | None = None

    @staticmethod
    def parse(version: str) -> "VersionBuild":
        """Parses a version string."""
        if "+" in version:
            semversion, build = version.split("+")
        else:
            semversion = version
            build = None
        return VersionBuild(semver.VersionInfo.parse(semversion), build)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VersionBuild):
            return self.semversion == other.semversion and self.build == other.build
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __str__(self) -> str:
        out = str(self.semversion)
        if self.build is not None:
            out += f"+{self.build}"
        return out


@dataclass
class ParsedReq:
    """Parsed requirement"""

    package_name: str
    enum_operator: Operator | None = None
    semversion: VersionBuild | None = None
    build_options: str | None = None

    @staticmethod
    def parse(requirement: str) -> "ParsedReq":
        # Split the requirement string into package name, version and build_options
        operator = None
        semversion = None
        build_options = None
        if "--" in requirement:
            requirement, build_options = requirement.split("--", 1)
            build_options = "--" + build_options
        # strip
        requirement = requirement.strip()
        if build_options is not None:
            build_options = build_options.strip()
        for op in Operator:
            if op.value in requirement:
                package_name, version = requirement.split(op.value)
                operator = op
                semversion = VersionBuild.parse(version)
                break
        else:
            package_name = requirement
        # Return a new ParsedRequirement instance
        return ParsedReq(package_name, operator, semversion, build_options)

    def compare(
        self,
        other_package_name: str,
        other_semversion: VersionBuild | None = None,
        other_build_options: str | None = None,
    ) -> Tuple[bool, bool, bool]:
        """Compares the parsed requirement with another parsed requirement"""
        package_name_matches = comp(self.package_name, other_package_name)
        if not package_name_matches:
            return False, False, False
        semversion_matches = comp(self.semversion, other_semversion)
        build_options_matches = comp(self.build_options, other_build_options)
        return True, semversion_matches, build_options_matches

    def __str__(self) -> str:
        out = self.package_name
        if self.enum_operator is not None:
            out += str(self.enum_operator)
            out += str(self.semversion)
        if self.build_options is not None:
            out += f" {self.build_options}"
        return out

    def get_package_str(self) -> str:
        out = self.package_name
        if self.enum_operator is not None:
            out += str(self.enum_operator)
            out += str(self.semversion)
        return out

    def get_build_options(self) -> str | None:
        return self.build_options


@dataclass
class ParsedReqs:
    """Parsed requirements"""

    reqs: List[ParsedReq]

    def _has_pckg_str(self, line: str) -> bool:
        req = ParsedReq.parse(line)
        for r in self.reqs:
            matches = r.compare(req.package_name, req.semversion, req.build_options)
            if matches[0]:
                return all(matches)
        return False

    def _has_pckg_req(self, req: ParsedReq) -> bool:
        for r in self.reqs:
            matches = r.compare(req.package_name, req.semversion, req.build_options)
            if matches[0]:
                return all(matches)
        return False

    def has(self, other: Union["ParsedReqs", ParsedReq, str, List[str]]) -> bool:
        if isinstance(other, str):
            return self._has_pckg_str(other)
        if isinstance(other, ParsedReq):
            return self._has_pckg_req(other)
        if isinstance(other, list):
            return all(self._has_pckg_str(line) for line in other)
        for req in other.reqs:
            if not self._has_pckg_req(req):
                return False
        return True

    def __contains__(self, other: Union["ParsedReqs", str, List[str]]) -> bool:
        return self.has(other)

    def __len__(self) -> int:
        return len(self.reqs)

    def __getitem__(self, index: int) -> ParsedReq:
        return self.reqs[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.reqs)


class Requirements:
    """Requirements"""

    def __init__(self, packages: list[str]) -> None:
        assert isinstance(packages, list)
        self._packages = packages
        self._parsed = self._parse()

    def has(self, other: Union["Requirements", ParsedReq, str, List[str]]) -> bool:
        if isinstance(other, Requirements):
            return self._parsed.has(other._parsed)  # pylint: disable=protected-access
        return self._parsed.has(other)

    def add(self, other: Union[str, List[str]]) -> None:
        if isinstance(other, str):
            self._packages.append(other)
        elif isinstance(other, list):
            self._packages.extend(other)
        self._parsed = self._parse()

    def _parse(self) -> ParsedReqs:
        """Parses the requirements"""
        reqs = [ParsedReq.parse(package) for package in self._packages]
        return ParsedReqs(reqs)

    def __contains__(
        self, other: Union["Requirements", ParsedReq, str, List[str]]
    ) -> bool:
        return self.has(other)

    def __len__(self) -> int:
        return len(self._parsed)

    def __getitem__(self, index: int) -> ParsedReq:
        return self._parsed[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._parsed)

    def to_json(self) -> str:
        """Returns a JSON representation of the requirements."""
        out = json.dumps(self._packages, indent=4, sort_keys=True)
        return out

    def __str__(self) -> str:
        return self.to_json()

    def __repr__(self) -> str:
        return self.to_json()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Requirements):
            return self._packages == __value._packages
        return NotImplemented

    @staticmethod
    def from_json(json_str: str) -> "Requirements":
        """Returns a Requirements instance from a JSON string."""
        return Requirements(json.loads(json_str))
