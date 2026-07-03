from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from tel import decisions, kanban, nouns, patterns, project


def _context_path() -> Path:
    return project.tel_dir() / "loop-context.md"


def _constraints_path() -> Path:
    return project.tel_dir() / "constraints.md"


def _append_grouped(sections: list[str], items: list, *, max_items_per_domain: int | None = None) -> None:
    by_domain: dict[str, list] = defaultdict(list)
    for d in items:
        by_domain[d.domain].append(d)
    for domain in sorted(by_domain.keys()):
        sections.append(f"### {domain}")
        domain_items = by_domain[domain]
        shown = domain_items if max_items_per_domain is None else domain_items[:max_items_per_domain]
        for d in shown:
            sections.append(f"- [{d.filename}](decisions/{d.filename}): {d.choice}")
        if max_items_per_domain is not None and len(domain_items) > max_items_per_domain:
            sections.append(f"- ... {len(domain_items) - max_items_per_domain} more; see summaries/domains/{domain}.md")


def _append_summary_links(sections: list[str], current_project: str) -> None:
    summary_root = project.tel_dir() / "summaries"
    if not summary_root.exists():
        return
    sections.append("## Experience Summaries")
    index_path = summary_root / "index.md"
    project_path = summary_root / "projects" / f"{current_project}.md"
    compact_path = summary_root / "compact.md"
    if index_path.exists():
        sections.append("- [TEL summary index](summaries/index.md)")
    if project_path.exists():
        sections.append(f"- [Current project summary](summaries/projects/{current_project}.md)")
    if compact_path.exists():
        sections.append("- [Compact review](summaries/compact.md)")
    sections.append("")


def _append_global_nouns(sections: list[str]) -> None:
    all_nouns = nouns.query()
    if not all_nouns:
        return
    sections.append("## Global Nouns")
    for noun in all_nouns[:12]:
        sections.append(f"- {noun.term} -> {noun.meaning}")
    if len(all_nouns) > 12:
        sections.append(f"- ... {len(all_nouns) - 12} more; see nouns.md")
    sections.append("")


def _one_line(text: str, limit: int = 220) -> str:
    value = " ".join(text.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


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

    _append_global_nouns(sections)

    _append_summary_links(sections, current_project)

    sections.append("## Relevant Decisions")
    all_active = decisions.query(status="active")
    if active:
        related = decisions.related_to(active.title)
        if related:
            for d in related[:15]:
                sections.append(f"- [{d.filename}](decisions/{d.filename}): {_one_line(d.choice)}")
            if len(related) > 15:
                sections.append(f"- ... {len(related) - 15} more; see summaries/index.md")
        else:
            sections.append("(none matched active task; see summaries/index.md)")
    else:
        if all_active:
            sections.append("No active task. Use summaries/index.md and the current project summary for lookup.")
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


def regenerate(project_id: str | None = None, *, refresh_summaries: bool = True):
    if refresh_summaries:
        from tel import organize

        organize.write_summaries(project_id=project_id)
    _context_path().write_text(assemble(project_id))
