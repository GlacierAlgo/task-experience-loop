# Task-Experience Loop Skill

You are operating within the Task-Experience Loop (TEL) protocol. This protocol turns you from a chat-based agent into a task-based agent with persistent design memory.

## On Every Session Start

Read the loop context file first:
```
cat /Users/yanghh/obs/tel/loop-context.md
```

This gives you: active task, global constraints, relevant design decisions, and planned next steps.

## When to Write a Decision

A decision is worth recording ONLY if it passes this test:

> "If a different agent starts a similar task 3 months from now, would this decision prevent it from making a wrong choice or re-evaluating an already-settled question?"

**Record** (design assets that constrain future work):
- A choice was made between 2+ viable alternatives (architecture, tool, format, pattern)
- A constraint was discovered that wasn't obvious (performance ceiling, cost limit, API quirk)
- An option was explicitly rejected with reasons (prevents future re-evaluation)
- An interface contract was established (API shape, data format, naming convention)

**Do NOT record**:
- What was done in this session (that's kanban, not decisions)
- How code was implemented (that's in the code itself)
- Research findings without a decision (that's notes)
- Anything that only applies to this one task and won't recur

**Litmus test**: If removing this decision file would cause a future agent to make a worse choice, keep it. If not, don't write it.

## Decision File Format

Write to `/Users/yanghh/obs/tel/decisions/{domain}--{slug}.md`:

```markdown
---
domain: {domain}
decided: {YYYY-MM-DD}
status: active
---

# {choice title — what was chosen, not what was decided}

## Decision Point
{the question that was answered — framed as a reusable design question}

## Option Space
- {option 1}
- {option 2}
- {option 3}

## Choice
{the selected option}

## Constraints & Rationale
- {each constraint that drove this choice — these are the reusable insights}

## Implications
- {what follows from this choice — concrete downstream effects}

## Evolution Trigger
- {specific measurable conditions that would invalidate this decision}
```

Domain must be one of: `architecture`, `interface`, `data`, `deployment`, `frontend`, `workflow`, `research`

## Task Management

Update `/Users/yanghh/obs/tel/kanban.md`:

```
## Backlog
- {short task title}

## Active
- {short task title} | {optional brief context}

## Done
- {short task title} | {YYYY-MM-DD}
```

Keep titles concise — a task name, not a sentence describing what was done.

## Patterns (reusable practices)

Lighter than decisions. When you discover "doing X in situation Y works well", write to `/Users/yanghh/obs/tel/patterns/{slug}.md`:

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

**Decision vs Pattern**:
- Decision = "we chose X over Y because Z" (constrains future choices)
- Pattern = "when facing S, doing A works well" (reusable practice)

When reusing a pattern, bump its `uses:` count.

## Autonomous Execution Rules

- **Execute autonomously** when: the decision aligns with existing constraints or decisions
- **Execute autonomously** when: choosing the simpler option among valid alternatives
- **Pause for confirmation** when: constraints conflict with each other
- **Pause for confirmation** when: entering a domain with zero prior decisions
- **Pause for confirmation** when: a decision would supersede an existing one

## After Completing Work

- Update `kanban.md`
- If the work implies obvious follow-up tasks, add them to Backlog (not mandatory)
- Regenerate:
```
tel context
```
