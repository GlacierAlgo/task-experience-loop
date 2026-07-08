from __future__ import annotations

import click

from tel import compact, context, decisions, kanban, nouns, organize


@click.group()
def cli():
    """Task-Experience Loop — design decision asset manager."""


@cli.group()
def task():
    """Manage kanban tasks."""


@task.command("add")
@click.argument("title")
def task_add(title: str):
    """Add a task to backlog."""
    kanban.add(title)
    click.echo(f"Added to {kanban.current_project()}: {title}")
    context.regenerate()


@task.command("activate")
@click.argument("title")
def task_activate(title: str):
    """Move a task to Active."""
    kanban.activate(title)
    click.echo(f"Activated in {kanban.current_project()}: {title}")
    context.regenerate()


@task.command("done")
@click.argument("title")
def task_done(title: str):
    """Mark a task as done."""
    kanban.complete(title)
    click.echo(f"Completed in {kanban.current_project()}: {title}")
    context.regenerate()


@task.command("list")
def task_list():
    """Show all tasks."""
    click.echo(f"Project: {kanban.current_project()}")
    click.echo(f"Kanban: {kanban.kanban_path()}")
    board = kanban.list_all()
    for col, tasks in board.items():
        click.echo(f"\n## {col}")
        if not tasks:
            click.echo("  (empty)")
        for t in tasks:
            click.echo(f"  - {t.title}" + (f" | {t.meta}" if t.meta else ""))


@cli.command("context")
def context_cmd():
    """Regenerate loop-context.md."""
    context.regenerate()
    click.echo(f"Regenerated loop-context.md for {kanban.current_project()}")


@cli.command("organize")
@click.option("--project", default=None, help="Project id to include when it has no kanban entries")
@click.option("--quiet", is_flag=True, help="Suppress summary output")
def organize_cmd(project: str | None, quiet: bool):
    """Organize TEL experience into summaries and refresh loop-context.md."""
    report = organize.organize(project_id=project)
    if quiet:
        return
    click.echo(f"Organized TEL experience under {report.summary_dir}")
    click.echo(
        "Indexed "
        f"{report.decision_count} decisions, "
        f"{report.pattern_count} patterns, "
        f"{report.project_count} projects"
    )
    if report.validation_error_count or report.duplicate_candidate_count:
        click.echo(
            "Review queue: "
            f"{report.validation_error_count} validation issue files, "
            f"{report.duplicate_candidate_count} duplicate candidates"
        )


@cli.command("compact")
def compact_cmd():
    """Generate compact proposals for user-approved memory cleanup."""
    report = compact.write_review()
    click.echo(f"Wrote compact review: {report.review_path}")
    click.echo(
        "Found "
        f"{report.proposal_count} review item(s) across "
        f"{report.decision_count} active decisions and "
        f"{report.pattern_count} patterns."
    )
    click.echo("Source records were not changed. Ask an agent to review and request approval before edits.")


@cli.command("search")
@click.argument("keyword")
def search_cmd(keyword: str):
    """Search decisions by keyword (matches domain, choice, decision point, constraints)."""
    keyword_lower = keyword.lower()
    all_d = decisions.query(status="active")
    matches = []
    for d in all_d:
        searchable = f"{d.domain} {d.choice} {d.decision_point} {' '.join(d.constraints)}".lower()
        if keyword_lower in searchable:
            matches.append(d)
    if not matches:
        click.echo(f"No decisions matching '{keyword}'.")
        return
    for d in matches:
        click.echo(f"  [{d.domain}] {d.filename}")
        click.echo(f"    {d.choice}")
        click.echo()


@cli.group()
def noun():
    """Manage user-specific global nouns."""


@noun.command("add")
@click.argument("term")
@click.argument("meaning", nargs=-1, required=True)
def noun_add(term: str, meaning: tuple[str, ...]):
    """Record a global noun resolution."""
    entry = nouns.record(term=term, meaning=" ".join(meaning))
    click.echo(f"Recorded noun: {entry.term} -> {entry.meaning}")
    context.regenerate()


@noun.command("list")
def noun_list():
    """List global noun resolutions."""
    entries = nouns.query()
    if not entries:
        click.echo("No global nouns yet.")
        return
    for entry in entries:
        click.echo(f"  {entry.term} -> {entry.meaning}")


def main():
    cli()
