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

## 4. Open the vault in Obsidian

Open the configured `vault_path` as an Obsidian vault. Start with:

- `00_System/index.md` for navigation
- `00_System/source-register.md` for source intake
- `00_System/interaction-ledger.md` for one row per interaction
- `00_System/stakeholder-interest-register.md` for attributed interests

Add only notes you are allowed to store. Keep raw notes separate from
maintained synthesis and preserve a source link for every claim or interaction.

## 5. Validate before generating an output

```bash
python3 scripts/lint_vault.py ~/Documents/relationship-intelligence-vault
```

The linter checks the required system files, internal links, source metadata,
and the minimum provenance fields on interaction-ledger rows.

## 6. Generate a monthly digest

```bash
python3 scripts/generate_relationship_digest.py \
  ~/Documents/relationship-intelligence-vault/00_System/interaction-ledger.md \
  --period 2026-08 \
  --out ~/Documents/relationship-intelligence-vault/05_Outputs/2026-08-relationship-digest.md
```

The digest is a starting point for review. Confirm owners, dates, attribution,
and privacy before sharing it.

## What this does not do

This public starter kit does not connect to Granola, Obsidian Sync, Gmail,
Slack, a CRM, or any other private system automatically. Those adapters belong
in your local workflow. No transcripts, contact data, credentials, or private
automation state are included here.
