---
name: tel
description: Task-Experience Loop — read loop-context.md on session start, record design decisions and reusable patterns during work, resolve global nouns, compact the experience pool with user approval, and update kanban on task completion. Use when the user invokes $tel, asks to record a decision, check experience pool, compact TEL, manage global nouns, or manage the task board.
---

# Task-Experience Loop (TEL)

## On Session Start

Read the loop context for the **current working directory's project**:
```bash
tel context --stdout
```

This gives you: active task, global constraints, global nouns, design decisions, reusable patterns, and planned next steps — all scoped to the cwd project automatically.

If you read `/Users/yanghh/obs/tel/loop-context.md` directly and its `Project:` line differs from your cwd project, **ignore the stale file** — use `tel context --stdout` instead.

Global nouns are user-specific term resolutions and take precedence over generic meanings unless the current user message explicitly overrides them.

## When to Write a Decision

> "If a different agent starts a similar task 3 months from now, would this decision prevent it from making a wrong choice?"

**Record** when:
- A choice was made between 2+ viable alternatives
- A constraint was discovered that wasn't obvious
- An option was explicitly rejected with reasons
- An interface contract was established

**Do NOT record**:
- What was done (that's kanban)
- How code works (that's in the code)
- Research without a decision (that's notes)
- One-off task specifics

Before writing, check `decisions/` for existing coverage. Never duplicate.

Write to `/Users/yanghh/obs/tel/decisions/{domain}--{slug}.md`:

```markdown
---
domain: {domain}
decided: {YYYY-MM-DD}
status: active
---

# {choice title}

## Decision Point
{the question answered — framed as reusable}

## Option Space
- {option 1}
- {option 2}
- {option 3}

## Choice
{selected option}

## Constraints & Rationale
- {why — these are the reusable insights}

## Implications
- {concrete downstream effects}

## Evolution Trigger
- {measurable conditions that invalidate this}
```

Domain: `architecture`, `interface`, `data`, `deployment`, `frontend`, `workflow`, `research`

## When to Write a Pattern

Lighter than decisions. Record when "doing X in situation Y works well."

Write to `/Users/yanghh/obs/tel/patterns/{slug}.md`:

```markdown
---
domain: {domain}
created: {YYYY-MM-DD}
uses: 0
---

# {slug}

## Situation
{when does this apply}

## Action
{what to do}

## Outcome
{why it works}
```

When reusing a pattern, bump its `uses:` count.

**Decision vs Pattern**:
- Decision = "we chose X over Y because Z" (constrains future choices)
- Pattern = "when facing S, doing A works well" (reusable practice)

## Task Management

Update `/Users/yanghh/obs/tel/kanban.md`:

```
## Backlog
- {task name}

## Active
- {task name} | {optional context}

## Done
- {task name} | {YYYY-MM-DD}
```

Keep titles concise — a task name, not a description.

If work implies obvious follow-up tasks, add them to Backlog (not mandatory).

## Global Nouns

Global nouns are user-specific referents such as machine names, server aliases, or recurring acronyms. They are not constraints; they are pointer-resolution hints.

Manage them through:
```bash
tel noun add aliyun "SSH host aliyun, Alibaba Cloud server"
tel noun list
```

When resolving a term, use this precedence:
1. Current user message explicit definition
2. Project-local context
3. Global nouns
4. Repository names and code
5. Generic meaning

## Compact

When the user asks for `tel compact` or TEL memory compaction:

1. Run:
   ```bash
   tel compact
   ```
2. Read `summaries/compact.md` and inspect the referenced source records.
3. Autonomously analyze whether candidates should be merged, edited, deprecated, superseded, deleted, or kept.
4. Present a small change set to the user and ask for approval before modifying any source record.
5. Only after approval, edit decision/pattern source files, regenerate summaries/context, and report the exact changes.

Do not treat compact as text compression. It is experience-pool governance. The CLI may generate candidates, but an agent must verify current repo reality and get user approval before changing source records.

## After Completing Work

```bash
tel context
```

## Autonomy Rules

- Execute autonomously when choice aligns with existing constraints/decisions
- Execute autonomously when choosing the simpler option
- Pause when constraints conflict, domain is new, or superseding existing decision

## Cross-Project Scope

Decisions, patterns, constraints, and nouns are **global shared knowledge** — not owned by any single project. An agent working in `shadow-backtest` can and should write a decision with domain `data` even if that decision was prompted by work in `shadow-derivatives`.

**Project-scoped**: kanban tasks only. Use `tel task add/activate/done` which automatically targets the cwd project.

**Global-scoped** (write from any project):
- Decisions (`/Users/yanghh/obs/tel/decisions/`)
- Patterns (`/Users/yanghh/obs/tel/patterns/`)
- Constraints (`/Users/yanghh/obs/tel/constraints.md`)
- Nouns (`tel noun add`)

Never refuse to write a decision or pattern because `loop-context.md` points to a different project. The file is a cache; your cwd determines your project identity.
