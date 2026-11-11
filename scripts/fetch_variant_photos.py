"""Resolve Wikimedia Commons metadata for the variant photo gallery.

Reads data/variant_photos.json, asks the Commons API for each file's thumbnail
URL, author, license and description page, downloads a 960 px thumbnail into
docs/assets/images/variants/ and writes data/variant_photo_sources.json. The
site build only reads that output, so it stays offline and reproducible.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GUIDE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = GUIDE_ROOT / "data"
INPUT = DATA_DIR / "variant_photos.json"
OUTPUT = DATA_DIR / "variant_photo_sources.json"
IMAGE_DIR = GUIDE_ROOT / "docs" / "assets" / "images" / "variants"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "south-china-trip-guide/0.1 (static personal travel guide)"}
THUMB_WIDTH = 960
BATCH = 20


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def api_get(params: dict[str, str]) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=40) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise
            time.sleep(15 * (attempt + 1))
    raise RuntimeError("Commons API kept returning 429")


def fetch(titles: list[str]) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    for start in range(0, len(titles), BATCH):
        chunk = titles[start : start + BATCH]
        data = api_get(
            {
                "action": "query",
                "format": "json",
                "titles": "|".join(chunk),
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": str(THUMB_WIDTH),
                "iiextmetadatafilter": "Artist|Credit|LicenseShortName|LicenseUrl",
            }
        )
        query = data.get("query", {})
        aliases = {item["to"]: item["from"] for key in ("normalized", "redirects") for item in query.get(key, [])}
        for page in query.get("pages", {}).values():
            if "imageinfo" not in page:
                print(f"MISSING: {page.get('title')}")
                continue
            info = page["imageinfo"][0]
            meta = info.get("extmetadata", {})
            title = aliases.get(page["title"], page["title"])
            results[title] = {
                "commons_title": page["title"],
                "thumb": info.get("thumburl") or info["url"],
                "source": info["descriptionurl"],
                "artist": strip_html(meta.get("Artist", {}).get("value", "")) or "nieznany autor",
                "license": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
                "license_url": meta.get("LicenseUrl", {}).get("value", ""),
            }
        time.sleep(3)
    return results


def slugify(title: str) -> str:
    stem = title.removeprefix("File:").rsplit(".", 1)[0]
    ascii_stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
    return f"{ascii_stem[:60] or 'photo'}-{digest}.jpg"


def download(resolved: dict[str, dict[str, str]]) -> None:
    """Store thumbnails in docs/ so GitHub Pages does not depend on hotlinking."""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for title, meta in resolved.items():
        target = IMAGE_DIR / slugify(title)
        meta["file"] = f"assets/images/variants/{target.name}"
        if target.exists() and target.stat().st_size > 0:
            continue
        url = meta["thumb"].split("?", 1)[0]
        for attempt in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
                    target.write_bytes(response.read())
                break
            except urllib.error.HTTPError as error:
                if error.code != 429:
                    raise
                time.sleep(15 * (attempt + 1))
            except (TimeoutError, urllib.error.URLError):
                time.sleep(5 * (attempt + 1))
        else:
            print(f"FAILED download: {title}")
        time.sleep(2)


def main() -> None:
    config = json.loads(INPUT.read_text(encoding="utf-8"))
    titles = [photo["commons_title"] for place in config["places"] for photo in place["photos"]]
    resolved = fetch(titles)
    download(resolved)
    missing = [title for title in titles if title not in resolved]
    OUTPUT.write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resolved {len(resolved)}/{len(titles)} photos -> {OUTPUT.relative_to(GUIDE_ROOT)}")
    if missing:
        print("Missing:", *missing, sep="\n  ")


if __name__ == "__main__":
    main()
