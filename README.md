*Give AI agents a way to remember why decisions were made and which approaches actually worked.*

# Task Experience Loop

English | [简体中文](README.zh-CN.md)

Task Experience Loop (TEL) is a lightweight memory layer for long-running agent work.

This repository contains:

- `tel/`: CLI utilities for decisions, patterns, kanban, and generated loop context.
- `skills/`: global Codex skill sources for action-oriented SOP skills.

Kanban tasks are scoped to the current project inside one canonical TEL
directory. By default this is `/Users/yanghh/obs/tel`. Set `TEL_DIR` to override
the local TEL directory.

Under each `Backlog` and `Active` column in `kanban.md`, the first
bullet level is the project id and the second bullet level contains tasks. TEL
derives the project from the nearest Git root directory name; set `TEL_PROJECT`
to override the scope for non-repository workspaces.

Project-specific decisions declare `projects: [project-id]` in frontmatter.
`tel search <project-id>`, generated project summaries, and project-scoped
context use that explicit ownership instead of inferring relationships from
task-title keyword overlap. Project summaries show Backlog, Active, and
explicitly assigned active decisions.

Kanban stores only unfinished commitments. `tel task done` removes the task
from the live board instead of keeping completion history. Session JSONL, Git,
deployment state, and project artifacts remain the authorities for past
activity.

The task state machine has only three transitions:

```text
absent --add--> Backlog
absent/Backlog --start--> Active
Backlog/Active --done--> absent
```

Each project has at most one Active task. `tel task` displays the current board,
`tel task done` defaults to that Active task, and an explicit title is only
needed when removing a Backlog item.

Global user-specific nouns live in `nouns.md` and are included in generated
context as pointer-resolution hints:

```bash
tel noun add aliyun "SSH host aliyun, Alibaba Cloud server"
tel noun
```

`tel compact` generates `summaries/compact.md` with candidate memory-pool
cleanup proposals. It does not edit source decision or pattern records; an agent
must inspect the referenced records and ask for user approval before applying any
merge, deprecation, supersession, edit, or deletion.

## Installation

Install skills into both Codex and Claude Code with one command:

```bash
./install.sh
```

This symlinks every skill under `skills/` (plus the shared `_shared/` norms and
the `tel` protocol skill) into `~/.codex/skills/` and `~/.claude/skills/`. Because
they are symlinks, editing a skill in this repo updates both tools immediately —
the repo is the single source of truth. Unrelated skills already present in either
target directory are left untouched.

The `tel` protocol skill (`skills/tel/SKILL.md`) is shared by both tools and
replaces the earlier Claude-only `.claude/commands/tel.md` command.

The current SOP skill set uses canonical hyphen-case names such as `sop-grill`,
`sop-explore`, `sop-propose`, and `sop-diagnose`. `sop-propose` owns both bounded
design shaping and distant-objective boundary/gap discovery. `sop-grill` handles
the narrower case where a concrete action is visible but unresolved user choices
would still change its shape.
