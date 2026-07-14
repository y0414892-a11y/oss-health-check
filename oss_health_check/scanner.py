from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ScanReport:
    root: Path
    results: tuple[CheckResult, ...]

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def missing_count(self) -> int:
        return len(self.results) - self.passed_count

    @property
    def score_percent(self) -> int:
        if not self.results:
            return 0
        return round((self.passed_count / len(self.results)) * 100)


def scan_project(root: Path) -> ScanReport:
    root = root.resolve()
    results = (
        _check_any_file(root, "README", ("README.md", "README.rst", "README.txt"), "Found a README file.", "Add a README with purpose, setup, and usage instructions."),
        _check_any_file(root, "License", ("LICENSE", "LICENSE.md", "COPYING"), "Found a license file.", "Add a license so people know how they may use the project."),
        _check_any_file(root, "Contributing guide", ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"), "Found a contributing guide.", "Add CONTRIBUTING.md with local setup and contribution workflow."),
        _check_tests(root),
        _check_ci(root),
        _check_issue_templates(root),
        _check_any_file(root, "Pull request template", (".github/pull_request_template.md", "PULL_REQUEST_TEMPLATE.md"), "Found a pull request template.", "Add a pull request template with a short review checklist."),
        _check_any_file(root, "Security policy", ("SECURITY.md", ".github/SECURITY.md"), "Found a security policy.", "Add SECURITY.md with vulnerability reporting instructions."),
        _check_any_file(root, "Changelog", ("CHANGELOG.md", "HISTORY.md", "NEWS.md"), "Found a changelog.", "Add CHANGELOG.md to document user-visible changes."),
    )
    return ScanReport(root=root, results=results)


def format_report(report: ScanReport) -> str:
    lines = [
        f"OSS Health Check: {report.root}",
        f"Score: {report.passed_count}/{len(report.results)} ({report.score_percent}%)",
        "",
    ]

    for result in report.results:
        status = "ok" if result.passed else "missing"
        lines.append(f"[{status}] {result.name}")
        lines.append(f"     {result.detail}")

    return "\n".join(lines)


def _check_any_file(
    root: Path,
    name: str,
    candidates: tuple[str, ...],
    found_detail: str,
    missing_detail: str,
) -> CheckResult:
    passed = any((root / candidate).is_file() for candidate in candidates)
    return CheckResult(name=name, passed=passed, detail=found_detail if passed else missing_detail)


def _check_tests(root: Path) -> CheckResult:
    test_paths = (root / "tests", root / "test")
    has_test_dir = any(path.is_dir() and any(path.iterdir()) for path in test_paths)
    has_test_files = any(root.glob("test_*.py")) or any(root.glob("*_test.py"))
    passed = has_test_dir or has_test_files
    detail = "Found test files." if passed else "Add tests so contributors can verify their changes."
    return CheckResult(name="Tests", passed=passed, detail=detail)


def _check_ci(root: Path) -> CheckResult:
    workflow_dir = root / ".github" / "workflows"
    passed = workflow_dir.is_dir() and any(workflow_dir.glob("*.yml")) or any(workflow_dir.glob("*.yaml")) if workflow_dir.exists() else False
    detail = "Found a GitHub Actions workflow." if passed else "Add a CI workflow that runs tests on pull requests."
    return CheckResult(name="Continuous integration", passed=passed, detail=detail)


def _check_issue_templates(root: Path) -> CheckResult:
    template_dir = root / ".github" / "ISSUE_TEMPLATE"
    passed = template_dir.is_dir() and any(template_dir.iterdir())
    detail = "Found issue templates." if passed else "Add issue templates for bug reports and feature requests."
    return CheckResult(name="Issue templates", passed=passed, detail=detail)

