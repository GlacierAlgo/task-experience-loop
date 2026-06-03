# Task Experience Loop

Task Experience Loop (TEL) is a lightweight memory layer for long-running agent work.

This repository contains:

- `tel/`: CLI utilities for decisions, patterns, kanban, and generated loop context.
- `skills/`: global Codex skill sources for action-oriented SOP skills.
- `machine-handoffs/`: compressed Mac/Windows information packets for facts the other machine should see after `git pull`.

Kanban tasks are scoped to the current project inside one canonical
`/Users/yanghh/obs/tel/kanban.md` file. Under each `Backlog`, `Active`, and
`Done` column, the first bullet level is the project id and the second bullet
level contains tasks. TEL derives the project from the nearest Git root
directory name; set `TEL_PROJECT` to override the scope for non-repository
workspaces.

The install target for global Codex usage is:

```bash
~/.codex/skills
```

The current SOP skill set uses canonical hyphen-case names such as `sop-explore`,
`sop-propose`, `sop-diagnose`, and `sop-bootstrap`.
