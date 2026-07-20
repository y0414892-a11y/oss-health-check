from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Config, find_config, load_config
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
    parser.add_argument(
        "--config",
        help="Path to a JSON config file. Defaults to oss-health-check.json in the scanned repository.",
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

    config = _load_cli_config(parser, root, args.config)
    try:
        report = scan_project(root, ignored_checks=config.ignored_checks)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        print(_format_json_report(report))
    else:
        print(format_report(report))

    fail_under = args.fail_under if args.fail_under is not None else config.fail_under
    if args.strict and report.missing_count:
        return 1
    if fail_under is not None and report.score_percent < fail_under:
        return 1
    return 0


def _load_cli_config(parser: argparse.ArgumentParser, root: Path, config_path: str | None) -> Config:
    path = Path(config_path) if config_path else find_config(root)
    if path is None:
        return Config()

    try:
        return load_config(path)
    except OSError as exc:
        parser.error(f"could not read config {path}: {exc}")
    except ValueError as exc:
        parser.error(f"invalid config {path}: {exc}")


def _format_json_report(report: ScanReport) -> str:
    data = {
        "root": str(report.root),
        "passed_count": report.passed_count,
        "missing_count": report.missing_count,
        "score_percent": report.score_percent,
        "ignored_checks": list(report.ignored_checks),
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
