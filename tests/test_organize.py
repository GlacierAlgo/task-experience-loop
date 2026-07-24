from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from tel import context, decisions, kanban, organize, patterns
from tel.cli import cli


class OrganizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_tel_dir = os.environ.get("TEL_DIR")
        self.previous_project = os.environ.get("TEL_PROJECT")
        os.environ["TEL_DIR"] = self.tempdir.name
        os.environ["TEL_PROJECT"] = "alpha"

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

    def test_organize_writes_index_domain_project_and_conflicts(self) -> None:
        kanban.add("agent runtime")
        decisions.record(
            domain="architecture",
            slug="agent-runtime-boundary",
            decision_point="Where should agent runtime state live?",
            option_space=["frontend state", "backend state"],
            choice="Keep agent runtime state in the backend.",
            constraints=["The backend owns durable task execution."],
            implications=["Frontend reads backend state through APIs."],
            projects=["alpha"],
        )
        patterns.record(
            slug="small-summary-first",
            situation="A memory pool grows beyond direct reading.",
            action="Generate small summaries before detailed lookup.",
            outcome="Agents load less context while retaining source links.",
            domain="workflow",
        )

        report = organize.organize()

        root = Path(self.tempdir.name)
        self.assertEqual(report.decision_count, 1)
        self.assertEqual(report.pattern_count, 1)
        self.assertTrue((root / "summaries" / "index.md").exists())
        self.assertTrue((root / "summaries" / "conflicts.md").exists())
        self.assertTrue((root / "summaries" / "domains" / "architecture.md").exists())
        self.assertTrue((root / "summaries" / "projects" / "alpha.md").exists())
        project_text = (root / "summaries" / "projects" / "alpha.md").read_text()
        self.assertIn("architecture--agent-runtime-boundary.md", project_text)

        context_text = (root / "loop-context.md").read_text()
        self.assertIn("## Experience Summaries", context_text)
        self.assertIn("summaries/index.md", context_text)
        self.assertIn("summaries/projects/alpha.md", context_text)

    def test_context_regeneration_keeps_no_active_task_context_compact(self) -> None:
        for index in range(20):
            decisions.record(
                domain="architecture",
                slug=f"decision-{index}",
                decision_point=f"Where should decision {index} live?",
                option_space=["option a", "option b"],
                choice=f"Choose compact context behavior number {index}.",
                constraints=["Context should stay readable."],
                implications=["Detailed inventory stays in summaries."],
            )

        text = context.assemble()

        self.assertIn("No active task. Use summaries/index.md and the current project summary for lookup.", text)
        self.assertLess(len(text), 4000)

    def test_context_requires_multiple_distinct_relevance_hits(self) -> None:
        os.environ["TEL_PROJECT"] = "agent-server"
        decisions.record(
            domain="architecture",
            slug="agent-runtime-boundary",
            decision_point="Where should the unrelated runtime live?",
            option_space=["frontend", "backend"],
            choice="Keep the unrelated agent runtime in the backend.",
            constraints=["The backend owns execution."],
            implications=["The frontend reads an API."],
        )
        decisions.record(
            domain="architecture",
            slug="agent-server-runtime-boundary",
            decision_point="Where should the agent server runtime live?",
            option_space=["frontend", "backend"],
            choice="Keep the agent server runtime in the backend.",
            constraints=["The backend owns execution."],
            implications=["The frontend reads an API."],
            projects=["agent-server"],
        )
        kanban.add("investigation")
        kanban.start("investigation")

        text = context.assemble()

        self.assertNotIn("architecture--agent-runtime-boundary.md", text)
        self.assertIn("architecture--agent-server-runtime-boundary.md", text)

    def test_organize_removes_stale_generated_summaries(self) -> None:
        root = Path(self.tempdir.name)
        stale_project = root / "summaries" / "projects" / "old-project.md"
        stale_domain = root / "summaries" / "domains" / "old-domain.md"
        stale_project.parent.mkdir(parents=True, exist_ok=True)
        stale_domain.parent.mkdir(parents=True, exist_ok=True)
        stale_project.write_text("# old project\n")
        stale_domain.write_text("# old domain\n")

        kanban.add("agent runtime")
        decisions.record(
            domain="architecture",
            slug="agent-runtime-boundary",
            decision_point="Where should agent runtime state live?",
            option_space=["frontend state", "backend state"],
            choice="Keep agent runtime state in the backend.",
            constraints=["The backend owns durable task execution."],
            implications=["Frontend reads backend state through APIs."],
        )

        report = organize.organize()

        self.assertFalse(stale_project.exists())
        self.assertFalse(stale_domain.exists())
        self.assertIn(stale_project, report.removed_files)
        self.assertIn(stale_domain, report.removed_files)

    def test_explicit_project_ownership_drives_summary_and_context_without_kanban(self) -> None:
        decisions.record(
            domain="architecture",
            slug="butterfly-runtime",
            decision_point="Where does runtime state live?",
            option_space=["browser", "server"],
            choice="Keep Butterfly runtime state in the server.",
            constraints=["Runtime state must survive browser refreshes."],
            implications=["The browser reads server-owned state."],
            projects=["butterfly-effect"],
        )
        decisions.record(
            domain="architecture",
            slug="unrelated-runtime",
            decision_point="Where does an unrelated runtime live?",
            option_space=["browser", "server"],
            choice="Butterfly-like wording must not imply project ownership.",
            constraints=["Project ownership is explicit."],
            implications=["Keyword overlap does not assign a project."],
        )

        organize.organize()

        project_summary = (
            Path(self.tempdir.name) / "summaries" / "projects" / "butterfly-effect.md"
        ).read_text()
        self.assertIn("architecture--butterfly-runtime.md", project_summary)
        self.assertNotIn("architecture--unrelated-runtime.md", project_summary)
        self.assertIn(
            "architecture--butterfly-runtime.md",
            context.assemble(project_id="butterfly-effect"),
        )

    def test_project_summary_omits_completion_history(self) -> None:
        decisions.record(
            domain="workflow",
            slug="live-board-only",
            decision_point="What belongs on the live task board?",
            option_space=["all task history", "unfinished commitments"],
            choice="Keep only unfinished commitments.",
            constraints=["History has authoritative sources elsewhere."],
            implications=["Completed tasks leave the board."],
            projects=["alpha"],
        )
        kanban.add("temporary task")
        kanban.complete("temporary task")

        organize.organize()

        project_summary = (
            Path(self.tempdir.name) / "summaries" / "projects" / "alpha.md"
        ).read_text()
        self.assertNotIn("temporary task", project_summary)
        self.assertNotIn("Recent Completions", project_summary)

    def test_search_matches_decision_project_id(self) -> None:
        decisions.record(
            domain="architecture",
            slug="runtime-boundary",
            decision_point="Where should runtime state live?",
            option_space=["browser", "server"],
            choice="Keep runtime state in the server.",
            constraints=["The server owns execution."],
            implications=["The browser reads an API."],
            projects=["butterfly-effect"],
        )

        result = CliRunner().invoke(cli, ["search", "butterfly-effect"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("architecture--runtime-boundary.md", result.output)


if __name__ == "__main__":
    unittest.main()
