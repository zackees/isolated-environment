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
class Req:
    """Parsed requirement"""

    package_name: str
    enum_operator: Operator | None = None
    semversion: semver.VersionInfo | None = None
    extra_index_url: str | None = None

    @staticmethod
    def parse(requirement: str) -> "Req":
        # Split the requirement string into package name, version and extra_index_url
        operator = None
        semversion = None
        extra_index_url = None
        if "--extra-index-url" in requirement:
            requirement, extra_index_url = requirement.split("--extra-index-url")
        # strip
        requirement = requirement.strip()
        if extra_index_url is not None:
            extra_index_url = extra_index_url.strip()
        for op in Operator:
            if op.value in requirement:
                package_name, version = requirement.split(op.value)
                operator = op
                semversion = semver.VersionInfo.parse(version)
                break
        else:
            package_name = requirement
        # Return a new ParsedRequirement instance
        return Req(package_name, operator, semversion, extra_index_url)

    def compare(
        self,
        other_package_name: str,
        other_semversion: semver.VersionInfo | None = None,
        other_extra_index_url: str | None = None,
    ) -> Tuple[bool, bool, bool]:
        """Compares the parsed requirement with another parsed requirement"""
        package_name_matches = comp(self.package_name, other_package_name)
        if not package_name_matches:
            return False, False, False
        semversion_matches = comp(self.semversion, other_semversion)
        extra_index_url_matches = comp(self.extra_index_url, other_extra_index_url)
        return True, semversion_matches, extra_index_url_matches


@dataclass
class Reqs:
    """Parsed requirements"""

    reqs: List[Req]

    def _has_pckg_str(self, line: str) -> bool:
        req = Req.parse(line)
        return all(
            r.compare(req.package_name, req.semversion, req.extra_index_url)
            for r in self.reqs
        )

    def _has_pckg_req(self, req: Req) -> bool:
        return all(
            r.compare(req.package_name, req.semversion, req.extra_index_url)
            for r in self.reqs
        )

    def has(self, other: Union["Reqs", str, List[str]]) -> bool:
        if isinstance(other, str):
            return self._has_pckg_str(other)
        if isinstance(other, list):
            return all(self._has_pckg_str(line) for line in other)
        for req in other.reqs:
            if not self._has_pckg_req(req):
                return False
        return True

    def __contains__(self, other: Union["Reqs", str, List[str]]) -> bool:
        return self.has(other)

    def __len__(self) -> int:
        return len(self.reqs)

    def __getitem__(self, index: int) -> Req:
        return self.reqs[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.reqs)


@dataclass
class Requirements:
    """Requirements"""

    packages: List[str]

    def parse(self) -> Reqs:
        """Parses the requirements"""
        reqs = [Req.parse(package) for package in self.packages]
        return Reqs(reqs)
