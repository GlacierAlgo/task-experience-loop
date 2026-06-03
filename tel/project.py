from __future__ import annotations

import os
import re
from pathlib import Path

WINDOWS_DEFAULT_TEL_DIR = Path("D:/obs/tel")
MAC_DEFAULT_TEL_DIR = Path("/Users/yanghh/obs/tel")
DEFAULT_TEL_DIR = WINDOWS_DEFAULT_TEL_DIR if os.name == "nt" else MAC_DEFAULT_TEL_DIR


def tel_dir() -> Path:
    configured = os.environ.get("TEL_DIR")
    if not configured:
        return default_tel_dir()
    return Path(configured).expanduser()


def default_tel_dir(platform: str | None = None) -> Path:
    platform_name = platform or os.name
    if platform_name == "nt":
        return WINDOWS_DEFAULT_TEL_DIR
    return MAC_DEFAULT_TEL_DIR


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
