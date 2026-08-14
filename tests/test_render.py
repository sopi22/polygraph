from polygraph.model import CheckResult, Observation
from polygraph.render import render_table
from polygraph.report import ArtifactReport


def _report():
    return ArtifactReport(
        checkpoint="malicious_pickle.pkl",
        claim="claim_pickle.json",
        results=[
            CheckResult("sandboxed_load", Observation.FAIL, "wrote to scratch"),
            CheckResult("declared_format_cross_check", Observation.PASS, "honest label"),
        ],
    )


def test_render_table_plain_has_no_escape_codes():
    text = render_table(_report(), use_color=False)
    assert "\033[" not in text
    assert "FAIL" in text
    assert "PASS" in text


def test_render_table_color_wraps_observation_values():
    text = render_table(_report(), use_color=True)
    assert "\033[31m" in text  # red, for the FAIL row
    assert "\033[32m" in text  # green, for the PASS row
