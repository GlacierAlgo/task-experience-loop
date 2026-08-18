from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tel import decisions, kanban, patterns, project


MAX_DECISIONS_PER_DOMAIN_SUMMARY = 80


@dataclass
class OrganizationReport:
    summary_dir: Path
    written_files: list[Path] = field(default_factory=list)
    removed_files: list[Path] = field(default_factory=list)
    decision_count: int = 0
    pattern_count: int = 0
    project_count: int = 0


def summaries_dir() -> Path:
    return project.tel_dir() / "summaries"


def _project_summaries_dir() -> Path:
    return summaries_dir() / "projects"


def _domain_summaries_dir() -> Path:
    return summaries_dir() / "domains"


def _write(path: Path, content: str, report: OrganizationReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    report.written_files.append(path)


def _remove_stale_summary_files(directory: Path, expected_filenames: set[str], report: OrganizationReport) -> None:
    if not directory.exists():
        return
    for path in directory.glob("*.md"):
        if path.name not in expected_filenames:
            path.unlink()
            report.removed_files.append(path)


def _one_line(text: str, limit: int = 180) -> str:
    value = " ".join(text.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _related_decisions(
    project_id: str,
    all_decisions: list[decisions.Decision],
) -> list[decisions.Decision]:
    return sorted(
        (d for d in all_decisions if project_id in d.projects),
        key=lambda d: (d.domain, d.slug),
    )


def _all_boards() -> dict[str, dict[str, list[kanban.Task]]]:
    return {project_id: kanban.list_all(project_id) for project_id in kanban.list_projects()}


def _render_index(
    all_decisions: list[decisions.Decision],
    all_patterns: list[patterns.Pattern],
    boards: dict[str, dict[str, list[kanban.Task]]],
) -> str:
    current_project = project.current_project_id()
    domain_counts = Counter(d.domain for d in all_decisions)
    lines = [
        "# TEL Experience Summary",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Current project: `{current_project}`",
        "",
        "## Inventory",
        f"- Active decisions: {len(all_decisions)}",
        f"- Patterns: {len(all_patterns)}",
        f"- Projects: {len(boards)}",
        "",
        "## Domain Summaries",
    ]
    if domain_counts:
        for domain, count in domain_counts.most_common():
            lines.append(f"- [{domain}](domains/{domain}.md): {count} active decisions")
    else:
        lines.append("(none)")

    lines.extend(["", "## Project Summaries"])
    if boards:
        for project_id in sorted(boards):
            board = boards[project_id]
            backlog = len(board.get("Backlog", []))
            active = len(board.get("Active", []))
            lines.append(
                f"- [{project_id}](projects/{project_id}.md): "
                f"{backlog} backlog, {active} active"
            )
    else:
        lines.append("(none)")

    lines.append("")
    return "\n".join(lines)


def _render_domain_summary(domain: str, items: list[decisions.Decision]) -> str:
    items = sorted(items, key=lambda d: (d.decided, d.slug), reverse=True)
    lines = [
        f"# {domain}",
        "",
        f"Active decisions: {len(items)}",
        "",
        "## Current Decisions",
    ]

    for d in items[:MAX_DECISIONS_PER_DOMAIN_SUMMARY]:
        decided = f" ({d.decided})" if d.decided else ""
        lines.append(f"- [{d.filename}](../../decisions/{d.filename}){decided}: {_one_line(d.choice)}")
    if len(items) > MAX_DECISIONS_PER_DOMAIN_SUMMARY:
        lines.append(f"- ... {len(items) - MAX_DECISIONS_PER_DOMAIN_SUMMARY} more active decisions omitted")
    lines.append("")
    return "\n".join(lines)


def _render_project_summary(
    project_id: str,
    board: dict[str, list[kanban.Task]],
    related: list[decisions.Decision],
) -> str:
    lines = [
        f"# {project_id}",
        "",
        "## Current Work",
    ]
    for column in ("Backlog", "Active"):
        tasks = board.get(column, [])
        lines.append(f"### {column}")
        if not tasks:
            lines.append("(empty)")
            continue
        for task in tasks[:40]:
            suffix = f" | {task.meta}" if task.meta else ""
            lines.append(f"- {task.title}{suffix}")
        if len(tasks) > 40:
            lines.append(f"- ... {len(tasks) - 40} more tasks omitted")

    lines.extend(["", "## Current Decisions"])
    if related:
        for d in related:
            lines.append(
                f"- [{d.filename}](../../decisions/{d.filename}) - {_one_line(d.choice)}"
            )
    else:
        lines.append("(none explicitly assigned)")
    lines.append("")
    return "\n".join(lines)


def write_summaries(project_id: str | None = None) -> OrganizationReport:
    all_decisions = decisions.query(status="active")
    all_patterns = patterns.query()
    boards = _all_boards()
    for d in all_decisions:
        for decision_project in d.projects:
            boards.setdefault(decision_project, kanban.list_all(decision_project))
    requested_project = project.slugify(project_id) if project_id else project.current_project_id()
    if requested_project not in boards:
        boards[requested_project] = kanban.list_all(requested_project)

    report = OrganizationReport(
        summary_dir=summaries_dir(),
        decision_count=len(all_decisions),
        pattern_count=len(all_patterns),
        project_count=len(boards),
    )

    by_domain: dict[str, list[decisions.Decision]] = defaultdict(list)
    for d in all_decisions:
        by_domain[d.domain].append(d)

    _remove_stale_summary_files(
        _domain_summaries_dir(),
        {f"{domain}.md" for domain in by_domain},
        report,
    )
    _remove_stale_summary_files(
        _project_summaries_dir(),
        {f"{board_project_id}.md" for board_project_id in boards},
        report,
    )
    obsolete_review = summaries_dir() / "conflicts.md"
    if obsolete_review.exists():
        obsolete_review.unlink()
        report.removed_files.append(obsolete_review)

    _write(
        summaries_dir() / "index.md",
        _render_index(all_decisions, all_patterns, boards),
        report,
    )

    for domain, items in sorted(by_domain.items()):
        _write(_domain_summaries_dir() / f"{domain}.md", _render_domain_summary(domain, items), report)

    for board_project_id, board in sorted(boards.items()):
        related = _related_decisions(board_project_id, all_decisions)
        _write(
            _project_summaries_dir() / f"{board_project_id}.md",
            _render_project_summary(board_project_id, board, related),
            report,
        )

    return report
