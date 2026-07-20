from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_NAME = "oss-health-check.json"


@dataclass(frozen=True)
class Config:
    fail_under: int | None = None
    ignored_checks: tuple[str, ...] = ()


def find_config(root: Path) -> Path | None:
    path = root / DEFAULT_CONFIG_NAME
    if path.is_file():
        return path
    return None


def load_config(path: Path) -> Config:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError("config must be a JSON object")

    unknown_keys = sorted(set(data) - {"fail_under", "ignore"})
    if unknown_keys:
        raise ValueError(f"unknown config key: {', '.join(unknown_keys)}")

    fail_under = data.get("fail_under")
    if fail_under is not None:
        if isinstance(fail_under, bool) or not isinstance(fail_under, int):
            raise ValueError("fail_under must be an integer from 0 to 100")
        if fail_under < 0 or fail_under > 100:
            raise ValueError("fail_under must be an integer from 0 to 100")

    ignored_checks = data.get("ignore", [])
    if not isinstance(ignored_checks, list):
        raise ValueError("ignore must be a list of check names")

    normalized_ignored_checks = []
    for check_name in ignored_checks:
        if not isinstance(check_name, str) or not check_name.strip():
            raise ValueError("ignore must contain non-empty check names")
        normalized_ignored_checks.append(check_name.strip())

    return Config(fail_under=fail_under, ignored_checks=tuple(normalized_ignored_checks))
