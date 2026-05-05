from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HTML = DOCS / "index.html"
PLACES = ROOT / "data" / "places.json"
ROUTES = ROOT / "data" / "routes.json"
PROVINCES = ROOT / "data" / "provinces.geojson"
ATTRIBUTIONS = DOCS / "assets" / "image_attributions.json"
SITE_CSS = DOCS / "assets" / "site.css"
PLACES_DIR = DOCS / "places"
FOOD_PAGE = DOCS / "food.html"
REQUIRED_FOOD_IMAGES = [
    "dim_sum_har_gow.jpg",
    "siu_mai.jpg",
    "char_siu.jpg",
    "roast_goose.jpg",
    "wonton_noodles.jpg",
    "cheung_fun.jpg",
    "lo_mai_gai.jpg",
    "turnip_cake.jpg",
    "char_siu_bao.jpg",
    "claypot_rice.jpg",
    "beef_chow_fun.jpg",
    "guilin_rice_noodles.jpg",
    "yangshuo_beer_fish.jpg",
    "chaozhou_braised_goose.jpg",
    "chaoshan_beef_hotpot.jpg",
    "xiamen_shacha_noodles.jpg",
    "hainan_chicken_rice.jpg",
    "wenchang_chicken.jpg",
    "hongkong_egg_waffle.jpg",
    "milk_tea.jpg",
    "pineapple_bun.jpg",
    "macau_egg_tart.jpg",
    "macau_pork_chop_bun.jpg",
    "macanese_minchi.jpg",
    "dahongpao_tea.jpg",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    places = load_json(PLACES)
    routes = load_json(ROUTES)
    provinces = load_json(PROVINCES)
    attributions = load_json(ATTRIBUTIONS)
    html = HTML.read_text(encoding="utf-8")

    require(HTML.exists(), "docs/index.html is missing")
    require(len(places) >= 10, "expected at least 10 mapped places")
    require(len(routes) >= 10, "expected at least 10 transport routes")
    require(len(provinces.get("features", [])) >= 6, "expected at least 6 province/region polygons")
    require(len(attributions) >= len({place["photo_id"] for place in places}), "missing image attributions")

    required_phrases = [
        "Południe Chin 2026/27",
        "Budżet noclegów",
        "Przejazdy",
        "Prowincje i regiony",
        "Kolorowe obszary",
        "Atrakcje",
        "Otwórz stronę miejsca",
        "places/",
        "Noclegi:",
        "assets/images/",
        "leaflet",
    ]
    for phrase in required_phrases:
        require(phrase in html, f"HTML missing phrase: {phrase}")

    for place in places:
        require(place["name"] in html, f"HTML missing place: {place['name']}")
        require(f"places/{place['id']}.html" in html, f"HTML missing place page link: {place['name']}")
        require(str(place["avg_lodging_pln_pp"]) in html, f"HTML missing lodging price for: {place['name']}")
        require(place.get("summary", "") in html, f"HTML missing region summary for: {place['name']}")
        require(place.get("what_to_see"), f"place lacks what_to_see list: {place['name']}")
        require(place.get("attractions"), f"place lacks attractions: {place['name']}")

        page = PLACES_DIR / f"{place['id']}.html"
        require(page.exists(), f"missing place page: {page}")
        page_html = page.read_text(encoding="utf-8")
        require(place["name"] in page_html, f"place page missing title: {place['name']}")
        require(place.get("summary", "") in page_html, f"place page missing summary: {place['name']}")
        require("../index.html" in page_html, f"place page missing map backlink: {place['name']}")
        require("../assets/site.css" in page_html, f"place page missing site CSS: {place['name']}")
        require("Połączenia z mapy" in page_html, f"place page missing route section: {place['name']}")

    place_ids = {place["id"] for place in places}
    for route in routes:
        require(route["from"] in place_ids, f"route has unknown from id: {route['id']}")
        require(route["to"] in place_ids, f"route has unknown to id: {route['id']}")
        require(route["cost_pln"] in html, f"HTML missing route cost: {route['id']}")
        require(route["time"] in html, f"HTML missing route time: {route['id']}")

    for feature in provinces.get("features", []):
        props = feature.get("properties", {})
        require(props.get("name") in html, f"HTML missing province name: {props.get('name')}")
        require(props.get("color") in html, f"HTML missing province color: {props.get('name')}")
        require(props.get("description") in html, f"HTML missing province description: {props.get('name')}")

    for removed_name in ["Kunming / Yunnan", "Yunnan", "Guizhou", "Syczuan"]:
        require(removed_name not in html, f"HTML still contains removed region: {removed_name}")

    image_files = list((DOCS / "assets" / "images").glob("*"))
    require(len(image_files) >= len({place["photo_id"] for place in places}), "not enough copied images")

    require(SITE_CSS.exists(), "site CSS is missing")
    for page_name in ["places/index.html", "itinerary.html", "food.html", "practical.html"]:
        page = DOCS / page_name
        require(page.exists(), f"missing static guide page: {page_name}")
        page_html = page.read_text(encoding="utf-8")
        require("Południe Chin 2026/27" in page_html, f"static page missing site title: {page_name}")
        require("assets/site.css" in page_html or "../assets/site.css" in page_html, f"static page missing CSS: {page_name}")

    food_html = FOOD_PAGE.read_text(encoding="utf-8")
    require("food-region-card" in food_html, "food page missing regional food cards")
    require("dish-grid" in food_html, "food page missing dish gallery")
    require("potraw" in food_html, "food page missing dish section")
    require(food_html.count('class="dish-card"') >= 50, "food page should list at least 50 dishes")
    for image_name in REQUIRED_FOOD_IMAGES:
        require((DOCS / "assets" / "images" / image_name).exists(), f"missing food image file: {image_name}")
        require(image_name in food_html, f"food page does not reference image: {image_name}")
    attributions_by_id = {item["id"]: item for item in attributions}
    require("Har gow" in attributions_by_id["dim_sum_har_gow"]["commons_title"], "har gow image source looks incorrect")
    require("Roast_Pork" in attributions_by_id["char_siu"]["source"], "char siu image source looks incorrect")
    require("Guilin_mifan" in attributions_by_id["guilin_rice_noodles"]["source"], "Guilin noodles image source looks incorrect")
    require("Seafood_Shacha_Noodle" in attributions_by_id["xiamen_shacha_noodles"]["source"], "Xiamen shacha noodles image source looks incorrect")

    print("OK: map artifact covers places, lodging prices, attractions, route costs, images, and summaries.")
    print(f"Places: {len(places)}")
    print(f"Routes: {len(routes)}")
    print(f"Provinces: {len(provinces.get('features', []))}")
    print(f"Images: {len(image_files)}")
    print(f"Place pages: {len(list(PLACES_DIR.glob('*.html'))) - 1}")


if __name__ == "__main__":
    main()
