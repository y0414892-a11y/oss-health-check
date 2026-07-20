from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scanner import ScanReport, format_report, scan_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-health-check",
        description="Check whether a repository is ready for open-source contributors.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to scan. Defaults to the current directory.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when any check is missing.",
    )
    parser.add_argument(
        "--fail-under",
        type=_score_threshold,
        metavar="PERCENT",
        help="Exit with status 1 when the score is below this percent.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.path)

    if not root.exists():
        parser.error(f"path does not exist: {root}")
    if not root.is_dir():
        parser.error(f"path is not a directory: {root}")

    report = scan_project(root)
    if args.json:
        print(_format_json_report(report))
    else:
        print(format_report(report))

    if args.strict and report.missing_count:
        return 1
    if args.fail_under is not None and report.score_percent < args.fail_under:
        return 1
    return 0


def _format_json_report(report: ScanReport) -> str:
    data = {
        "root": str(report.root),
        "passed_count": report.passed_count,
        "missing_count": report.missing_count,
        "score_percent": report.score_percent,
        "categories": [
            {
                "name": category.name,
                "passed_count": category.passed_count,
                "total_count": category.total_count,
                "score_percent": category.score_percent,
            }
            for category in report.category_scores
        ],
        "next_steps": [
            {
                "name": result.name,
                "category": result.category,
                "detail": result.detail,
            }
            for result in report.next_steps
        ],
        "results": [
            {
                "name": result.name,
                "category": result.category,
                "passed": result.passed,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def _score_threshold(value: str) -> int:
    try:
        threshold = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer from 0 to 100") from exc

    if threshold < 0 or threshold > 100:
        raise argparse.ArgumentTypeError("must be an integer from 0 to 100")
    return threshold
