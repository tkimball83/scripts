#!/usr/bin/env python3

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pymediainfo import MediaInfo
from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.output import hide_interrupt_echo, spinner, status

ENGLISH = {"en", "eng"}

try:
    WORKERS = int(os.environ.get("WORKERS", "8"))
except ValueError:
    WORKERS = 8
if WORKERS < 1:
    WORKERS = 8


def probe_languages(file: Path) -> tuple[str, list[str]] | None:
    media_info = MediaInfo.parse(file, parse_speed=0.25)
    if not any(t.track_type == "Video" for t in media_info.tracks):
        return None
    audio = [t for t in media_info.tracks if t.track_type == "Audio"]
    if not audio:
        return "-", []

    def lang(track) -> str:
        return (track.language or "und").lower()

    default = next((t for t in audio if t.default == "Yes"), audio[0])
    return lang(default), sorted({lang(t) for t in audio})


def is_english(lang: str) -> bool:
    return lang.split("-")[0] in ENGLISH


def needs_attention(default_lang: str, languages: list[str]) -> bool:
    if not is_english(default_lang):
        return True
    return any(not is_english(lang) for lang in languages)


def walk_files(directory: Path, errors: list[str]) -> list[Path]:
    files = []
    for root, _dirs, names in os.walk(
        directory, onerror=lambda e: errors.append(str(e))
    ):
        files.extend(Path(root) / name for name in names)
    return sorted(files)


def main() -> int:
    if len(sys.argv) < 2:
        status(f"USAGE: {Path(sys.argv[0]).name} DIR [DIR ...]")
        return 2
    directories = [Path(d) for d in sys.argv[1:]]

    rows = []
    errors: list[str] = []
    scanned = 0
    skipped = 0

    files = []
    for directory in directories:
        if not directory.is_dir():
            errors.append(f"not a directory: {directory}")
            continue
        with spinner(f"Scanning {directory}"):
            files.extend(walk_files(directory, errors))

    status(f"Found {len(files)} file(s) to check")
    pool = ThreadPoolExecutor(max_workers=WORKERS)
    try:
        futures = {pool.submit(probe_languages, file): file for file in files}
        for future in as_completed(futures):
            file = futures[future]
            status(f"Checking {file.name}")
            try:
                probed = future.result()
            except (OSError, RuntimeError, ValueError) as exc:
                errors.append(f"{file}: {exc}")
                continue
            if probed is None:
                skipped += 1
                continue
            scanned += 1
            default_lang, languages = probed
            if needs_attention(default_lang, languages):
                rows.append((str(file), default_lang, ",".join(languages) or "-"))
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    rows.sort()

    if rows:
        print(
            tabulate(rows, headers=["File", "Default", "Languages"], tablefmt="simple")
        )

    for error in errors:
        status(f"ERROR: {error}")
    status(
        f"Scanned {scanned} video file(s), skipped {skipped} non-video, flagged {len(rows)}."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        with hide_interrupt_echo():
            sys.exit(main())
    except KeyboardInterrupt:
        status("Interrupted.")
        os._exit(130)
