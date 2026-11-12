"""Small command-line client for the Gemini Generate Content API.

Usage:
    python main.py "Explain recursion in one sentence"
    python main.py                 # prompts interactively
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from time import sleep
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-flash-lite-latest"


def load_dotenv(path: Path) -> None:
    """Load simple KEY=value entries without overwriting real environment values."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if key:
            os.environ.setdefault(key, value)


def generate(prompt: str, api_key: str, model: str) -> str:
    body = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]},
    ).encode("utf-8")
    request = Request(
        API_URL.format(model=model),
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    for attempt in range(3):
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.load(response)
            break
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(detail).get("error", {}).get("message", detail)
            except json.JSONDecodeError:
                message = detail
            if error.code in {429, 500, 503} and attempt < 2:
                sleep(2**attempt)
                continue
            raise RuntimeError(f"Gemini API returned HTTP {error.code}: {message}") from error
        except URLError as error:
            raise RuntimeError(f"Could not reach the Gemini API: {error.reason}") from error

    candidates = payload.get("candidates", [])
    if not candidates:
        reason = payload.get("promptFeedback", {}).get("blockReason", "no response candidates")
        raise RuntimeError(f"Gemini did not return text ({reason}).")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts)
    if not text:
        raise RuntimeError("Gemini returned a response with no text content.")
    return text


def main() -> int:
    load_dotenv(Path(__file__).with_name(".env"))
    parser = argparse.ArgumentParser(description="Send a prompt to Gemini.")
    parser.add_argument("prompt", nargs="*", help="Prompt text; omit for interactive input.")
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        help=f"Gemini model name (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Missing GEMINI_API_KEY. Add it to .env or set it as an environment variable.", file=sys.stderr)
        return 2

    prompt = " ".join(args.prompt).strip() if args.prompt else input("Prompt: ").strip()
    if not prompt:
        print("A prompt is required.", file=sys.stderr)
        return 2

    try:
        print(generate(prompt, api_key, args.model))
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
