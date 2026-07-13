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


def _relevant_decisions(current_project: str, active_task: kanban.Task | None) -> list[decisions.Decision]:
    """Find decisions relevant to the current context.

    Strategy: combine active task keyword matching with project-name matching.
    Requires a minimum relevance score to avoid flooding context with loosely
    related decisions (e.g. all "shadow-*" projects sharing one word).
    """
    all_active = decisions.query(status="active")
    if not all_active:
        return []

    # Collect relevance signals from multiple sources
    keywords: set[str] = set()

    # Signal 1: active task title words (strongest intent signal)
    if active_task:
        keywords.update(active_task.title.lower().replace("-", " ").replace("_", " ").split())

    # Signal 2: project name words (e.g. "shadow-backtest" → {"shadow", "backtest"})
    project_words = set(current_project.lower().replace("-", " ").replace("_", " ").split())
    keywords.update(project_words)

    # Remove noise words that cause false positives
    noise = {"the", "a", "an", "and", "or", "of", "to", "in", "for", "is", "it", "on",
             "no", "not", "as", "at", "by", "be", "do", "use", "all", "this", "that",
             "with", "from", "are", "was", "were", "been", "has", "have", "had"}
    keywords -= noise

    # Require multi-word project names to match at least 2 words to avoid
    # "shadow" alone pulling in all shadow-* decisions
    min_score = 2 if len(project_words - noise) > 1 and not active_task else 1

    # Score each decision by keyword overlap
    scored: list[tuple[int, decisions.Decision]] = []
    for d in all_active:
        score = 0
        domain_words = set(d.domain.lower().replace("-", " ").replace("_", " ").split())
        choice_words = set(d.choice.lower().replace("-", " ").replace("_", " ").split())
        point_words = set(d.decision_point.lower().replace("-", " ").replace("_", " ").split())
        slug_words = set(d.slug.lower().replace("-", " ").replace("_", " ").split())

        # Slug match is strong (directly names the topic)
        slug_hits = len(keywords & slug_words)
        domain_hits = len(keywords & domain_words)
        choice_hits = len(keywords & choice_words)
        point_hits = len(keywords & point_words)

        score += slug_hits * 3
        score += domain_hits * 2
        score += choice_hits * 2
        score += point_hits * 1

        if score >= min_score:
            scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored]


def assemble(project_id: str | None = None) -> str:
    current_project = project_id or project.current_project_id()
    root = project.current_project_root()
    board_path = kanban.kanban_path()

    sections = [
        "# Task-Experience Loop Context",
        "<!-- Auto-generated. Do not edit manually. Run `tel context` to regenerate. -->",
        "",
    ]

    # --- Project-specific section ---
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

    # --- Global knowledge section (shared across all projects) ---
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

    # Decisions: use multi-signal relevance instead of active-task-only matching
    sections.append("## Relevant Decisions")
    related = _relevant_decisions(current_project, active)
    if related:
        for d in related[:15]:
            sections.append(f"- [{d.filename}](decisions/{d.filename}): {_one_line(d.choice)}")
        if len(related) > 15:
            sections.append(f"- ... {len(related) - 15} more; see summaries/index.md")
    else:
        all_active = decisions.query(status="active")
        if all_active:
            sections.append("No keyword matches. Use `tel search <keyword>` or see summaries/index.md.")
        else:
            sections.append("(none yet)")
    sections.append("")

    # --- Project-specific progress ---
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

    # --- Global patterns (shared) ---
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


def ensure_current():
    """If loop-context.md points to a different project than cwd, regenerate it.

    Call this at CLI entry to keep the file fresh without manual intervention.
    """
    ctx_path = _context_path()
    if not ctx_path.exists():
        regenerate(refresh_summaries=False)
        return

    current = project.current_project_id()
    # Quick check: read the first few lines to find the Project: line
    for line in ctx_path.read_text().splitlines()[:10]:
        if line.startswith("- Project: `"):
            stored = line.split("`")[1] if "`" in line else ""
            if stored != current:
                regenerate(refresh_summaries=False)
            return
    # Could not determine stored project; regenerate to be safe
    regenerate(refresh_summaries=False)
