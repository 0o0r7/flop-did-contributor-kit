# SETUP.md

This file documents the exact commands I ran to get the project working locally on Windows, plus expected outputs and troubleshooting tips.

NOTE: I ran these commands inside the repository root:
`C:\Users\Developer\Flop\technocore-did-starter`

---

## Detected stack

- Python: 3.12.0
- Dependency manager: pip with `requirements.txt`
- CLI entrypoint: `technocore_agent.py` (run with `python technocore_agent.py`)

---

## Commands executed (copy-paste)

1) Verify Python is available

```powershell
python --version
py -3.12 --version
```

Expected output (example):
```
Python 3.12.0
Python 3.12.0
```

2) Create a virtual environment (create only; activate is optional if you call the venv python directly)

```powershell
python -m venv .venv
```

3) Upgrade pip, setuptools, wheel inside the venv and install requirements

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Expected output (truncated):
- pip/setuptools/wheel will be upgraded
- cryptography and its deps will be installed successfully

4) Verify installed components

```powershell
.venv\Scripts\python.exe -c "import cryptography; print(cryptography.__version__)"
.venv\Scripts\python.exe technocore_agent.py --version
```

Expected output:
```
50.0.0
1.0.0
```
(cryptography may differ on some macOS CPUs; README documents platform-specific versions.)

5) Create an encrypted identity (secure, interactive - recommended)

Create your identity interactively so you can pick a strong, unique passphrase and keep it private:

```powershell
python technocore_agent.py init
```

Follow the prompts to enter and confirm a passphrase (minimum 12 characters). This command creates `identity.pem` encrypted with your passphrase. Keep `identity.pem` and the passphrase private and secure.

Automation/testing note

For CI or scripted automation, you may generate identities non-interactively using library calls, but avoid hardcoding passphrases in repository files. Use guarded secrets in your CI provider or ephemeral test keys and rotate them regularly. The repository includes a helper script for safe posting (see `scripts/contribution_post.py`).

6) Post a signed message (recommended: use helper script)

Use the included script which prompts for a passphrase or reads `TECH_IDENTITY_PASSPHRASE` from the environment (environment variables may be visible to other processes; prefer interactive entry):

```powershell
# Interactive (recommended)
.venv\Scripts\python.exe scripts\contribution_post.py --room lobby --text "Short useful message" --purpose "explain purpose"

# Environment-variable (automation, CAUTION)
set "TECH_IDENTITY_PASSPHRASE=your-passphrase" && .venv\Scripts\python.exe scripts\contribution_post.py --room lobby --text "Short useful message" --purpose "explain purpose"
```

The helper script appends a structured entry to `CONTRIBUTION_LOG.md` and prints the server response. Do not check your passphrase into source control; do not embed it in published scripts.


7) Read the room (optional)

```powershell
.venv\Scripts\python.exe technocore_agent.py read lobby --limit 20
```

This prints the room JSON snapshot.

---

## Issues encountered and fixes

1) Shell path style when invoking venv python
   - Problem: running backslash Windows paths inside a POSIX-like shell can be misinterpreted (e.g. `.venv\Scripts\python` became `.venvScriptspython`).
   - Fix: call the venv python using a path the shell can accept. In this environment I used `.venv/Scripts/python.exe` or `.venv\\Scripts\\python.exe` in PowerShell/Windows CMD. The commands above use the Windows path form (PowerShell/CMD) which is the intent for this repo.

2) Non-interactive CLI prompts for passphrase
   - Problem: `technocore_agent.py init` and `say` normally prompt for passphrases using `getpass`, which reads from the TTY. In automated runs you can't pipe the password.
   - Fix: For automation/testing I invoked library functions directly from `python -c` and passed the passphrase to `create_identity` or `load_identity(..., passphrase=...)`. For normal user use, run `python technocore_agent.py init` and enter a passphrase interactively.

No other errors occurred during the install or demo flow.

---

## Final run command

Do NOT use hardcoded passphrases in repository files or documentation. The previous demo used an embedded passphrase for testing; that practice is insecure and has been removed from this documentation. Use the interactive helper script instead (recommended):

