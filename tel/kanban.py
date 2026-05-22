from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tel import project

COLUMNS = ("Backlog", "Active", "Done")
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
    return any(re.match(r"^\s+- ", line) for line in text.splitlines())


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
    path = kanban_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render({name: board for name, board in boards.items() if _has_any_task(board)}))


def _read_board(project_id: str | None = None) -> dict[str, list[Task]]:
    boards = _read_all_boards()
    return boards.get(_project_key(project_id), _empty_board())


def _write_board(board: dict[str, list[Task]], project_id: str | None = None):
    boards = _read_all_boards()
    key = _project_key(project_id)
    if _has_any_task(board):
        boards[key] = board
    else:
        boards.pop(key, None)
    _write_all_boards(boards)


def get_active(project_id: str | None = None) -> Task | None:
    board = _read_board(project_id)
    tasks = board.get("Active", [])
    return tasks[0] if tasks else None


def add(title: str, column: str = "Backlog", project_id: str | None = None):
    board = _read_board(project_id)
    board[column].append(Task(title=title, column=column))
    _write_board(board, project_id)


def activate(title: str, project_id: str | None = None):
    board = _read_board(project_id)
    found = None
    for col in COLUMNS:
        for task in board[col]:
            if task.title == title:
                found = task
                board[col].remove(task)
                break
        if found:
            break
    if not found:
        raise ValueError(f"Task not found: {title}")
    found.column = "Active"
    board["Active"].append(found)
    _write_board(board, project_id)


def complete(title: str, project_id: str | None = None):
    from datetime import date

    board = _read_board(project_id)
    found = None
    for col in COLUMNS:
        for task in board[col]:
            if task.title == title:
                found = task
                board[col].remove(task)
                break
        if found:
            break
    if not found:
        raise ValueError(f"Task not found: {title}")
    found.column = "Done"
    found.meta = date.today().isoformat()
    board["Done"].append(found)
    _write_board(board, project_id)


def list_all(project_id: str | None = None) -> dict[str, list[Task]]:
    return _read_board(project_id)


def list_projects() -> list[str]:
    return list(_read_all_boards().keys())
