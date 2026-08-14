"""Runs INSIDE the bwrap sandbox only -- never imported directly by
the rest of the package. Loads a checkpoint file the way it was
already determined to be formatted (sniffed OUTSIDE the sandbox by
polygraph.format_sniff, since sniffing is pure byte-reading and safe
unsandboxed) -- this script's only job is to perform the actual load
under isolation and do nothing else. A completely clean load should
write nothing to disk and touch no network; anything that does either
is the observation, checked by the caller after this process exits.

`declared_format` here means "the format sniff_format() already
determined," not an unverified claim from a model card -- naming
avoided to prevent confusion with CHECK 2's own "declared claim"
concept, which is a different thing (see RESEARCH_HYPOTHESIS.txt).
"""

from __future__ import annotations

import json
import pickle
import struct
import sys


def main() -> None:
    checkpoint_path, detected_format = sys.argv[1], sys.argv[2]

    if detected_format == "safetensors":
        with open(checkpoint_path, "rb") as f:
            (header_len,) = struct.unpack("<Q", f.read(8))
            json.loads(f.read(header_len))
        print("loaded as safetensors")
    else:
        # pickle, or unknown/ambiguous -- unknown is deliberately
        # treated as the riskier path (pickle.load), not skipped,
        # since erring toward caution is the right default for a
        # format sniff_format() couldn't confidently identify.
        with open(checkpoint_path, "rb") as f:
            pickle.load(f)
        print("loaded as pickle")


if __name__ == "__main__":
    main()
