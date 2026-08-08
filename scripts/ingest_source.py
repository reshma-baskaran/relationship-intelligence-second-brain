from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from vault_tools import append_section_row, first_markdown_table


EVIDENCE_CONTEXTS = ("direct_interaction", "public_statement", "third_party", "internal")
RELATIONSHIP_STATUSES = ("active", "historical", "research_only", "unknown")
PRIVACY_LEVELS = ("public", "internal", "confidential", "restricted")
ATTRIBUTIONS = ("confirmed", "inferred", "review_needed")
RECORD_MODES = ("production", "simulation", "test_fixture")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "source"


def source_id(source_reference: str, content: str) -> tuple[str, str]:
    digest = hashlib.sha256((source_reference.strip() + "\n" + content).encode("utf-8")).hexdigest()
    return f"src-{digest[:12]}", digest


def _existing_sources(register: Path) -> tuple[set[str], set[str]]:
    if not register.exists():
        return set(), set()
    rows = first_markdown_table(register.read_text(encoding="utf-8"))
    ids = {row.get("Source ID", "").strip() for row in rows}
    references = {
        (row.get("Source reference") or row.get("Source URL") or "").strip()
        for row in rows
    }
    return ids, references


def build_source_page(*, title: str, source_type: str, evidence_context: str, relationship_status: str, privacy: str, attribution: str, source_date: str, organization: str, source_url: str, source_ref: str, record_mode: str, source_identifier: str, content_hash: str, content: str) -> str:
    return "\n".join([
        "---",
        "type: source",
        f'source_id: "{source_identifier}"',
        f'source_type: "{source_type}"',
        f'evidence_context: "{evidence_context}"',
        f'relationship_status: "{relationship_status}"',
        f'attribution: "{attribution}"',
        f'privacy: "{privacy}"',
        f'record_mode: "{record_mode}"',
        f'date: "{source_date}"',
        'status: "unprocessed"',
        f'organization: "{organization}"',
        f'source_url: "{source_url}"',
        f'source_ref: "{source_ref}"',
        f'content_hash: "{content_hash}"',
        "---",
        "",
        f"# {title}",
        "",
        "> Source material below is preserved as provided. Classification does not create a relationship, interaction, commitment, or buying signal.",
        "",
        content.rstrip(),
        "",
    ])


def ingest(*, vault: Path, source_file: Path, title: str, summary: str, source_url: str = "", source_ref: str = "", source_date: str, source_type: str, evidence_context: str, relationship_status: str, privacy: str, attribution: str, organization: str, record_mode: str = "production", dry_run: bool = False) -> dict:
    if evidence_context == "public_statement" and relationship_status != "research_only":
        raise ValueError("public_statement sources must use relationship_status research_only")
    if not summary.strip():
        raise ValueError("summary is required and must remain source-bounded")
    if record_mode not in RECORD_MODES:
        raise ValueError(f"record_mode must be one of: {', '.join(RECORD_MODES)}")
    parsed_url = urlparse(source_url)
    valid_https = parsed_url.scheme == "https" and bool(parsed_url.netloc)
    valid_local = source_ref.startswith("local://") and len(source_ref) > len("local://")
    if evidence_context in {"public_statement", "third_party"} and not valid_https:
        raise ValueError("public_statement and third_party sources require a valid HTTPS source_url")
    if evidence_context in {"direct_interaction", "internal"} and not (valid_https or valid_local):
        raise ValueError("direct_interaction and internal sources require an HTTPS source_url or local:// source_ref")
    source_reference = source_url if valid_https else source_ref
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", source_date):
        raise ValueError("date must use YYYY-MM-DD")
    content = source_file.read_text(encoding="utf-8")
    identifier, digest = source_id(source_reference, content)
    register = vault / "00_System/source-register.md"
    known_ids, known_references = _existing_sources(register)
    if identifier in known_ids or source_reference in known_references:
        raise ValueError(f"duplicate source: {identifier}")
    filename = f"{source_date}-{slugify(title)}-{identifier[-6:]}.md"
    destination = vault / "02_Raw Sources" / filename
    safe_summary = " ".join(summary.split()).replace("|", "/")
    has_record_mode = "| Record mode |" in register.read_text(encoding="utf-8")
    if has_record_mode:
        row = (
            f"| {identifier} | {source_date} | {source_type} | {evidence_context} | "
            f"{relationship_status} | {privacy} | {record_mode} | {organization} | {attribution} | unprocessed | "
            f"{source_reference} | {safe_summary} | [[02_Raw Sources/{destination.stem}]] |"
        )
    else:
        row = (
            f"| {identifier} | {source_date} | {source_type} | {evidence_context} | "
            f"{relationship_status} | {privacy} | {organization} | {attribution} | unprocessed | {source_reference} | "
            f"{safe_summary} | [[02_Raw Sources/{destination.stem}]] |"
        )
    result = {
        "status": "dry_run" if dry_run else "ingested",
        "source_id": identifier,
        "destination": str(destination),
        "evidence_context": evidence_context,
        "relationship_status": relationship_status,
        "record_mode": record_mode,
        "interaction_created": False,
    }
    if dry_run:
        return result

    destination.parent.mkdir(parents=True, exist_ok=True)
    original_register = register.read_text(encoding="utf-8")
    try:
        destination.write_text(
            build_source_page(
                title=title,
                source_type=source_type,
                evidence_context=evidence_context,
                relationship_status=relationship_status,
                privacy=privacy,
                attribution=attribution,
                source_date=source_date,
                organization=organization,
                source_url=source_url,
                source_ref=source_ref,
                record_mode=record_mode,
                source_identifier=identifier,
                content_hash=digest,
                content=content,
            ),
            encoding="utf-8",
        )
        append_section_row(register, row)
    except Exception:
        register.write_text(original_register, encoding="utf-8")
        if destination.exists():
            destination.unlink()
        raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Transactionally ingest one permitted source into a relationship vault.")
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True, help="one source-bounded sentence; do not add inferred relationship claims")
    parser.add_argument("--source-url", default="", help="required for public or third-party sources")
    parser.add_argument("--source-ref", default="", help="local:// reference for permitted private or internal sources")
    parser.add_argument("--date", required=True)
    parser.add_argument("--source-type", required=True)
    parser.add_argument("--evidence-context", choices=EVIDENCE_CONTEXTS, required=True)
    parser.add_argument("--relationship-status", choices=RELATIONSHIP_STATUSES, required=True)
    parser.add_argument("--privacy", choices=PRIVACY_LEVELS, required=True)
    parser.add_argument("--attribution", choices=ATTRIBUTIONS, required=True)
    parser.add_argument("--organization", required=True)
    parser.add_argument("--record-mode", choices=RECORD_MODES, default="production")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = ingest(
            vault=args.vault.resolve(),
            source_file=args.source_file.resolve(),
            title=args.title,
            summary=args.summary,
            source_url=args.source_url,
            source_ref=args.source_ref,
            source_date=args.date,
            source_type=args.source_type,
            evidence_context=args.evidence_context,
            relationship_status=args.relationship_status,
            privacy=args.privacy,
            attribution=args.attribution,
            organization=args.organization,
            record_mode=args.record_mode,
            dry_run=args.dry_run,
        )
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
