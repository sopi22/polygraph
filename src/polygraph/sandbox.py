"""bubblewrap-based isolated execution. The only sandbox mechanism this
project uses (entropy budget: sandbox mechanism = 1, bwrap) -- see
RESEARCH.txt Clarification Gate for why Docker is named but not used.

Bind strategy, verified by hand against a real bwrap invocation before
being written here (a filesystem-write-outside-bind test initially
succeeded when only /usr,/lib,/bin were explicitly bound -- bwrap's own
synthetic root is writable by default unless the real root is itself
bound read-only first): bind the entire real filesystem read-only
(`--ro-bind / /`), then punch exactly one writable hole for the scratch
directory. Network is fully unshared, not filtered -- no interface is
configured at all inside the sandbox.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class SandboxUnavailableError(Exception):
    """bwrap itself isn't available or failed to start -- an
    infrastructure problem, not a signal about the artifact under
    test. Callers must map this to an UNKNOWN observation, never FAIL,
    same rule Pulse's AdbTransportError follows for the same reason."""


@dataclass(frozen=True)
class SandboxResult:
    returncode: int
    stdout: str
    stderr: str
    scratch_files: list[str]  # filenames that appeared in the scratch dir


def run_sandboxed(
    script_path: Path,
    script_args: list[str],
    scratch_dir: Path,
    read_only_binds: dict[Path, Path] | None = None,
    timeout_seconds: float = 15.0,
) -> SandboxResult:
    """Run `python3 <script_path> <script_args...>` inside bwrap.

    The real filesystem is bound read-only in its entirety; `scratch_dir`
    is the one writable exception. `read_only_binds` lets a caller expose
    additional read-only paths at a different in-sandbox location (used
    to hand the checkpoint file to the loader at a fixed path) -- these
    are still read-only, so they don't weaken the write isolation.
    """
    if shutil.which("bwrap") is None:
        raise SandboxUnavailableError("bwrap not found on PATH")

    scratch_dir.mkdir(parents=True, exist_ok=True)

    argv = [
        "bwrap",
        "--ro-bind", "/", "/",
        "--bind", str(scratch_dir), str(scratch_dir),
    ]
    for host_path, sandbox_path in (read_only_binds or {}).items():
        argv += ["--ro-bind", str(host_path), str(sandbox_path)]
    argv += [
        "--proc", "/proc",
        "--dev", "/dev",
        "--unshare-net",
        "--unshare-pid",
        "--die-with-parent",
        "--new-session",
        "--chdir", str(scratch_dir),
        "python3", str(script_path), *script_args,
    ]

    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout_seconds
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise SandboxUnavailableError(f"{argv!r} failed: {exc}") from exc

    scratch_files = sorted(p.name for p in scratch_dir.iterdir())

    return SandboxResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        scratch_files=scratch_files,
    )
