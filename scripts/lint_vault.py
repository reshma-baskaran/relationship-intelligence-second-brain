from __future__ import annotations

import argparse
from pathlib import Path

from vault_tools import first_markdown_table, markdown_files, wikilink_targets


REQUIRED = (
    "00_System/index.md",
    "00_System/source-register.md",
    "00_System/interaction-ledger.md",
    "00_System/stakeholder-interest-register.md",
    "00_System/log.md",
)


def _value(row: dict[str, str], *names: str) -> str:
    lowered = {key.casefold(): value.strip() for key, value in row.items()}
    for name in names:
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return ""


def lint(root: Path) -> list[str]:
    problems: list[str] = []
    files = list(markdown_files(root))
    stems = {path.stem for path in files}
    for relative in REQUIRED:
        if not (root / relative).exists():
            problems.append(f"missing required file: {relative}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        for target in wikilink_targets(text):
            if Path(target).stem not in stems:
                problems.append(f"broken wikilink: {path.relative_to(root)} -> {target}")
        if "type: source" in text and "source_url:" not in text:
            problems.append(f"source page lacks source_url field: {path.relative_to(root)}")

    ledger = root / "00_System/interaction-ledger.md"
    if ledger.exists():
        for number, row in enumerate(first_markdown_table(ledger.read_text(encoding="utf-8")), start=1):
            if not any(cell.strip() for cell in row.values()):
                continue
            missing = []
            if not _value(row, "Date"):
                missing.append("Date")
            if not _value(row, "Organization", "Firm"):
                missing.append("Organization")
            if not _value(row, "Source", "Source URL"):
                missing.append("Source")
            if missing:
                problems.append(
                    "interaction-ledger row "
                    f"{number} is missing provenance fields: {', '.join(missing)}"
                )
    return sorted(set(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a relationship-intelligence Obsidian vault.")
    parser.add_argument("vault", type=Path)
    args = parser.parse_args()
    problems = lint(args.vault.resolve())
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print("Vault passes structural lint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
