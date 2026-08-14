"""CHECK 1 -- sandboxed_load (behavioral). See RESEARCH_HYPOTHESIS.txt
Section 3 for the full design and its named limitation.

Assumption under test: loading this checkpoint touches nothing outside
one declared scratch directory and makes no network attempt. A clean
load is a pure read operation for both formats this project checks
(pickle.load reading a well-formed, non-hostile pickle stream writes
nothing; parsing a safetensors header writes nothing) -- so ANY file
appearing in the scratch directory after the load, or a non-zero exit
from the sandboxed process, is itself the FAIL signal. Nothing more
sophisticated is needed to catch the deliberate FAIL-detection case
(see tests/) because the sandbox's own isolation (RESEARCH.txt: bind
strategy verified by hand) makes "wrote somewhere" and "wrote inside
the one writable directory" the only two possible outcomes for a
write attempt -- there is no third, silent option.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ..format_sniff import sniff_format
from ..model import CheckResult, Observation
from ..sandbox import SandboxUnavailableError, run_sandboxed

_LOADER_SCRIPT = Path(__file__).resolve().parent.parent / "_sandbox_loader.py"

# A blocked escape attempt can leave the process exiting 0 with an
# empty scratch dir -- e.g. `os.system("touch /x 2>/y")` where BOTH /x
# and the stderr redirect target /y are outside scratch: the shell's
# own "cannot create /y: Read-only file system" message leaks into the
# captured stderr even though nothing was written and nothing raised.
# Found by deliberately testing this exact case (see tests/), not
# assumed safe from the scratch-dir/returncode checks alone. These
# signatures are host kernel/shell error text, not attacker-controlled
# strings, so they're a safe basis for a FAIL match.
_ESCAPE_ATTEMPT_SIGNATURES = (
    "read-only file system",
    "permission denied",
    "network is unreachable",
    "operation not permitted",
    "no route to host",
)


def sandboxed_load(checkpoint_path: str | Path) -> CheckResult:
    checkpoint_path = Path(checkpoint_path).resolve()

    if not checkpoint_path.is_file():
        return CheckResult(
            "sandboxed_load", Observation.UNKNOWN, f"no such file: {checkpoint_path}"
        )

    detected_format = sniff_format(str(checkpoint_path))

    with tempfile.TemporaryDirectory(prefix="polygraph-scratch-") as scratch:
        scratch_dir = Path(scratch)
        try:
            result = run_sandboxed(
                script_path=_LOADER_SCRIPT,
                script_args=[str(checkpoint_path), detected_format.value],
                scratch_dir=scratch_dir,
            )
        except SandboxUnavailableError as exc:
            return CheckResult(
                "sandboxed_load", Observation.UNKNOWN, f"sandbox unavailable: {exc}"
            )

        if result.scratch_files:
            return CheckResult(
                "sandboxed_load",
                Observation.FAIL,
                "load wrote to the sandbox's writable directory: "
                f"{result.scratch_files} (a clean load should write nothing) -- "
                f"stderr: {result.stderr.strip()[:500]}",
            )

        if result.returncode != 0:
            return CheckResult(
                "sandboxed_load",
                Observation.FAIL,
                f"load exited {result.returncode} (detected format: "
                f"{detected_format.value}) -- stderr: {result.stderr.strip()[:500]}",
            )

        stderr_lower = result.stderr.lower()
        matched_signature = next(
            (sig for sig in _ESCAPE_ATTEMPT_SIGNATURES if sig in stderr_lower), None
        )
        if matched_signature:
            return CheckResult(
                "sandboxed_load",
                Observation.FAIL,
                "clean exit and empty scratch dir, but stderr shows a blocked "
                f"escape attempt (matched {matched_signature!r}) -- "
                f"stderr: {result.stderr.strip()[:500]}",
            )

        return CheckResult(
            "sandboxed_load",
            Observation.PASS,
            f"load completed cleanly, detected format: {detected_format.value}",
        )
