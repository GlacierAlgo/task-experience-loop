from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from tel import decisions, patterns, project


MAX_PROPOSALS_PER_KIND = 20
STALE_WORD_HINTS = ("deprecated", "obsolete", "temporary")


@dataclass(frozen=True)
class CompactProposal:
    action: str
    title: str
    records: list[str]
    reason: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class CompactReport:
    review_path: Path
    proposals: list[CompactProposal]
    decision_count: int = 0
    pattern_count: int = 0

    @property
    def proposal_count(self) -> int:
        return len(self.proposals)


@dataclass(frozen=True)
class DuplicateCandidate:
    first: str
    second: str
    reason: str


def compact_review_path() -> Path:
    return project.tel_dir() / "summaries" / "compact.md"


def _normal_words(text: str) -> set[str]:
    normalized = text.lower().replace("_", " ").replace("-", " ")
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}|[\u4e00-\u9fff]{2,}", normalized)
        if token not in {"the", "and", "for", "with", "from", "that", "this"}
    }


def _text_len(*values: str) -> int:
    text = " ".join(values)
    return len(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text))


def _decision_duplicate_candidates(
    all_decisions: list[decisions.Decision],
) -> list[DuplicateCandidate]:
    candidates: list[DuplicateCandidate] = []
    seen_pairs: set[tuple[str, str]] = set()

    def add(left: decisions.Decision, right: decisions.Decision, reason: str) -> None:
        pair = tuple(sorted((left.filename, right.filename)))
        if pair in seen_pairs:
            return
        seen_pairs.add(pair)
        candidates.append(DuplicateCandidate(pair[0], pair[1], reason))

    by_exact_choice: dict[str, list[decisions.Decision]] = defaultdict(list)
    by_slug: dict[str, list[decisions.Decision]] = defaultdict(list)
    by_domain: dict[str, list[decisions.Decision]] = defaultdict(list)
    for decision in all_decisions:
        choice_key = re.sub(r"\s+", " ", decision.choice.lower()).strip()
        if len(choice_key) >= 24:
            by_exact_choice[choice_key].append(decision)
        by_slug[decision.slug].append(decision)
        by_domain[decision.domain].append(decision)

    for groups, reason in (
        (by_exact_choice.values(), "same normalized choice text"),
        (by_slug.values(), "same slug across domains"),
    ):
        for group in groups:
            for left, right in zip(group, group[1:]):
                add(left, right, reason)

    for group in by_domain.values():
        tokenized = [(decision, _normal_words(decision.choice)) for decision in group]
        for index, (left, left_tokens) in enumerate(tokenized):
            if len(left_tokens) < 5:
                continue
            for right, right_tokens in tokenized[index + 1 :]:
                if len(right_tokens) < 5:
                    continue
                overlap = left_tokens & right_tokens
                union = left_tokens | right_tokens
                if len(overlap) >= 5 and len(overlap) / len(union) >= 0.62:
                    add(left, right, "high choice-token overlap")
    return candidates


def _duplicate_decision_proposals(all_decisions: list[decisions.Decision]) -> list[CompactProposal]:
    proposals = []
    for candidate in _decision_duplicate_candidates(all_decisions)[:MAX_PROPOSALS_PER_KIND]:
        proposals.append(
            CompactProposal(
                action="merge_or_keep",
                title="Review near-duplicate decisions",
                records=[f"decisions/{candidate.first}", f"decisions/{candidate.second}"],
                reason=candidate.reason,
                evidence=["If both records encode the same reusable choice, merge into one canonical record."],
            )
        )
    return proposals


def _validation_proposals() -> list[CompactProposal]:
    proposals = []
    for filename, errors in list(decisions.validate_all().items())[:MAX_PROPOSALS_PER_KIND]:
        proposals.append(
            CompactProposal(
                action="edit_or_deprecate",
                title="Repair invalid decision record",
                records=[f"decisions/{filename}"],
                reason="Decision file does not satisfy the TEL decision contract.",
                evidence=errors,
            )
        )
    return proposals


