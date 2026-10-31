"""Combined report: runs both checks against one checkpoint (+ its
label file) and writes a single JSON report to one predictable
location -- matching Label Card's own convention (one JSON report,
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
    label: str
    results: list[CheckResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "checkpoint": self.checkpoint,
            "label": self.label,
            "checks": [r.to_dict() for r in self.results],
        }


def run_all_checks(checkpoint_path: str, label_path: str) -> ArtifactReport:
    results = [
        sandboxed_load(checkpoint_path),
        declared_format_cross_check(checkpoint_path, label_path),
    ]
    return ArtifactReport(checkpoint=checkpoint_path, label=label_path, results=results)


def write_report(report: ArtifactReport, out_path: str | Path) -> None:
    Path(out_path).write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    )
