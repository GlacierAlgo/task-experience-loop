from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

KANBAN_PATH = Path("/Users/yanghh/obs/tel/kanban.md")

COLUMNS = ("Backlog", "Active", "Done")


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


def _parse(text: str) -> dict[str, list[Task]]:
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
            content = line[2:].strip()
            parts = content.split(" | ", 1)
            title = parts[0]
            meta = parts[1] if len(parts) > 1 else ""
            board[current_col].append(Task(title=title, meta=meta, column=current_col))
    return board


def _render(board: dict[str, list[Task]]) -> str:
    sections = []
    for col in COLUMNS:
        lines = [f"## {col}"]
        for task in board.get(col, []):
            lines.append(task.line)
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def _read_board() -> dict[str, list[Task]]:
    if not KANBAN_PATH.exists():
        return {col: [] for col in COLUMNS}
    return _parse(KANBAN_PATH.read_text())


def _write_board(board: dict[str, list[Task]]):
    KANBAN_PATH.write_text(_render(board))


def get_active() -> Task | None:
    board = _read_board()
    tasks = board.get("Active", [])
    return tasks[0] if tasks else None


def add(title: str, column: str = "Backlog"):
    board = _read_board()
    board[column].append(Task(title=title, column=column))
    _write_board(board)


def activate(title: str):
    board = _read_board()
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
    _write_board(board)


def complete(title: str):
    from datetime import date

    board = _read_board()
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
    _write_board(board)


def list_all() -> dict[str, list[Task]]:
    return _read_board()
