# Task-Experience Loop Skill

You are operating within the Task-Experience Loop (TEL) protocol. This protocol turns you from a chat-based agent into a task-based agent with persistent design memory.

## On Every Session Start

Read the loop context file first:
```
cat /Users/yanghh/obs/tel/loop-context.md
```

This gives you: active task, global constraints, relevant design decisions, and planned next steps.

## During Work

### When you identify a design decision (architecture choice, interface design, constraint discovery, option rejection):

Write it directly to `/Users/yanghh/obs/tel/decisions/{domain}--{slug}.md` with this format:

```markdown
---
domain: {domain}
decided: {YYYY-MM-DD}
status: active
---

# {choice title}

## Decision Point
{what is being decided}

## Option Space
- {option 1}
- {option 2}
- ...

## Choice
{what was chosen}

## Constraints & Rationale
- {why this choice, what constraints drove it}

## Implications
- {what follows from this choice}

## Evolution Trigger
- {when to revisit this decision}
```

### What to record (design assets only):
- Architecture choices (deployment, storage, communication patterns)
- Interface design (API contracts, data formats, naming conventions)
- Constraint discovery (performance limits, cost boundaries, team capacity)
- Option rejection (why NOT X — prevents re-evaluation)

### What NOT to record:
- Implementation details (how a function works)
- Bug fixes
- Temporary debugging info

## Task Management

Update the kanban when tasks change state:
- Add task: append `- {title}` under `## Backlog` in `/Users/yanghh/obs/tel/kanban.md`
- Activate: move from Backlog to `## Active`
- Complete: move to `## Done` with date suffix `| YYYY-MM-DD`

## Autonomous Execution Rules

- **Execute autonomously** when: the decision aligns with existing constraints or decisions
- **Execute autonomously** when: choosing the simpler option among valid alternatives
- **Pause for confirmation** when: constraints conflict with each other
- **Pause for confirmation** when: entering a domain with zero prior decisions
- **Pause for confirmation** when: a decision would supersede an existing one

## After Completing Work

Regenerate the context file by running:
```
cd /Users/yanghh/Documents/code/quant/task-experience-loop && uv run tel context
```

This keeps loop-context.md current for the next session.
