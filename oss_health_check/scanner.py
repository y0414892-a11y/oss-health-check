from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


MAX_NEXT_STEPS = 3


@dataclass(frozen=True)
class CheckResult:
    name: str
    category: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class CategoryScore:
    name: str
    passed_count: int
    total_count: int

    @property
    def score_percent(self) -> int:
        if not self.total_count:
            return 0
        return round((self.passed_count / self.total_count) * 100)


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

    @property
    def category_scores(self) -> tuple[CategoryScore, ...]:
        scores: dict[str, list[int]] = {}
        for result in self.results:
            passed_count, total_count = scores.setdefault(result.category, [0, 0])
            scores[result.category] = [passed_count + int(result.passed), total_count + 1]

        return tuple(
            CategoryScore(name=name, passed_count=counts[0], total_count=counts[1])
            for name, counts in scores.items()
        )

    @property
    def next_steps(self) -> tuple[CheckResult, ...]:
        return tuple(result for result in self.results if not result.passed)[:MAX_NEXT_STEPS]


def scan_project(root: Path) -> ScanReport:
    root = root.resolve()
    results = (
        _check_any_file(root, "Documentation", "README", ("README.md", "README.rst", "README.txt"), "Found a README file.", "Add a README with purpose, setup, and usage instructions."),
        _check_readme_section(root, "README installation section", ("installation", "install", "setup"), "Found README installation instructions.", "Add an Installation or Setup section to the README."),
        _check_readme_section(root, "README usage section", ("usage", "quick start", "getting started"), "Found README usage instructions.", "Add a Usage or Quick Start section to the README."),
        _check_readme_section(root, "README example section", ("example", "examples", "example output"), "Found a README example section.", "Add an Example section to the README."),
        _check_readme_image_alt_text(root),
        _check_any_file(root, "Community", "License", ("LICENSE", "LICENSE.md", "COPYING"), "Found a license file.", "Add a license so people know how they may use the project."),
        _check_any_file(root, "Community", "Contributing guide", ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"), "Found a contributing guide.", "Add CONTRIBUTING.md with local setup and contribution workflow."),
        _check_tests(root),
        _check_ci(root),
        _check_issue_templates(root),
        _check_any_file(root, "Community", "Pull request template", (".github/pull_request_template.md", "PULL_REQUEST_TEMPLATE.md"), "Found a pull request template.", "Add a pull request template with a short review checklist."),
        _check_any_file(root, "Community", "Security policy", ("SECURITY.md", ".github/SECURITY.md"), "Found a security policy.", "Add SECURITY.md with vulnerability reporting instructions."),
        _check_any_file(root, "Documentation", "Changelog", ("CHANGELOG.md", "HISTORY.md", "NEWS.md"), "Found a changelog.", "Add CHANGELOG.md to document user-visible changes."),
    )
    return ScanReport(root=root, results=results)


def format_report(report: ScanReport) -> str:
    lines = [
        f"OSS Health Check: {report.root}",
        f"Score: {report.passed_count}/{len(report.results)} ({report.score_percent}%)",
        "",
        "Categories:",
    ]

    for category in report.category_scores:
        lines.append(f"- {category.name}: {category.passed_count}/{category.total_count} ({category.score_percent}%)")

    lines.extend([
        "",
        "Next steps:",
    ])

    if report.next_steps:
        for result in report.next_steps:
            lines.append(f"- {result.category}: {result.detail}")
    else:
        lines.append("- No missing checks. This repository looks ready for contributors.")

    lines.extend([
        "",
        "Checks:",
    ])

    for result in report.results:
        status = "ok" if result.passed else "missing"
        lines.append(f"[{status}] {result.name}")
        lines.append(f"     {result.detail}")

    return "\n".join(lines)


def _check_any_file(
    root: Path,
    category: str,
    name: str,
    candidates: tuple[str, ...],
    found_detail: str,
    missing_detail: str,
) -> CheckResult:
    passed = any((root / candidate).is_file() for candidate in candidates)
    return CheckResult(name=name, category=category, passed=passed, detail=found_detail if passed else missing_detail)


def _check_readme_section(
    root: Path,
    name: str,
    headings: tuple[str, ...],
    found_detail: str,
    missing_detail: str,
) -> CheckResult:
    readme = _find_readme(root)
    if readme is None:
        return CheckResult(name=name, category="Documentation", passed=False, detail=missing_detail)

    readme_headings = _read_markdown_headings(readme)
    passed = any(heading in readme_headings for heading in headings)
    return CheckResult(name=name, category="Documentation", passed=passed, detail=found_detail if passed else missing_detail)


def _find_readme(root: Path) -> Path | None:
    for candidate in ("README.md", "README.rst", "README.txt"):
        path = root / candidate
        if path.is_file():
            return path
    return None


def _read_markdown_headings(path: Path) -> set[str]:
    headings = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            headings.add(line.lstrip("#").strip().lower())
    return headings


def _check_readme_image_alt_text(root: Path) -> CheckResult:
    readme = _find_readme(root)
    if readme is None:
        return CheckResult(
            name="README image alt text",
            category="Documentation",
            passed=False,
            detail="Add alt text to README images so screen reader users can understand them.",
        )

    content = readme.read_text(encoding="utf-8")
    missing_alt = any(match.group(1).strip() == "" for match in re.finditer(r"!\[([^\]]*)\]\(", content))
    detail = (
        "README images have alt text."
        if not missing_alt
        else "Add alt text to README images so screen reader users can understand them."
    )
    return CheckResult(name="README image alt text", category="Documentation", passed=not missing_alt, detail=detail)


def _check_tests(root: Path) -> CheckResult:
    test_paths = (root / "tests", root / "test")
    has_test_dir = any(path.is_dir() and any(path.iterdir()) for path in test_paths)
    has_test_files = any(root.glob("test_*.py")) or any(root.glob("*_test.py"))
    passed = has_test_dir or has_test_files
    detail = "Found test files." if passed else "Add tests so contributors can verify their changes."
    return CheckResult(name="Tests", category="Automation", passed=passed, detail=detail)


def _check_ci(root: Path) -> CheckResult:
    workflow_dir = root / ".github" / "workflows"
    passed = workflow_dir.is_dir() and any(workflow_dir.glob("*.yml")) or any(workflow_dir.glob("*.yaml")) if workflow_dir.exists() else False
    detail = "Found a GitHub Actions workflow." if passed else "Add a CI workflow that runs tests on pull requests."
    return CheckResult(name="Continuous integration", category="Automation", passed=passed, detail=detail)


def _check_issue_templates(root: Path) -> CheckResult:
    template_dir = root / ".github" / "ISSUE_TEMPLATE"
    passed = template_dir.is_dir() and any(template_dir.iterdir())
    detail = "Found issue templates." if passed else "Add issue templates for bug reports and feature requests."
    return CheckResult(name="Issue templates", category="Community", passed=passed, detail=detail)
