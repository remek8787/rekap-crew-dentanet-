#!/usr/bin/env python3
"""Extract maintenance schedule messages from OpenClaw gateway logs.

Usage:
  openclaw logs --limit 20000 --max-bytes 10000000 --plain --no-color \
    | python3 tools/extract-maintenance-log.py --group 6285259199495-1496927635@g.us

Notes:
- Gateway `web-inbound` plain logs may include only group id, body, and timestamp.
- If participant/senderId is absent in the log line, this script leaves sender as unknown
  instead of guessing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--group", required=True, help="WhatsApp group JID, e.g. 628...@g.us")
    p.add_argument("--contains", default="Maintenance", help="Body keyword filter")
    return p.parse_args()


def extract_json_after_module(line: str) -> dict | None:
    # Plain OpenClaw log shape often contains two JSON objects; the second one is message data.
    # Example: ... {"module":"web-inbound"} {"from":"...","body":"..."} inbound message
    objs = re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", line)
    for raw in reversed(objs):
        try:
            data = json.loads(raw)
        except Exception:
            continue
        if "body" in data or "from" in data:
            return data
    return None


def normalize_ts(ms: int | None) -> str:
    if not ms:
        return "-"
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return str(ms)


def main() -> int:
    args = parse_args()
    keyword = args.contains.lower()
    found = 0
    for line in sys.stdin:
        if args.group not in line:
            continue
        data = extract_json_after_module(line)
        if not data:
            continue
        body = str(data.get("body") or "")
        if keyword and keyword not in body.lower():
            continue
        found += 1
        sender = data.get("participant") or data.get("senderId") or data.get("sender") or data.get("author") or "UNKNOWN_PARTICIPANT_NOT_IN_LOG"
        print(f"--- message {found} ---")
        print(f"group: {data.get('from') or args.group}")
        print(f"sender: {sender}")
        print(f"timestamp_utc: {normalize_ts(data.get('timestamp'))}")
        print("body:")
        print(body)
        print()
    if found == 0:
        print("No matching maintenance messages found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
