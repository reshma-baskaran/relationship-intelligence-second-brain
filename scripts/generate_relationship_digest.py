from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

from vault_tools import first_markdown_table


def value(row: dict[str, str], *names: str) -> str:
    lowered = {key.casefold(): val for key, val in row.items()}
    for name in names:
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return ""


def build_digest(rows: list[dict[str, str]], period: str) -> str:
    selected = [row for row in rows if value(row, "Date").startswith(period)]
    health = Counter(value(row, "Health", "RAG") or "Unspecified" for row in selected)
    organizations = sorted({value(row, "Organization", "Firm") for row in selected if value(row, "Organization", "Firm")})
    lines = [
        "---",
        "type: output",
        "output_type: relationship_digest",
        f"period: {period}",
        f"generated: {date.today().isoformat()}",
        "---",
        "",
        f"# Relationship intelligence digest — {period}",
        "",
        f"- Interactions: {len(selected)}",
        f"- Organizations covered: {len(organizations)}",
        f"- Health: {', '.join(f'{key} {count}' for key, count in sorted(health.items())) or 'No interactions'}",
        "",
        "## Interaction signals",
        "",
    ]
    if selected:
        for row in selected:
            organization = value(row, "Organization", "Firm") or "Unspecified organization"
            signal = value(row, "Primary signal") or "No primary signal recorded"
            lines.append(f"- **{organization}:** {signal}")
    else:
        lines.append("- No interactions recorded for this period.")

    lines.extend(["", "## Open follow-ups", ""])
    followups = [
        (value(row, "Organization", "Firm"), value(row, "Follow-up", "Follow-up / question"))
        for row in selected
        if value(row, "Follow-up", "Follow-up / question")
    ]
    if followups:
        lines.extend(f"- **{organization or 'Unspecified organization'}:** {followup}" for organization, followup in followups)
    else:
        lines.append("- No follow-ups recorded.")

    lines.extend([
        "",
        "## Review before sharing",
        "",
        "- Confirm owners and due dates.",
        "- Resolve review-needed attribution.",
        "- Remove private details before external use.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a monthly relationship digest from a Markdown ledger.")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--period", required=True, help="YYYY-MM")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows = first_markdown_table(args.ledger.read_text(encoding="utf-8"))
    digest = build_digest(rows, args.period)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(digest, encoding="utf-8")
    else:
        print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

