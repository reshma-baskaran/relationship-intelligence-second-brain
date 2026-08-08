# Quickstart

This repository is a portable starter kit for a relationship-intelligence
vault. It gives you the structure, rules, templates, and deterministic tools;
your notes and relationship data stay in a vault you control.

## 1. Clone the starter kit

```bash
git clone https://github.com/reshma-baskaran/relationship-intelligence-second-brain.git
cd relationship-intelligence-second-brain
```

## 2. Create a local configuration file

Make a local copy of the example and change `vault_path` to a location outside
this public repository:

```bash
cp relationship-intelligence.config.example.json relationship-intelligence.config.json
```

The local file is ignored by Git. It may contain paths on your computer, but it
must never contain credentials or relationship records.

## 3. Create your blank vault

```bash
python3 scripts/init_vault.py --config relationship-intelligence.config.json
```

The initializer creates the folders and empty system registers without
overwriting an existing file. Use `--overwrite` only when you intentionally
want the template to replace an existing file.

## 4. Ingest a permitted source

Use `scripts/ingest_source.py` for a local Markdown source. Classify every
source with:

- evidence context: `direct_interaction`, `public_statement`, `third_party`, or `internal`;
- relationship status: `active`, `historical`, `research_only`, or `unknown`;
- attribution: `confirmed`, `inferred`, or `review_needed`;
- privacy: `public`, `internal`, `confidential`, or `restricted`.

A `public_statement` must be `research_only`. The ingest command never creates
an interaction automatically. Use `--dry-run` to inspect the planned source ID
and destination before writing. Supply a one-sentence `--summary` that stays
within the source and does not invent a relationship, request, or commitment.

Use an HTTPS `--source-url` for public and third-party material. For a
permitted private direct or internal note without a web URL, use a stable
`--source-ref local://...`. Set `--record-mode simulation` or
`--record-mode test_fixture` for QA data; production is the default.

## 5. Open the vault in Obsidian

Open the configured `vault_path` as an Obsidian vault. Start with:

- `00_System/index.md` for navigation
- `00_System/source-register.md` for source intake
- `00_System/interaction-ledger.md` for one row per interaction
- `00_System/stakeholder-interest-register.md` for attributed interests

Add only notes you are allowed to store. Keep raw notes separate from
maintained synthesis and preserve a source link for every claim or interaction.

## 6. Validate before generating an output

```bash
python3 scripts/lint_vault.py ~/Documents/relationship-intelligence-vault
```

The linter checks required system files, exact or unambiguous internal links,
source URLs, duplicate source IDs, evidence context, relationship status,
attribution, privacy, and direct-interaction boundaries.

## 7. Generate a monthly digest

```bash
python3 scripts/generate_relationship_digest.py \
  ~/Documents/relationship-intelligence-vault \
  --period 2026-08 \
  --out ~/Documents/relationship-intelligence-vault/05_Outputs/2026-08-relationship-digest.md
```

The digest keeps direct relationship activity separate from public and market
intelligence, includes stakeholder interests and open commitments, and retains
source links. Confirm owners, dates, attribution, evidence context, and privacy
before sharing it.

Simulation and test fixtures are excluded from production metrics. Use
`--include-simulation` only to append a separate QA section.

## What this does not do

This public starter kit does not connect to Granola, Obsidian Sync, Gmail,
Slack, a CRM, or any other private system automatically. Those adapters belong
in your local workflow. No transcripts, contact data, credentials, or private
automation state are included here.
