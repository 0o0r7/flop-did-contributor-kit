#!/usr/bin/env python3
"""Weekly review helper for CONTRIBUTION_LOG.md

Outputs:
- count by week (ISO year-week)
- count by room
- average self-quality score
- duplicate/similar message warnings (exact-match and case-insensitive duplicates)
- entries missing links or follow-up

Usage:
  .venv\Scripts\python.exe scripts\review_contributions.py
"""
from __future__ import annotations

import collections
import datetime
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

LOG = Path("CONTRIBUTION_LOG.md")
ENTRY_SEP = re.compile(r"^---\s*$", re.MULTILINE)
TS_HEADER = re.compile(r"^###\s+(?P<ts>[^\s]+)\s+UTC", re.IGNORECASE)
FIELD_RE = re.compile(r"^-\s*(?P<key>[^:]+):\s*(?P<value>.*)$")


def read_entries() -> List[str]:
    if not LOG.exists():
        return []
    text = LOG.read_text(encoding="utf-8")
    # Split on '---' separators; keep parts that contain a timestamp header
    parts = ENTRY_SEP.split(text)
    entries = [p.strip() for p in parts if p.strip() and '###' in p]
    return entries


def parse_entry_block(block: str) -> Dict[str, Optional[str]]:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    result: Dict[str, Optional[str]] = {"raw": block}
    # find timestamp
    for line in lines:
        m = TS_HEADER.match(line)
        if m:
            result["ts"] = m.group("ts")
            break
    # parse simple - Key: value lines
    for line in lines:
        m = FIELD_RE.match(line)
        if m:
            key = m.group("key").strip().lower()
            val = m.group("value").strip()
            result[key] = val
    # extract full text block between ``` fences
    if '```' in block:
        between = re.search(r"```\n(.*?)\n```", block, re.DOTALL)
        if between:
            result['full_text'] = between.group(1).strip()
    return result


def iso_week(ts: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(ts.replace('Z',''))
    except Exception:
        return 'unknown'
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


def analyze(entries: List[Dict[str, Optional[str]]]):
    by_week = collections.Counter()
    by_room = collections.Counter()
    scores = []
    text_seen = collections.Counter()
    missing_links = []
    missing_followup = []

    for e in entries:
        ts = e.get('ts') or ''
        week = iso_week(ts) if ts else 'unknown'
        by_week[week] += 1
        room = (e.get('room') or '').strip('`')
        by_room[room or 'unknown'] += 1
        score_val = e.get('self-quality score (1-5)') or e.get('self-quality score') or '-'
        try:
            score_int = int(score_val)
            scores.append(score_int)
        except Exception:
            pass
        text = (e.get('full_text') or '').strip()
        key = text.lower()
        if key:
            text_seen[key] += 1
        links = e.get('links') or '-'
        if links.strip() in ('', '-', None):
            missing_links.append(e.get('ts') or 'unknown')
        follow = e.get('follow-up') or e.get('followup') or '-'
        if follow.strip() in ('', '-', None):
            missing_followup.append(e.get('ts') or 'unknown')

    avg_score = (sum(scores) / len(scores)) if scores else None

    print("Weekly review summary:\n")
    print("Entries by week:")
    for k, v in sorted(by_week.items()):
        print(f"  {k}: {v}")
    print("\nEntries by room:")
    for k, v in sorted(by_room.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {k or 'unknown'}: {v}")
    print('\nAverage self-quality score:', f"{avg_score:.2f}" if avg_score is not None else 'n/a')

    print('\nPotential duplicate or repeated messages:')
    duplicates = [(t, c) for t, c in text_seen.items() if c > 1]
    if duplicates:
        for t, c in duplicates:
            print(f"  {c}x: {repr(t[:80])}")
    else:
        print("  none detected")

    print('\nEntries missing links:', len(missing_links))
    if missing_links:
        for ts in missing_links:
            print(f"  missing links at: {ts}")

    print('\nEntries missing follow-up:', len(missing_followup))
    if missing_followup:
        for ts in missing_followup:
            print(f"  missing follow-up at: {ts}")


if __name__ == '__main__':
    raw = read_entries()
    parsed = [parse_entry_block(p) for p in raw]
    analyze(parsed)
