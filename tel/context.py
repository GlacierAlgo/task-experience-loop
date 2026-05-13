from __future__ import annotations

from pathlib import Path

from tel import decisions, kanban

TEL_DIR = Path("/Users/yanghh/obs/tel")
CONTEXT_PATH = TEL_DIR / "loop-context.md"
CONSTRAINTS_PATH = TEL_DIR / "constraints.md"


def assemble() -> str:
    sections = [
        "# Task-Experience Loop Context",
        "<!-- Auto-generated. Do not edit manually. Run `tel context` to regenerate. -->",
        "",
    ]

    active = kanban.get_active()
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
    if CONSTRAINTS_PATH.exists():
        for line in CONSTRAINTS_PATH.read_text().splitlines():
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
        if not related:
            related = all_active[:5]
    else:
        related = all_active[:5]
    if related:
        for d in related:
            sections.append(f"- [{d.filename}](decisions/{d.filename}): {d.choice}")
    else:
        sections.append("(none yet)")
    sections.append("")

    sections.append("## Recent Completions")
    board = kanban.list_all()
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

    return "\n".join(sections) + "\n"


def regenerate():
    CONTEXT_PATH.write_text(assemble())
