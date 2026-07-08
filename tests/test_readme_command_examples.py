"""Regression tests for README command coverage."""
from __future__ import annotations

import unittest
from pathlib import Path


PUBLIC_COMMANDS = (
    "python scripts/check_repository.py --root . --log-level INFO",
    "python scripts/verify_certificate.py --root . --log-level INFO",
    "python scripts/replay_certificate_chain.py --root . --log-level INFO",
    "python scripts/replay_per_record_evidence.py --root . --log-level INFO",
    "python scripts/replay_construction_audit.py --root . --log-level INFO",
    "python scripts/replay_witness_construction.py --root . --log-level INFO",
    "python scripts/replay_final_adjudication.py --root . --log-level INFO",
    "python -B -m unittest discover -s tests",
)


class ReadmeCommandExamplesTests(unittest.TestCase):
    """Check that public commands stay documented in both README files."""

    def test_public_commands_are_documented_in_both_readmes(self) -> None:
        """Every public verification command must appear in both README files."""
        readmes = [Path("README.md"), Path("README.zh-CN.md")]
        for readme in readmes:
            text = readme.read_text(encoding="utf-8")
            for command in PUBLIC_COMMANDS:
                with self.subTest(readme=readme.as_posix(), command=command):
                    self.assertIn(command, text)

    def test_new_validation_coverage_is_described(self) -> None:
        """README files must describe all release-quality checks added here."""
        english = Path("README.md").read_text(encoding="utf-8")
        chinese = Path("README.zh-CN.md").read_text(encoding="utf-8")
        for phrase in [
            "release/version consistency",
            "loguru",
            "archive/public mirror consistency",
            "paper claim-boundary checks",
            "paper title consistency",
            "text-file final-newline hygiene",
            "generated-artifact exclusion",
            "python -B",
        ]:
            with self.subTest(language="english", phrase=phrase):
                self.assertIn(phrase, english)
        for phrase in [
            "\u7248\u672c\u4e00\u81f4\u6027",
            "loguru",
            "\u5f52\u6863\u4e0e\u516c\u5f00\u5c55\u5f00\u6587\u4ef6\u4e00\u81f4\u6027",
            "\u8bba\u6587\u58f0\u660e\u8fb9\u754c\u68c0\u67e5",
            "\u8bba\u6587\u6807\u9898\u4e00\u81f4\u6027",
            "\u6587\u672c\u6587\u4ef6\u672b\u5c3e\u6362\u884c",
            "\u7f16\u8bd1\u4e2d\u95f4\u4ea7\u7269\u6392\u9664",
            "python -B",
        ]:
            with self.subTest(language="chinese", phrase=phrase):
                self.assertIn(phrase, chinese)


if __name__ == "__main__":
    unittest.main()
