# Task Experience Loop

Task Experience Loop (TEL) is a lightweight memory layer for long-running agent work.

This repository contains:

- `tel/`: CLI utilities for decisions, patterns, kanban, and generated loop context.
- `skills/`: global Codex skill sources for action-oriented SOP skills.

Kanban tasks are scoped to the current project inside one canonical TEL
directory. By default this is `/Users/yanghh/obs/tel`. Set `TEL_DIR` to override
the local TEL directory.

Under each `Backlog`, `Active`, and `Done` column in `kanban.md`, the first
bullet level is the project id and the second bullet level contains tasks. TEL
derives the project from the nearest Git root directory name; set `TEL_PROJECT`
to override the scope for non-repository workspaces.

Global user-specific nouns live in `nouns.md` and are included in generated
context as pointer-resolution hints:

```bash
tel noun add aliyun "SSH host aliyun, Alibaba Cloud server"
tel noun list
```

`tel compact` generates `summaries/compact.md` with candidate memory-pool
cleanup proposals. It does not edit source decision or pattern records; an agent
must inspect the referenced records and ask for user approval before applying any
merge, deprecation, supersession, edit, or deletion.

The install target for global Codex usage is:

```bash
~/.codex/skills
```

The current SOP skill set uses canonical hyphen-case names such as `sop-explore`,
`sop-propose`, `sop-diagnose`, and `sop-bootstrap`.