def _stale_hint_proposals(all_decisions: list[decisions.Decision]) -> list[CompactProposal]:
    proposals = []
    for d in all_decisions:
        # Lifecycle words in decision prose are usually about temporary files,
        # ephemeral runtime values, or rejected obsolete options. Only an
        # explicit lifecycle marker in the record identity is strong enough to
        # create a compact review candidate without repository evidence.
        words = _normal_words(d.slug)
        matched = [hint for hint in STALE_WORD_HINTS if hint in words]
        if not matched:
            continue
        proposals.append(
            CompactProposal(
                action="verify_stale",
                title="Verify potentially stale decision",
                records=[f"decisions/{d.filename}"],
                reason=f"Record identity contains lifecycle language: {', '.join(matched)}.",
                evidence=[
                    "An agent should compare this record with the current repository before proposing deprecation."
                ],
            )
        )
        if len(proposals) >= MAX_PROPOSALS_PER_KIND:
            break
    return proposals


def _pattern_duplicate_proposals(all_patterns: list[patterns.Pattern]) -> list[CompactProposal]:
    proposals = []
    seen_pairs: set[tuple[str, str]] = set()
    tokenized = [
        (p, _normal_words(" ".join([p.slug, p.situation, p.action, p.outcome]))) for p in all_patterns
    ]
    for index, (left, left_tokens) in enumerate(tokenized):
        if len(left_tokens) < 5:
            continue
        for right, right_tokens in tokenized[index + 1 :]:
            if len(right_tokens) < 5:
                continue
            overlap = left_tokens & right_tokens
            union = left_tokens | right_tokens
            if len(overlap) >= 5 and len(overlap) / len(union) >= 0.62:
                pair = (left.filename, right.filename)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                proposals.append(
                    CompactProposal(
                        action="merge_or_keep",
                        title="Review near-duplicate patterns",
                        records=[f"patterns/{left.filename}", f"patterns/{right.filename}"],
                        reason="high pattern-token overlap",
                        evidence=["If one pattern fully covers the other, keep the canonical one and delete or rewrite the weaker one."],
                    )
                )
                if len(proposals) >= MAX_PROPOSALS_PER_KIND:
                    return proposals
    return proposals


def _low_value_pattern_proposals(all_patterns: list[patterns.Pattern]) -> list[CompactProposal]:
    proposals = []
    for p in all_patterns:
        if p.uses != 0:
            continue
        if _text_len(p.situation, p.action, p.outcome) >= 24:
            continue
        proposals.append(
            CompactProposal(
                action="delete_or_rewrite_pattern",
                title="Review low-signal unused pattern",
                records=[f"patterns/{p.filename}"],
                reason="Pattern has never been reused and has very little explanatory content.",
                evidence=["A pattern should survive only if it gives a reusable practice for future agents."],
            )
        )
        if len(proposals) >= MAX_PROPOSALS_PER_KIND:
            break
    return proposals


def analyze() -> CompactReport:
    all_decisions = decisions.query(status="active")
    all_patterns = patterns.query()
    proposals: list[CompactProposal] = []
    proposals.extend(_validation_proposals())
    proposals.extend(_duplicate_decision_proposals(all_decisions))
    proposals.extend(_stale_hint_proposals(all_decisions))
    proposals.extend(_pattern_duplicate_proposals(all_patterns))
    proposals.extend(_low_value_pattern_proposals(all_patterns))

    return CompactReport(
        review_path=compact_review_path(),
        proposals=proposals,
        decision_count=len(all_decisions),
        pattern_count=len(all_patterns),
    )


def render(report: CompactReport) -> str:
    lines = [
        "# TEL Compact Review",
        "",
        "This file is advisory. Source records are unchanged until a user approves a proposed change.",
        "",
        "## Inventory",
        f"- Active decisions: {report.decision_count}",
        f"- Patterns: {report.pattern_count}",
        f"- Proposed review items: {report.proposal_count}",
        "",
        "## Confirmation Rule",
        "- An agent may analyze these proposals autonomously.",
        "- An agent must ask the user before editing, deleting, merging, deprecating, or superseding source records.",
        "",
        "## Proposed Changes",
    ]
    if not report.proposals:
        lines.append("(none detected)")
        lines.append("")
        return "\n".join(lines)

    for index, proposal in enumerate(report.proposals, 1):
        lines.extend(
            [
                f"### {index}. {proposal.title}",
                f"- Action: {proposal.action}",
                f"- Reason: {proposal.reason}",
                "- Records:",
            ]
        )
        for record in proposal.records:
            lines.append(f"  - {record}")
        if proposal.evidence:
            lines.append("- Evidence:")
            for item in proposal.evidence:
                lines.append(f"  - {item}")
        lines.append("")
    return "\n".join(lines)


def write_review() -> CompactReport:
    report = analyze()
    report.review_path.parent.mkdir(parents=True, exist_ok=True)
    report.review_path.write_text(render(report) + "\n")
    return report
