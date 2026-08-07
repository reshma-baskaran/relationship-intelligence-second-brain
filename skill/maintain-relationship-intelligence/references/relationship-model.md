# Relationship model

## Evidence context

Use exactly one:

- `direct_interaction`: a permitted meeting, email, call, or direct exchange.
- `public_statement`: first-party public material; always `research_only`.
- `third_party`: reporting or analysis about the organization or stakeholder.
- `internal`: the user's own interpretation or operating note.

Also preserve:

- relationship status: `active`, `historical`, `research_only`, or `unknown`;
- attribution: `confirmed`, `inferred`, or `review_needed`;
- privacy: `public`, `internal`, `confidential`, or `restricted`.

## Interaction

Record date, organization, stakeholders, relationship type, evidence context,
relationship status, privacy, attribution, source, relationship health, primary
signal, follow-up, owner, and due date. Only `direct_interaction` belongs in the
interaction ledger.

## Interest

Record stakeholder, organization, interest, attribution, evidence, confidence, and best next asset. Use `confirmed`, `inferred`, or `review_needed` attribution.

## Commitment

Record the exact commitment, who owns it, who expects it, source, due date, status, and completion proof.

## Health

Health describes the state of the relationship and its operating context; it is not a personal rating. Use:

- `green`: clear mutual value, concrete progress, or an active next step.
- `amber`: useful relationship with unresolved proof, timing, ownership, or positioning.
- `red`: material trust, fit, or delivery risk.
- `review_needed`: source or attribution is incomplete.
