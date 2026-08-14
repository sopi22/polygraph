"""The experimental model: locked vocabulary (assumption/probe/
observation/sandbox/cross-check, see RESEARCH_HYPOTHESIS.txt), same
shape as this project family's other two repos' own models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Observation(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CheckResult:
    """A single check's outcome on a single artifact. `check` is the
    provisional, deliberately unambitious identifier for what ran
    (e.g. "sandboxed_load"), not a claim of architectural significance
    -- same convention Pulse's ProbeResult already follows."""

    check: str
    observation: Observation
    detail: str

    def to_dict(self) -> dict:
        return {
            "check": self.check,
            "observation": self.observation.value,
            "detail": self.detail,
        }
