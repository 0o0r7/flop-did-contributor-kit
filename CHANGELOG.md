# CHANGELOG

All notable changes to this fork are recorded in this file.

## [Unreleased] - Personalization by @0o0r7

### Added
- `scripts/healthcheck.py` — environment and server health checker
- `scripts/safe_post.py` — guarded wrapper for posting with quality checks and duplicate prevention
- `scripts/log_append.py` — CLI tool to append structured entries to CONTRIBUTION_LOG.md
- `scripts/review_contributions.py` — weekly audit helper (stdlib-only)
- `CONTRIBUTION_LOG.md` — enhanced log template and contribution rubric
- `AUTHORS.md`, `SECURITY.md` — ownership and security guidance
- `QUICKSTART_CONTRIBUTOR.md` — updated onboarding and rotation guidance
- `AUTHORS.md` and README updates to reflect fork identity and upstream attribution

### Changed
- `README.md` — rebranded title and intro, added Quick Start, Safe Posting Flow, Logging Flow, SEO-friendly keywords
- `.gitignore` — expanded to include common secret file patterns and editor/OS artifacts

### Security
- Enforced that `*.pem`, `*.key`, `.env`, and `.venv/` are ignored
- Removed insecure demo passphrase examples from docs

