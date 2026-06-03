# Machine Handoffs

This folder carries compressed information packets between local machines.

It is not an `obs` mirror, not TEL source storage, and not a task database. Use it only when one machine needs the other machine to notice a small set of facts after `git pull`.

`sop-handoff` owns when and how to write these packets. If a packet should be visible immediately, finish by running `sop-upload` for this repo.

## Layout

- `mac-to-windows/`: packets written from Mac for Windows.
- `windows-to-mac/`: packets written from Windows for Mac.

Use one short Markdown file per handoff:

```text
YYYY-MM-DD-short-topic.md
```

## Packet Shape

```markdown
# Short Topic

## Context
- What changed or what the other machine needs to know.

## Boundary
- What this does and does not imply.

## Action
- What the receiving machine should do, if anything.

## References
- Repo paths, commit hashes, issue links, or TEL decision names.
```

## Rules

- Keep packets compressed and actionable.
- Do not write secrets, tokens, private credentials, local runtime state, or full chat logs.
- Do not copy `obs`, `loop-context.md`, caches, or generated artifacts here.
- The receiving machine initializes or updates its own `obs`, TEL decisions, and kanban locally.
- Promote a packet into a TEL decision or pattern only after it becomes a reusable boundary.
