# QUICKSTART_CONTRIBUTOR.md

Short, copy-paste commands for daily contributor workflow. Run these from the repository root.

1) Activate your virtual environment (Windows PowerShell)

```powershell
Set-Location C:\path\to\technocore-did-starter
.venv\Scripts\Activate.ps1
```

(Or on Command Prompt)

```bat
.venv\Scripts\activate.bat
```

(Or on macOS / Linux)

```bash
source .venv/bin/activate
```

2) Create your identity (one-time, interactive)

```bash
python technocore_agent.py init
```

Follow the interactive prompts and choose a strong passphrase. Do not reuse passphrases from other services.

3) Post a contribution (interactive passphrase prompt)

```bash
python scripts/contribution_post.py --room lobby --text "Short useful message explaining what you did and why it's helpful" --purpose "short purpose note" --links "https://example.com/report"
```

4) Confirm the log entry

```bash
git status --short
# Open CONTRIBUTION_LOG.md or:
less CONTRIBUTION_LOG.md
```

Notes:
- Use the `--links`, `--purpose`, and `--followup` flags to add context for reviewers.
- For automation, set the `TECH_IDENTITY_PASSPHRASE` env var before running the script. Be aware of OPSEC tradeoffs.

WARNING: Never reuse leaked, demo, or otherwise compromised credentials. If you believe your passphrase or `identity.pem` was exposed, rotate your identity immediately (archive the old key outside the repo and generate a new one). See the Identity Rotation section below.

Identity rotation (one-time if you need to rotate)

1) Archive the old identity file outside this repository (example):

```powershell
# Windows PowerShell
Move-Item -Path .\identity.pem -Destination C:\secure-backups\technocore\identity-OLD.pem

# macOS / Linux
mkdir -p ~/secure-backups/technocore && mv identity.pem ~/secure-backups/technocore/identity-OLD.pem
```

2) Generate a new identity interactively (inside the repo):

```bash
python technocore_agent.py init
```

3) Verify the new DID:

```bash
python technocore_agent.py did
```

After rotation, use the new `identity.pem` for all routine posts.

Pre-post checklist

Before you post, confirm all of the following:

- Is this message useful to other participants (bug report, clarification, data, link)?
- Is this not a duplicate of something you or others already posted?
- Is the message specific, actionable, and concise?
- Does it include links to public artifacts (if relevant) and enough context to verify?
- Will this post add long-term value rather than noisy repetition?

Recommended cadence and anti-spam guidance

- Favor consistent, thoughtful contributions (e.g., 1-3 high-quality posts per week) over high-volume posting.
- Do not post identical content to multiple rooms or accounts. Avoid short/empty posts like "+1" or "nice".
- If unsure whether something is appropriate, ask for review or post in a dedicated discussion space first.

