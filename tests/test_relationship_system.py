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
ingest_module = load("ingest_source", ROOT / "scripts" / "ingest_source.py")


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
                handle.write("| 2026-08-01 | Organization A | Person A | partner | direct_interaction | active | internal | confirmed | production |  | green | Signal |  | Owner |  |\n")
            problems = lint_module.lint(vault)
        self.assertTrue(any("missing provenance fields: Source" in problem for problem in problems))

    def test_public_source_is_research_only_and_not_an_interaction(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "pipedrive.md"
            source.write_text("Pipedrive published a partner-program announcement.", encoding="utf-8")
            result = ingest_module.ingest(
                vault=vault,
                source_file=source,
                title="Pipedrive partner announcement",
                summary="Pipedrive described partner expertise and customer value as ecosystem priorities.",
                source_url="https://www.pipedrive.com/en/newsroom/example",
                source_date="2026-03-10",
                source_type="company_announcement",
                evidence_context="public_statement",
                relationship_status="research_only",
                privacy="public",
                attribution="confirmed",
                organization="Pipedrive",
            )
            self.assertFalse(result["interaction_created"])
            themes = vault / "03_Wiki/themes"
            themes.mkdir(parents=True, exist_ok=True)
            (themes / "Partner-led customer value.md").write_text(
                "---\n"
                "type: theme\n"
                "status: active\n"
                "updated: 2026-03-10\n"
                "confidence: medium\n"
                "evidence_context: public_statement\n"
                "relationship_status: research_only\n"
                "privacy: public\n"
                "attribution: confirmed\n"
                "source_url: https://www.pipedrive.com/en/newsroom/example\n"
                "---\n\n"
                "# Partner-led customer value\n\n"
                "## Current synthesis\n\n"
                "Pipedrive publicly emphasizes partner expertise and customer value.\n",
                encoding="utf-8",
            )
            self.assertEqual([], lint_module.lint(vault))
            rendered = digest.build_vault_digest(vault, "2026-03")
        self.assertIn("Pipedrive", rendered)
        self.assertIn("public_statement", rendered)
        self.assertIn("No direct interactions", rendered)
        self.assertIn("https://www.pipedrive.com/en/newsroom/example", rendered)
        self.assertIn("partner expertise", rendered)
        self.assertIn("Maintained themes", rendered)
        self.assertIn("Partner-led customer value", rendered)

    def test_public_source_cannot_claim_active_relationship(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "source.md"
            source.write_text("Public statement", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "research_only"):
                ingest_module.ingest(
                    vault=vault,
                    source_file=source,
                    title="Public statement",
                    summary="A bounded public statement.",
                    source_url="https://example.com/source",
                    source_date="2026-08-07",
                    source_type="company_announcement",
                    evidence_context="public_statement",
                    relationship_status="active",
                    privacy="public",
                    attribution="confirmed",
                    organization="Example",
                )

    def test_ingest_detects_duplicate_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "source.md"
            source.write_text("Public statement", encoding="utf-8")
            kwargs = dict(
                vault=vault,
                source_file=source,
                title="Public statement",
                summary="A bounded public statement.",
                source_url="https://example.com/source",
                source_date="2026-08-07",
                source_type="company_announcement",
                evidence_context="public_statement",
                relationship_status="research_only",
                privacy="public",
                attribution="confirmed",
                organization="Example",
            )
            ingest_module.ingest(**kwargs)
            with self.assertRaisesRegex(ValueError, "duplicate source"):
                ingest_module.ingest(**kwargs)

    def test_ingest_rejects_invalid_source_url_before_writing(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "source.md"
            source.write_text("Public statement", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                ingest_module.ingest(
                    vault=vault,
                    source_file=source,
                    title="Public statement",
                    summary="A bounded public statement.",
                    source_url="http://x",
                    source_date="2026-08-07",
                    source_type="company_announcement",
                    evidence_context="public_statement",
                    relationship_status="research_only",
                    privacy="public",
                    attribution="confirmed",
                    organization="Example",
                )
            self.assertEqual([], list((vault / "02_Raw Sources").glob("*.md")))

    def test_private_direct_source_accepts_local_provenance(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "meeting.md"
            source.write_text("Permitted private meeting note.", encoding="utf-8")
            result = ingest_module.ingest(
                vault=vault,
                source_file=source,
                title="Private meeting note",
                summary="A permitted direct interaction was captured.",
                source_ref="local://meeting-exports/meeting-123",
                source_date="2026-08-08",
                source_type="meeting_note",
                evidence_context="direct_interaction",
                relationship_status="active",
                privacy="restricted",
                attribution="confirmed",
                organization="Example",
            )
            self.assertEqual("production", result["record_mode"])
            self.assertEqual([], lint_module.lint(vault))
            page = Path(result["destination"]).read_text(encoding="utf-8")
            self.assertIn('source_ref: "local://meeting-exports/meeting-123"', page)

    def test_digest_excludes_simulation_and_normalizes_organization_names(self):
        interactions = [
            {"Date": "2026-08-01", "Organization": "[[Mixpanel]]", "Record mode": "production", "Health": "green", "Primary signal": "Real"},
            {"Date": "2026-08-02", "Organization": "Mixpanel", "Record mode": "simulation", "Health": "green", "Primary signal": "SIMULATION ONLY"},
        ]
        sources = [
            {"Date": "2026-08-03", "Organization": "Mixpanel", "Record mode": "production", "Evidence context": "public_statement"},
            {"Date": "2026-08-04", "Organization": "Other", "Record mode": "test_fixture", "Evidence context": "public_statement"},
        ]
        rendered = digest.build_sections(
            interactions=interactions,
            sources=sources,
            interests=[],
            themes=[],
            commitments=[],
            period="2026-08",
        )
        self.assertIn("Direct interactions: 1", rendered)
        self.assertIn("Organizations covered: 1", rendered)
        self.assertNotIn("SIMULATION ONLY", rendered)
        with_simulation = digest.build_sections(
            interactions=interactions,
            sources=sources,
            interests=[],
            themes=[],
            commitments=[],
            period="2026-08",
            include_simulation=True,
        )
        self.assertIn("Simulation / QA", with_simulation)
        self.assertIn("Simulated interactions: 1", with_simulation)

    def test_lint_requires_machine_readable_simulation_mode(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            init_module.install_template(vault)
            source = root / "simulation.md"
            source.write_text("SIMULATION ONLY fixture.", encoding="utf-8")
            result = ingest_module.ingest(
                vault=vault,
                source_file=source,
                title="Simulation fixture",
                summary="Simulation fixture for QA only.",
                source_ref="local://qa/simulation-1",
                source_date="2026-08-08",
                source_type="meeting_note",
                evidence_context="direct_interaction",
                relationship_status="active",
                privacy="restricted",
                attribution="confirmed",
                organization="Example",
                record_mode="simulation",
            )
            page = Path(result["destination"])
            page.write_text(page.read_text(encoding="utf-8").replace('record_mode: "simulation"', 'record_mode: "production"'), encoding="utf-8")
            problems = lint_module.lint(vault)
        self.assertTrue(any("simulation content" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
