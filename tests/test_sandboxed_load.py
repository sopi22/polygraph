"""Live tests -- these actually invoke bwrap, not a mock. Skipped
cleanly if bwrap isn't on PATH, same pattern Pulse's live-device tests
use for adb."""

from __future__ import annotations

import shutil

import pytest

from polygraph.checks.sandboxed_load import sandboxed_load
from polygraph.model import Observation

pytestmark = pytest.mark.skipif(
    shutil.which("bwrap") is None, reason="bwrap not available -- skipping live sandbox tests"
)


def test_safe_safetensors_passes(fixtures_dir):
    result = sandboxed_load(fixtures_dir / "safe_safetensors.bin")
    assert result.observation is Observation.PASS, result.detail


def test_safe_pickle_passes(fixtures_dir):
    # deliberately pickle-format but with no __reduce__ trick -- must
    # PASS on behavior even though it's the "riskier" format, since
    # this check is about observed behavior, not format alone.
    result = sandboxed_load(fixtures_dir / "safe_pickle.pkl")
    assert result.observation is Observation.PASS, result.detail


def test_malicious_pickle_writing_into_cwd_is_caught(fixtures_dir):
    """Deliberate FAIL-detection case #1 (required before any PASS
    result counts, per RESEARCH_HYPOTHESIS.txt's falsification
    criteria): a payload that writes a marker file into the sandbox's
    scratch directory (its CWD) must be observed as FAIL, not PASS."""
    result = sandboxed_load(fixtures_dir / "malicious_pickle.pkl")
    assert result.observation is Observation.FAIL, (
        "expected FAIL for a payload that writes into the sandbox's own "
        f"writable directory -- if this is PASS, the check isn't actually "
        f"detecting compromise: {result.detail}"
    )
    assert "polygraph_marker_of_compromise" in result.detail


def test_malicious_pickle_targeting_outside_scratch_is_caught(fixtures_dir):
    """Deliberate FAIL-detection case #2: a payload that targets an
    absolute path entirely outside scratch (with its own stderr
    redirected outside scratch too) leaves scratch empty and exits 0
    -- this is the case that caught a real gap in the first version of
    this check during Phase 1 (see checks/sandboxed_load.py). Must
    still be observed as FAIL via the stderr escape-attempt signature."""
    result = sandboxed_load(fixtures_dir / "malicious_pickle_outside_scratch.pkl")
    assert result.observation is Observation.FAIL, (
        "expected FAIL for a payload that attempted a write outside the "
        f"sandbox entirely -- if this is PASS, the check only catches "
        f"attacks that happen to land inside scratch: {result.detail}"
    )


def test_nonexistent_file_is_unknown_not_fail():
    result = sandboxed_load("/does/not/exist.pkl")
    assert result.observation is Observation.UNKNOWN
