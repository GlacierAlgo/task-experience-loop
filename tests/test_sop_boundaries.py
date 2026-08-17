from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "task-experience-loop"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
ACTION_NORM = PLUGIN_ROOT / "_shared" / "action.md"


def sop_skills() -> dict[str, Path]:
    return {
        path.parent.name.removeprefix("sop-"): path
        for path in sorted(SKILLS_ROOT.glob("sop-*/SKILL.md"))
    }


def skill_body(path: Path) -> str:
    return path.read_text().split("---", 2)[-1]


class SopBoundaryTests(unittest.TestCase):
    def test_shared_router_classifies_every_sop_exactly_once(self) -> None:
        text = ACTION_NORM.read_text()
        role_section = text.split("## Action roles", 1)[1].split(
            "## Action routing", 1
        )[0]
        role_lines = "\n".join(
            line for line in role_section.splitlines() if line.startswith("- **")
        )
        role_members = re.findall(r"`([a-z-]+)`", role_lines)
        counts = Counter(role_members)

        self.assertEqual(set(counts), set(sop_skills()))
        self.assertTrue(
            all(count == 1 for count in counts.values()),
            f"SOPs must have exactly one role: {counts}",
        )

    def test_individual_sops_do_not_encode_peer_transitions(self) -> None:
        skills = sop_skills()

        for current, path in skills.items():
            body = skill_body(path)
            peer_pattern = re.compile(
                r"(?<![A-Za-z0-9-])(?:"
                + "|".join(re.escape(peer) for peer in skills if peer != current)
                + r")(?![A-Za-z0-9-])"
            )
            peer_references = sorted(set(peer_pattern.findall(body)))
            self.assertEqual(
                peer_references,
                [],
                f"{path} delegates routing to the shared norm",
            )

    def test_every_sop_applies_shared_resolution_and_routing_norms(self) -> None:
        for path in sop_skills().values():
            body = skill_body(path)
            self.assertIn("../../_shared/resolve.md", body, str(path))
            self.assertIn("../../_shared/action.md", body, str(path))


if __name__ == "__main__":
    unittest.main()
