import contextlib
import io
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
