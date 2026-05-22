from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from tel import decisions, kanban, patterns, project


def _context_path() -> Path:
    return project.tel_dir() / "loop-context.md"


def _constraints_path() -> Path:
    return project.tel_dir() / "constraints.md"


def _append_grouped(sections: list[str], items: list) -> None:
    by_domain: dict[str, list] = defaultdict(list)
    for d in items:
        by_domain[d.domain].append(d)
    for domain in sorted(by_domain.keys()):
        sections.append(f"### {domain}")
        for d in by_domain[domain]:
            sections.append(f"- [{d.filename}](decisions/{d.filename}): {d.choice}")


def assemble(project_id: str | None = None) -> str:
    current_project = project_id or project.current_project_id()
    root = project.current_project_root()
    board_path = kanban.kanban_path()

    sections = [
        "# Task-Experience Loop Context",
        "<!-- Auto-generated. Do not edit manually. Run `tel context` to regenerate. -->",
        "",
    ]

    sections.append("## Project Scope")
    sections.append(f"- Project: `{current_project}`")
    sections.append(f"- Root: `{root}`")
    sections.append(f"- Kanban: `{board_path}`")
    sections.append("")

    active = kanban.get_active(current_project)
    sections.append("## Active Task")
    if active:
        line = active.title
        if active.meta:
            line += f" | {active.meta}"
        sections.append(line)
    else:
        sections.append("(none)")
    sections.append("")

    sections.append("## Global Constraints")
    constraints_path = _constraints_path()
    if constraints_path.exists():
        for line in constraints_path.read_text().splitlines():
            if line.startswith("- "):
                sections.append(line)
            elif line.startswith("## ") and "Global Constraints" not in line:
                sections.append("#" + line)
    else:
        sections.append("(none defined)")
    sections.append("")

    sections.append("## Relevant Decisions")
    all_active = decisions.query(status="active")
    if active:
        related = decisions.related_to(active.title)
        if related:
            for d in related:
                sections.append(f"- [{d.filename}](decisions/{d.filename}): {d.choice}")
        else:
            _append_grouped(sections, all_active)
    else:
        _append_grouped(sections, all_active)
    if not all_active:
        sections.append("(none yet)")
    sections.append("")

    sections.append("## Recent Completions")
    board = kanban.list_all(current_project)
    done = board.get("Done", [])
    recent = done[-3:] if len(done) > 3 else done
    if recent:
        for task in reversed(recent):
            line = f"- {task.title}"
            if task.meta:
                line += f" ({task.meta})"
            sections.append(line)
    else:
        sections.append("(none yet)")
    sections.append("")

    sections.append("## Next Steps (Agent-Planned)")
    backlog = board.get("Backlog", [])
    if backlog:
        for i, task in enumerate(backlog[:5], 1):
            sections.append(f"{i}. {task.title}")
    else:
        sections.append("(awaiting tasks)")
    sections.append("")

    all_patterns = patterns.query()
    if all_patterns:
        sections.append("## Reusable Patterns")
        for p in sorted(all_patterns, key=lambda x: x.uses, reverse=True)[:10]:
            sections.append(f"- **{p.slug}**: {p.situation[:60]} → {p.action[:60]}")

    return "\n".join(sections) + "\n"


def regenerate(project_id: str | None = None):
    _context_path().write_text(assemble(project_id))
