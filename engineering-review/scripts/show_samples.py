#!/usr/bin/env python3
"""Print captured comments for reviewer candidates from discover_reviewers.py."""
import argparse
import json
import os
import re

CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def terminal_safe(text):
    return CONTROL_RE.sub("", text or "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--user", action="append", required=True)
    parser.add_argument("--max", type=int, default=4)
    args = parser.parse_args()
    skill_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    evidence_root = os.path.join(skill_dir, "evidence")
    args.path = os.path.realpath(args.path)
    if os.path.commonpath((evidence_root, args.path)) != evidence_root:
        raise SystemExit("sample path must be inside %s" % evidence_root)
    with open(args.path) as source:
        rows = {row["user"]: row for row in json.load(source)}

    for user in args.user:
        row = rows.get(user)
        print("=" * 78)
        if not row:
            print(terminal_safe(user), "- not found")
            continue
        print(
            "%s | substantive=%d inline=%d deep=%d engaged=%d MRs=%d authors=%d"
            % (
                terminal_safe(user),
                row["substantive"],
                row["inline"],
                row["deep"],
                row["engaged"],
                row["mrs"],
                row["authors"],
            )
        )
        print("areas:", terminal_safe(", ".join(row["top_areas"])))
        for sample in row["samples"][: args.max]:
            print("-" * 70)
            print(
                "  !%s  %s"
                % (sample["iid"], terminal_safe(sample["file"] or "(top-level)"))
            )
            print("  " + terminal_safe(sample["body"]))


if __name__ == "__main__":
    main()
