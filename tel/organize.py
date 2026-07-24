from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tel import decisions, kanban, patterns, project


MAX_DECISIONS_PER_DOMAIN_SUMMARY = 80


@dataclass
class DuplicateCandidate:
    first: str
    second: str
    reason: str


@dataclass
class OrganizationReport:
    summary_dir: Path
    written_files: list[Path] = field(default_factory=list)
    removed_files: list[Path] = field(default_factory=list)
    decision_count: int = 0
    pattern_count: int = 0
    project_count: int = 0
    validation_error_count: int = 0
    duplicate_candidate_count: int = 0


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


def _tokenize(text: str) -> set[str]:
    tokens = set()
    normalized = text.lower().replace("_", " ").replace("-", " ")
    for token in re.findall(r"[a-z0-9]{3,}|[\u4e00-\u9fff]{2,}", normalized):
        if token not in {"the", "and", "for", "with", "from", "that", "this"}:
            tokens.add(token)
    return tokens


def _related_decisions(
    project_id: str,
    all_decisions: list[decisions.Decision],
) -> list[decisions.Decision]:
    return sorted(
        (d for d in all_decisions if project_id in d.projects),
        key=lambda d: (d.domain, d.slug),
    )


def _find_duplicate_candidates(all_decisions: list[decisions.Decision]) -> list[DuplicateCandidate]:
    candidates: list[DuplicateCandidate] = []
    by_exact_choice: dict[str, list[decisions.Decision]] = defaultdict(list)
    by_slug: dict[str, list[decisions.Decision]] = defaultdict(list)

    for d in all_decisions:
        choice_key = re.sub(r"\s+", " ", d.choice.lower()).strip()
        if len(choice_key) >= 24:
            by_exact_choice[choice_key].append(d)
        by_slug[d.slug].append(d)

    for group in by_exact_choice.values():
        if len(group) < 2:
            continue
        for first, second in zip(group, group[1:]):
            candidates.append(
                DuplicateCandidate(first.filename, second.filename, "same normalized choice text")
            )

    for group in by_slug.values():
        if len(group) < 2:
            continue
        for first, second in zip(group, group[1:]):
            candidates.append(DuplicateCandidate(first.filename, second.filename, "same slug across domains"))

    by_domain: dict[str, list[decisions.Decision]] = defaultdict(list)
    for d in all_decisions:
        by_domain[d.domain].append(d)

    seen_pairs = {(c.first, c.second) for c in candidates}
    for group in by_domain.values():
        tokenized = [(d, _tokenize(d.choice)) for d in group]
        for index, (left, left_tokens) in enumerate(tokenized):
            if len(left_tokens) < 5:
                continue
            for right, right_tokens in tokenized[index + 1 :]:
                if len(right_tokens) < 5:
                    continue
                overlap = left_tokens & right_tokens
                union = left_tokens | right_tokens
                if len(overlap) >= 5 and len(overlap) / len(union) >= 0.62:
                    pair = (left.filename, right.filename)
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        candidates.append(
                            DuplicateCandidate(left.filename, right.filename, "high choice-token overlap")
                        )
    return candidates


def _all_boards() -> dict[str, dict[str, list[kanban.Task]]]:
    return {project_id: kanban.list_all(project_id) for project_id in kanban.list_projects()}


def _render_index(
    all_decisions: list[decisions.Decision],
    all_patterns: list[patterns.Pattern],
    boards: dict[str, dict[str, list[kanban.Task]]],
    validation_errors: dict[str, list[str]],
    duplicate_candidates: list[DuplicateCandidate],
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
        f"- Validation issue files: {len(validation_errors)}",
        f"- Duplicate review candidates: {len(duplicate_candidates)}",
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

    lines.extend(
        [
            "",
            "## Review Queue",
            "- [conflicts.md](conflicts.md) lists validation issues and duplicate candidates.",
            "- Original decision and pattern files remain the source of truth.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_domain_summary(domain: str, items: list[decisions.Decision]) -> str:
    items = sorted(items, key=lambda d: (d.decided, d.slug), reverse=True)
    keyword_counts = Counter()
    for d in items:
        keyword_counts.update(_tokenize(f"{d.slug} {d.choice}"))

    lines = [
        f"# {domain}",
        "",
        f"Active decisions: {len(items)}",
        "",
        "## Common Signals",
    ]
    signals = [token for token, _count in keyword_counts.most_common(12)]
    lines.append(", ".join(signals) if signals else "(none)")
    lines.extend(["", "## Current Decisions"])

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


def _render_conflicts(
    validation_errors: dict[str, list[str]],
    duplicate_candidates: list[DuplicateCandidate],
) -> str:
    lines = [
        "# TEL Review Queue",
        "",
        "This file is advisory. It points to items that may need human review; it does not change source records.",
        "",
        "## Validation Issues",
    ]
    if validation_errors:
        for filename, issues in validation_errors.items():
            lines.append(f"### {filename}")
            for issue in issues:
                lines.append(f"- {issue}")
    else:
        lines.append("(none detected)")

    lines.extend(["", "## Duplicate Candidates"])
    if duplicate_candidates:
        for candidate in duplicate_candidates[:200]:
            lines.append(f"- {candidate.first} <> {candidate.second}: {candidate.reason}")
        if len(duplicate_candidates) > 200:
            lines.append(f"- ... {len(duplicate_candidates) - 200} more candidates omitted")
    else:
        lines.append("(none detected)")
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

    validation_errors = decisions.validate_all()
    duplicate_candidates = _find_duplicate_candidates(all_decisions)

    report = OrganizationReport(
        summary_dir=summaries_dir(),
        decision_count=len(all_decisions),
        pattern_count=len(all_patterns),
        project_count=len(boards),
        validation_error_count=len(validation_errors),
        duplicate_candidate_count=len(duplicate_candidates),
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

    _write(
        summaries_dir() / "index.md",
        _render_index(all_decisions, all_patterns, boards, validation_errors, duplicate_candidates),
        report,
    )
    _write(summaries_dir() / "conflicts.md", _render_conflicts(validation_errors, duplicate_candidates), report)

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


def organize(project_id: str | None = None) -> OrganizationReport:
    from tel import context

    report = write_summaries(project_id=project_id)
    context.regenerate(project_id=project_id, refresh_summaries=False)
    return report
