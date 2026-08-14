"""Builds the small, hand-constructed synthetic fixture set this
project's Phase 1 uses -- deliberately not depending on torch/
safetensors (entropy budget: stdlib only). Run once to (re)generate
examples/fixtures/*.

Fixtures:
  safe_safetensors.bin  -- a real, valid, minimal safetensors file.
  safe_pickle.pkl        -- a plain pickle of ordinary data, no
                             __reduce__ trick -- a clean load should
                             PASS the sandboxed_load check even though
                             it's pickle-format, since the check is
                             about observed behavior, not format alone.
  malicious_pickle.pkl    -- the deliberate FAIL-detection case: a
                             __reduce__ payload that writes a marker
                             file into whatever directory it's run
                             from (the sandbox's scratch dir, since
                             that's the only writable location visible
                             to it) when unpickled.
  claim_safetensors.json / claim_pickle.json / claim_mismatch.json
                          -- sidecar claim files for CHECK 2.
"""

from __future__ import annotations

import json
import pickle
import struct
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent


def build_safetensors(path: Path) -> None:
    header = {
        "weight": {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, 16]},
        "__metadata__": {"format": "pt"},
    }
    header_bytes = json.dumps(header).encode("utf-8")
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(header_bytes)))
        f.write(header_bytes)
        f.write(b"\x00" * 16)


def build_safe_pickle(path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump({"weights": [0.1, 0.2, 0.3], "meta": "ordinary data, no tricks"}, f)


class _MaliciousReduce:
    """Deliberate FAIL-detection payload: on unpickling, runs a shell
    command that writes a marker file into the current working
    directory -- which, inside the sandbox, is set to the one
    writable scratch directory (see sandbox.py's --chdir). A clean
    load never writes anything, so this file's mere appearance is the
    FAIL signal sandboxed_load.py checks for."""

    def __reduce__(self):
        import os

        return (os.system, ("touch polygraph_marker_of_compromise",))


def build_malicious_pickle(path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(_MaliciousReduce(), f)


class _MaliciousReduceOutsideScratch:
    """A second, harder deliberate FAIL-detection case: targets an
    absolute path entirely outside the scratch dir, with its own
    stderr redirected to another path also outside scratch. This
    variant leaves scratch empty and the process exiting 0 -- caught
    only because the shell's own blocked-redirect error leaks into
    stderr (see checks/sandboxed_load.py's _ESCAPE_ATTEMPT_SIGNATURES,
    added specifically because this exact fixture caught a real gap
    in the first version of the check during Phase 1)."""

    def __reduce__(self):
        import os

        return (
            os.system,
            (
                "touch /tmp/polygraph_outside_attack_marker "
                "2>/tmp/polygraph_attack_stderr.txt",
            ),
        )


def build_malicious_pickle_outside_scratch(path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(_MaliciousReduceOutsideScratch(), f)


def build_claims() -> None:
    (FIXTURES_DIR / "claim_safetensors.json").write_text(
        json.dumps({"declared_format": "safetensors"}, indent=2) + "\n"
    )
    (FIXTURES_DIR / "claim_pickle.json").write_text(
        json.dumps({"declared_format": "pickle"}, indent=2) + "\n"
    )
    # deliberately wrong claim, for CHECK 2's own FAIL-detection case:
    # claims safetensors but will be paired with the pickle fixture.
    (FIXTURES_DIR / "claim_mismatch.json").write_text(
        json.dumps({"declared_format": "safetensors"}, indent=2) + "\n"
    )


def main() -> None:
    build_safetensors(FIXTURES_DIR / "safe_safetensors.bin")
    build_safe_pickle(FIXTURES_DIR / "safe_pickle.pkl")
    build_malicious_pickle(FIXTURES_DIR / "malicious_pickle.pkl")
    build_malicious_pickle_outside_scratch(
        FIXTURES_DIR / "malicious_pickle_outside_scratch.pkl"
    )
    build_claims()
    print(f"fixtures written to {FIXTURES_DIR}")


if __name__ == "__main__":
    main()
