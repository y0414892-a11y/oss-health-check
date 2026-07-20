import json
import tempfile
import unittest
from pathlib import Path

from oss_health_check.config import find_config, load_config


class ConfigTests(unittest.TestCase):
    def test_find_config_returns_default_config_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "oss-health-check.json"
            config_path.write_text("{}", encoding="utf-8")

            self.assertEqual(find_config(root), config_path)

    def test_load_config_reads_fail_under_and_ignored_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(
                json.dumps({"fail_under": 80, "ignore": ["Changelog", "Security policy"]}),
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertEqual(config.fail_under, 80)
        self.assertEqual(config.ignored_checks, ("Changelog", "Security policy"))

    def test_load_config_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_bytes(b'\xef\xbb\xbf{"fail_under": 80}')

            config = load_config(config_path)

        self.assertEqual(config.fail_under, 80)

    def test_load_config_rejects_invalid_fail_under(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(json.dumps({"fail_under": 101}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
