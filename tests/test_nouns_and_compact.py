from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from tel import compact, context, decisions, nouns
from tel.cli import cli
from tests.support import write_decision


class NounsAndCompactTests(unittest.TestCase):
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

    def test_global_nouns_are_rendered_in_context(self) -> None:
        nouns.record("aliyun", "SSH host `aliyun`, Alibaba Cloud server")
        nouns.record("CDP", "Chrome DevTools Protocol unless context says otherwise")

        text = context.assemble()

        self.assertIn("## Global Nouns", text)
        self.assertIn("aliyun -> SSH host `aliyun`, Alibaba Cloud server", text)
        self.assertIn("CDP -> Chrome DevTools Protocol unless context says otherwise", text)

    def test_compact_writes_review_without_changing_source_records(self) -> None:
        for slug in ("runtime-a", "runtime-b"):
            write_decision(
                domain="architecture",
                slug=slug,
                decision_point="Where should runtime state live?",
                option_space=["frontend", "backend"],
                choice="Keep runtime state in the backend control plane.",
                constraints=["The backend owns durable task execution."],
                implications=["The frontend reads task state through APIs."],
            )

        report = compact.write_review()

        self.assertGreaterEqual(report.proposal_count, 1)
        self.assertTrue(report.review_path.exists())
        review_text = report.review_path.read_text()
        self.assertIn("Source records are unchanged", review_text)
        self.assertIn("merge_or_keep", review_text)
        self.assertIn("summaries/compact.md", context.assemble())
        self.assertTrue(Path(self.tempdir.name, "decisions", "architecture--runtime-a.md").exists())
        self.assertTrue(Path(self.tempdir.name, "decisions", "architecture--runtime-b.md").exists())

    def test_compact_cli_takes_no_required_arguments(self) -> None:
        runner = CliRunner()

        result = runner.invoke(cli, ["compact"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Wrote compact review", result.output)
        self.assertTrue(Path(self.tempdir.name, "summaries", "compact.md").exists())

    def test_compact_does_not_treat_compatibility_terms_as_stale(self) -> None:
        write_decision(
            domain="interface",
            slug="stable-compatibility-boundary",
            decision_point="How should compatibility be handled?",
            option_space=["compatibility mapping", "breaking rename"],
            choice="Keep compatibility aliases inside the declared semantic boundary.",
            constraints=["Compatibility is an active public interface constraint."],
            implications=["Future changes must preserve the compatibility envelope."],
        )
        write_decision(
            domain="interface",
            slug="temporary-debug-route",
            decision_point="How should a temporary route be handled?",
            option_space=["keep", "remove"],
            choice="Keep the temporary debug route until the replacement is ready.",
            constraints=["The replacement has not shipped."],
            implications=["Compact should review this later."],
        )

        report = compact.analyze()
        rendered = compact.render(report)

        self.assertNotIn("stable-compatibility-boundary", rendered)
        self.assertIn("temporary-debug-route", rendered)

    def test_decision_validation_accepts_ordered_options_and_prose_sections(self) -> None:
        path = Path(self.tempdir.name, "decisions", "architecture--mixed-markdown.md")
        path.parent.mkdir(parents=True)
        path.write_text(
            """---
domain: architecture
decided: 2026-07-24
status: active
---

# Mixed Markdown Decision

## Decision Point
Which storage model should be used?

## Option Space
1. One shared store.
2. One store per project.

## Choice
Use one store per project.

## Constraints & Rationale
Projects have independent lifecycles and access boundaries.

## Implications
Each project owns its migrations and backups.
"""
        )

        self.assertEqual(decisions.validate(path), [])

        path.write_text(path.read_text().replace("status: active", "status: accepted"))
        self.assertIn("Invalid status 'accepted'", decisions.validate(path)[0])


if __name__ == "__main__":
    unittest.main()
