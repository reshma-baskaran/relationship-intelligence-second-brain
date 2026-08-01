import importlib.util
import json
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
init_module = load("init_vault", ROOT / "scripts" / "init_vault.py")


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

    def test_initializer_creates_a_lintable_blank_vault(self):
        with TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            created, skipped = init_module.install_template(vault)
            self.assertGreater(len(created), 0)
            self.assertEqual(skipped, [])
            self.assertEqual(lint_module.lint(vault), [])

    def test_initializer_reads_vault_path_from_config(self):
        with TemporaryDirectory() as directory:
            config = Path(directory) / "relationship-intelligence.config.json"
            configured_path = Path(directory) / "configured-vault"
            config.write_text(json.dumps({"vault_path": str(configured_path)}), encoding="utf-8")
            self.assertEqual(init_module.configured_vault(config), configured_path)

    def test_lint_requires_source_for_interaction_rows(self):
        with TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            init_module.install_template(vault)
            ledger = vault / "00_System/interaction-ledger.md"
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write("| 2026-08-01 | Organization A | Person A | partner |  | green | Signal |  | Owner |  |\n")
            problems = lint_module.lint(vault)
        self.assertTrue(any("missing provenance fields: Source" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
