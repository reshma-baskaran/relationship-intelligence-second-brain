from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from vault_tools import first_markdown_table, frontmatter, markdown_files, wikilink_targets


REQUIRED = (
    "00_System/index.md",
    "00_System/source-register.md",
    "00_System/interaction-ledger.md",
    "00_System/stakeholder-interest-register.md",
    "00_System/log.md",
)
ENUMS = {
    "evidence_context": {"direct_interaction", "public_statement", "third_party", "internal"},
    "relationship_status": {"active", "historical", "research_only", "unknown"},
    "attribution": {"confirmed", "inferred", "review_needed"},
    "privacy": {"public", "internal", "confidential", "restricted"},
}


def _value(row: dict[str, str], *names: str) -> str:
    lowered = {key.casefold(): value.strip() for key, value in row.items()}
    for name in names:
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return ""


def _is_https(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _check_enum(problems: list[str], label: str, field: str, value: str) -> None:
    if value not in ENUMS[field]:
        problems.append(f"{label} has invalid {field}: {value or '<blank>'}")


def lint(root: Path) -> list[str]:
    problems: list[str] = []
    files = list(markdown_files(root))
    by_stem: dict[str, list[Path]] = {}
    relative_targets = {str(path.relative_to(root).with_suffix("")): path for path in files}
    for path in files:
        by_stem.setdefault(path.stem, []).append(path)
    for relative in REQUIRED:
        if not (root / relative).exists():
            problems.append(f"missing required file: {relative}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        for target in wikilink_targets(text):
            normalized = target.removesuffix(".md")
            if "/" in normalized:
                if normalized not in relative_targets:
                    problems.append(f"broken wikilink: {path.relative_to(root)} -> {target}")
            elif len(by_stem.get(Path(normalized).stem, [])) == 0:
                problems.append(f"broken wikilink: {path.relative_to(root)} -> {target}")
            elif len(by_stem.get(Path(normalized).stem, [])) > 1:
                problems.append(f"ambiguous wikilink: {path.relative_to(root)} -> {target}")
        metadata = frontmatter(text)
        if metadata.get("type") == "source":
            label = f"source page {path.relative_to(root)}"
            if not _is_https(metadata.get("source_url", "")):
                problems.append(f"{label} lacks a valid HTTPS source_url")
            for field in ENUMS:
                _check_enum(problems, label, field, metadata.get(field, ""))
            if metadata.get("evidence_context") == "public_statement" and metadata.get("relationship_status") != "research_only":
                problems.append(f"{label} public_statement must use relationship_status research_only")
        if metadata.get("type") == "theme":
            label = f"theme page {path.relative_to(root)}"
            for field in ENUMS:
                _check_enum(problems, label, field, metadata.get(field, ""))
            if not _is_https(metadata.get("source_url", "")):
                problems.append(f"{label} lacks a valid HTTPS source_url")

    source_register = root / "00_System/source-register.md"
    if source_register.exists():
        seen_ids: set[str] = set()
        for number, row in enumerate(first_markdown_table(source_register.read_text(encoding="utf-8")), start=1):
            source_id = _value(row, "Source ID")
            label = f"source-register row {number}"
            if not source_id:
                problems.append(f"{label} is missing Source ID")
            elif source_id in seen_ids:
                problems.append(f"duplicate source ID: {source_id}")
            seen_ids.add(source_id)
            if not _is_https(_value(row, "Source URL")):
                problems.append(f"{label} lacks a valid HTTPS Source URL")
            for field, heading in (("evidence_context", "Evidence context"), ("relationship_status", "Relationship status"), ("privacy", "Privacy"), ("attribution", "Attribution")):
                _check_enum(problems, label, field, _value(row, heading))

    ledger = root / "00_System/interaction-ledger.md"
    if ledger.exists():
        for number, row in enumerate(first_markdown_table(ledger.read_text(encoding="utf-8")), start=1):
            if not any(cell.strip() for cell in row.values()):
                continue
            label = f"interaction-ledger row {number}"
            missing = []
            if not _value(row, "Date"):
                missing.append("Date")
            if not _value(row, "Organization", "Firm"):
                missing.append("Organization")
            if not _value(row, "Source", "Source URL"):
                missing.append("Source")
            if missing:
                problems.append(f"{label} is missing provenance fields: {', '.join(missing)}")
            context = _value(row, "Evidence context")
            _check_enum(problems, label, "evidence_context", context)
            _check_enum(problems, label, "relationship_status", _value(row, "Relationship status"))
            _check_enum(problems, label, "privacy", _value(row, "Privacy"))
            _check_enum(problems, label, "attribution", _value(row, "Attribution"))
            if context != "direct_interaction":
                problems.append(f"{label} must use evidence_context direct_interaction")

    interests = root / "00_System/stakeholder-interest-register.md"
    if interests.exists():
        for number, row in enumerate(first_markdown_table(interests.read_text(encoding="utf-8")), start=1):
            if not any(cell.strip() for cell in row.values()):
                continue
            label = f"stakeholder-interest row {number}"
            for field, heading in (("evidence_context", "Evidence context"), ("relationship_status", "Relationship status"), ("privacy", "Privacy"), ("attribution", "Attribution")):
                _check_enum(problems, label, field, _value(row, heading))
    return sorted(set(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint structure, provenance, evidence context, and privacy in a relationship vault.")
    parser.add_argument("vault", type=Path)
    args = parser.parse_args()
    problems = lint(args.vault.resolve())
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print("Vault passes structural and evidence-context lint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
