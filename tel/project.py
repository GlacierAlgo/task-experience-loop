from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_TEL_DIR = Path("/Users/yanghh/obs/tel")


def tel_dir() -> Path:
    configured = os.environ.get("TEL_DIR")
    if not configured:
        return DEFAULT_TEL_DIR
    return Path(configured).expanduser()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-").lower()
    return slug or "default"


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def current_project_id(start: Path | None = None) -> str:
    explicit = os.environ.get("TEL_PROJECT")
    if explicit:
        return slugify(explicit)
    return slugify(find_project_root(start).name)


def current_project_root(start: Path | None = None) -> Path:
    return find_project_root(start)
