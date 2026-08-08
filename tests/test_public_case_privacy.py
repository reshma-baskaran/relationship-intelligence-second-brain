from pathlib import Path
import unittest


CASE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "cases"
    / "july-relationship-operations.md"
)


class PublicCasePrivacyTests(unittest.TestCase):
    def test_case_preserves_aggregate_state_and_boundary(self):
        text = CASE_PATH.read_text(encoding="utf-8")
        self.assertIn("| Relationship interactions included in the monthly operating period | 7 |", text)
        self.assertIn("| Interactions already represented in the vault | 6 |", text)
        self.assertIn("## Outcome boundary", text)

    def test_case_excludes_private_source_identifiers(self):
        text = CASE_PATH.read_text(encoding="utf-8").lower()
        prohibited = (
            "gartner",
            "forrester",
            "metrigy",
            "everest",
            "hfs research",
            "cmp research",
            "nuplay",
            "nurix",
            "granola",
            "linkedin.com",
            "drive.google.com",
        )
        for value in prohibited:
            with self.subTest(value=value):
                self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
