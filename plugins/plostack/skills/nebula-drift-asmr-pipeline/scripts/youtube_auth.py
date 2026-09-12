#!/usr/bin/env python3
"""Run the one-time interactive YouTube OAuth flow without printing tokens."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def path_value(raw: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    windows_match = re.match(r"^([A-Za-z]):[\\/](.*)$", expanded)
    if windows_match:
        drive, rest = windows_match.groups()
        return (Path("/mnt") / drive.lower() / rest.replace("\\", "/")).resolve()
    return Path(expanded).resolve()


def load_client_config(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OAuth client-secret JSON is unreadable: {path}") from exc
    config = data.get("installed") or data.get("web")
    if not isinstance(config, dict):
        raise RuntimeError("OAuth client-secret JSON must contain an installed or web config")
    required = ("client_id", "client_secret", "auth_uri", "token_uri")
    if any(not isinstance(config.get(key), str) or not config[key] for key in required):
        raise RuntimeError("OAuth client-secret JSON is missing required fields")
    return {key: str(config[key]) for key in required}


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler.
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.callback_query = query  # type: ignore[attr-defined]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body><p>YouTube authorization received. You can close this window.</p></body></html>")

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def exchange_code(config: dict[str, str], code: str, redirect_uri: str) -> dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        config["token_uri"],
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "nebula-drift-asmr-pipeline"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OAuth token exchange failed ({type(exc).__name__})") from exc
    if not isinstance(result, dict) or not result.get("access_token") or not result.get("refresh_token"):
        raise RuntimeError("OAuth response did not include the required access and refresh tokens")
    return result


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

    client_secrets = path_value(args.client_secrets)
    token_file = path_value(args.token_file)
    if not client_secrets.is_file():
        print(f"ERROR: OAuth client-secret file not found: {client_secrets}", file=sys.stderr)
        return 2

    try:
        config = load_client_config(client_secrets)
        callback_server = HTTPServer(("127.0.0.1", args.port), CallbackHandler)
        callback_server.timeout = 300
        redirect_uri = f"http://localhost:{callback_server.server_port}/"
        state = secrets.token_urlsafe(32)
        authorization_url = "{}?{}".format(
            config["auth_uri"],
            urllib.parse.urlencode(
                {
                    "client_id": config["client_id"],
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": SCOPE,
                    "access_type": "offline",
                    "prompt": "consent",
                    "state": state,
                }
            ),
        )
        print("Open this URL in the user-visible browser to authorize YouTube upload:")
        print(authorization_url)
        webbrowser.open(authorization_url)
        callback_server.handle_request()
        callback_server.server_close()
        query = getattr(callback_server, "callback_query", {})
        if query.get("state", [None])[0] != state:
            raise RuntimeError("OAuth callback state did not match")
        if query.get("error"):
            raise RuntimeError(f"OAuth authorization was denied ({query['error'][0]})")
        code = query.get("code", [None])[0]
        if not code:
            raise RuntimeError("OAuth callback did not include an authorization code")
        token = exchange_code(config, code, redirect_uri)
        token.update(
            {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "token_uri": config["token_uri"],
                "scope": SCOPE,
                "created_at": int(time.time()),
                "expires_at": int(time.time()) + int(token.get("expires_in", 3600)),
            }
        )
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(json.dumps(token, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        token_file.chmod(0o600)
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"OAuth token saved to: {token_file}")
    print("The token path is local-only; do not commit it or copy it into Vault.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
