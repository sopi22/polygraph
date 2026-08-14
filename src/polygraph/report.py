"""Combined report: runs both checks against one checkpoint (+ its
claim file) and writes a single JSON report to one predictable
location -- matching Claim Card's own convention (one JSON report,
one location, no new format).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .checks.declared_format_cross_check import declared_format_cross_check
from .checks.sandboxed_load import sandboxed_load
from .model import CheckResult


@dataclass
class ArtifactReport:
    checkpoint: str
    claim: str
    results: list[CheckResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "checkpoint": self.checkpoint,
            "claim": self.claim,
            "checks": [r.to_dict() for r in self.results],
        }


def run_all_checks(checkpoint_path: str, claim_path: str) -> ArtifactReport:
    results = [
        sandboxed_load(checkpoint_path),
        declared_format_cross_check(checkpoint_path, claim_path),
    ]
    return ArtifactReport(checkpoint=checkpoint_path, claim=claim_path, results=results)


def write_report(report: ArtifactReport, out_path: str | Path) -> None:
    Path(out_path).write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    )
