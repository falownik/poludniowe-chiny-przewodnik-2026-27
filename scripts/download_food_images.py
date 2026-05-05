from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
IMAGE_DIR = DOCS / "assets" / "images"
FOOD_SOURCES = ROOT / "data" / "food_image_sources.json"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "southern-china-guide/1.0 (travel planning; Wikimedia Commons image attribution)"


FOOD_IMAGE_TITLES: dict[str, str] = {
    "dim_sum_har_gow": "File:HK TKO 寶琳 Po Lam MCP 新都城中心 Metro City Plaza mall One shop 海港酒家 Victoria Harbour Seafood Restaurant 點心 dim sum white Shrimp dumpling 蝦餃 Har gow January 2024 R12S 01.jpg",
    "siu_mai": "File:Li Wah Dim Sum - Siu Mai (5340363810).jpg",
    "char_siu": "File:Roast Pork, Char Siu (8523604878).jpg",
    "roast_goose": "File:Roast goose in yat lok restaurant.JPG",
    "wonton_noodles": "File:Wanton noodles.jpg",
    "cheung_fun": "File:Rice noodle roll 腸粉 Tim Ho Wan, the Dim-Sum Specialists, Sham Shui Po 添好運點心專門店, 深水埗 SML.20120820.G12.00089 (7884987988).jpg",
    "lo_mai_gai": "File:Lo mai gai 2.JPG",
    "turnip_cake": "File:Li Wah Dim Sum - Turnip Cake (5339806715).jpg",
    "char_siu_bao": "File:Char siu bao.jpg",
    "claypot_rice": "File:Cured Meat Claypot Rice at The Soup Kitchen (20200718171540).jpg",
    "beef_chow_fun": "File:Beef chow fun.jpg",
    "white_cut_chicken": "File:BeiQieJi-WhiteCutChicken.jpg",
    "steamed_fish": "File:Cantonese style steamed fish and special side dishes in lunch.jpg",
    "guilin_rice_noodles": "File:Guilin mifan.jpg",
    "yangshuo_beer_fish": "File:Pijiu Yu (Beer fish) (253141965).jpg",
    "chaozhou_congee": "File:潮州蚝糜 Chaozhou Congee with Oysters and Minced Pork - 朝江春 Chiu Chow Garden, Taikoo (2229893487).jpg",
    "chaoshan_beef_hotpot": "File:Chaoshan Beef Hot Pot at Baheli Haiji, ZGC1 (20221003132726).jpg",
    "chaozhou_braised_goose": "File:卤水鹅片 Braised Goose Breast - 朝江春 Chiu Chow Garden, Taikoo (2229895089).jpg",
    "xiamen_shacha_noodles": "File:20230131 Seafood Shacha Noodle.jpg",
    "hainan_chicken_rice": "File:Hainanese Chicken Rice.jpg",
    "wenchang_chicken": "File:Wenchang Chicken 1.JPG",
    "hongkong_egg_waffle": "File:A kind of egg waffles.jpg",
    "milk_tea": "File:Hong Kong-style Milk Tea.jpg",
    "pineapple_bun": "File:A Pineapple bun in bun mei Hong Kong style restaurant.jpg",
    "macau_egg_tart": "File:Portuguese egg tart in Macau.jpg",
    "macau_pork_chop_bun": "File:Pork chop bun with ice milk tea.jpg",
    "macanese_african_chicken": "File:African chicken macau.JPG",
    "macanese_minchi": "File:Minchi.jpg",
    "double_skin_milk": "File:Double skin milk.jpg",
    "ginger_milk_curd": "File:Ginger Milk Pudding.jpg",
    "hakka_stuffed_tofu": "File:酿豆腐 2.jpg",
    "hakka_lei_cha": "File:Kenny's Mum's 擂茶饭 Lei Cha Rice (1576303537).jpg",
    "fujian_lychee_pork": "File:Litchi Pork.jpg",
    "buddha_jumps_wall": "File:Buddha jumps over the wall at Jingrong (20161203135907).jpg",
    "dahongpao_tea": "File:20121030 Da Hong Pao.jpg",
    "fujian_fish_balls": "File:Fishball closeup.jpg",
}


def commons_metadata(session: requests.Session, titles: list[str]) -> dict[str, dict[str, Any]]:
    response = session.get(
        COMMONS_API,
        params={
            "action": "query",
            "format": "json",
            "titles": "|".join(titles),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1200,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    result: dict[str, dict[str, Any]] = {}
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title")
        info = (page.get("imageinfo") or [{}])[0]
        if title and info.get("thumburl"):
            result[title] = info
    return result


def meta_value(metadata: dict[str, Any], key: str) -> str:
    return str(metadata.get(key, {}).get("value", "") or "")


def download_image(session: requests.Session, url: str, target: Path) -> None:
    for attempt in range(6):
        response = session.get(url, timeout=90)
        if response.status_code == 429:
            time.sleep(8 * (attempt + 1))
            continue
        response.raise_for_status()
        target.write_bytes(response.content)
        return
    response.raise_for_status()


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    by_title: dict[str, dict[str, Any]] = {}
    titles = list(FOOD_IMAGE_TITLES.values())
    for start in range(0, len(titles), 40):
        by_title.update(commons_metadata(session, titles[start : start + 40]))

    sources = []
    missing = []
    for image_id, title in FOOD_IMAGE_TITLES.items():
        info = by_title.get(title)
        if not info:
            missing.append(title)
            continue
        target = IMAGE_DIR / f"{image_id}.jpg"
        download_image(session, info["thumburl"], target)
        metadata = info.get("extmetadata", {})
        sources.append(
            {
                "id": image_id,
                "title": meta_value(metadata, "ObjectName") or title.removeprefix("File:"),
                "commons_title": title,
                "artist": meta_value(metadata, "Artist"),
                "license": meta_value(metadata, "LicenseShortName"),
                "source": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                "file": f"assets/images/{target.name}",
            }
        )
        time.sleep(1.2)

    FOOD_SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Downloaded food images: {len(sources)}")
    if missing:
        print("Missing:")
        for title in missing:
            print(f"- {title}")


if __name__ == "__main__":
    main()
