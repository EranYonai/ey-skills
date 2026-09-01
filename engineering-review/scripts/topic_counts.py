#!/usr/bin/env python3
"""Print per-reviewer topic counts split by outcome."""
import argparse
import json
import os
from collections import Counter, defaultdict

ACCEPTING = {"accepted", "discussed_resolved", "resolved_silently"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir")
    parser.add_argument("--reviewer")
    args = parser.parse_args()
    skill_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    evidence_root = os.path.join(skill_dir, "evidence")
    args.evidence_dir = os.path.realpath(args.evidence_dir)
    if os.path.commonpath((evidence_root, args.evidence_dir)) != evidence_root:
        raise SystemExit("evidence directory must be inside %s" % evidence_root)
    with open(os.path.join(args.evidence_dir, "events.jsonl")) as source:
        events = [json.loads(line) for line in source]
    if args.reviewer:
        events = [event for event in events if event["reviewer"] == args.reviewer]

    counts = defaultdict(lambda: defaultdict(Counter))
    for event in events:
        for topic in event["topics"]:
            bucket = "adopted" if event["outcome"] in ACCEPTING else event["outcome"]
            counts[event["reviewer"]][topic][bucket] += 1
            counts[event["reviewer"]][topic]["total"] += 1

    for reviewer in sorted(counts):
        print("=" * 72)
        print(reviewer)
        for topic, values in sorted(counts[reviewer].items(), key=lambda item: -item[1]["total"]):
            print(
                "  %-20s total=%-4d adopted=%-4d rejected=%-3d no_response=%-4d unresolved=%d"
                % (
                    topic,
                    values["total"],
                    values["adopted"],
                    values["rejected"],
                    values["no_response"],
                    values["discussed_unresolved"],
                )
            )


if __name__ == "__main__":
    main()
