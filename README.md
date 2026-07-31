# Relationship Intelligence Second Brain

![Relationship Intelligence Second Brain cover](assets/cover.svg)

An LLM-maintained Obsidian system that turns client, partner, analyst, vendor, and other strategic conversations into durable relationship history, commitments, interests, and recurring operating briefs.

## The problem

Meeting summaries are easy to accumulate and hard to use. Important asks disappear between documents, relationship context stays with one person, follow-ups lose owners, and monthly reporting becomes a manual reconstruction exercise.

This system separates immutable sources from maintained knowledge, then turns that knowledge into an interaction ledger, stakeholder-interest register, weekly updates, and monthly digests.

## What is included

- A reusable Codex skill for relationship-intelligence ingestion.
- A source and wiki architecture for Obsidian.
- Stakeholder, source, theme, and commitment templates.
- A structural vault linter.
- A monthly relationship-digest generator.
- The transactional contract used by the live meeting-note ingest.
- Privacy boundaries for public and external use.

## Architecture

See [docs/architecture.md](docs/architecture.md) and the [meeting-note ingest contract](docs/granola-ingest-contract.md).

The system maintains five operating layers:

```text
raw sources
  → source summaries
  → organizations, stakeholders, themes, claims, commitments
  → interaction and interest registers
  → weekly updates and monthly digests
```

## Relationship outputs

- What changed in recent conversations?
- What does each stakeholder demonstrably care about?
- What did we commit to, who owns it, and when is it due?
- What material should we read or share next?
- Which relationships have unresolved timing, proof, or attribution risk?
- What should the next month of engagement prioritize?

The system originated in my analyst-relations work and is presented here as a broader client-and-partner relationship model.

## Run the tools

Lint a vault:

```bash
python scripts/lint_vault.py /path/to/vault
```

Generate a monthly digest from an interaction ledger:

```bash
python scripts/generate_relationship_digest.py \
  /path/to/vault/00_System/interaction-ledger.md \
  --period 2026-07 \
  --out /path/to/vault/05_Outputs/2026-07-relationship-digest.md
```

## Privacy model

This repository contains the engine, schema, and templates—not my private vault. It excludes transcripts, stakeholder histories, licensed reports, contact information, commercial terms, connector credentials, and private automation state.

## Inspiration and extension

Andrej Karpathy described a useful pattern: immutable raw sources, an LLM-maintained wiki, a schema, and ingest/query/lint operations. My working system applies that pattern to relationship operations and adds interaction history, attributed interests, commitments, health, automation state, and recurring weekly/monthly synthesis. See [Karpathy's original gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Current status

This public extraction is based on an active Obsidian system with recurring meeting-note ingestion and monthly relationship reporting. The public code is connector-neutral; the private data and credentials remain local.

## Author

Built by **Reshma Baskaran**, a GTM and growth marketer building practical research, outbound, and knowledge systems.
