#!/usr/bin/env python3
"""Turn collected GitLab discussion threads into atomic review events."""
import json
import os
import re
import sys
from collections import Counter, defaultdict


USERS = set(filter(None, (u.strip() for u in os.environ.get("ER_USERS", "").split(","))))
if not USERS:
    raise SystemExit("missing required environment variable: ER_USERS")

BOT_RE = re.compile(
    r"^\s*!?\[?danger|gitlab-ci|coverage decreased|sonarqube|^\s*:robot:|"
    r"assigned to @|^added \d+ commit|changed the description|requested review from|"
    r"approved this merge request|marked this merge request|resolved all threads|"
    r"enabled an automatic merge|mentioned in|changed target branch",
    re.I,
)
TRIVIAL_RE = re.compile(
    r"^\s*(lgtm|looks good|nice|thanks?|thx|ok|okay|\+1|done|good catch|great|"
    r"cool|sure|same|ditto|agreed?|yes|no|np|ping|bump|kudos|:\w+:)[\s.!?]*$",
    re.I,
)
ACCEPT_RE = re.compile(
    r"\b(done|fixed|changed|updated|removed|added|good catch|you'?re right|will do|"
    r"makes sense|agreed?|adopted|refactored|addressed)\b",
    re.I,
)
REJECT_RE = re.compile(
    r"\b(i (don'?t|do not) think|disagree|not (needed|necessary|relevant|true)|"
    r"intentional|on purpose|by design|prefer to keep|out of scope|will not|won'?t|"
    r"no need|already handled)\b",
    re.I,
)
TOPICS = {
    "tests": r"\b(test|assert|fixture|mock|coverage|flak|unit test|e2e)\b",
    "error-handling": r"\b(exception|raise|error handling|swallow|fail(ure|s)? silently|catch)\b",
    "naming": r"\b(naming|rename|variable name|typo|misleading name|call it)\b",
    "duplication": r"\b(duplicat|copy[- ]?paste|dry|repeated|same code|reuse)\b",
    "abstraction": r"\b(abstract|helper|utility|wrapper|generic|over[- ]?engineer|simplif|too complex|refactor)\b",
    "concurrency": r"\b(race|thread|lock|mutex|deadlock|concurren|async|await|atomic)\b",
    "api-design": r"\b(api|interface|signature|parameter|argument|return value|contract|backward)\b",
    "security": r"\b(secret|password|token|credential|injection|sanitiz|permission|privilege)\b",
    "performance": r"\b(performance|slow|memory|leak|cpu|expensive|optimi[sz])\b",
    "cleanup": r"\b(cleanup|teardown|finally|context manager|close\(|resource|revert)\b",
    "documentation": r"\b(docstring|comment|document|readme|explain why)\b",
    "ci": r"\b(pipeline|ci|job|stage|runner|artifact)\b",
    "correctness": r"\b(bug|wrong|incorrect|broken|will fail|edge case|null|crash)\b",
}
TOPIC_RES = {name: re.compile(pattern, re.I) for name, pattern in TOPICS.items()}
CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def clean(body):
    body = body or ""
    body = CONTROL_RE.sub("", body)
    body = re.sub(r"```.*?```", " <code> ", body, flags=re.S)
    body = re.sub(r"`[^`]*`", " <code> ", body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " <img> ", body)
    return re.sub(r"\s+", " ", body).strip()


def classify_outcome(thread, reviewer, mr_author):
    replies = thread[1:]
    author_replies = [n for n in replies if n["author"] == mr_author and not n["system"]]
    reviewer_replies = [n for n in replies if n["author"] == reviewer and not n["system"]]
    resolved = any(n.get("resolved") for n in thread)
    text = " ".join(clean(n["body"]) for n in author_replies)
    if ACCEPT_RE.search(text):
        return "accepted"
    if REJECT_RE.search(text):
        return "rejected"
    if resolved and not author_replies:
        return "resolved_silently"
    if resolved:
        return "discussed_resolved"
    if reviewer_replies or author_replies:
        return "discussed_unresolved"
    return "no_response"


def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    evidence_dir = os.path.join(skill_dir, "evidence")
    out_dir = os.path.realpath(sys.argv[1])
    if os.path.commonpath((evidence_dir, out_dir)) != evidence_dir:
        raise SystemExit("evidence directory must be inside %s" % evidence_dir)
    events = []
    with open(os.path.join(out_dir, "notes.jsonl")) as notes_file:
        for line in notes_file:
            record = json.loads(line)
            human = [note for note in record["notes"] if not note["system"]]
            if not human:
                continue
            opener = human[0]
            reviewer = opener["author"]
            body = clean(opener["body"])
            if reviewer not in USERS or reviewer == record["mr_author"]:
                continue
            if not body or len(body) < 15 or BOT_RE.search(body) or TRIVIAL_RE.match(body):
                continue
            outcome = classify_outcome(human, reviewer, record["mr_author"])
            replies = [
                {
                    "author": note["author"],
                    "body": clean(note["body"])[:1200],
                    "created_at": note["created_at"],
                    "resolved": note.get("resolved"),
                }
                for note in human[1:]
            ]
            events.append(
                {
                    "reviewer": reviewer,
                    "project": record["project"],
                    "iid": record["iid"],
                    "web_url": record["web_url"],
                    "mr_title": record["mr_title"],
                    "mr_author": record["mr_author"],
                    "file": opener.get("file"),
                    "line": opener.get("line"),
                    "inline": bool(opener.get("file")),
                    "created_at": opener["created_at"],
                    "observation": body[:1200],
                    "replies": replies,
                    "reply_count": len(human) - 1,
                    "outcome": outcome,
                    "topics": sorted(name for name, regex in TOPIC_RES.items() if regex.search(body)),
                    "strength": "strong"
                    if outcome in ("accepted", "rejected") and len(body) > 80
                    else "medium"
                    if outcome in ("accepted", "rejected", "discussed_resolved", "discussed_unresolved")
                    else "weak",
                }
            )

    events.sort(key=lambda event: (event["reviewer"], event["created_at"]))
    events_path = os.path.join(out_dir, "events.jsonl")
    descriptor = os.open(events_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(events_path, 0o600)
    with os.fdopen(descriptor, "w") as output:
        for event in events:
            output.write(json.dumps(event) + "\n")

    if "--stats" in sys.argv:
        print("total events:", len(events))
        for reviewer, count in Counter(e["reviewer"] for e in events).most_common():
            print("  %-20s %d" % (reviewer, count))
        topics = defaultdict(Counter)
        for event in events:
            topics[event["reviewer"]].update(event["topics"])
        for reviewer in sorted(topics):
            print("  %-20s %s" % (reviewer, ", ".join("%s:%d" % item for item in topics[reviewer].most_common(8))))


if __name__ == "__main__":
    main()
