"""CHECK 2 -- declared_format_cross_check (structural claims). See
RESEARCH_HYPOTHESIS.txt Section 3.

Assumption under test: a checkpoint's accompanying claim about its own
format matches what the file's own bytes actually are. Phase 1 uses a
small, explicit sidecar JSON claim file (`{"declared_format": "..."}`)
rather than parsing a real model card -- named as a deliberate
simplification, not silently done: real model-card parsing (reusing
claim-card's own doc-discovery convention) is a later phase, not
required to get a first real reading on this check's own logic.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..format_sniff import sniff_format
from ..model import CheckResult, Observation


def declared_format_cross_check(
    checkpoint_path: str | Path, claim_path: str | Path
) -> CheckResult:
    checkpoint_path = Path(checkpoint_path)
    claim_path = Path(claim_path)

    if not checkpoint_path.is_file():
        return CheckResult(
            "declared_format_cross_check",
            Observation.UNKNOWN,
            f"no such checkpoint file: {checkpoint_path}",
        )
    if not claim_path.is_file():
        return CheckResult(
            "declared_format_cross_check",
            Observation.UNKNOWN,
            f"no such claim file: {claim_path}",
        )

    try:
        claim = json.loads(claim_path.read_text())
        declared = claim["declared_format"]
    except (json.JSONDecodeError, KeyError) as exc:
        return CheckResult(
            "declared_format_cross_check",
            Observation.UNKNOWN,
            f"claim file unreadable or missing 'declared_format': {exc}",
        )

    actual = sniff_format(str(checkpoint_path)).value

    if declared == actual:
        return CheckResult(
            "declared_format_cross_check",
            Observation.PASS,
            f"declared format {declared!r} matches actual format {actual!r}",
        )

    return CheckResult(
        "declared_format_cross_check",
        Observation.FAIL,
        f"declared format {declared!r} does NOT match actual format {actual!r}",
    )
