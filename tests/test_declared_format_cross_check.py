from polygraph.checks.declared_format_cross_check import declared_format_cross_check
from polygraph.model import Observation


def test_honest_safetensors_claim_passes(fixtures_dir):
    result = declared_format_cross_check(
        fixtures_dir / "safe_safetensors.bin", fixtures_dir / "claim_safetensors.json"
    )
    assert result.observation is Observation.PASS, result.detail


def test_honest_pickle_claim_passes(fixtures_dir):
    result = declared_format_cross_check(
        fixtures_dir / "safe_pickle.pkl", fixtures_dir / "claim_pickle.json"
    )
    assert result.observation is Observation.PASS, result.detail


def test_mismatched_claim_is_caught(fixtures_dir):
    """Deliberate FAIL-detection case for CHECK 2: a file that is
    actually pickle-format but paired with a claim of safetensors must
    be observed as FAIL, not PASS."""
    result = declared_format_cross_check(
        fixtures_dir / "malicious_pickle.pkl", fixtures_dir / "claim_mismatch.json"
    )
    assert result.observation is Observation.FAIL, (
        "expected FAIL for a mismatched format claim -- if this is PASS, "
        f"the check isn't actually comparing claim to reality: {result.detail}"
    )


def test_missing_claim_file_is_unknown(fixtures_dir):
    result = declared_format_cross_check(
        fixtures_dir / "safe_pickle.pkl", fixtures_dir / "does_not_exist.json"
    )
    assert result.observation is Observation.UNKNOWN
