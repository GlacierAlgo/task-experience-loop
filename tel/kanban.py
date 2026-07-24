from __future__ import annotations

import fcntl
import re
from dataclasses import dataclass
from pathlib import Path

from tel import project

COLUMNS = ("Backlog", "Active")
LEGACY_PROJECT = "legacy"


@dataclass
class Task:
    title: str
    meta: str = ""
    column: str = "Backlog"

    @property
    def line(self) -> str:
        if self.meta:
            return f"- {self.title} | {self.meta}"
        return f"- {self.title}"


def _empty_board() -> dict[str, list[Task]]:
    return {col: [] for col in COLUMNS}


def _project_key(project_id: str | None = None) -> str:
    return project.slugify(project_id) if project_id else project.current_project_id()


def _parse_task(content: str, column: str) -> Task:
    parts = content.split(" | ", 1)
    title = parts[0]
    meta = parts[1] if len(parts) > 1 else ""
    return Task(title=title, meta=meta, column=column)


def _parse_flat(text: str) -> dict[str, list[Task]]:
    board: dict[str, list[Task]] = {col: [] for col in COLUMNS}
    current_col = None
    for line in text.splitlines():
        header = re.match(r"^## (.+)$", line)
        if header:
            name = header.group(1).strip()
            if name in board:
                current_col = name
            continue
        if current_col and line.startswith("- "):
            board[current_col].append(_parse_task(line[2:].strip(), current_col))
    return board


def _has_nested_tasks(text: str) -> bool:
    current_col = None
    for line in text.splitlines():
        header = re.match(r"^## (.+)$", line)
        if header:
            name = header.group(1).strip()
            current_col = name if name in COLUMNS else None
            continue
        if current_col and re.match(r"^\s+- ", line):
            return True
    return False


def _parse(text: str) -> dict[str, dict[str, list[Task]]]:
    if not text.strip():
        return {}
    if not _has_nested_tasks(text):
        legacy = _parse_flat(text)
        return {LEGACY_PROJECT: legacy} if _has_any_task(legacy) else {}

    boards: dict[str, dict[str, list[Task]]] = {}
    current_col = None
    current_project = None

    for line in text.splitlines():
        header = re.match(r"^## (.+)$", line)
        if header:
            name = header.group(1).strip()
            current_col = name if name in COLUMNS else None
            current_project = None
            continue

        if not current_col:
            continue

        if line.startswith("- "):
            current_project = project.slugify(line[2:].strip())
            boards.setdefault(current_project, _empty_board())
            continue

        task = re.match(r"^\s+- (.+)$", line)
        if task and current_project:
            boards[current_project][current_col].append(_parse_task(task.group(1).strip(), current_col))

    return {name: board for name, board in boards.items() if _has_any_task(board)}


def _has_any_task(board: dict[str, list[Task]]) -> bool:
    return any(board.get(col) for col in COLUMNS)


def _render(boards: dict[str, dict[str, list[Task]]]) -> str:
    sections = []
    for col in COLUMNS:
        lines = [f"## {col}"]
        for project_id, board in boards.items():
            tasks = board.get(col, [])
            if not tasks:
                continue
            lines.append(f"- {project_id}")
            for task in tasks:
                lines.append(f"  {task.line}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def current_project() -> str:
    return project.current_project_id()


def kanban_path(project_id: str | None = None) -> Path:
    return project.tel_dir() / "kanban.md"


def legacy_kanban_path() -> Path:
    return kanban_path()


def _read_all_boards() -> dict[str, dict[str, list[Task]]]:
    path = kanban_path()
    if not path.exists():
        return {}
    return _parse(path.read_text())


def _write_all_boards(boards: dict[str, dict[str, list[Task]]]) -> None:
    """Write boards to disk. Used for bulk/admin operations only."""
    path = kanban_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            f.truncate()
            f.write(_render({n: b for n, b in boards.items() if _has_any_task(b)}))
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _atomic_update(project_id: str | None, fn) -> dict[str, list[Task]]:
    """Read-modify-write a project's board atomically under file lock.

    `fn` receives the current board and must return the updated board.
    """
    path = kanban_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    key = _project_key(project_id)

    with open(path, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            all_boards = _parse(f.read())
            board = all_boards.get(key, _empty_board())
            board = fn(board)
            if _has_any_task(board):
                all_boards[key] = board
            else:
                all_boards.pop(key, None)
            f.seek(0)
            f.truncate()
            f.write(_render({n: b for n, b in all_boards.items() if _has_any_task(b)}))
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return board


def _read_board(project_id: str | None = None) -> dict[str, list[Task]]:
    boards = _read_all_boards()
    return boards.get(_project_key(project_id), _empty_board())


def get_active(project_id: str | None = None) -> Task | None:
    board = _read_board(project_id)
    tasks = board.get("Active", [])
    return tasks[0] if tasks else None


def add(title: str, project_id: str | None = None) -> Task:
    added: Task | None = None

    def _add(board):
        nonlocal added
        for col in COLUMNS:
            for task in board[col]:
                if task.title == title:
                    added = task
                    return board
        added = Task(title=title)
        board["Backlog"].append(added)
        return board

    _atomic_update(project_id, _add)
    assert added is not None
    return added


def start(title: str, project_id: str | None = None) -> Task:
    started: Task | None = None

    def _start(board):
        nonlocal started
        for task in board["Active"]:
            if task.title == title:
                started = task
                return board
        if board["Active"]:
            raise ValueError(f"Active task already exists: {board['Active'][0].title}")

        for task in board["Backlog"]:
            if task.title == title:
                board["Backlog"].remove(task)
                started = task
                break
        if started is None:
            started = Task(title=title)
        started.column = "Active"
        board["Active"].append(started)
        return board

    _atomic_update(project_id, _start)
    assert started is not None
    return started


def complete(title: str | None = None, project_id: str | None = None) -> Task:
    completed: Task | None = None

    def _complete(board):
        nonlocal completed
        if title is None:
            if not board["Active"]:
                raise ValueError("No active task")
            completed = board["Active"].pop(0)
            return board

        for col in COLUMNS:
            for task in board[col]:
                if task.title == title:
                    board[col].remove(task)
                    completed = task
                    return board
        raise ValueError(f"Task not found: {title}")

    _atomic_update(project_id, _complete)
    assert completed is not None
    return completed


def list_all(project_id: str | None = None) -> dict[str, list[Task]]:
    return _read_board(project_id)


def list_projects() -> list[str]:
    return list(_read_all_boards().keys())
