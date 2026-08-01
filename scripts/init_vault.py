from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPOSITORY_ROOT / "vault-template"


def configured_vault(config_path: Path) -> Path:
    """Read and resolve the vault path from a local JSON configuration file."""
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"configuration file does not exist: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"configuration file is not valid JSON: {config_path}") from error

    raw_path = config.get("vault_path") if isinstance(config, dict) else None
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("configuration must contain a non-empty string: vault_path")
    return Path(raw_path).expanduser()


def _ensure_safe_target(target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if resolved == REPOSITORY_ROOT.resolve() or REPOSITORY_ROOT.resolve() in resolved.parents:
        raise ValueError(
            "choose a vault path outside this public repository so private notes cannot be committed by accident"
        )
    if resolved == TEMPLATE_ROOT.resolve() or TEMPLATE_ROOT.resolve() in resolved.parents:
        raise ValueError("the vault path cannot be inside vault-template")
    return resolved


def install_template(target: Path, *, overwrite: bool = False) -> tuple[list[str], list[str]]:
    """Copy the blank template without deleting or replacing user files by default."""
    if not TEMPLATE_ROOT.is_dir():
        raise ValueError(f"template directory is missing: {TEMPLATE_ROOT}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"vault path is not a directory: {target}")

    target.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []

    for source in sorted(TEMPLATE_ROOT.rglob("*")):
        destination = target / source.relative_to(TEMPLATE_ROOT)
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        relative = str(destination.relative_to(target))
        if destination.exists() and not overwrite:
            skipped.append(relative)
            continue
        shutil.copy2(source, destination)
        created.append(relative)

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a blank relationship-intelligence vault outside the public repository."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--vault", type=Path, help="destination path for the new vault")
    target.add_argument("--config", type=Path, help="local JSON config containing vault_path")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace files that already exist; never deletes files (use with care)",
    )
    args = parser.parse_args()

    try:
        requested = args.vault if args.vault is not None else configured_vault(args.config)
        destination = _ensure_safe_target(requested)
        created, skipped = install_template(destination, overwrite=args.overwrite)
    except ValueError as error:
        parser.error(str(error))

    print(f"Vault ready: {destination}")
    print(f"Created: {len(created)} files")
    if skipped:
        print(f"Skipped existing files: {len(skipped)}")
    print("Open the destination in Obsidian, then run scripts/lint_vault.py against it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
