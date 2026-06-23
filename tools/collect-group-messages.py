#!/usr/bin/env python3
"""Non-AI collector for OpenClaw WhatsApp group messages.

This script archives raw gateway log entries for a configured WhatsApp group into
repo-local JSONL files without calling any AI model. It is designed for low-cost
periodic cron/systemd usage.

Default output:
  raw/whatsapp/YYYY-MM-DD.jsonl
  state/collector-state.json

Usage:
  python3 tools/collect-group-messages.py
  python3 tools/collect-group-messages.py --limit 5000 --max-bytes 1000000

Exit codes:
  0 success, including no new messages
  1 collector error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_GROUP = "6285259199495-1496927635@g.us"
STATE_PATH = REPO / "state" / "collector-state.json"
RAW_DIR = REPO / "raw" / "whatsapp"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--group", default=DEFAULT_GROUP)
    p.add_argument("--limit", type=int, default=5000)
    p.add_argument("--max-bytes", type=int, default=1_000_000)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def run_openclaw_logs(limit: int, max_bytes: int) -> str:
    cmd = [
        os.environ.get("OPENCLAW_BIN", "/root/.nvm/versions/node/v22.22.1/bin/openclaw"),
        "logs",
        "--limit",
        str(limit),
        "--max-bytes",
        str(max_bytes),
        "--plain",
        "--no-color",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "openclaw logs failed").strip())
    return proc.stdout


def extract_json_objects(line: str) -> list[dict[str, Any]]:
    objs: list[dict[str, Any]] = []
    # Current plain logs use simple one-level JSON objects. Keep parser conservative.
    for raw in re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", line):
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        if isinstance(obj, dict):
            objs.append(obj)
    return objs


def parse_line(line: str, group: str) -> dict[str, Any] | None:
    if group not in line:
        return None
    objs = extract_json_objects(line)
    data = None
    for obj in reversed(objs):
        # Strict mode: archive only real inbound records whose sender/chat is the target group.
        # Do not archive private chats that merely mention the group JID in text.
        if obj.get("from") == group or obj.get("chatId") == group:
            if "body" in obj or "timestamp" in obj or "from" in obj:
                data = obj
                break
    if not data:
        return None

    body = str(data.get("body") or data.get("text") or "")
    ts_ms = data.get("timestamp")
    ts_iso = None
    local_date = datetime.now(timezone.utc).date().isoformat()
    if isinstance(ts_ms, (int, float)) and ts_ms:
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        ts_iso = dt.isoformat()
        local_date = dt.date().isoformat()

    sender = (
        data.get("participant")
        or data.get("senderId")
        or data.get("sender")
        or data.get("author")
        or data.get("pushName")
        or None
    )
    event = {
        "schema": "rekap-crew.whatsapp.raw.v1",
        "group": group,
        "timestamp_ms": ts_ms,
        "timestamp_utc": ts_iso,
        "date_utc": local_date,
        "sender": sender,
        "sender_available": bool(sender),
        "from": data.get("from"),
        "to": data.get("to"),
        "body": body,
        "raw": data,
    }
    stable = json.dumps({
        "group": group,
        "timestamp_ms": ts_ms,
        "from": data.get("from"),
        "to": data.get("to"),
        "body": body,
        "sender": sender,
    }, ensure_ascii=False, sort_keys=True)
    event["id"] = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:24]
    return event


def load_seen() -> set[str]:
    if not STATE_PATH.exists():
        return set()
    try:
        data = json.loads(STATE_PATH.read_text())
        return set(data.get("seen_ids") or [])
    except Exception:
        return set()


def save_seen(seen: set[str], added: int) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Keep state bounded; raw jsonl remains source of truth.
    keep = sorted(seen)[-5000:]
    STATE_PATH.write_text(json.dumps({
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "seen_ids": keep,
        "last_added": added,
    }, indent=2), encoding="utf-8")


def append_event(event: dict[str, Any]) -> None:
    date = event.get("date_utc") or datetime.now(timezone.utc).date().isoformat()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{date}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    try:
        output = run_openclaw_logs(args.limit, args.max_bytes)
        seen = load_seen()
        added = 0
        candidates = 0
        for line in output.splitlines():
            event = parse_line(line, args.group)
            if not event:
                continue
            candidates += 1
            eid = str(event["id"])
            if eid in seen:
                continue
            if not args.dry_run:
                append_event(event)
                seen.add(eid)
            added += 1
        if not args.dry_run:
            save_seen(seen, added)
        print(json.dumps({"ok": True, "group": args.group, "candidates": candidates, "added": added, "dry_run": args.dry_run}, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
