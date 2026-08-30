#!/usr/bin/env python3
"""Post a signed Technocore message and append a structured entry to CONTRIBUTION_LOG.md

Usage examples:
  # Interactive prompt for passphrase (recommended)
  .venv\Scripts\python.exe scripts\contribution_post.py --room lobby --text "Short helpful message" --purpose "announce update"

  # Use environment variable (CAUTION: env var may be visible in process lists)
  set "TECH_IDENTITY_PASSPHRASE=your-passphrase" && .venv\Scripts\python.exe scripts\contribution_post.py --room lobby --text "Short message" --purpose "automation test"

Notes:
- This script never writes your passphrase to disk.
- Prefer interactive passphrase entry. Use TECH_IDENTITY_PASSPHRASE only for automation where you understand the OPSEC implications.
"""
from __future__ import annotations

import argparse
import datetime
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path when the script is executed from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from technocore_agent import load_identity, post_signed_message, did_from_private_key


def append_log(entry: str, path: Path = Path("CONTRIBUTION_LOG.md")) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(entry)


def build_entry(
    ts: str,
    did: str,
    room: str,
    seq: int | None,
    text: str,
    purpose: str | None,
    links: str | None,
    followup: str | None,
    server_posted: Any,
    problem: str | None = None,
    why: str | None = None,
    outcome: str | None = None,
    score: int | None = None,
) -> str:
    summary = (text[:200] + ("…" if len(text) > 200 else "")) if text else ""
    posted_json = json.dumps(server_posted, ensure_ascii=False)
    parts = [
        f"### {ts} UTC",
        "",
        f"- DID: `{did}`",
        f"- Room: `{room}`",
        f"- Sequence: `{seq}`",
        f"- Message summary: {summary!r}",
        "- Full text:",
        "```",
        text,
        "```",
        f"- Problem addressed: {problem or '-'}",
        f"- Why this helps ecosystem: {why or '-'}",
        f"- Outcome / feedback link: {outcome or '-'}",
        f"- Self-quality score (1-5): {score or '-'}",
        f"- Server posted metadata: `{posted_json}`",
        f"- Links: {links or '-'}",
        f"- Purpose / value: {purpose or '-'}",
        f"- Follow-up: {followup or '-'}",
        "",
        "---",
        "",
    ]
    return "\n".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post a signed Technocore message and log it")
    parser.add_argument("--key", type=Path, default=Path("identity.pem"), help="Path to encrypted identity PEM")
    parser.add_argument("--room", required=True, help="Technocore room name (e.g. lobby)")
    parser.add_argument("--text", required=True, help="Message text to post (keep it useful and non-spam)")
    parser.add_argument("--base-url", default="https://technocore.chat", help="Technocore base URL")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout seconds")
    parser.add_argument("--purpose", help="Short note about the purpose or value of this post")
    parser.add_argument("--links", help="Comma-separated public links related to this contribution")
    parser.add_argument("--followup", help="Planned follow-up tasks or notes")
    parser.add_argument("--problem", help="Short description: problem addressed")
    parser.add_argument("--why", help="Why this helps the ecosystem")
    parser.add_argument("--outcome", help="Outcome or feedback link")
    parser.add_argument("--score", type=int, choices=range(1,6), help="Self-quality score (1-5)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    key_path: Path = args.key.expanduser().resolve()
    if not key_path.exists():
        print(f"error: identity not found at {key_path}. Create one with: python technocore_agent.py init", file=sys.stderr)
        return 2

    env_pass = os.getenv("TECH_IDENTITY_PASSPHRASE")
    if env_pass:
        # Warn about env var use
        print("Warning: using TECH_IDENTITY_PASSPHRASE environment variable. Ensure you understand OPSEC implications.")
        passphrase = env_pass.encode("utf-8")
    else:
        entered = getpass.getpass(f"Passphrase for {key_path}: ")
        passphrase = entered.encode("utf-8")

    # Load private key
    try:
        private_key = load_identity(key_path, passphrase, allow_prompt=False)
    except Exception as e:
        print(f"error: failed to load identity: {e}", file=sys.stderr)
        return 3

    # Post message
    try:
        response = post_signed_message(private_key, args.room, args.text, base_url=args.base_url, timeout=args.timeout)
    except Exception as e:
        print(f"error: failed to post message: {e}", file=sys.stderr)
        return 4

    posted = response.get("posted") or {}
    did = posted.get("from") or did_from_private_key(private_key)
    seq = posted.get("seq")
    ts = posted.get("ts") or datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    entry = build_entry(
        ts,
        did,
        args.room,
        seq,
        args.text,
        args.purpose,
        args.links,
        args.followup,
        posted,
        problem=args.problem,
        why=args.why,
        outcome=args.outcome,
        score=args.score,
    )
    append_log(entry)

    print(json.dumps(response, ensure_ascii=False, indent=2))
    print(f"Appended contribution entry to CONTRIBUTION_LOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
