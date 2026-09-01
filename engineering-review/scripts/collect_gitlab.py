#!/usr/bin/env python3
"""Collect GitLab MR discussions for configured reviewers.

Required environment variables:
    ER_GITLAB_URL=https://gitlab.example.com
    ER_PROJECTS=123,456
    ER_USERS=alice,bob
    GITLAB_TOKEN=...

Optional:
    ER_SINCE=2025-01-01T00:00:00Z

Usage:
    python3 collect_gitlab.py [OUT_DIR]

OUT_DIR defaults to this skill's gitignored evidence/gitlab directory and must
remain under evidence/ because the output contains private review content.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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
OUT_DIR = os.path.realpath(
    sys.argv[1] if len(sys.argv) > 1 else os.path.join(EVIDENCE_DIR, "gitlab")
)
if os.path.commonpath((EVIDENCE_DIR, OUT_DIR)) != EVIDENCE_DIR:
    raise SystemExit("OUT_DIR must be inside %s" % EVIDENCE_DIR)
SINCE = os.environ.get("ER_SINCE", "2025-01-01T00:00:00Z")
USERS = set(filter(None, (u.strip() for u in required("ER_USERS").split(","))))
PROJECT_IDS = set(filter(None, (p.strip() for p in required("ER_PROJECTS").split(","))))


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        old = urllib.parse.urlsplit(request.full_url)
        new = urllib.parse.urlsplit(new_url)
        if (old.scheme, old.netloc) != (new.scheme, new.netloc):
            raise urllib.error.HTTPError(new_url, code, "cross-origin redirect refused", headers, fp)
        return super().redirect_request(request, fp, code, message, headers, new_url)


OPENER = urllib.request.build_opener(SameOriginRedirect())


def private_open(path):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(path, 0o600)
    return os.fdopen(descriptor, "w")


def get(path, params=None, retries=4):
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


def list_all(path, params):
    results = []
    params = dict(params, per_page=100)
    page = 1
    while True:
        params["page"] = page
        data, headers = get(path, params)
        if not data:
            break
        results.extend(data)
        next_page = headers.get("X-Next-Page") or headers.get("x-next-page")
        if not next_page:
            break
        page = int(next_page)
    return results


def project_name(project_id):
    data, _ = get("projects/%s" % urllib.parse.quote(project_id, safe=""))
    return (data or {}).get("path_with_namespace") or project_id


def list_merge_requests():
    futures = []
    merge_requests = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        for project_id in PROJECT_IDS:
            for user in USERS:
                base = {"updated_after": SINCE, "state": "all"}
                path = "projects/%s/merge_requests" % urllib.parse.quote(project_id, safe="")
                futures.append(pool.submit(list_all, path, dict(base, reviewer_username=user)))
                futures.append(
                    pool.submit(list_all, path, dict(base, **{"approved_by_usernames[]": user}))
                )
        for future in as_completed(futures):
            for mr in future.result() or []:
                merge_requests[(str(mr["project_id"]), mr["iid"])] = mr
    return merge_requests


def fetch_discussions(project_id, iid):
    path = "projects/%s/merge_requests/%d/discussions" % (
        urllib.parse.quote(project_id, safe=""),
        iid,
    )
    return project_id, iid, list_all(path, {})


def main():
    os.makedirs(OUT_DIR, mode=0o700, exist_ok=True)
    os.chmod(OUT_DIR, 0o700)
    names = {project_id: project_name(project_id) for project_id in PROJECT_IDS}
    merge_requests = list_merge_requests()

    mrs_path = os.path.join(OUT_DIR, "mrs.jsonl")
    mrs_tmp = mrs_path + ".tmp"
    kept = 0
    notes_path = os.path.join(OUT_DIR, "notes.jsonl")
    notes_tmp = notes_path + ".tmp"
    try:
        with private_open(mrs_tmp) as output:
            for (project_id, iid), mr in sorted(merge_requests.items()):
                output.write(
                    json.dumps(
                        {
                            "project": names.get(project_id, project_id),
                            "project_id": project_id,
                            "iid": iid,
                            "title": mr.get("title"),
                            "description": mr.get("description"),
                            "state": mr.get("state"),
                            "author": (mr.get("author") or {}).get("username"),
                            "reviewers": [r["username"] for r in mr.get("reviewers") or []],
                            "created_at": mr.get("created_at"),
                            "merged_at": mr.get("merged_at"),
                            "web_url": mr.get("web_url"),
                            "labels": mr.get("labels"),
                            "target_branch": mr.get("target_branch"),
                        }
                    )
                    + "\n"
                )

        with private_open(notes_tmp) as output, ThreadPoolExecutor(max_workers=16) as pool:
            futures = [
                pool.submit(fetch_discussions, project_id, iid)
                for project_id, iid in merge_requests
            ]
            for future in as_completed(futures):
                project_id, iid, discussions = future.result()
                mr = merge_requests[(project_id, iid)]
                for discussion in discussions or []:
                    notes = discussion.get("notes") or []
                    if not any((n.get("author") or {}).get("username") in USERS for n in notes):
                        continue
                    thread = []
                    for note in notes:
                        position = note.get("position") or {}
                        thread.append(
                            {
                                "author": (note.get("author") or {}).get("username"),
                                "system": note.get("system"),
                                "created_at": note.get("created_at"),
                                "resolved": note.get("resolved"),
                                "resolvable": note.get("resolvable"),
                                "resolved_by": (note.get("resolved_by") or {}).get("username"),
                                "body": note.get("body"),
                                "file": position.get("new_path") or position.get("old_path"),
                                "line": position.get("new_line") or position.get("old_line"),
                            }
                        )
                    if all(note["system"] for note in thread):
                        continue
                    kept += 1
                    output.write(
                        json.dumps(
                            {
                                "project": names.get(project_id, project_id),
                                "iid": iid,
                                "mr_title": mr.get("title"),
                                "mr_author": (mr.get("author") or {}).get("username"),
                                "mr_state": mr.get("state"),
                                "web_url": mr.get("web_url"),
                                "discussion_id": discussion.get("id"),
                                "notes": thread,
                            }
                        )
                        + "\n"
                    )
        os.replace(mrs_tmp, mrs_path)
        os.replace(notes_tmp, notes_path)
    except BaseException:
        for temporary in (mrs_tmp, notes_tmp):
            try:
                os.remove(temporary)
            except FileNotFoundError:
                pass
        raise
    sys.stderr.write("done: %d MRs, %d threads kept\n" % (len(merge_requests), kept))


if __name__ == "__main__":
    main()
