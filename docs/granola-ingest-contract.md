# Meeting-note ingest contract

The working system uses a recurring Granola-to-Obsidian ingest. The public contract is connector-neutral so credentials and private endpoint assumptions remain outside this repository.

## State-first flow

1. List recent meetings and obtain stable meeting IDs.
2. Compare those IDs with `processedMeetingIds` and `retryNeeded`.
3. Fetch the full note for unseen IDs.
4. Preserve the raw note.
5. Classify it as a strategic relationship, internal insight, or `needs_review`.
6. Update the source register, content index, activity log, and relevant relationship pages.
7. Validate every write.
8. Add the ID to `processedMeetingIds` only after successful filing.

If the connector fails before IDs are returned, leave the vault and state unchanged. A transport failure is not evidence that there were no new notes.

The ingest performs no email, Slack, CRM, or external publishing actions.

