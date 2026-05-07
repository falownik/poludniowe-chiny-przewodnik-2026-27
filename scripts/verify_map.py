from __future__ import annotations

import html as html_lib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HTML = DOCS / "index.html"
PLACES = ROOT / "data" / "places.json"
ROUTES = ROOT / "data" / "routes.json"
PROVINCES = ROOT / "data" / "provinces.geojson"
NEARBY = ROOT / "data" / "nearby_places.json"
ATTRIBUTIONS = DOCS / "assets" / "image_attributions.json"
SITE_CSS = DOCS / "assets" / "site.css"
PLACES_DIR = DOCS / "places"
FOOD_PAGE = DOCS / "food.html"
RESEARCH_PAGE = DOCS / "research.html"
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
    "hakka_stuffed_tofu.jpg",
    "hakka_lei_cha.jpg",
    "hongkong_egg_waffle.jpg",
    "milk_tea.jpg",
    "pineapple_bun.jpg",
    "macau_egg_tart.jpg",
    "macau_pork_chop_bun.jpg",
    "macanese_african_chicken.jpg",
    "macanese_minchi.jpg",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def html_contains_json_text(html: str, value: str) -> bool:
    escaped_json_value = json.dumps(value, ensure_ascii=True)[1:-1]
    return value in html or escaped_json_value in html


def html_contains_text(html: str, value: str) -> bool:
    return html_contains_json_text(html, value) or html_lib.escape(value, quote=True) in html


