#!/usr/bin/env python3
"""Fail-fast OAuth/API preflight for non-EpicBharat production workflows.

Only checks credential presence and JSON shape. Never prints secret values,
writes credentials, uploads content, or calls external APIs.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

TOKEN_PATHS = {
    "buzzstorm": ROOT / "blog" / "credentials" / "blogger_token.json",
    "tiger": ROOT / "channels" / "TigerVlogs-2026" / "token.json",
    "indian-horror": ROOT / "channels" / "IndianHorrorTapes" / "token.json",
    "all-train": ROOT / "channels" / "AllTrainReels" / "token.json",
    "digital-immortals": ROOT / "channels" / "DigitalImmortals" / "token.json",
}

def parse_token(raw: str, label: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label} must contain a JSON object")
    if not data.get("refresh_token"):
        raise RuntimeError(f"{label} has no refresh_token; re-authenticate the intended channel")
    return data

def read_file(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing at {path.relative_to(ROOT)}")
    return parse_token(path.read_text(encoding="utf-8"), label)

def mindnest_token(lang: str) -> tuple[dict, str]:
    lang_path = ROOT / "channels" / "MindNestTales" / "credentials" / f"token_{lang}.json"
    if lang_path.is_file():
        return read_file(lang_path, f"MindNest {lang.upper()} token"), "language-specific file"

    bundle = os.environ.get("MINDNEST_ALL_TOKENS_JSON", "").strip()
    if bundle:
        try:
            values = json.loads(bundle)
        except json.JSONDecodeError as exc:
            raise RuntimeError("MINDNEST_ALL_TOKENS_JSON is not valid JSON") from exc
        if isinstance(values, dict) and lang in values:
            value = values[lang]
            raw = value if isinstance(value, str) else json.dumps(value)
            return parse_token(raw, f"MindNest {lang.upper()} bundled token"), "all-tokens bundle"

    raw = os.environ.get(f"MINDNEST_TOKEN_{lang.upper()}_JSON", "").strip()
    if raw:
        return parse_token(raw, f"MINDNEST_TOKEN_{lang.upper()}_JSON"), "language secret"

    # The scheduler also supports a shared token file/secret, but its runtime
    # channel-ID guard remains authoritative and can reject a wrong-channel token.
    fallback = ROOT / "channels" / "MindNestTales" / "token.json"
    if fallback.is_file():
        return read_file(fallback, "MindNest master token"), "master token (runtime channel-ID check required)"
    raw = os.environ.get("MINDNEST_TOKEN_JSON", "").strip()
    if raw:
        return parse_token(raw, "MINDNEST_TOKEN_JSON"), "master secret (runtime channel-ID check required)"
    raise RuntimeError(
        f"No OAuth token configured for MindNest {lang.upper()}. "
        f"Add MINDNEST_TOKEN_{lang.upper()}_JSON or include '{lang}' in MINDNEST_ALL_TOKENS_JSON."
    )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True, choices=sorted((*TOKEN_PATHS, "mindnest")))
    parser.add_argument("--language", help="MindNest language code")
    args = parser.parse_args()

    try:
        if args.channel == "digital-immortals":
            if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
                raise RuntimeError("ANTHROPIC_API_KEY is missing; script_gen requires Claude API access.")
            raw = os.environ.get("DIGITALIMMORTALS_TOKEN_JSON", "").strip()
            if raw:
                parse_token(raw, "DIGITALIMMORTALS_TOKEN_JSON")
                source = "DIGITALIMMORTALS_TOKEN_JSON"
            elif all(os.environ.get(k, "").strip() for k in ("YT_REFRESH_TOKEN", "YT_CLIENT_ID", "YT_CLIENT_SECRET")):
                source = "YT_REFRESH_TOKEN + OAuth client settings"
            else:
                raise RuntimeError(
                    "Upload is enabled but no complete YouTube OAuth configuration exists. "
                    "Provide DIGITALIMMORTALS_TOKEN_JSON or YT_REFRESH_TOKEN, YT_CLIENT_ID and YT_CLIENT_SECRET."
                )
        elif args.channel == "mindnest":
            if not args.language:
                raise RuntimeError("--language is required for MindNest preflight")
            _, source = mindnest_token(args.language)
        else:
            path = TOKEN_PATHS[args.channel]
            read_file(path, f"{args.channel} OAuth token")
            source = str(path.relative_to(ROOT))

        print(f"OAuth preflight passed for {args.channel}: credential source={source}")
        return 0
    except Exception as exc:
        print(f"::error::{exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
