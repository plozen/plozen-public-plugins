#!/usr/bin/env python3
"""Run the one-time interactive YouTube OAuth flow without printing tokens."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def path_value(raw: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    windows_match = re.match(r"^([A-Za-z]):[\\/](.*)$", expanded)
    if windows_match:
        drive, rest = windows_match.groups()
        return (Path("/mnt") / drive.lower() / rest.replace("\\", "/")).resolve()
    return Path(expanded).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-secrets", default=os.environ.get("YOUTUBE_CLIENT_SECRETS"), help="Local OAuth client-secret JSON path")
    parser.add_argument(
        "--token-file",
        default=os.environ.get("YOUTUBE_TOKEN_FILE", "~/.config/plozen/youtube-oauth.json"),
        help="Local ignored path for the refresh token JSON",
    )
    parser.add_argument("--port", type=int, default=0, help="Local callback port; 0 chooses a free port")
    args = parser.parse_args()
    if not args.client_secrets:
        print("ERROR: pass --client-secrets or set YOUTUBE_CLIENT_SECRETS", file=sys.stderr)
        return 2

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ModuleNotFoundError:
        print("ERROR: install scripts/requirements.txt before running OAuth", file=sys.stderr)
        return 2

    client_secrets = path_value(args.client_secrets)
    token_file = path_value(args.token_file)
    if not client_secrets.is_file():
        print(f"ERROR: OAuth client-secret file not found: {client_secrets}", file=sys.stderr)
        return 2
    token_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
        credentials = flow.run_local_server(port=args.port, access_type="offline", prompt="consent")
        token_file.write_text(credentials.to_json() + "\n", encoding="utf-8")
        token_file.chmod(0o600)
    except Exception as exc:  # OAuth libraries expose provider-specific exception types.
        print(f"ERROR: OAuth authorization failed ({type(exc).__name__})", file=sys.stderr)
        return 1

    print(f"OAuth token saved to: {token_file}")
    print("The token path is local-only; do not commit it or copy it into Vault.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
