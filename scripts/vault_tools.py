from __future__ import annotations

import re
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        yield path


def wikilink_targets(text: str) -> set[str]:
    return {match.strip() for match in WIKILINK_RE.findall(text)}


def append_section_row(path: Path, row: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + row.rstrip() + "\n", encoding="utf-8")


def split_table_row(row: str) -> list[str]:
    row = row.strip().strip("|")
    cells: list[str] = []
    current: list[str] = []
    in_link = False
    index = 0
    while index < len(row):
        if row.startswith("[[", index):
            in_link = True
            current.append("[[")
            index += 2
            continue
        if row.startswith("]]", index):
            in_link = False
            current.append("]]" )
            index += 2
            continue
        if row[index] == "|" and not in_link:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(row[index])
        index += 1
    cells.append("".join(current).strip())
    return cells


def first_markdown_table(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = split_table_row(lines[0])
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        cells = split_table_row(line)
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
            continue
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows
