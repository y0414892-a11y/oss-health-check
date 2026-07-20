import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from oss_health_check.cli import main


class CliTests(unittest.TestCase):
    def test_fail_under_returns_failure_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = main([tmp, "--fail-under", "80"])

        self.assertEqual(exit_code, 1)

    def test_fail_under_returns_success_at_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = main([tmp, "--fail-under", "0"])

        self.assertEqual(exit_code, 0)

    def test_fail_under_rejects_invalid_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main([tmp, "--fail-under", "101"])

        self.assertEqual(raised.exception.code, 2)

    def test_config_fail_under_returns_failure_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "oss-health-check.json").write_text(json.dumps({"fail_under": 80}), encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = main([tmp])

        self.assertEqual(exit_code, 1)

    def test_cli_fail_under_overrides_config_fail_under(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "oss-health-check.json").write_text(json.dumps({"fail_under": 100}), encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = main([tmp, "--fail-under", "0"])

        self.assertEqual(exit_code, 0)

    def test_json_outputs_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([tmp, "--json"])

        report = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["passed_count"], 0)
        self.assertEqual(report["missing_count"], 13)
        self.assertEqual(report["score_percent"], 0)
        self.assertEqual(report["categories"][0]["name"], "Documentation")
        self.assertEqual(report["categories"][0]["total_count"], 6)
        self.assertEqual(report["next_steps"][0]["name"], "README")
        self.assertEqual(len(report["next_steps"]), 3)
        self.assertEqual(report["results"][0]["name"], "README")
        self.assertEqual(report["results"][0]["category"], "Documentation")

    def test_json_output_includes_configured_ignored_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "oss-health-check.json").write_text(json.dumps({"ignore": ["README"]}), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([tmp, "--json"])

        report = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["ignored_checks"], ["README"])
        self.assertEqual(report["missing_count"], 12)
        self.assertEqual(report["next_steps"][0]["name"], "README installation section")

    def test_unknown_configured_ignored_check_exits_with_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "oss-health-check.json").write_text(json.dumps({"ignore": ["Typo"]}), encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main([tmp])

        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
