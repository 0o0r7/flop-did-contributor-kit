#!/usr/bin/env python3
"""Guarded posting wrapper around technocore_agent.post_signed_message

Enforces quality guardrails and prevents immediate duplicate postings.
Stores a small local cache at .cache/recent_posts.json
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Ensure repo root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from technocore_agent import load_identity, post_signed_message, did_from_private_key

CACHE = Path('.cache')
CACHE_FILE = CACHE / 'recent_posts.json'
MIN_LEN = 40
MAX_CACHE = 50


def load_cache():
    if not CACHE_FILE.exists():
        return []
    try:
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return []


def save_cache(entries):
    CACHE.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(entries[-MAX_CACHE:], ensure_ascii=False), encoding='utf-8')


def is_duplicate(text, entries):
    norm = ' '.join(text.split()).strip().lower()
    for e in entries:
        if e.get('text','').strip().lower() == norm:
            return True
    return False


def parse_args():
    p = argparse.ArgumentParser(description='Safely post a Technocore message with guardrails')
    p.add_argument('--room', required=True)
    p.add_argument('--text', required=True)
    p.add_argument('--key', default=Path('identity.pem'), type=Path)
    p.add_argument('--timeout', type=float, default=20.0)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--purpose', help='Short purpose note appended to message')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    text = args.text.strip()
    if len(text) < MIN_LEN:
        print(f"error: message too short (min {MIN_LEN} characters)", file=sys.stderr)
        return 2

    entries = load_cache()
    if is_duplicate(text, entries):
        print("error: duplicate message detected in recent cache; aborting", file=sys.stderr)
        return 3

    full_text = text
    if args.purpose:
        full_text = f"{text}\n\n[ purpose: {args.purpose} ]"

    if args.dry_run:
        print("DRY RUN - validated message would be posted:")
        print(full_text)
        return 0

    # prompt for passphrase
    env_pass = os.getenv('TECH_IDENTITY_PASSPHRASE')
    if env_pass:
        passphrase = env_pass.encode('utf-8')
    else:
        entered = getpass.getpass('Passphrase for identity.pem: ')
        passphrase = entered.encode('utf-8')

    try:
        private_key = load_identity(args.key, passphrase, allow_prompt=False)
    except Exception as e:
        print(f"error: cannot load identity: {e}", file=sys.stderr)
        return 4

    try:
        response = post_signed_message(private_key, args.room, full_text, base_url='https://technocore.chat', timeout=args.timeout)
    except Exception as e:
        print(f"error: failed to post message: {e}", file=sys.stderr)
        return 5

    posted = response.get('posted') or {}
    entry = {'ts': posted.get('ts') or time.strftime('%Y-%m-%dT%H:%M:%SZ'), 'room': args.room, 'text': text}
    entries.append(entry)
    save_cache(entries)

    print(json.dumps(response, ensure_ascii=False, indent=2))
    print('Posted and cached locally')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
