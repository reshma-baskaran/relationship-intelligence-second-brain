from __future__ import annotations

import argparse
from pathlib import Path

from vault_tools import markdown_files, wikilink_targets


REQUIRED = (
    "00_System/index.md",
    "00_System/source-register.md",
    "00_System/interaction-ledger.md",
    "00_System/stakeholder-interest-register.md",
    "00_System/log.md",
)


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

