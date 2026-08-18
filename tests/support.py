from __future__ import annotations

from datetime import date
from pathlib import Path

import frontmatter

from tel import project


def write_decision(
    *,
    domain: str,
    slug: str,
    decision_point: str,
    option_space: list[str],
    choice: str,
    constraints: list[str],
    implications: list[str],
    evolution_trigger: list[str] | None = None,
    projects: list[str] | None = None,
) -> Path:
    metadata: dict[str, object] = {
        "domain": domain,
        "decided": date.today().isoformat(),
        "status": "active",
    }
    if projects:
        metadata["projects"] = projects
    post = frontmatter.Post(content="", handler=None, **metadata)
    body = [
        f"# {choice}",
        "",
        "## Decision Point",
        decision_point,
        "",
        "## Option Space",
        *[f"- {option}" for option in option_space],
        "",
        "## Choice",
        choice,
        "",
        "## Constraints & Rationale",
        *[f"- {constraint}" for constraint in constraints],
        "",
        "## Implications",
        *[f"- {implication}" for implication in implications],
    ]
    if evolution_trigger:
        body.extend(["", "## Evolution Trigger", *[f"- {trigger}" for trigger in evolution_trigger]])
    post.content = "\n".join(body)

    path = project.tel_dir() / "decisions" / f"{domain}--{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter.dumps(post) + "\n")
    return path


def write_pattern(
    *,
    slug: str,
    situation: str,
    action: str,
    outcome: str,
    domain: str = "",
) -> Path:
    post = frontmatter.Post(
        content=(
            f"# {slug}\n\n"
            f"## Situation\n{situation}\n\n"
            f"## Action\n{action}\n\n"
            f"## Outcome\n{outcome}\n"
        ),
        handler=None,
        domain=domain,
        created=date.today().isoformat(),
        uses=0,
    )
    path = project.tel_dir() / "patterns" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter.dumps(post) + "\n")
    return path
