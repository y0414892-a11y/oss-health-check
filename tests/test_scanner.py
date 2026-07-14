import tempfile
import unittest
from pathlib import Path

from oss_health_check.scanner import format_report, scan_project


class ScanProjectTests(unittest.TestCase):
    def test_empty_repository_reports_missing_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = scan_project(Path(tmp))

        self.assertEqual(report.passed_count, 0)
        self.assertEqual(report.missing_count, 9)

    def test_repository_with_core_files_passes_expected_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

            report = scan_project(root)

        passed_names = {result.name for result in report.results if result.passed}
        self.assertIn("README", passed_names)
        self.assertIn("License", passed_names)
        self.assertIn("Contributing guide", passed_names)
        self.assertIn("Tests", passed_names)

    def test_format_report_includes_score_and_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            report = scan_project(root)

        output = format_report(report)

        self.assertIn("Score: 1/9", output)
        self.assertIn("[ok] README", output)
        self.assertIn("[missing] License", output)


if __name__ == "__main__":
    unittest.main()

