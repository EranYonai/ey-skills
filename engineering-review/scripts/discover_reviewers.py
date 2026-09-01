#!/usr/bin/env python3
"""Rank GitLab reviewers by substantive review activity.

Required environment variables:
    ER_GITLAB_URL=https://gitlab.example.com
    GITLAB_TOKEN=...

Usage:
    python3 discover_reviewers.py PROJECT_ID [OUT_DIR] [--sample N]

OUT_DIR defaults to this skill's gitignored evidence/discovery directory and
must remain under evidence/ because samples contain private review content.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit("missing required environment variable: %s" % name)
    return value


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
EVIDENCE_DIR = os.path.join(SKILL_DIR, "evidence")
BASE_URL = required("ER_GITLAB_URL").rstrip("/")
if urllib.parse.urlsplit(BASE_URL).scheme != "https":
    raise SystemExit("ER_GITLAB_URL must use HTTPS")
API = BASE_URL + "/api/v4/"
TOKEN = required("GITLAB_TOKEN")


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        old = urllib.parse.urlsplit(request.full_url)
        new = urllib.parse.urlsplit(new_url)
        if (old.scheme, old.netloc) != (new.scheme, new.netloc):
            raise urllib.error.HTTPError(new_url, code, "cross-origin redirect refused", headers, fp)
        return super().redirect_request(request, fp, code, message, headers, new_url)


OPENER = urllib.request.build_opener(SameOriginRedirect())
BOT_RE = re.compile(
    r"^\s*!?\[?danger|gitlab-ci|coverage decreased|sonarqube|^\s*:robot:|"
    r"assigned to @|^added \d+ commit|changed the description|requested review from|"
    r"approved this merge request|marked this merge request|resolved all threads|"
    r"enabled an automatic merge|mentioned in|changed target branch",
    re.I,
)
BOT_USER_RE = re.compile(r"bot|jenkins|gitlab|service|ci[-_]|automation|webhook", re.I)
TRIVIAL_RE = re.compile(
    r"^\s*(lgtm|looks good|nice|thanks?|thx|ok|okay|\+1|done|good catch|great|"
    r"cool|sure|same|ditto|agreed?|yes|no|np|ping|bump|kudos|:\w+:)[\s.!?]*$",
    re.I,
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def get(path, params=None, retries=3):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    request = urllib.request.Request(url, headers={"PRIVATE-TOKEN": TOKEN})
    for attempt in range(retries):
        try:
            with OPENER.open(request, timeout=60) as response:
                return json.loads(response.read().decode()), dict(response.headers)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries - 1:
                raise RuntimeError("GitLab request failed: %s: %s" % (url, exc))
            time.sleep(1.5 * (attempt + 1))


def list_pages(path, params, max_items):
    results = []
    params = dict(params, per_page=100)
    page = 1
    while len(results) < max_items:
        params["page"] = page
        data, headers = get(path, params)
        if not data:
            break
        results.extend(data)
        next_page = headers.get("X-Next-Page") or headers.get("x-next-page")
        if not next_page:
            break
        page = int(next_page)
    return results[:max_items]


def clean(body):
    body = body or ""
    body = CONTROL_RE.sub("", body)
    body = re.sub(r"```.*?```", " <code> ", body, flags=re.S)
    body = re.sub(r"`[^`]*`", " <code> ", body)
    return re.sub(r"\s+", " ", body).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("out_dir", nargs="?", default=os.path.join(EVIDENCE_DIR, "discovery"))
    parser.add_argument("--sample", type=int, default=1200)
    parser.add_argument("--since", default="2025-01-01T00:00:00Z")
    args = parser.parse_args()
    args.out_dir = os.path.realpath(args.out_dir)
    if os.path.commonpath((EVIDENCE_DIR, args.out_dir)) != EVIDENCE_DIR:
        raise SystemExit("OUT_DIR must be inside %s" % EVIDENCE_DIR)
    project = urllib.parse.quote(args.project_id, safe="")
    merge_requests = list_pages(
        "projects/%s/merge_requests" % project,
        {"updated_after": args.since, "state": "merged", "order_by": "updated_at"},
        args.sample,
    )

    stats = defaultdict(Counter)
    mrs_seen = defaultdict(set)
    authors_seen = defaultdict(set)
    areas = defaultdict(Counter)
    samples = defaultdict(list)

    def discussions(mr):
        path = "projects/%s/merge_requests/%d/discussions" % (project, mr["iid"])
        return mr, list_pages(path, {}, 500)

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(discussions, mr) for mr in merge_requests]
        for future in as_completed(futures):
            mr, records = future.result()
            mr_author = (mr.get("author") or {}).get("username")
            for discussion in records or []:
                human = [note for note in discussion.get("notes") or [] if not note.get("system")]
                if not human:
                    continue
                opener = human[0]
                user = (opener.get("author") or {}).get("username")
                body = clean(opener.get("body"))
                if not user or user == mr_author or BOT_USER_RE.search(user):
                    continue
                if len(body) < 15 or BOT_RE.search(body) or TRIVIAL_RE.match(body):
                    continue
                position = opener.get("position") or {}
                path = position.get("new_path") or position.get("old_path")
                stats[user]["substantive"] += 1
                if path:
                    stats[user]["inline"] += 1
                    areas[user][path.split("/", 1)[0]] += 1
                if len(body) >= 200:
                    stats[user]["deep"] += 1
                if len(human) > 1:
                    stats[user]["engaged"] += 1
                mrs_seen[user].add(mr["iid"])
                authors_seen[user].add(mr_author)
                if len(body) >= 250 and len(samples[user]) < 5:
                    samples[user].append({"iid": mr["iid"], "file": path, "body": body[:900]})

    rows = []
    for user, counts in stats.items():
        rows.append(
            {
                "user": user,
                "substantive": counts["substantive"],
                "inline": counts["inline"],
                "deep": counts["deep"],
                "engaged": counts["engaged"],
                "mrs": len(mrs_seen[user]),
                "authors": len(authors_seen[user]),
                "top_areas": [area for area, _ in areas[user].most_common(4)],
                "samples": samples[user],
            }
        )
    rows.sort(key=lambda row: -row["deep"])
    os.makedirs(args.out_dir, mode=0o700, exist_ok=True)
    os.chmod(args.out_dir, 0o700)
    output_path = os.path.join(args.out_dir, "reviewers_%s.json" % args.project_id.replace("/", "_"))
    descriptor = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(output_path, 0o600)
    with os.fdopen(descriptor, "w") as output:
        json.dump(rows, output, indent=2)
    print("wrote %d candidates to %s" % (len(rows), output_path))


if __name__ == "__main__":
    main()
