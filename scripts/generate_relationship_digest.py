from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

from vault_tools import first_markdown_table, frontmatter


def value(row: dict[str, str], *names: str) -> str:
    lowered = {key.casefold(): val.strip() for key, val in row.items()}
    for name in names:
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return ""


def _table(path: Path) -> list[dict[str, str]]:
    return first_markdown_table(path.read_text(encoding="utf-8")) if path.exists() else []


def _linked(label: str, url: str) -> str:
    return f"[{label}]({url})" if url.startswith("https://") else label


def build_digest(rows: list[dict[str, str]], period: str) -> str:
    """Backward-compatible interaction-only renderer used by older callers."""
    return build_sections(interactions=rows, sources=[], interests=[], commitments=[], period=period)


def build_sections(*, interactions: list[dict[str, str]], sources: list[dict[str, str]], interests: list[dict[str, str]], commitments: list[dict[str, str]], period: str) -> str:
    selected_interactions = [row for row in interactions if value(row, "Date").startswith(period)]
    selected_sources = [row for row in sources if value(row, "Date").startswith(period)]
    health = Counter(value(row, "Health", "RAG") or "Unspecified" for row in selected_interactions)
    organizations = sorted({value(row, "Organization", "Firm") for row in selected_interactions + selected_sources if value(row, "Organization", "Firm")})
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
        f"- Direct interactions: {len(selected_interactions)}",
        f"- Public or research sources: {len([row for row in selected_sources if value(row, 'Evidence context') != 'direct_interaction'])}",
        f"- Organizations covered: {len(organizations)}",
        f"- Relationship health: {', '.join(f'{key} {count}' for key, count in sorted(health.items())) or 'No direct interactions'}",
        "",
        "## Direct relationship activity",
        "",
    ]
    if selected_interactions:
        for row in selected_interactions:
            organization = value(row, "Organization", "Firm") or "Unspecified organization"
            signal = value(row, "Primary signal") or "No primary signal recorded"
            source = value(row, "Source", "Source URL")
            lines.append(f"- **{organization}:** {signal} — source: {source}")
    else:
        lines.append("- No direct interactions recorded for this period.")

    lines.extend(["", "## Public and market intelligence", ""])
    public_sources = [row for row in selected_sources if value(row, "Evidence context") != "direct_interaction"]
    if public_sources:
        for row in public_sources:
            organization = value(row, "Organization") or "Unspecified organization"
            context = value(row, "Evidence context") or "unclassified"
            source_url = value(row, "Source URL")
            source_identifier = value(row, "Source ID") or "source"
            summary = value(row, "Summary") or "Source ingested; synthesis pending."
            lines.append(f"- **{organization}** · `{context}` · {_linked(source_identifier, source_url)} — {summary}")
    else:
        lines.append("- No public or market-intelligence sources recorded for this period.")

    lines.extend(["", "## Stakeholder interests", ""])
    relevant_interests = [row for row in interests if value(row, "Evidence") or value(row, "Interest")]
    if relevant_interests:
        for row in relevant_interests:
            stakeholder = value(row, "Stakeholder") or "Unspecified stakeholder"
            organization = value(row, "Organization")
            interest = value(row, "Interest") or "No interest recorded"
            context = value(row, "Evidence context") or "unclassified"
            evidence = value(row, "Evidence")
            lines.append(f"- **{stakeholder}**{f' · {organization}' if organization else ''}: {interest} (`{context}`) — evidence: {evidence}")
    else:
        lines.append("- No attributed interests recorded.")

    lines.extend(["", "## Open commitments and follow-ups", ""])
    followups = [
        (value(row, "Organization", "Firm"), value(row, "Follow-up", "Follow-up / question"))
        for row in selected_interactions
        if value(row, "Follow-up", "Follow-up / question")
    ]
    if followups:
        lines.extend(f"- **{organization or 'Unspecified organization'}:** {followup}" for organization, followup in followups)
    open_commitments = [row for row in commitments if value(row, "status") == "open"]
    for commitment in open_commitments:
        lines.append(
            f"- **Commitment:** {value(commitment, 'title') or 'Untitled'} · owner: {value(commitment, 'owner') or 'unassigned'} · due: {value(commitment, 'due') or 'unspecified'} · source: {value(commitment, 'source') or 'missing'}"
        )
    if not followups and not open_commitments:
        lines.append("- No open commitments or follow-ups recorded.")

    lines.extend([
        "",
        "## Review before sharing",
        "",
        "- Keep public research separate from direct relationship activity.",
        "- Confirm owners, due dates, attribution, evidence context, and privacy.",
        "- Retain source links on every externally shared claim.",
        "",
    ])
    return "\n".join(lines)


def build_vault_digest(vault: Path, period: str) -> str:
    system = vault / "00_System"
    commitments: list[dict[str, str]] = []
    for path in (vault / "03_Wiki/commitments").glob("*.md") if (vault / "03_Wiki/commitments").exists() else []:
        metadata = frontmatter(path.read_text(encoding="utf-8"))
        metadata["title"] = path.stem
        commitments.append(metadata)
    return build_sections(
        interactions=_table(system / "interaction-ledger.md"),
        sources=_table(system / "source-register.md"),
        interests=_table(system / "stakeholder-interest-register.md"),
        commitments=commitments,
        period=period,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a source-preserving monthly relationship digest from a vault.")
    parser.add_argument("source", type=Path, help="vault directory, or a legacy interaction-ledger path")
    parser.add_argument("--period", required=True, help="YYYY-MM")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    digest = build_vault_digest(args.source, args.period) if args.source.is_dir() else build_digest(_table(args.source), args.period)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(digest, encoding="utf-8")
    else:
        print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
