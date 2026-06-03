# Handoff SOP

## Context
- `task-experience-loop` now has `machine-handoffs/` for compressed Mac/Windows information packets.
- `sop-handoff` owns when and how to write these packets.
- SOP actions can now point to other SOP actions through shared action pointers, for example `explore -> propose -> handoff -> upload`.

## Boundary
- This is not an `obs` mirror, TEL source sync, task queue, or chat backup.
- The receiving machine should initialize or update its own local `obs`, TEL decisions, patterns, and kanban.
- Handoff packets should stay short and actionable; long-lived reusable boundaries should be promoted into local TEL decisions.

## Action
- After `git pull`, install or sync the updated SOP skills from this repo into the local Codex skills directory.
- Read `machine-handoffs/README.md` and this packet before relying on cross-machine handoff.
- Use `machine-handoffs/windows-to-mac/` for future compressed packets from Windows to Mac.

## References
- `skills/sop-handoff/SKILL.md`
- `skills/_shared/action.md`
- `machine-handoffs/README.md`
- TEL decision: `workflow--project-based-shared-cognition-machine-presets`
