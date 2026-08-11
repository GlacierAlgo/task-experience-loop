*Give AI agents a way to remember why decisions were made and which approaches actually worked.*

# Task Experience Loop

English | [简体中文](README.zh-CN.md)

Task Experience Loop (TEL) is a local, auditable memory layer for long-running work with Codex. It keeps unfinished commitments, durable decisions, and proven working patterns in Markdown so a new task can pick up the reasoning behind earlier work.

TEL is not a chat archive or an agent orchestrator. It keeps only what should still matter later:

- the work a project has not finished;
- decisions that should constrain future work;
- approaches worth reusing;
- user-specific names that an agent should resolve consistently.

## Install

TEL has two separate parts: the Python CLI manages local data, while the Codex Plugin provides the TEL protocol and action-oriented SOP skills.

### 1. Install the CLI

TEL requires Python 3.12 or later. With `uv`:

```bash
uv tool install git+https://github.com/GlacierAlgo/task-experience-loop.git
```

Or install from a checkout:

```bash
git clone https://github.com/GlacierAlgo/task-experience-loop.git
cd task-experience-loop
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

TEL stores data in `~/.tel` by default. Set `TEL_DIR` only when you want a different location:

```bash
export TEL_DIR="$HOME/path/to/tel-data"
```

### 2. Install the Codex Plugin

Add this repository as a Codex marketplace, then install the plugin:

```bash
codex plugin marketplace add GlacierAlgo/task-experience-loop
codex plugin add task-experience-loop@task-experience-loop
```

Start a new Codex task after installation so the bundled skills are discovered.

The plugin does not edit global `AGENTS.md`, create links into a development checkout, or enable session-start behavior automatically. Invoke `$tel` when you need it. If you deliberately want TEL active in every project, copy the small [always-on profile](plugins/task-experience-loop/profiles/always-on/AGENTS.md) into your personal global instructions.

## Try it

Run these commands inside any Git repository:

```bash
tel task start "make search results explainable"
tel context --stdout
tel task
```

When the work is complete:

```bash
tel task done
```

TEL derives the project id from the nearest Git root. Set `TEL_PROJECT` only for workspaces where that is not possible.

## CLI

```bash
tel task add "next task"              # add to this project's Backlog
tel task start "current task"         # one Active task per project
tel task done                          # remove the completed commitment
tel noun add dgx "DGX execution host" # record a user-specific term
tel search architecture                # search durable decisions
tel compact                            # propose memory-pool cleanup
tel context --stdout                   # print context for this project
```

`tel compact` never edits decision or pattern records. It writes review proposals; an agent must inspect them and obtain user approval before changing source records.

## Data layout

```text
~/.tel/
├── kanban.md              # unfinished commitments for all projects
├── constraints.md         # cross-project constraints
├── nouns.md               # user-specific terms
├── decisions/             # durable decisions
├── patterns/              # reusable working patterns
├── summaries/             # generated indexes and review proposals
├── archive/               # superseded decisions
└── loop-context.md        # generated context for the current project
```

Project-specific decisions declare `projects: [project-id]` in frontmatter. TEL does not infer ownership from project names that happen to appear in prose or old task titles.

The task state machine is intentionally small:

```text
absent --add--> Backlog
absent/Backlog --start--> Active
Backlog/Active --done--> absent
```

Completed work belongs in Git, project artifacts, or session history instead of accumulating forever on the live board.

## Repository layout

- `tel/`: the Python CLI and local Markdown data model.
- `plugins/task-experience-loop/`: the installable Codex Plugin.
- `plugins/task-experience-loop/skills/`: TEL and action-oriented SOP skills.
- `.agents/plugins/marketplace.json`: the repository marketplace entry.
- `tests/`: focused CLI and data-contract tests.

The plugin and CLI are intentionally separate. Installing the plugin does not grant it a database, remote service, or access to private data; the CLI reads and writes only the local directory selected by `TEL_DIR`.
