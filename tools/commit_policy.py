#!/usr/bin/env python3
"""Format and validate Agent Commons commit messages."""

from __future__ import annotations

import argparse
import re
import sys


CONVENTIONAL_PREFIX = re.compile(
    r"^(?:feat|fix|docs|chore|refactor|test|style|perf|build|ci)(?:\([^\r\n)]+\))?\s*:",
    re.IGNORECASE,
)
TICKET = re.compile(r"(?<![A-Z0-9])([A-Z][A-Z0-9]{1,19}-[1-9][0-9]*)(?![A-Z0-9])")
ATTRIBUTION_TRAILER = re.compile(
    r"^(?:co-authored-by|generated-by|created-by|assisted-by)\s*:",
    re.IGNORECASE | re.MULTILINE,
)
INTEGRATION_BRANCHES = {"main", "master", "develop", "development", "trunk"}


def ticket_from_branch(branch: str) -> str | None:
    """Return one conservative uppercase ticket identifier from a task branch."""
    normalized = branch.strip()
    if not normalized or normalized.casefold() in INTEGRATION_BRANCHES:
        return None
    matches = list(dict.fromkeys(TICKET.findall(normalized)))
    return matches[0] if len(matches) == 1 else None


def validate_message(message: str) -> list[str]:
    """Return policy errors for a complete commit message."""
    errors: list[str] = []
    subject = message.splitlines()[0].strip() if message.splitlines() else ""
    if not subject:
        errors.append("commit subject must not be empty")
    elif CONVENTIONAL_PREFIX.match(subject):
        errors.append("Conventional Commit type prefixes are prohibited")
    if ATTRIBUTION_TRAILER.search(message):
        errors.append("co-author and agent-attribution trailers are prohibited")
    return errors


def compose_message(summary: str, branch: str = "") -> str:
    """Create a compliant subject, adding a reliable ticket prefix when available."""
    subject = summary.strip()
    errors = validate_message(subject)
    if errors:
        raise ValueError("; ".join(errors))
    ticket = ticket_from_branch(branch)
    if ticket and not subject.startswith(f"[{ticket}] "):
        subject = f"[{ticket}] {subject}"
    return subject


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("message")
    compose_parser = subparsers.add_parser("compose")
    compose_parser.add_argument("summary")
    compose_parser.add_argument("--branch", default="")
    args = parser.parse_args()
    if args.command == "compose":
        try:
            print(compose_message(args.summary, args.branch))
            return 0
        except ValueError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 1
    errors = validate_message(args.message)
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
