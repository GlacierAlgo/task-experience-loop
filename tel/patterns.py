from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import frontmatter

from tel import project


def patterns_dir() -> Path:
    return project.tel_dir() / "patterns"


@dataclass
class Pattern:
    slug: str
    situation: str
    action: str
    outcome: str
    domain: str = ""
    created: str = ""
    uses: int = 0

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"


def _load(path: Path) -> Pattern:
    post = frontmatter.load(str(path))
    content = post.content
    situation = _extract_section(content, "Situation")
    action = _extract_section(content, "Action")
    outcome = _extract_section(content, "Outcome")
    return Pattern(
        slug=path.stem,
        situation=situation,
        action=action,
        outcome=outcome,
        domain=post.metadata.get("domain", ""),
        created=str(post.metadata.get("created", "")),
        uses=post.metadata.get("uses", 0),
    )


def _extract_section(content: str, header: str) -> str:
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


def query(domain: str | None = None) -> list[Pattern]:
    directory = patterns_dir()
    if not directory.exists():
        return []
    results = []
    for f in sorted(directory.iterdir()):
        if not f.suffix == ".md":
            continue
        p = _load(f)
        if domain and p.domain != domain:
            continue
        results.append(p)
    return results
