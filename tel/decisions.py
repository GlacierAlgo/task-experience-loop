from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import frontmatter

DECISIONS_DIR = Path("/Users/yanghh/obs/tel/decisions")
ARCHIVE_DIR = Path("/Users/yanghh/obs/tel/archive")


@dataclass
class Decision:
    domain: str
    slug: str
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

    @property
    def title(self) -> str:
        return self.choice


def _decision_path(slug: str) -> Path | None:
    for f in DECISIONS_DIR.iterdir():
        if f.stem.endswith(f"--{slug}") or f.stem == slug:
            return f
    return None


def _parse_list_section(content: str, header: str) -> list[str]:
    lines = content.split("\n")
    items = []
    in_section = False
    for line in lines:
        if line.startswith("## ") and header.lower() in line.lower():
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            break
        if in_section and line.startswith("- "):
            items.append(line[2:].strip())
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
        decision_point=_parse_section_text(content, "Decision Point"),
        option_space=_parse_list_section(content, "Option Space"),
        choice=_parse_section_text(content, "Choice"),
        constraints=_parse_list_section(content, "Constraints & Rationale"),
        implications=_parse_list_section(content, "Implications"),
        evolution_trigger=_parse_list_section(content, "Evolution Trigger"),
        decided=str(post.metadata.get("decided", "")),
        status=post.metadata.get("status", "active"),
    )


def _render(d: Decision) -> str:
    meta = frontmatter.Post(
        content="",
        handler=None,
        domain=d.domain,
        decided=d.decided or date.today().isoformat(),
        status=d.status,
    )

    body_parts = [
        f"# {d.choice}",
        "",
        "## Decision Point",
        d.decision_point,
        "",
        "## Option Space",
        *[f"- {opt}" for opt in d.option_space],
        "",
        "## Choice",
        d.choice,
        "",
        "## Constraints & Rationale",
        *[f"- {c}" for c in d.constraints],
        "",
        "## Implications",
        *[f"- {imp}" for imp in d.implications],
    ]

    if d.evolution_trigger:
        body_parts.extend(["", "## Evolution Trigger", *[f"- {t}" for t in d.evolution_trigger]])

    meta.content = "\n".join(body_parts)
    return frontmatter.dumps(meta) + "\n"


def record(
    domain: str,
    slug: str,
    decision_point: str,
    option_space: list[str],
    choice: str,
    constraints: list[str],
    implications: list[str],
    evolution_trigger: list[str] | None = None,
) -> Decision:
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    d = Decision(
        domain=domain,
        slug=slug,
        decision_point=decision_point,
        option_space=option_space,
        choice=choice,
        constraints=constraints,
        implications=implications,
        evolution_trigger=evolution_trigger or [],
        decided=date.today().isoformat(),
    )
    path = DECISIONS_DIR / d.filename
    path.write_text(_render(d))
    return d


def query(domain: str | None = None, status: str = "active") -> list[Decision]:
    if not DECISIONS_DIR.exists():
        return []
    results = []
    for f in sorted(DECISIONS_DIR.iterdir()):
        if not f.suffix == ".md":
            continue
        d = _load(f)
        if status and d.status != status:
            continue
        if domain and d.domain != domain:
            continue
        results.append(d)
    return results


def get(slug: str) -> Decision | None:
    path = _decision_path(slug)
    if path is None:
        return None
    return _load(path)


def supersede(old_slug: str, new_slug: str, reason: str):
    old_path = _decision_path(old_slug)
    if old_path is None:
        raise ValueError(f"Decision not found: {old_slug}")
    old = _load(old_path)
    old.status = "superseded"
    old_path.write_text(_render(old))
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    old_path.rename(ARCHIVE_DIR / old_path.name)


def related_to(task_title: str) -> list[Decision]:
    keywords = set(task_title.lower().replace("-", " ").replace("_", " ").split())
    all_decisions = query()
    results = []
    for d in all_decisions:
        domain_words = set(d.domain.lower().replace("-", " ").replace("_", " ").split())
        if keywords & domain_words:
            results.append(d)
            continue
        choice_words = set(d.choice.lower().replace("-", " ").replace("_", " ").split())
        if keywords & choice_words:
            results.append(d)
    return results
