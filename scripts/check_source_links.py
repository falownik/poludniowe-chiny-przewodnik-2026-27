from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def walk_urls(value: Any, source: str) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "url" and isinstance(nested, str) and nested.startswith(("http://", "https://")):
                urls.append((nested, source))
            elif key == "sources" and isinstance(nested, list):
                for item in nested:
                    if isinstance(item, str) and item.startswith(("http://", "https://")):
                        urls.append((item, source))
            else:
                urls.extend(walk_urls(nested, source))
    elif isinstance(value, list):
        for item in value:
            urls.extend(walk_urls(item, source))
    return urls


def collect_urls() -> list[tuple[str, str]]:
    seen: set[str] = set()
    urls: list[tuple[str, str]] = []
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for url, source in walk_urls(data, path.name):
            if url not in seen:
                seen.add(url)
                urls.append((url, source))
    return urls


def check_url(url: str, timeout: float) -> tuple[int | None, str]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "southern-china-map-link-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, "HEAD"
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405, 429}:
            request = urllib.request.Request(url, method="GET", headers={"User-Agent": "southern-china-map-link-check/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return response.status, "GET"
            except urllib.error.HTTPError as get_exc:
                return get_exc.code, "GET"
            except Exception as get_exc:  # noqa: BLE001 - diagnostic script
                return None, f"GET {type(get_exc).__name__}"
        return exc.code, "HEAD"
    except Exception as exc:  # noqa: BLE001 - diagnostic script
        return None, type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description="Check external source URLs used by data JSON files.")
    parser.add_argument("--limit", type=int, default=0, help="Check only the first N unique URLs.")
    parser.add_argument("--timeout", type=float, default=8.0, help="Per-request timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Pause between requests.")
    args = parser.parse_args()

    urls = collect_urls()
    if args.limit:
        urls = urls[: args.limit]

    failed = 0
    warnings = 0
    for index, (url, source) in enumerate(urls, start=1):
        status, method = check_url(url, args.timeout)
        hard_failure = status is not None and status >= 400
        warning = status is None
        if hard_failure:
            failed += 1
        if warning:
            warnings += 1
        status_text = str(status) if status is not None else "ERR"
        print(f"{index:03d} {status_text:>3} {method:<18} {source:<28} {url}")
        time.sleep(args.sleep)

    print(f"Checked {len(urls)} URLs; HTTP failures: {failed}; network warnings: {warnings}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
