# Architecture

```mermaid
flowchart TD
  A[Meeting notes, transcripts, reports] --> B[Immutable raw sources]
  B --> C[Source summaries]
  C --> D[Organizations and stakeholders]
  C --> E[Themes, claims, commitments]
  D --> F[Interaction ledger]
  E --> F
  F --> G[Weekly relationship update]
  F --> H[Monthly relationship digest]
  I[Processed source state] --> A
  B --> I
```

The raw-source layer is evidence. The wiki is maintained synthesis. Registers turn prose into operating data. Outputs are generated from those maintained layers and retain source links.

