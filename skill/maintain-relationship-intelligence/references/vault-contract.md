# Vault contract

## Required system files

- `00_System/index.md`: content catalog and navigation map.
- `00_System/source-register.md`: source intake ledger with date and status.
- `00_System/interaction-ledger.md`: one row per strategic interaction.
- `00_System/stakeholder-interest-register.md`: attributed interests and next assets.
- `00_System/log.md`: append-only maintenance chronology.

## Layers

- `01_Inbox`: material awaiting classification.
- `02_Raw Sources`: immutable source material and source summaries.
- `03_Wiki`: maintained pages for organizations, people, themes, claims, and commitments.
- `04_Synthesis`: cross-source analysis and recommendations.
- `05_Outputs`: weekly updates, monthly digests, and briefing material.

## Transaction boundary

Treat a connector-backed ingest as a transaction. Fetch a stable source ID, preserve the source, update required registers, validate the writes, and only then mark the source processed. On partial failure, record a retry item rather than pretending the ingest completed.

## Evidence and privacy contract

Every source, interest, interaction, commitment, and output must preserve an
evidence context, relationship status, attribution state, and privacy level.
Public statements must remain `research_only` and cannot create interaction or
commitment records. Run structural and evidence-context lint before marking an
ingest successful.