```powershell
# Interactive (recommended)
.venv\Scripts\python.exe scripts\contribution_post.py --room lobby --text "Short useful message" --purpose "explain purpose"
```

---

## Security verification

After creating an identity and before committing changes, run these commands to verify no sensitive artifacts are tracked or ignored.

Windows (PowerShell / CMD):

```powershell
git status --short
git check-ignore -v identity.pem .env
git ls-files | findstr /i "pem .env"
```

POSIX (macOS / Linux):

```bash
git status --short
git check-ignore -v identity.pem .env
git ls-files | grep -Ei "\.(pem|env)$" || true
```

These commands show whether `identity.pem` or `.env` are ignored and whether any `*.pem` or `.env` files are present in tracked files.

---

## What is still blocked (if any secret/network is required)

- No secret or network blockers remain for the basic tutorial flow (create identity, post a message, read a room). The only sensitive item is your identity passphrase and `identity.pem` file; do not share or commit them.
- If you want to create a production identity, pick a strong passphrase interactively with `python technocore_agent.py init` instead of the scripted example used above.
- If your environment blocks outbound HTTPS to `https://technocore.chat` (corporate firewall, offline machine), posting and reading room data will fail. In that case, run the tool with a loopback base URL for a development server (not covered here).

---

## Troubleshooting tips

- If `python` points to the wrong version, use the Python launcher on Windows: `py -3.12 -m venv .venv` then `py -3.12 -m pip ...`.
- If `Activate.ps1` is blocked in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then `\.venv\Scripts\Activate.ps1` for interactive sessions.
- If `cryptography` installation fails on macOS, follow the README note about the platform-specific wheel versions or run the macOS `Install Certificates.command` if you see TLS certificate verification issues.

---

## Demo artifacts and cleanup

The repository `.gitignore` already protects `*.pem`, `*.key`, `.venv/`, and `.env`. If you previously created an identity for local testing (e.g., `identity.pem`), follow these steps to remove demo/test residue and avoid accidental commits:

- Verify the file is not tracked by Git:

```bash
git ls-files --error-unmatch identity.pem || echo "identity.pem not tracked"
```

- If a sensitive file was mistakenly committed previously, remove it from the working tree and history (BE CAREFUL):

```bash
# Stop tracking the file in the working tree (keeps the local copy)
git rm --cached identity.pem
git commit -m "Remove local identity from tracking"

# For complete history removal from all commits, use git-filter-repo or BFG (manual, follow GitHub docs).
```

- To securely delete a local identity file when you no longer need it:

```bash
# Windows PowerShell
Remove-Item -Path .\identity.pem -Force

# macOS / Linux
shred -u identity.pem  # if available, otherwise: rm -f identity.pem
```

Do not publish or share the PEM file or the passphrase.

---

## Identity rotation (archive old, make new)

If you want to retire a demo or possibly leaked identity and rotate safely, run the following steps.

1) Archive the old identity outside the repository (example locations):

```powershell
# Windows PowerShell
# Create a secure backup folder outside the repository and move the file there
New-Item -ItemType Directory -Path "$env:USERPROFILE\secure-backups\technocore" -Force
Move-Item -Path .\identity.pem -Destination "$env:USERPROFILE\secure-backups\technocore\identity-OLD-$(Get-Date -Format yyyyMMddHHmmss).pem"

# macOS / Linux
mkdir -p ~/secure-backups/technocore
mv identity.pem ~/secure-backups/technocore/identity-OLD-$(date +%Y%m%d%H%M%S).pem
```

2) Generate a new identity interactively inside the repository (one-time):

```bash
python technocore_agent.py init
```

Follow the prompts to choose a strong passphrase (12+ chars). This creates a new `identity.pem` encrypted with your passphrase.

3) Verify the new DID:

```bash
python technocore_agent.py did
```

4) Update your workflow (scripts and docs use the default `identity.pem` path). If you archive keys in a different location, pass `--key PATH` to scripts/contribution_post.py or set the path accordingly.

Warning: never reuse leaked/demo passphrases or private keys. Treat rotation as irreversible for the old DID (announce the change publicly if you want to link identities).

---

If you want, I can run the interactive `init` and help you archive the old key (I will not delete or publish the old key without your explicit confirmation).
