---
name: maintain-relationship-intelligence
description: Initialize and maintain an Obsidian relationship-intelligence system for client, partner, analyst, vendor, or other strategic relationships; ingest permitted notes, update source records, stakeholder pages, interaction history, interests, commitments, themes, and recurring briefs. Use when a user wants to set up the starter vault or turn meeting notes into durable, traceable relationship intelligence rather than isolated summaries.
---

# Maintain Relationship Intelligence

Turn each conversation into traceable institutional memory.

## Start a new vault

For a new user or a new local installation:

1. Copy `relationship-intelligence.config.example.json` to a local
   `relationship-intelligence.config.json` and set `vault_path` outside the
   public repository.
2. Run `python3 scripts/init_vault.py --config relationship-intelligence.config.json`.
3. Open the destination in Obsidian and run `python3 scripts/lint_vault.py <vault-path>` before filing any notes.
4. Add only permitted source material. Do not create fictional relationship
   records to demonstrate the workflow.

The initializer creates missing files but does not overwrite existing vault
files unless `--overwrite` is explicitly supplied. Read `QUICKSTART.md` for the
complete first-run path.

## Ingest workflow

1. Identify source type, date, organization, stakeholders, owner, intended use,
   evidence context, relationship status, privacy, and attribution.
2. Use only these evidence contexts: `direct_interaction`, `public_statement`,
   `third_party`, or `internal`.
3. Classify a public statement as `research_only`; never convert it into an
   interaction, commitment, relationship claim, or buying signal.
4. Preserve the raw source without rewriting it. For a local permitted source,
   use `scripts/ingest_source.py` so the source receives a stable ID, hash,
   duplicate check, source-bounded summary, and source-register row. Run
   `--dry-run` first when needed.
5. Create or update a source summary.
6. Separate confirmed facts, interpretation, recommendation, and unknowns.
7. Update relevant organization, stakeholder, theme, commitment, and claim pages.
8. Add an interaction-ledger row only for `direct_interaction` evidence.
9. Update the stakeholder-interest register only when attribution is clear;
   retain evidence context and relationship status on the row.
10. Update the content index and source register.
11. Append a maintenance-log entry only after lint passes.
12. Advance automation state only after all required writes succeed.

For connector-neutral use, accept user-provided Markdown notes or another
locally exported source format. Keep any Granola, Gmail, Slack, CRM, or other
connector adapter outside this public repository unless it is explicitly
sanitized and safe to publish.

Read [references/vault-contract.md](references/vault-contract.md) before changing a vault. Use [references/relationship-model.md](references/relationship-model.md) when deciding what belongs in each register.

## Recurring synthesis

For a weekly update, report:

- interactions since the previous update
- confirmed stakeholder interests
- commitments due or overdue
- useful materials or reports to review
- relationship risks and unresolved attribution
- next actions with owners

For a monthly digest, use the vault root with
`scripts/generate_relationship_digest.py <vault> --period YYYY-MM`. Keep direct
relationship activity separate from public and market intelligence, retain
source links, and add recurring themes, coverage gaps, next-month engagement
priorities, and changes in relationship health.

## Safety

- Never invent an ask, commitment, interest, source, or relationship outcome.
- Preserve source links, dates, and attribution status.
- Keep raw sources separate from synthesis.
- Do not expose private transcripts, commercial terms, contact data, or internal product details.
- Do not send messages or write to CRM from an ingest task.
- If the source connector fails before returning stable source IDs, do not advance state.
- Never label a public executive statement as a direct relationship, ask,
  commitment, or permission to contact.