def main() -> None:
    places = load_json(PLACES)
    routes = load_json(ROUTES)
    provinces = load_json(PROVINCES)
    nearby_places = load_json(NEARBY)
    attributions = load_json(ATTRIBUTIONS)
    html = HTML.read_text(encoding="utf-8")

    require(HTML.exists(), "docs/index.html is missing")
    require(len(places) >= 10, "expected at least 10 mapped places")
    require(len(routes) >= 10, "expected at least 10 transport routes")
    require(len(provinces.get("features", [])) >= 4, "expected at least 4 province/region polygons")
    require(len(nearby_places) >= 30, "expected at least 30 researched nearby places")
    require(
        {"Guangzhou", "Guilin / Yangshuo", "Nanning", "Shenzhen", "Shantou / Chaozhou"}.issubset(
            {item["hub"] for item in nearby_places}
        ),
        "nearby research does not cover all chosen hubs",
    )
    require({"A", "B", "C"}.issubset({item["rank"] for item in nearby_places}), "nearby research lacks A/B/C ranks")
    require(len(attributions) >= len({place["photo_id"] for place in places}), "missing image attributions")
    require(any(place["id"] == "nanning" for place in places), "Nanning is missing from places")
    require(any(place["id"] == "fangchenggang" for place in places), "Fangchenggang is missing from places")
    require(any(place["id"] == "detian" for place in places), "Detian is missing from places")
    require(all(place["id"] not in {"hainan", "xiamen", "longji"} for place in places), "removed Hainan/Xiamen/Longji places should not be mapped")
    flight_routes = [route for route in routes if "flight" in route["mode"].lower()]
    if flight_routes:
        require(any(route.get("train_alt") for route in flight_routes), "flight routes lack train alternatives")
    route_layers = {route.get("layer") for route in routes}
    require({"hub_hsr", "local_hub", "optional"}.issubset(route_layers), "route layer split is incomplete")
    require(all(route.get("layer") in {"hub_hsr", "local_hub", "optional"} for route in routes), "route has invalid layer")
    require(any(route["id"] == "nanning_shenzhen" for route in routes), "Nanning-Shenzhen hub route is missing")
    require(any(route["id"] == "nanning_detian" for route in routes), "Nanning-Detian route is missing")
    require(
        any(route["id"] == "nanning_fangchenggang" and route.get("layer") == "local_hub" for route in routes),
        "Fangchenggang day-trip route should be local_hub",
    )
    require(
        all(route["from"] not in {"hainan", "xiamen", "longji"} and route["to"] not in {"hainan", "xiamen", "longji"} for route in routes),
        "routes should not reference removed Hainan/Xiamen/Longji places",
    )

    required_phrases = [
        "Południe Chin 2026/27",
        "Budżet noclegów",
        "Przejazdy",
        "Prowincje i regiony",
        "Kolorowe obszary",
        "Atrakcje",
        "Otwórz stronę miejsca",
        "popup-actions",
        "trip-panel-toggle",
        "Research hubów",
        "plan-panel-toggle",
        "plan-panel",
        "itinerary-day",
        "data-place-ids",
        "Poprawiony plan",
        "Sylwester w Chaoshan",
        "itinerary-marker-active",
        "markerNames",
        "legend-toggle",
        "trip-panel-hidden",
        "legend-hidden",
        '<body class="trip-panel-hidden legend-hidden">',
        'document.body.classList.add("trip-panel-hidden")',
        'document.body.classList.add("legend-hidden")',
        "route-tooltip-card",
        "route-layer-hub-hsr",
        "route-layer-local-hub",
        "Research: miejsca wokół hubów",
        "research.html",
        "Pętla HSR",
        "Wypady z baz",
        "opcje rezerwowe, domyślnie wyłączone",
        "Detian Waterfall / Mingshi",
        "Fangchenggang / Dongxing",
        "leaflet-tooltip.route-tooltip",
        "width: max-content",
        "overflow-wrap: break-word",
        "leaflet-tooltip.foliumtooltip",
        "table-layout: fixed",
        "width: 320px !important",
        "max-height: min(560px, calc(100vh - 130px))",
        "max-height: min(260px, calc(100vh - 110px))",
        "places/",
        "Noclegi:",
        "assets/images/",
        "leaflet",
    ]
    for phrase in required_phrases:
        require(html_contains_json_text(html, phrase), f"HTML missing phrase: {phrase}")

    require("route-label" not in html, "route labels should not be rendered permanently")
    require("<th>Koszt</th>" not in html, "route cost column should not be visible in the sidebar")
    require('"collapsed": true' in html, "layer control should start collapsed")
    require("places/hainan.html" not in html, "map should not link removed Hainan page")
    require("places/xiamen.html" not in html, "map should not link removed Xiamen page")
    require("places/longji.html" not in html, "map should not link removed Longji page")
    require("Longji Rice Terraces" not in html, "map should not contain removed Longji point")

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
        if route.get("train_alt"):
            require(route["train_alt"]["cost_pln"] in html, f"HTML missing train alternative cost: {route['id']}")
            require(route["train_alt"]["time"] in html, f"HTML missing train alternative time: {route['id']}")

    for item in nearby_places:
        require(html_contains_text(html, item["name"]), f"map HTML missing nearby research point: {item['name']}")
        require(html_contains_text(html, item.get("summary", "")), f"map HTML missing nearby summary: {item['name']}")
        require(item.get("image_id"), f"nearby research point lacks image_id: {item['name']}")
        require(item.get("sources"), f"nearby research point lacks sources: {item['name']}")

    for feature in provinces.get("features", []):
        props = feature.get("properties", {})
        require(html_contains_json_text(html, props.get("name", "")), f"HTML missing province name: {props.get('name')}")
        require(props.get("color") in html, f"HTML missing province color: {props.get('name')}")
        require(html_contains_json_text(html, props.get("description", "")), f"HTML missing province description: {props.get('name')}")

    for removed_name in ["Kunming / Yunnan", "Yunnan", "Guizhou", "Syczuan", "Hainan", "Fujian", "Xiamen", "Longji"]:
        require(removed_name not in html, f"HTML still contains removed region: {removed_name}")

    for stale_name in ["hainan.html", "xiamen.html", "longji.html"]:
        require(not (PLACES_DIR / stale_name).exists(), f"stale removed place page should be deleted: {stale_name}")

    image_files = list((DOCS / "assets" / "images").glob("*"))
    require(len(image_files) >= len({place["photo_id"] for place in places}), "not enough copied images")

    require(SITE_CSS.exists(), "site CSS is missing")
    for page_name in ["places/index.html", "itinerary.html", "research.html", "food.html", "practical.html"]:
        page = DOCS / page_name
        require(page.exists(), f"missing static guide page: {page_name}")
        page_html = page.read_text(encoding="utf-8")
        require("Południe Chin 2026/27" in page_html, f"static page missing site title: {page_name}")
        require("assets/site.css" in page_html or "../assets/site.css" in page_html, f"static page missing CSS: {page_name}")

    research_html = RESEARCH_PAGE.read_text(encoding="utf-8")
    require("Research miejsc wokół hubów" in research_html, "research page missing title")
    require("research-grid" in research_html, "research page missing card grid")
    require(research_html.count('class="research-card') >= len(nearby_places), "research page missing researched cards")
    for hub in ["Guangzhou", "Guilin / Yangshuo", "Nanning", "Shenzhen", "Shantou / Chaozhou"]:
        require(hub in research_html, f"research page missing hub: {hub}")
    for label in ["A · mocno polecane", "B · dobre przy zapasie", "C · tylko dla konkretnego celu"]:
        require(label in research_html, f"research page missing rank label: {label}")
    attributions_by_id = {item["id"]: item for item in attributions}
    for image_id in {item["image_id"] for item in nearby_places if item.get("image_id")}:
        require(image_id in attributions_by_id, f"nearby image lacks attribution: {image_id}")

    food_html = FOOD_PAGE.read_text(encoding="utf-8")
    require("food-region-card" in food_html, "food page missing regional food cards")
    require("dish-grid" in food_html, "food page missing dish gallery")
    require("potraw" in food_html, "food page missing dish section")
    require(food_html.count('class="dish-card"') >= 50, "food page should list at least 50 dishes")
    for removed_food_term in ["Hainan", "Fujian", "Xiamen", "Longji", "Sichuan", "tulou", "Fuzhou", "Wuyi", "Haikou", "Sanya", "Wanning"]:
        require(removed_food_term not in food_html, f"food page still contains out-of-plan term: {removed_food_term}")
    for image_name in REQUIRED_FOOD_IMAGES:
        require((DOCS / "assets" / "images" / image_name).exists(), f"missing food image file: {image_name}")
        require(image_name in food_html, f"food page does not reference image: {image_name}")
    attributions_by_id = {item["id"]: item for item in attributions}
    require("Har gow" in attributions_by_id["dim_sum_har_gow"]["commons_title"], "har gow image source looks incorrect")
    require("Roast_Pork" in attributions_by_id["char_siu"]["source"], "char siu image source looks incorrect")
    require("Guilin_mifan" in attributions_by_id["guilin_rice_noodles"]["source"], "Guilin noodles image source looks incorrect")

    print("OK: map artifact covers places, lodging prices, attractions, route costs, images, and summaries.")
    print(f"Places: {len(places)}")
    print(f"Routes: {len(routes)}")
    print(f"Provinces: {len(provinces.get('features', []))}")
    print(f"Nearby research points: {len(nearby_places)}")
    print(f"Images: {len(image_files)}")
    print(f"Place pages: {len(list(PLACES_DIR.glob('*.html'))) - 1}")


if __name__ == "__main__":
    main()
