#!/usr/bin/env python3
"""Auto-sort a folder by file type into subfolders."""

import argparse
import shutil
import sys
import time
from pathlib import Path

CATEGORIES: dict[str, tuple[str, ...]] = {
    "Images": (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
               ".tiff", ".ico", ".heic", ".raw"),
    "Videos": (".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv",
               ".m4v", ".mpg", ".mpeg"),
    "Audio": (".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
              ".opus"),
    "Documents": (".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
                  ".tex", ".epub", ".pages"),
    "Spreadsheets": (".xls", ".xlsx", ".ods", ".csv", ".tsv", ".numbers"),
    "Presentations": (".ppt", ".pptx", ".odp", ".key"),
    "Archives": (".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
                 ".tgz", ".tbz2"),
    "Code": (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
             ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".sh",
             ".html", ".css", ".scss", ".json", ".xml", ".yml", ".yaml",
             ".sql", ".toml"),
    "Executables": (".exe", ".msi", ".deb", ".rpm", ".dmg", ".pkg",
                    ".appimage", ".apk"),
    "Fonts": (".ttf", ".otf", ".woff", ".woff2"),
    "Torrents": (".torrent",),
}

OTHER = "Other"

EXT_TO_CATEGORY = {
    ext: category
    for category, exts in CATEGORIES.items()
    for ext in exts
}


def category_for(path: Path) -> str:
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHER)


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def organize(source: Path, dry_run: bool) -> int:
    if not source.is_dir():
        print(f"error: {source} is not a directory", file=sys.stderr)
        return 1

    category_dirs = set(CATEGORIES.keys()) | {OTHER}
    moved = 0

    for entry in sorted(source.iterdir()):
        if entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name == Path(__file__).name and entry.parent == Path(__file__).parent:
            continue

        category = category_for(entry)
        target_dir = source / category
        dest = unique_destination(target_dir / entry.name)

        action = "would move" if dry_run else "moved"
        print(f"{action}: {entry.name} -> {category}/{dest.name}")

        if not dry_run:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(entry), str(dest))
        moved += 1

    if moved == 0:
        print("Nothing to organize.")
    else:
        suffix = " (dry run)" if dry_run else ""
        print(f"\n{moved} file(s) processed{suffix}.")
    _ = category_dirs  # kept for readability
    return 0


def watch(source: Path, dry_run: bool, interval: float) -> int:
    print(f"Watching {source} (every {interval}s). Ctrl+C to stop.")
    try:
        while True:
            organize(source, dry_run)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-sort a folder by file type.")
    parser.add_argument("-p", "--path", type=Path,
                        default=Path.home() / "Downloads",
                        help="Folder to organize (default: ~/Downloads)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Show what would happen without moving anything")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="Keep running and re-check periodically")
    parser.add_argument("-i", "--interval", type=float, default=5.0,
                        help="Watch interval in seconds (default 5)")
    args = parser.parse_args()

    source = args.path.expanduser().resolve()
    if args.watch:
        sys.exit(watch(source, args.dry_run, args.interval))
    sys.exit(organize(source, args.dry_run))


if __name__ == "__main__":
    main()
