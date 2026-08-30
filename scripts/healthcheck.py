#!/usr/bin/env python3
"""Healthcheck for environment and Technocore server

Outputs a simple PASS/WARN/FAIL table and exits non-zero on FAIL.
"""
from __future__ import annotations

import json
import socket
import sys
import urllib.request
from pathlib import Path

MIN_PY = (3, 12)
REQUIRED_PKGS = ("cryptography",)
DEFAULT_BASE_URL = "https://technocore.chat"


def check_python_version():
    ok = sys.version_info >= MIN_PY
    return ("Python version", f"{sys.version.split()[0]}", "PASS" if ok else "FAIL")


def check_venv_active():
    # Heuristic: if sys.prefix contains '.venv' or a venv folder exists and matches
    prefix = sys.prefix or ""
    venv_path = Path(".venv").resolve()
    active = ".venv" in prefix or venv_path.exists() and prefix.startswith(str(venv_path))
    return ("Virtual environment active", prefix, "PASS" if active else "WARN")


def check_packages():
    missing = []
    for pkg in REQUIRED_PKGS:
        try:
            __import__(pkg)
        except Exception:
            missing.append(pkg)
    status = "PASS" if not missing else "FAIL"
    return ("Required packages", ", ".join(REQUIRED_PKGS) if not missing else "missing: " + ", ".join(missing), status)


def check_identity_exists():
    exists = Path("identity.pem").exists()
    return ("Identity file", "identity.pem present" if exists else "identity.pem missing", "PASS" if exists else "WARN")


def check_env_file():
    exists = Path(".env").exists()
    return (".env file", ".env present" if exists else ".env missing", "WARN" if exists else "PASS")


def check_server_reachable(timeout=5.0):
    try:
        with urllib.request.urlopen(f"{DEFAULT_BASE_URL}/r/lobby?format=json", timeout=timeout) as resp:
            if resp.status == 200:
                return ("Technocore server", f"{DEFAULT_BASE_URL} reachable", "PASS")
            return ("Technocore server", f"{DEFAULT_BASE_URL} returned {resp.status}", "WARN")
    except Exception as e:
        return ("Technocore server", f"unreachable: {e}", "WARN")


def main():
    checks = [
        check_python_version(),
        check_venv_active(),
        check_packages(),
        check_identity_exists(),
        check_env_file(),
        check_server_reachable(),
    ]

    print("Healthcheck results:\n")
    fail = False
    for name, detail, status in checks:
        print(f"{name:25} {status:5}  - {detail}")
        if status == "FAIL":
            fail = True
    print()
    if fail:
        sys.exit(2)
    sys.exit(0)


if __name__ == '__main__':
    main()
