# SECURITY

Reporting security issues

- If you discover a vulnerability or accidental secret exposure related to this
  repository, contact the maintainer @0o0r7 via a private channel (do not open a
  public issue with secrets).

What not to commit

- Never commit private keys, passphrases, `.env` files, or other secrets.
- This repository explicitly ignores `*.pem`, `*.key`, `.env`, and `.venv/`.

Key and passphrase handling checklist

- Create the identity interactively: `python technocore_agent.py init` and
  choose a unique passphrase (12+ characters).
- Do not store passphrases in repository files or public CI logs.
- Backup your `identity.pem` offline or in an encrypted password manager.
- If a key is suspected compromised, rotate the identity immediately and
  archive the old key outside the repository.

If a secret was accidentally committed

1. Remove it from the working tree: `git rm --cached path/to/secret` and commit.
2. To remove it from history, follow guidance for `git-filter-repo` or the BFG
   repo-cleaner. This is a sensitive, manual operation and may require
   coordination if the repository is public.

Contact

Maintainer: @0o0r7