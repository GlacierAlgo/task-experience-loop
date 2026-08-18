from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

from tel import project


def decisions_dir() -> Path:
    return project.tel_dir() / "decisions"


@dataclass
class Decision:
    domain: str
    slug: str
    projects: list[str]
    decision_point: str
    option_space: list[str]
    choice: str
    constraints: list[str]
    implications: list[str]
    evolution_trigger: list[str] = field(default_factory=list)
    decided: str = ""
    status: str = "active"

    @property
    def filename(self) -> str:
        return f"{self.domain}--{self.slug}.md"


def _parse_list_section(content: str, header: str) -> list[str]:
    lines = content.split("\n")
    items: list[str] = []
    current: list[str] = []
    in_section = False

    def flush() -> None:
        if current:
            items.append(" ".join(current))
            current.clear()

    for line in lines:
        if line.startswith("## ") and header.lower() in line.lower():
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            flush()
            break
        if not in_section:
            continue

        stripped = line.strip()
        if not stripped:
            flush()
            continue

        item = re.match(r"^(?:[-*+]|\d+[.)])\s+(.+)$", stripped)
        if item:
            flush()
            current.append(item.group(1).strip())
            continue

        current.append(stripped)

    flush()
    return items


def _parse_section_text(content: str, header: str) -> str:
    lines = content.split("\n")
    result = []
    in_section = False
    for line in lines:
        if line.startswith("## ") and header.lower() in line.lower():
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            break
        if in_section and line.strip():
            result.append(line.strip())
    return "\n".join(result)


def _load(path: Path) -> Decision:
    post = frontmatter.load(str(path))
    content = post.content
    stem = path.stem
    parts = stem.split("--", 1)
    domain = parts[0] if len(parts) > 1 else post.metadata.get("domain", "")
    slug = parts[1] if len(parts) > 1 else stem

    return Decision(
        domain=domain,
        slug=slug,
        projects=_parse_projects(post.metadata.get("projects", [])),
        decision_point=_parse_section_text(content, "Decision Point"),
        option_space=_parse_list_section(content, "Option Space"),
        choice=_parse_section_text(content, "Choice"),
        constraints=_parse_list_section(content, "Constraints & Rationale"),
        implications=_parse_list_section(content, "Implications"),
        evolution_trigger=_parse_list_section(content, "Evolution Trigger"),
        decided=str(post.metadata.get("decided", "")),
        status=post.metadata.get("status", "active"),
    )


def _parse_projects(value: object) -> list[str]:
    if isinstance(value, str):
        raw_projects = [value]
    elif isinstance(value, (list, tuple, set)):
        raw_projects = [str(item) for item in value]
    else:
        raw_projects = []
    return list(dict.fromkeys(project.slugify(item) for item in raw_projects if item.strip()))


def query(domain: str | None = None, status: str = "active") -> list[Decision]:
    directory = decisions_dir()
    if not directory.exists():
        return []
    results = []
    for f in sorted(directory.iterdir()):
        if not f.suffix == ".md":
            continue
        d = _load(f)
        if status and d.status != status:
            continue
        if domain and d.domain != domain:
            continue
        results.append(d)
    return results


VALID_DOMAINS = ("architecture", "interface", "data", "deployment", "frontend", "workflow", "research")
VALID_STATUSES = ("active", "superseded")


def validate(path: Path) -> list[str]:
    errors = []
    try:
        d = _load(path)
    except Exception as e:
        return [f"Parse error: {e}"]

    if not d.domain:
        errors.append("Missing domain in frontmatter")
    elif d.domain not in VALID_DOMAINS:
        errors.append(f"Invalid domain '{d.domain}', must be one of: {', '.join(VALID_DOMAINS)}")

    if not d.decided:
        errors.append("Missing decided date in frontmatter")

    if d.status not in VALID_STATUSES:
        errors.append(f"Invalid status '{d.status}', must be one of: {', '.join(VALID_STATUSES)}")

    if not d.choice:
        errors.append("Empty ## Choice section")

    if not d.decision_point:
        errors.append("Empty ## Decision Point section")

    if not d.option_space:
        errors.append("Empty ## Option Space section (need 2+ options)")
    elif len(d.option_space) < 2:
        errors.append(f"Option Space has only {len(d.option_space)} option (need 2+)")

    if not d.constraints:
        errors.append("Empty ## Constraints & Rationale section")

    if not d.implications:
        errors.append("Empty ## Implications section")

    return errors


def validate_all() -> dict[str, list[str]]:
    directory = decisions_dir()
    if not directory.exists():
        return {}
    results = {}
    for f in sorted(directory.iterdir()):
        if not f.suffix == ".md":
            continue
        errors = validate(f)
        if errors:
            results[f.name] = errors
    return results
