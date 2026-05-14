from __future__ import annotations

import click

from tel import context, decisions, kanban


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
    click.echo(f"Added: {title}")


@task.command("activate")
@click.argument("title")
def task_activate(title: str):
    """Move a task to Active."""
    kanban.activate(title)
    click.echo(f"Activated: {title}")
    context.regenerate()


@task.command("done")
@click.argument("title")
def task_done(title: str):
    """Mark a task as done."""
    kanban.complete(title)
    click.echo(f"Completed: {title}")
    context.regenerate()


@task.command("list")
def task_list():
    """Show all tasks."""
    board = kanban.list_all()
    for col, tasks in board.items():
        click.echo(f"\n## {col}")
        if not tasks:
            click.echo("  (empty)")
        for t in tasks:
            click.echo(f"  - {t.title}" + (f" | {t.meta}" if t.meta else ""))


@cli.command("decide")
@click.option("--domain", prompt="Domain (e.g. deployment, interface, data)")
@click.option("--slug", prompt="Slug (short kebab-case id)")
@click.option("--point", prompt="Decision point (what are you deciding?)")
@click.option("--options", prompt="Options (comma-separated)")
@click.option("--choice", prompt="Your choice")
@click.option("--constraints", prompt="Constraints & rationale (comma-separated)")
@click.option("--implications", prompt="Implications (comma-separated)")
@click.option("--triggers", prompt="Evolution triggers (comma-separated, or empty)", default="")
def decide(domain, slug, point, options, choice, constraints, implications, triggers):
    """Record a design decision."""
    d = decisions.record(
        domain=domain,
        slug=slug,
        decision_point=point,
        option_space=[o.strip() for o in options.split(",")],
        choice=choice,
        constraints=[c.strip() for c in constraints.split(",")],
        implications=[i.strip() for i in implications.split(",")],
        evolution_trigger=[t.strip() for t in triggers.split(",") if t.strip()],
    )
    click.echo(f"Recorded: {d.filename}")
    context.regenerate()


@cli.command("context")
def context_cmd():
    """Regenerate loop-context.md."""
    context.regenerate()
    click.echo("Regenerated loop-context.md")


@cli.command("status")
def status():
    """Show current loop status."""
    active = kanban.get_active()
    if active:
        click.echo(f"Active: {active.title}")
    else:
        click.echo("No active task")

    all_decisions = decisions.query(status="active")
    click.echo(f"Decisions: {len(all_decisions)} active")

    board = kanban.list_all()
    click.echo(f"Backlog: {len(board['Backlog'])} | Done: {len(board['Done'])}")


@cli.command("next")
def next_cmd():
    """Suggest next steps based on experience pool."""
    board = kanban.list_all()
    backlog = board.get("Backlog", [])
    if not backlog:
        click.echo("Backlog is empty. Add tasks with `tel task add`.")
        return

    click.echo("Suggested next steps:")
    for i, t in enumerate(backlog[:5], 1):
        related = decisions.related_to(t.title)
        suffix = f" (related decisions: {len(related)})" if related else ""
        click.echo(f"  {i}. {t.title}{suffix}")


@cli.command("validate")
def validate_cmd():
    """Validate all decision files for format compliance."""
    errors = decisions.validate_all()
    if not errors:
        total = len(decisions.query(status="active"))
        click.echo(f"All {total} decisions pass validation.")
        return

    for filename, issues in errors.items():
        click.echo(f"\n{filename}:")
        for issue in issues:
            click.echo(f"  - {issue}")
    click.echo(f"\n{len(errors)} file(s) with issues.")


def main():
    cli()
