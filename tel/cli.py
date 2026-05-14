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
@click.option("--force", is_flag=True, help="Skip duplicate check")
def decide(domain, slug, point, options, choice, constraints, implications, triggers, force):
    """Record a design decision."""
    if not force:
        existing = decisions.query(domain=domain)
        for e in existing:
            if e.slug == slug:
                click.echo(f"Decision already exists: {e.filename}. Use --force to overwrite.")
                return
            overlap = set(choice.lower().split()) & set(e.choice.lower().split())
            if len(overlap) >= 3:
                click.echo(f"Similar decision exists: {e.filename} ({e.choice})")
                click.echo("Use --force to create anyway, or update the existing one.")
                return
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


@cli.command("domains")
def domains_cmd():
    """Show decision count per domain."""
    from collections import Counter

    all_d = decisions.query(status="active")
    counts = Counter(d.domain for d in all_d)
    for domain, count in counts.most_common():
        click.echo(f"  {domain:15s} {count}")
    click.echo(f"  {'─' * 20}")
    click.echo(f"  {'total':15s} {len(all_d)}")


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


@cli.command("show")
@click.argument("slug")
def show_cmd(slug: str):
    """Show full details of a decision by slug."""
    d = decisions.get(slug)
    if not d:
        click.echo(f"Decision not found: {slug}")
        return
    click.echo(f"# {d.choice}")
    click.echo(f"Domain: {d.domain} | Decided: {d.decided} | Status: {d.status}")
    click.echo(f"\nDecision Point: {d.decision_point}")
    click.echo("\nOption Space:")
    for opt in d.option_space:
        click.echo(f"  - {opt}")
    click.echo(f"\nChoice: {d.choice}")
    click.echo("\nConstraints & Rationale:")
    for c in d.constraints:
        click.echo(f"  - {c}")
    click.echo("\nImplications:")
    for imp in d.implications:
        click.echo(f"  - {imp}")
    if d.evolution_trigger:
        click.echo("\nEvolution Trigger:")
        for t in d.evolution_trigger:
            click.echo(f"  - {t}")


def main():
    cli()
