import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


import sys
sys.path.insert(0, str(ROOT / "scripts"))
digest = load("digest", ROOT / "scripts" / "generate_relationship_digest.py")
lint_module = load("lint_vault", ROOT / "scripts" / "lint_vault.py")


class RelationshipSystemTests(unittest.TestCase):
    def test_digest_uses_only_requested_period(self):
        rows = [
            {"Date": "2026-07-01", "Organization": "Organization A", "Health": "Green", "Primary signal": "Confirmed priority", "Follow-up": "Send agreed material"},
            {"Date": "2026-06-01", "Organization": "Organization B", "Health": "Amber", "Primary signal": "Earlier signal", "Follow-up": ""},
        ]
        rendered = digest.build_digest(rows, "2026-07")
        self.assertIn("Organization A", rendered)
        self.assertNotIn("Organization B", rendered)

    def test_lint_requires_system_files(self):
        with TemporaryDirectory() as directory:
            problems = lint_module.lint(Path(directory))
        self.assertTrue(any("interaction-ledger.md" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()

