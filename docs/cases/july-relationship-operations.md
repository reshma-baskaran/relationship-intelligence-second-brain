# Real operating case: monthly relationship intelligence

This case is derived from a real July 2026 operating period in an active
Obsidian relationship-intelligence vault. The public version contains only the
workflow, aggregate control state, and output structure. People, organisations,
meeting content, transcripts, report details, commercial outcomes, links, and
substantive relationship intelligence are removed.

## Source basis

The working system used:

- recurring meeting-note ingestion from a signed-in note source;
- an immutable raw-source layer and source summaries;
- an interaction ledger and stakeholder-interest register;
- maintained relationship and theme pages;
- a monthly digest assembled from the vault;
- a duplicate/state guard so already-seen meetings were not reprocessed.

The recurring ingest was fail-closed: a meeting ID was added to state only
after successful filing, ambiguous notes went to a review inbox, and private
commercial or relationship details remained internal.

## July control state

| Control | Aggregate result |
|---|---:|
| Relationship interactions included in the monthly operating period | 7 |
| Interactions already represented in the vault | 6 |
| Interaction verified in the source system but not yet in the vault ledger | 1 |
| Relationship groups represented in the status table | 6 |
| Active relationship groups | 5 |
| Relationship group in initiation | 1 |

These counts come from the retained monthly digest. They are operating counts,
not pipeline, revenue, influence, or relationship-quality claims.

## The important finding

The digest did not silently treat the vault as complete. It explicitly
separated six processed interactions from one interaction that was verified in
the source system but had not reached the interaction ledger.

That distinction matters because a digest can look authoritative while still
being incomplete. The working system preserved three different states:

```text
present in source → represented in vault → included in synthesis
```

The unprocessed interaction remained an open ingestion item instead of being
invented from memory or omitted without disclosure.

## Source-to-brief workflow

| Stage | What happened | Control boundary |
|---|---|---|
| Detect | Poll for unseen saved meeting notes | Weekend and duplicate guards can stop the run without mutation |
| Preserve | Store raw material under the relevant source area | Raw content remains separate from synthesis |
| Classify | Route known relationship notes; send ambiguous notes to review | No forced classification |
| Maintain | Update registers, relationship pages, themes, claims, and commitments only when supported | Durable knowledge keeps source context |
| Close state | Record the meeting ID after successful filing | A partial ingest cannot masquerade as complete |
| Synthesize | Generate the monthly brief from ledgers and maintained knowledge | Missing ledger state is disclosed |

## Monthly output structure

The private digest contained the following reusable operating sections:

1. Executive snapshot for the period.
2. Repeated questions and themes across conversations.
3. What resonated and what evidence was requested.
4. Pushback, gaps, and unresolved proof requirements.
5. Relationship status against the month's operating goals.
6. A forward plan for the next three months.

No private section content is reproduced here. The public value is the control
model: each synthesis block is downstream of traceable sources and explicit
processing state.

## What this case proves

- The system operated across seven real interactions in one monthly period.
- It produced a recurring management brief from maintained relationship memory.
- It surfaced an ingestion gap rather than hiding it.
- It separated raw sources, maintained knowledge, and synthesis.
- The public extraction can demonstrate the mechanics without publishing the
  underlying relationship intelligence.

## Outcome boundary

This case establishes operating use and control behavior. It does not disclose
or claim the identities involved, the substance of their feedback, report
recognition, referrals, opportunities, revenue, or commercial influence.
