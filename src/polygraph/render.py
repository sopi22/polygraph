"""Human-readable claimed-vs-observed table for the CLI. Pure
function, no side effects -- the JSON report (report.py) stays the
one source of truth; this is presentation only, built on top of it,
never a second place PASS/FAIL logic could diverge.
"""

from __future__ import annotations

from .report import ArtifactReport

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_COLOR_BY_OBSERVATION = {"PASS": _GREEN, "FAIL": _RED, "UNKNOWN": _YELLOW}


def render_table(report: ArtifactReport, use_color: bool = True) -> str:
    name_width = max(len(r.check) for r in report.results)
    lines = [
        f"CHECKPOINT: {report.checkpoint}",
        f"CLAIM FILE: {report.claim}",
        "",
        f"  {'CHECK':<{name_width}}  OBSERVED",
        f"  {'-' * name_width}  --------",
    ]
    for r in report.results:
        value = r.observation.value
        if use_color:
            color = _COLOR_BY_OBSERVATION.get(value, "")
            shown = f"{_BOLD}{color}{value}{_RESET}"
        else:
            shown = value
        lines.append(f"  {r.check:<{name_width}}  {shown}")
    lines.append("")
    for r in report.results:
        lines.append(f"  [{r.check}] {r.detail}")
    return "\n".join(lines)
