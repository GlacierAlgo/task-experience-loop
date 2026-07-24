from __future__ import annotations

import click

from tel import compact, context, decisions, kanban, nouns


@click.group()
def cli():
    """Task-Experience Loop — design decision asset manager."""
    # Ensure loop-context.md matches the current project (cwd-based)
    context.ensure_current()


def _echo_board() -> None:
    click.echo(f"Project: {kanban.current_project()}")
    click.echo(f"Kanban: {kanban.kanban_path()}")
    board = kanban.list_all()
    for col, tasks in board.items():
        click.echo(f"\n## {col}")
        if not tasks:
            click.echo("  (empty)")
        for item in tasks:
            click.echo(f"  - {item.title}" + (f" | {item.meta}" if item.meta else ""))


@cli.group(invoke_without_command=True)
@click.pass_context
def task(ctx: click.Context):
    """Show the current board or change task state."""
    if ctx.invoked_subcommand is None:
        _echo_board()


@task.command("add")
@click.argument("title")
def task_add(title: str):
    """Add a task to backlog."""
    item = kanban.add(title)
    click.echo(f"{item.column} in {kanban.current_project()}: {item.title}")
    context.regenerate()


@task.command("start")
@click.argument("title")
def task_start(title: str):
    """Start a backlog task or create it directly as Active."""
    try:
        item = kanban.start(title)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Active in {kanban.current_project()}: {item.title}")
    context.regenerate()


@task.command("done")
@click.argument("title", required=False)
def task_done(title: str | None):
    """Remove a task; defaults to the current Active task."""
    try:
        item = kanban.complete(title)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Completed and removed from {kanban.current_project()}: {item.title}")
    context.regenerate()


@cli.command("context")
@click.option("--stdout", "to_stdout", is_flag=True, help="Print context to stdout without writing loop-context.md")
def context_cmd(to_stdout: bool):
    """Regenerate loop-context.md (or print to stdout with --stdout)."""
    if to_stdout:
        click.echo(context.assemble())
    else:
        context.regenerate()
        click.echo(f"Regenerated loop-context.md for {kanban.current_project()}")


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
    """Search decisions by keyword, slug, or explicit project id."""
    keyword_lower = keyword.lower()
    all_d = decisions.query(status="active")
    matches = []
    for d in all_d:
        searchable = " ".join(
            [
                d.domain,
                d.slug,
                d.filename,
                " ".join(d.projects),
                d.choice,
                d.decision_point,
                " ".join(d.constraints),
                " ".join(d.implications),
            ]
        ).lower()
        if keyword_lower in searchable:
            matches.append(d)
    if not matches:
        click.echo(f"No decisions matching '{keyword}'.")
        return
    for d in matches:
        click.echo(f"  [{d.domain}] {d.filename}")
        click.echo(f"    {d.choice}")
        click.echo()


def _echo_nouns() -> None:
    entries = nouns.query()
    if not entries:
        click.echo("No global nouns yet.")
        return
    for entry in entries:
        click.echo(f"  {entry.term} -> {entry.meaning}")


@cli.group(invoke_without_command=True)
@click.pass_context
def noun(ctx: click.Context):
    """Show or add user-specific global nouns."""
    if ctx.invoked_subcommand is None:
        _echo_nouns()


@noun.command("add")
@click.argument("term")
@click.argument("meaning", nargs=-1, required=True)
def noun_add(term: str, meaning: tuple[str, ...]):
    """Record a global noun resolution."""
    entry = nouns.record(term=term, meaning=" ".join(meaning))
    click.echo(f"Recorded noun: {entry.term} -> {entry.meaning}")
    context.regenerate()


def main():
    cli()
