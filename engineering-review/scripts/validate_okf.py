#!/usr/bin/env python3
"""Validate the engineering-review knowledge directory as an OKF v0.1 bundle."""
import os
import re
import sys

TYPES = {"index", "log", "reviewer", "team-principle", "surface", "conventions", "corpus"}
RECOMMENDED = ["title", "description", "tags", "timestamp"]
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def main():
    skill = sys.argv[1] if len(sys.argv) > 1 else "."
    knowledge = os.path.join(skill, "knowledge")
    errors = []
    warnings = []
    files = []

    if not os.path.isdir(knowledge):
        print("knowledge: no local model found; nothing to validate")
        return 0

    for root, dirs, names in os.walk(knowledge):
        dirs[:] = [directory for directory in dirs if not directory.startswith(".")]
        markdown = [name for name in names if name.endswith(".md")]
        if markdown and "index.md" not in markdown and root != knowledge:
            errors.append("%s: directory has no index.md" % os.path.relpath(root, skill))
        files.extend(os.path.join(root, name) for name in sorted(markdown))

    if files and not os.path.isfile(os.path.join(knowledge, "index.md")):
        errors.append("knowledge: populated bundle has no index.md")

    for path in files:
        relative = os.path.relpath(path, skill)
        with open(path) as source:
            text = source.read()
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            errors.append("%s: missing YAML frontmatter" % relative)
            continue
        if frontmatter.get("type") not in TYPES:
            errors.append("%s: missing or unknown type '%s'" % (relative, frontmatter.get("type")))
        for field in RECOMMENDED:
            if field not in frontmatter:
                warnings.append("%s: missing recommended field '%s'" % (relative, field))
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = target.split("#")[0]
            if target_path and not os.path.exists(
                os.path.normpath(os.path.join(os.path.dirname(path), target_path))
            ):
                errors.append("%s: broken link -> %s" % (relative, target))

    print("OKF bundle: %s" % os.path.relpath(knowledge, skill))
    print("concepts: %d" % len(files))
    for warning in warnings:
        print("WARN", warning)
    for error in errors:
        print("ERR ", error)
    if errors:
        return 1
    print("valid: frontmatter types and relative links are valid")
    print("note: this is structural validation only; review publishable content for privacy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
