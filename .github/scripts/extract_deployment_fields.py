#!/usr/bin/env python3
"""Parses a deployment-announcement issue body into a flat JSON array,
in the exact column order the Google Sheet expects (Timestamp and Email
Address are handled by the caller / the "Email Address" field below).
Field labels here must match .github/ISSUE_TEMPLATE/deployment-announcement.yml
exactly - matching is by heading text, not by field id.
"""
import json
import re
import sys

ORDER = [
    "Email Address",
    "Deployment Name / Release Name",
    "Release Info (summary)",
    "Severity/Impact",
    "Deployment Date",
    "Deployment Slot",
    "Deployment type",
    "Library / Package installation required?",
    "Config / Setting Changes required?",
    "Coordination required?",
    "Release Version / Commit ID",
    "Rollback Info",
    "API Deployment",
    "Celery Deployment",
    "Web Deployment",
    "Pre-deployment steps/instructions",
    "Post-Deployment steps/instructions",
    "Other comments (Deployment order etc.)",
]


CHECKBOX_LINE = re.compile(r"^- \[([xX ])\] (.+)$", re.M)


def collapse_checkboxes(value):
    """checkboxes fields render as a '- [x] label' list; keep only the
    checked labels, joined like the sheet's existing free-text format
    (e.g. "API - Marrow Web, API - Ikigai")."""
    matches = CHECKBOX_LINE.findall(value)
    if not matches:
        return value
    checked = [label.strip() for mark, label in matches if mark.strip().lower() == "x"]
    return ", ".join(checked)


def parse(body):
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    fields = {}
    it = iter(parts[1:])
    for heading, content in zip(it, it):
        value = content.strip()
        if value == "_No response_":
            value = ""
        fields[heading.strip()] = collapse_checkboxes(value)
    return fields


if __name__ == "__main__":
    body = sys.stdin.read()
    fields = parse(body)
    row = [fields.get(label, "") for label in ORDER]
    print(json.dumps(row))
