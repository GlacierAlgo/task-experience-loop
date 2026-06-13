from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tel import context, kanban, project


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

    def test_empty_tel_dir_uses_default_location(self) -> None:
        os.environ["TEL_DIR"] = ""

        self.assertEqual(project.tel_dir(), project.DEFAULT_TEL_DIR)

    def test_tel_dir_environment_override_wins(self) -> None:
        override = Path(self.tempdir.name, "custom-tel")
        os.environ["TEL_DIR"] = str(override)

        self.assertEqual(project.tel_dir(), override)

    def test_flat_legacy_board_is_not_current_project_backlog(self) -> None:
        Path(self.tempdir.name, "kanban.md").write_text("## Backlog\n- old mixed task\n\n## Active\n\n## Done\n")

        os.environ["TEL_PROJECT"] = "alpha"
        alpha = kanban.list_all()
        self.assertEqual(alpha["Backlog"], [])

        legacy = kanban.list_all("legacy")
        self.assertEqual([task.title for task in legacy["Backlog"]], ["old mixed task"])


if __name__ == "__main__":
    unittest.main()
