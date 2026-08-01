---
type: system
name: maintenance-log
---

# Maintenance log

Append one dated entry after a successful maintenance transaction. If an
ingest fails before stable source IDs are returned, do not advance state or
write a success entry.
