"""Pure, stdlib-only detection of a checkpoint file's real structural
format from its raw bytes -- independent of any claim made about it,
and independent of the sandboxed-load check. Never executes the
file's content; only reads and disassembles bytes.

Approximate, like every pattern-based check in this project family
(see claim-card's own vocab/entropy regexes): a heuristic for human
review, not a rigorous format identifier or a finding of fact.
"""

from __future__ import annotations

import json
import pickletools
import struct
from enum import Enum

_MAX_HEADER_LEN = 100_000_000  # sane upper bound -- real safetensors headers are KB-sized


class CheckpointFormat(str, Enum):
    SAFETENSORS = "safetensors"
    PICKLE = "pickle"
    UNKNOWN = "unknown"


def sniff_format(path: str) -> CheckpointFormat:
    with open(path, "rb") as f:
        data = f.read()

    is_safetensors = _looks_like_safetensors(data)
    is_pickle = _looks_like_pickle(data)

    if is_safetensors and not is_pickle:
        return CheckpointFormat.SAFETENSORS
    if is_pickle and not is_safetensors:
        return CheckpointFormat.PICKLE
    # both or neither structurally plausible -- named, not silently guessed
    return CheckpointFormat.UNKNOWN


def _looks_like_safetensors(data: bytes) -> bool:
    """Real safetensors spec: 8-byte little-endian header length, then
    that many bytes of a JSON header describing the tensors."""
    if len(data) < 8:
        return False
    (header_len,) = struct.unpack("<Q", data[:8])
    if header_len <= 0 or header_len > _MAX_HEADER_LEN:
        return False
    if 8 + header_len > len(data):
        return False
    header_bytes = data[8 : 8 + header_len]
    try:
        header = json.loads(header_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    return isinstance(header, dict)


def _looks_like_pickle(data: bytes) -> bool:
    """Disassembles as pickle opcodes without executing anything --
    the same read-only technique picklescan itself uses."""
    try:
        ops = list(pickletools.genops(data))
    except Exception:
        return False
    return len(ops) > 0
