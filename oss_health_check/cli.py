from __future__ import annotations

import argparse
from pathlib import Path

from .scanner import format_report, scan_project


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
    print(format_report(report))

    if args.strict and report.missing_count:
        return 1
    if args.fail_under is not None and report.score_percent < args.fail_under:
        return 1
    return 0


def _score_threshold(value: str) -> int:
    try:
        threshold = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer from 0 to 100") from exc

    if threshold < 0 or threshold > 100:
        raise argparse.ArgumentTypeError("must be an integer from 0 to 100")
    return threshold
