from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from tel import context, kanban, project
from tel.cli import cli


class ProjectScopedKanbanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_tel_dir = os.environ.get("TEL_DIR")
        self.previous_project = os.environ.get("TEL_PROJECT")
        os.environ["TEL_DIR"] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous_tel_dir is None:
            os.environ.pop("TEL_DIR", None)
        else:
            os.environ["TEL_DIR"] = self.previous_tel_dir
        if self.previous_project is None:
            os.environ.pop("TEL_PROJECT", None)
        else:
            os.environ["TEL_PROJECT"] = self.previous_project
        self.tempdir.cleanup()

    def test_boards_are_separated_by_project(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        kanban.add("alpha task")

        os.environ["TEL_PROJECT"] = "beta"
        kanban.add("beta task")

        os.environ["TEL_PROJECT"] = "alpha"
        alpha = kanban.list_all()
        self.assertEqual([task.title for task in alpha["Backlog"]], ["alpha task"])

        os.environ["TEL_PROJECT"] = "beta"
        beta = kanban.list_all()
        self.assertEqual([task.title for task in beta["Backlog"]], ["beta task"])

        kanban_file = Path(self.tempdir.name, "kanban.md")
        self.assertTrue(kanban_file.exists())
        self.assertFalse(Path(self.tempdir.name, "projects").exists())
        self.assertIn("- alpha\n  - alpha task", kanban_file.read_text())
        self.assertIn("- beta\n  - beta task", kanban_file.read_text())

    def test_context_uses_current_project_board(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        kanban.add("alpha next")

        os.environ["TEL_PROJECT"] = "beta"
        kanban.add("beta next")

        os.environ["TEL_PROJECT"] = "alpha"
        text = context.assemble()

        self.assertIn("Project: `alpha`", text)
        self.assertIn("alpha next", text)
        self.assertNotIn("beta next", text)

    def test_complete_removes_task_without_history(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        kanban.add("temporary task")
        kanban.start("temporary task")

        completed = kanban.complete()

        board = kanban.list_all()
        self.assertEqual(completed.title, "temporary task")
        self.assertEqual(board["Backlog"], [])
        self.assertEqual(board["Active"], [])
        kanban_text = Path(self.tempdir.name, "kanban.md").read_text()
        self.assertNotIn("temporary task", kanban_text)
        self.assertNotIn("## Done", kanban_text)

    def test_start_moves_backlog_or_creates_active_directly(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        kanban.add("planned")

        kanban.start("planned")
        kanban.start("planned")

        board = kanban.list_all()
        self.assertEqual(board["Backlog"], [])
        self.assertEqual([task.title for task in board["Active"]], ["planned"])

        kanban.complete()
        kanban.start("unplanned")

        board = kanban.list_all()
        self.assertEqual(board["Backlog"], [])
        self.assertEqual([task.title for task in board["Active"]], ["unplanned"])

    def test_start_rejects_a_second_active_task(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        kanban.start("first")

        with self.assertRaisesRegex(ValueError, "Active task already exists: first"):
            kanban.start("second")

    def test_cli_uses_direct_reads_and_removes_obsolete_commands(self) -> None:
        os.environ["TEL_PROJECT"] = "alpha"
        runner = CliRunner()

        self.assertEqual(runner.invoke(cli, ["task", "start", "work"]).exit_code, 0)
        task_read = runner.invoke(cli, ["task"])
        self.assertEqual(task_read.exit_code, 0)
        self.assertIn("## Active", task_read.output)
        self.assertIn("work", task_read.output)

        self.assertNotEqual(runner.invoke(cli, ["task", "activate", "work"]).exit_code, 0)
        self.assertNotEqual(runner.invoke(cli, ["task", "list"]).exit_code, 0)
        self.assertNotEqual(runner.invoke(cli, ["organize"]).exit_code, 0)

        self.assertEqual(runner.invoke(cli, ["noun", "add", "TEL", "Task Experience Loop"]).exit_code, 0)
        noun_read = runner.invoke(cli, ["noun"])
        self.assertEqual(noun_read.exit_code, 0)
        self.assertIn("TEL -> Task Experience Loop", noun_read.output)
        self.assertNotEqual(runner.invoke(cli, ["noun", "list"]).exit_code, 0)

    def test_empty_tel_dir_uses_default_location(self) -> None:
        os.environ["TEL_DIR"] = ""

        self.assertEqual(project.tel_dir(), project.DEFAULT_TEL_DIR)

    def test_tel_dir_environment_override_wins(self) -> None:
        override = Path(self.tempdir.name, "custom-tel")
        os.environ["TEL_DIR"] = str(override)

        self.assertEqual(project.tel_dir(), override)

    def test_flat_legacy_board_is_not_current_project_backlog(self) -> None:
        Path(self.tempdir.name, "kanban.md").write_text(
            "## Backlog\n- old mixed task\n\n## Active\n\n## Done\n- legacy\n  - old completion | 2026-01-01\n"
        )

        os.environ["TEL_PROJECT"] = "alpha"
        alpha = kanban.list_all()
        self.assertEqual(alpha["Backlog"], [])

        legacy = kanban.list_all("legacy")
        self.assertEqual([task.title for task in legacy["Backlog"]], ["old mixed task"])
        self.assertNotIn("Done", legacy)


if __name__ == "__main__":
    unittest.main()
