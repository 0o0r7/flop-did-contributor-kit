#!/usr/bin/env python3
"""Append a standardized entry to CONTRIBUTION_LOG.md from CLI args
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

LOG = Path('CONTRIBUTION_LOG.md')


def build_entry(ts, did, room, seq, text, purpose, links, score):
    parts = [
        f"### {ts} UTC",
        "",
        f"- DID: `{did}`",
        f"- Room: `{room}`",
        f"- Sequence: `{seq}`",
        f"- Message summary: {text[:200]!r}",
        "- Full text:",
        "```",
        text,
        "```",
        f"- Problem addressed: -",
        f"- Why this helps ecosystem: -",
        f"- Outcome / feedback link: -",
        f"- Self-quality score (1-5): {score}",
        f"- Server posted metadata: -",
        f"- Links: {links or '-'}",
        f"- Purpose / value: {purpose or '-'}",
        f"- Follow-up: -",
        "",
        "---",
        "",
    ]
    return "\n".join(parts)


def parse_args():
    p = argparse.ArgumentParser(description='Append entry to CONTRIBUTION_LOG.md')
    p.add_argument('--room', required=True)
    p.add_argument('--seq', type=int, required=False)
    p.add_argument('--did', required=True)
    p.add_argument('--text', required=True)
    p.add_argument('--purpose')
    p.add_argument('--links')
    p.add_argument('--score', type=int, choices=range(1,6), required=False)
    return p.parse_args()


def main():
    args = parse_args()
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    score = args.score or '-'
    entry = build_entry(ts, args.did, args.room, args.seq or '-', args.text, args.purpose, args.links, score)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(entry)
    print(f"Appended entry to {LOG}")


if __name__ == '__main__':
    main()
