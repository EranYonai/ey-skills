#!/usr/bin/env python3
"""Print filtered review events for manual principle extraction."""
import argparse
import json
import os
import re

CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def terminal_safe(text):
    return CONTROL_RE.sub("", text or "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir")
    parser.add_argument("--reviewer")
    parser.add_argument("--topic")
    parser.add_argument("--outcome")
    parser.add_argument("--project")
    parser.add_argument("--min-len", type=int, default=0)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--inline", action="store_true")
    parser.add_argument("--sort", choices=["len", "date"], default="len")
    args = parser.parse_args()
    skill_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    evidence_root = os.path.join(skill_dir, "evidence")
    args.evidence_dir = os.path.realpath(args.evidence_dir)
    if os.path.commonpath((evidence_root, args.evidence_dir)) != evidence_root:
        raise SystemExit("evidence directory must be inside %s" % evidence_root)

    with open(os.path.join(args.evidence_dir, "events.jsonl")) as source:
        events = [json.loads(line) for line in source]

    def keep(event):
        return not (
            (args.reviewer and event["reviewer"] != args.reviewer)
            or (args.topic and args.topic not in event["topics"])
            or (args.outcome and event["outcome"] != args.outcome)
            or (args.project and event["project"] != args.project)
            or (args.inline and not event["inline"])
            or len(event["observation"]) < args.min_len
        )

    selected = [event for event in events if keep(event)]
    selected.sort(
        key=(lambda event: -len(event["observation"]))
        if args.sort == "len"
        else (lambda event: event["created_at"])
    )
    print("matched %d events (showing %d)" % (len(selected), min(len(selected), args.limit)))
    for event in selected[: args.limit]:
        print("-" * 78)
        print(
            "%s | %s!%s | %s | %s | %s"
            % (
                terminal_safe(event["reviewer"]),
                terminal_safe(event["project"]),
                event["iid"],
                terminal_safe(event["created_at"][:10]),
                terminal_safe(event["outcome"]),
                terminal_safe(",".join(event["topics"]) or "-"),
            )
        )
        if event["file"]:
            print("  @ %s:%s" % (terminal_safe(event["file"]), event["line"]))
        print("  " + terminal_safe(event["observation"]))
        for reply in event.get("replies", []):
            print("  -> %s: %s" % (terminal_safe(reply["author"]), terminal_safe(reply["body"])))


if __name__ == "__main__":
    main()
