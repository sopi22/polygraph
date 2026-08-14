import json
import shutil

import pytest

from polygraph.report import run_all_checks, write_report

pytestmark = pytest.mark.skipif(
    shutil.which("bwrap") is None, reason="bwrap not available -- skipping live sandbox tests"
)


def test_combined_report_has_both_check_results(fixtures_dir, tmp_path):
    report = run_all_checks(
        str(fixtures_dir / "malicious_pickle.pkl"),
        str(fixtures_dir / "claim_pickle.json"),
    )
    checks = {r.check: r.observation.value for r in report.results}
    assert checks == {"sandboxed_load": "FAIL", "declared_format_cross_check": "PASS"}

    out = tmp_path / "report.json"
    write_report(report, out)
    written = json.loads(out.read_text())
    assert written["checkpoint"] == str(fixtures_dir / "malicious_pickle.pkl")
    assert len(written["checks"]) == 2
