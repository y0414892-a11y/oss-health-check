import tempfile
import unittest
from pathlib import Path

from oss_health_check.scanner import format_report, scan_project


class ScanProjectTests(unittest.TestCase):
    def test_empty_repository_reports_missing_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = scan_project(Path(tmp))

        self.assertEqual(report.passed_count, 0)
        self.assertEqual(report.missing_count, 13)
        self.assertEqual(
            [(category.name, category.passed_count, category.total_count) for category in report.category_scores],
            [("Documentation", 0, 6), ("Community", 0, 5), ("Automation", 0, 2)],
        )
        self.assertEqual(
            [result.name for result in report.next_steps],
            ["README", "README installation section", "README usage section"],
        )

    def test_repository_with_core_files_passes_expected_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n\n## Installation\n\n## Quick Start\n\n## Example Output\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

            report = scan_project(root)

        passed_names = {result.name for result in report.results if result.passed}
        self.assertIn("README", passed_names)
        self.assertIn("README installation section", passed_names)
        self.assertIn("README usage section", passed_names)
        self.assertIn("README example section", passed_names)
        self.assertIn("README image alt text", passed_names)
        self.assertIn("License", passed_names)
        self.assertIn("Contributing guide", passed_names)
        self.assertIn("Tests", passed_names)

    def test_format_report_includes_score_and_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            report = scan_project(root)

        output = format_report(report)

        self.assertIn("Score: 3/13", output)
        self.assertIn("Categories:", output)
        self.assertIn("- Documentation: 3/6 (50%)", output)
        self.assertIn("- Community: 0/5 (0%)", output)
        self.assertIn("- Automation: 0/2 (0%)", output)
        self.assertIn("Next steps:", output)
        self.assertIn("- Documentation: Add an Installation or Setup section to the README.", output)
        self.assertIn("- Documentation: Add a Usage or Quick Start section to the README.", output)
        self.assertIn("- Community: Add a license so people know how they may use the project.", output)
        self.assertIn("Checks:", output)
        self.assertIn("[ok] README", output)
        self.assertIn("[ok] README example section", output)
        self.assertIn("[ok] README image alt text", output)
        self.assertIn("[missing] README installation section", output)
        self.assertIn("[missing] README usage section", output)
        self.assertIn("[missing] License", output)

    def test_readme_image_without_alt_text_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n\n![  ](screenshot.png)\n", encoding="utf-8")

            report = scan_project(root)

        result = next(result for result in report.results if result.name == "README image alt text")
        self.assertFalse(result.passed)
        self.assertEqual(result.category, "Documentation")

    def test_format_report_says_when_no_next_steps_are_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n\n## Installation\n\n## Quick Start\n\n## Example Output\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "test.yml").write_text("name: Test\n", encoding="utf-8")
            (root / ".github" / "ISSUE_TEMPLATE").mkdir()
            (root / ".github" / "ISSUE_TEMPLATE" / "bug.md").write_text("# Bug\n", encoding="utf-8")
            (root / ".github" / "pull_request_template.md").write_text("# PR\n", encoding="utf-8")
            (root / "SECURITY.md").write_text("# Security\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

            report = scan_project(root)

        self.assertEqual(report.next_steps, ())
        self.assertIn("No missing checks", format_report(report))


if __name__ == "__main__":
    unittest.main()
