from __future__ import annotations

import fcntl
from dataclasses import dataclass
from pathlib import Path

from tel import project


@dataclass(frozen=True)
class Noun:
    term: str
    meaning: str


def nouns_path() -> Path:
    return project.tel_dir() / "nouns.md"


def _parse_line(line: str) -> Noun | None:
    stripped = line.strip()
    if not stripped.startswith("- "):
        return None
    body = stripped[2:].strip()
    if not body:
        return None

    if " -> " in body:
        term, meaning = body.split(" -> ", 1)
    elif ":" in body:
        term, meaning = body.split(":", 1)
    else:
        return None

    term = term.strip().strip("`")
    meaning = meaning.strip()
    if not term or not meaning:
        return None
    return Noun(term=term, meaning=meaning)


def query() -> list[Noun]:
    path = nouns_path()
    if not path.exists():
        return []
    results = []
    for line in path.read_text().splitlines():
        noun = _parse_line(line)
        if noun:
            results.append(noun)
    return results


def record(term: str, meaning: str) -> Noun:
    path = nouns_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    new_noun = Noun(term=term.strip(), meaning=meaning.strip())
    if not new_noun.term or not new_noun.meaning:
        raise ValueError("Both term and meaning are required")

    # Use advisory file lock to prevent concurrent write races
    with open(path, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            entries: dict[str, Noun] = {}
            for line in f.read().splitlines():
                noun = _parse_line(line)
                if noun:
                    entries[noun.term.lower()] = noun
            entries[new_noun.term.lower()] = new_noun

            lines = [
                "# Global Nouns",
                "",
                "User-specific terms that agents should resolve before generic meanings.",
                "",
            ]
            for key in sorted(entries):
                noun = entries[key]
                lines.append(f"- {noun.term} -> {noun.meaning}")

            f.seek(0)
            f.truncate()
            f.write("\n".join(lines) + "\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return new_noun
