from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import Fullscreen, MarkerCluster, MiniMap


ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = ROOT.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
ASSET_DIR = DOCS_DIR / "assets"
IMAGE_DIR = ASSET_DIR / "images"
OUTPUT = DOCS_DIR / "index.html"
PROVINCES = DATA_DIR / "provinces.geojson"

GUIDE_ROOT = PARENT_ROOT / "reports" / "southern_china_full_guide_2026_27"
GUIDE_ASSETS = GUIDE_ROOT / "assets"
GUIDE_MANIFEST = GUIDE_ASSETS / "image_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def place_page_href(place: dict[str, Any]) -> str:
    return f"places/{esc(place['id'])}.html"


def money_color(value: int) -> str:
    if value <= 50:
        return "#16803c"
    if value <= 75:
        return "#d88900"
    if value <= 120:
        return "#d46a00"
    return "#b42318"


def place_color(kind: str) -> str:
    return {
        "base": "blue",
        "main_route": "green",
        "budget_base": "cadetblue",
        "daytrip": "purple",
        "rural": "darkgreen",
        "food_extension": "orange",
        "transfer_base": "lightblue",
        "optional_extension": "gray",
    }.get(kind, "blue")


ROUTE_LAYERS: dict[str, dict[str, Any]] = {
    "hub_hsr": {
        "name": "Pętla: szybka kolej między hubami",
        "short": "Pętla HSR",
        "color": "#1d4ed8",
        "weight": 7,
        "opacity": 0.9,
        "show": True,
        "dash_array": None,
    },
    "local_hub": {
        "name": "Wypady z baz i dojazdy lokalne",
        "short": "Wypady z baz",
        "color": "#0f766e",
        "weight": 5,
        "opacity": 0.82,
        "show": True,
        "dash_array": "8 8",
    },
    "optional": {
        "name": "Opcje rezerwowe / poza aktualną pętlą",
        "short": "Opcje rezerwowe",
        "color": "#64748b",
        "weight": 4,
        "opacity": 0.45,
        "show": False,
        "dash_array": "3 8",
    },
}


TRIP_DAYS: list[dict[str, Any]] = [
    {
        "date": "16.12",
        "title": "Warszawa",
        "detail": "Wylot i dzień techniczny.",
        "place_ids": [],
    },
    {
        "date": "17.12",
        "title": "Guangzhou",
        "detail": "Przylot, pierwszy nocleg i spokojne wejście w trasę.",
        "place_ids": ["guangzhou"],
    },
    {
        "date": "18.12",
        "title": "Guangzhou / Foshan",
        "detail": "Kanton + kulinarny wypad do Foshan/Shunde.",
        "place_ids": ["guangzhou", "shunde_foshan"],
    },
    {
        "date": "19.12",
        "title": "Przejazd do Yangshuo",
        "detail": "Guangzhou -> Guilin -> Yangshuo.",
        "place_ids": ["guangzhou", "guilin", "yangshuo"],
    },
    {
        "date": "20.12",
        "title": "Yangshuo",
        "detail": "Rzeka Yulong, rower/skuter i krasowy krajobraz.",
        "place_ids": ["yangshuo"],
    },
    {
        "date": "21.12",
        "title": "Yangshuo",
        "detail": "Moon Hill, wioski i wolniejsze tempo.",
        "place_ids": ["yangshuo"],
    },
    {
        "date": "22.12",
        "title": "Yangshuo",
        "detail": "Xingping / Li River albo dzień zapasowy na pogodę.",
        "place_ids": ["yangshuo", "guilin"],
    },
    {
        "date": "23.12",
        "title": "Yangshuo",
        "detail": "Ostatni pełny dzień natury przed przejazdem na południe Guangxi.",
        "place_ids": ["yangshuo"],
    },
    {
        "date": "24.12",
        "title": "Nanning",
        "detail": "Yangshuo -> Guilin -> Nanning.",
        "place_ids": ["yangshuo", "guilin", "nanning"],
    },
    {
        "date": "25.12",
        "title": "Nanning",
        "detail": "Qingxiu Mountain, centrum i jedzenie Guangxi.",
        "place_ids": ["nanning"],
    },
    {
        "date": "26.12",
        "title": "Detian",
        "detail": "Długi day trip do Detian Waterfall / Mingshi.",
        "place_ids": ["nanning", "detian"],
    },
    {
        "date": "27.12",
        "title": "Fangchenggang / Dongxing",
        "detail": "Day trip na wybrzeże i pogranicze z Wietnamem.",
        "place_ids": ["nanning", "fangchenggang"],
    },
    {
        "date": "28.12",
        "title": "Shenzhen",
        "detail": "Nanning -> Shenzhen szybką koleją.",
        "place_ids": ["nanning", "shenzhen"],
    },
    {
        "date": "29.12",
        "title": "Shenzhen",
        "detail": "Futian, Huaqiangbei, Shenzhen Bay Park.",
        "place_ids": ["shenzhen"],
    },
    {
        "date": "30.12",
        "title": "Hongkong z Shenzhen",
        "detail": "Day trip: port, Kowloon, Star Ferry i jedzenie.",
        "place_ids": ["shenzhen", "hongkong"],
    },
    {
        "date": "31.12",
        "title": "Chaozhou",
        "detail": "Shenzhen -> Chaozhou; Sylwester w Chaoshan.",
        "place_ids": ["shenzhen", "chaozhou"],
    },
    {
        "date": "1.1",
        "title": "Chaozhou",
        "detail": "Guangji Bridge, Paifang Street, herbata gongfu.",
        "place_ids": ["chaozhou"],
    },
    {
        "date": "2.1",
        "title": "Chaozhou / Shantou",
        "detail": "Moduł foodie: gęś, hotpot wołowy, congee.",
        "place_ids": ["chaozhou"],
    },
    {
        "date": "3.1",
        "title": "Guangzhou",
        "detail": "Chaozhou -> Guangzhou, bufor przed końcówką.",
        "place_ids": ["chaozhou", "guangzhou"],
    },
    {
        "date": "4.1",
        "title": "Makao z Guangzhou",
        "detail": "Day trip przez Zhuhai: stare centrum, Taipa, egg tarty.",
        "place_ids": ["guangzhou", "zhuhai", "macau"],
    },
    {
        "date": "5.1",
        "title": "Guangzhou",
        "detail": "Ostatni pełny dzień: Liwan, zakupy, kolacja.",
        "place_ids": ["guangzhou"],
    },
    {
        "date": "6.1",
        "title": "Powrót",
        "detail": "Guangzhou jako bezpieczna baza pod lot.",
        "place_ids": ["guangzhou"],
    },
]


def route_color(mode: str) -> str:
    mode = mode.lower()
    if "flight" in mode:
        return "#d97706"
    if "hsr" in mode or "rail" in mode:
        return "#2563eb"
    if "border" in mode or "ferry" in mode:
        return "#7c3aed"
    return "#0f766e"


def route_layer_key(route: dict[str, Any]) -> str:
    layer = route.get("layer", "optional")
    return layer if layer in ROUTE_LAYERS else "optional"


def route_layer_meta(route: dict[str, Any]) -> dict[str, Any]:
    return ROUTE_LAYERS[route_layer_key(route)]


def route_layer_class(route: dict[str, Any]) -> str:
    return f"route-layer-{route_layer_key(route).replace('_', '-')}"


def province_style(feature: dict[str, Any]) -> dict[str, Any]:
    color = feature.get("properties", {}).get("color", "#64748b")
    muted = bool(feature.get("properties", {}).get("muted"))
    return {
        "fillColor": color,
        "color": color,
        "weight": 0.8 if muted else 1.2,
        "opacity": 0.38 if muted else 0.72,
        "fillOpacity": 0.035 if muted else 0.17,
    }


def province_highlight(feature: dict[str, Any]) -> dict[str, Any]:
    color = feature.get("properties", {}).get("color", "#334155")
    muted = bool(feature.get("properties", {}).get("muted"))
    return {
        "fillColor": color,
        "color": color,
        "weight": 1.4 if muted else 2.4,
        "opacity": 0.55 if muted else 0.95,
        "fillOpacity": 0.08 if muted else 0.29,
    }


def read_image_manifest() -> dict[str, dict[str, Any]]:
    if not GUIDE_MANIFEST.exists():
        return {}
    manifest = load_json(GUIDE_MANIFEST)
    return {item["id"]: item for item in manifest}


def copy_images(places: list[dict[str, Any]], manifest: dict[str, dict[str, Any]]) -> dict[str, str]:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    used_ids = {place["photo_id"] for place in places if place.get("photo_id")}
    copied: dict[str, str] = {}
    attributions: list[dict[str, str]] = []

    for image_id in sorted(used_ids):
        item = manifest.get(image_id)
        if not item:
            continue
        source = GUIDE_ROOT / item["file"]
        if not source.exists():
            continue
        target = IMAGE_DIR / source.name
        shutil.copy2(source, target)
        copied[image_id] = f"assets/images/{target.name}"
        attributions.append(
            {
                "id": image_id,
                "title": item.get("title", ""),
                "commons_title": item.get("commons_title", ""),
                "artist": item.get("artist", ""),
                "license": item.get("license", ""),
                "source": item.get("source", ""),
                "file": copied[image_id],
            }
        )

    (ASSET_DIR / "image_attributions.json").write_text(
        json.dumps(attributions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return copied


def attraction_list(place: dict[str, Any]) -> str:
    rows = []
    for attraction in place.get("attractions", []):
        rows.append(
            "<li>"
            f"<strong>{esc(attraction['name'])}</strong>"
            f"<br><span>{esc(attraction.get('time', ''))}, {esc(attraction.get('price_pln', ''))}</span>"
            f"<br>{esc(attraction.get('note', ''))}"
            "</li>"
        )
    return "<ul class='popup-list'>" + "".join(rows) + "</ul>" if rows else ""


def place_popup(place: dict[str, Any], image_path: str | None) -> str:
    attractions = attraction_list(place)
    bullets = "".join(f"<li>{esc(item)}</li>" for item in place.get("what_to_see", []))
    image = f"<img class='popup-img' src='{esc(image_path)}' alt='{esc(place['name'])}'>" if image_path else ""
    page_href = place_page_href(place)
    return f"""
    <div class="popup-card">
      {image}
      <h2>{esc(place['name'])}</h2>
      <div class="tag-row">
        <span>{esc(place['region'])}</span>
        <span>{esc(place['priority'])}</span>
      </div>
      <p>{esc(place['summary'])}</p>
      <p><strong>Noclegi:</strong> średnio ok. {esc(place['avg_lodging_pln_pp'])} PLN/os./noc.
      {esc(place['lodging_range_pln_pp'])}</p>
      <p><strong>Budżetowo:</strong> {esc(place['budget_note'])}</p>
      <p><strong>Sugerowany pobyt:</strong> {esc(place['suggested_nights'])}</p>
      <h3>Co tu jest</h3>
      <ul>{bullets}</ul>
      <h3>Atrakcje</h3>
      {attractions}
      <p class="popup-actions"><a class="popup-link" href="{page_href}" target="_self" onclick="window.location.href=this.getAttribute('href'); return false;">Otwórz stronę miejsca</a></p>
    </div>
    """


def place_tooltip(place: dict[str, Any], image_path: str | None) -> str:
    image = f"<img src='{esc(image_path)}' alt='{esc(place['name'])}'>" if image_path else ""
    top = ", ".join(place.get("what_to_see", [])[:3])
    return f"""
    <div class="hover-card">
      {image}
      <h3>{esc(place['name'])}</h3>
      <p>{esc(place['summary'])}</p>
      <p><strong>Nocleg:</strong> ok. {esc(place['avg_lodging_pln_pp'])} PLN/os./noc</p>
      <p><strong>Najważniejsze:</strong> {esc(top)}</p>
      <p>Kliknij marker, żeby przejść do strony miejsca.</p>
    </div>
    """


def route_popup(route: dict[str, Any], places_by_id: dict[str, dict[str, Any]]) -> str:
    from_name = places_by_id[route["from"]]["name"]
    to_name = places_by_id[route["to"]]["name"]
    layer = route_layer_meta(route)
    return f"""
    <div class="route-popup">
      <h3>{esc(from_name)} → {esc(to_name)}</h3>
      <p><strong>Warstwa:</strong> {esc(layer['short'])}</p>
      <p><strong>Tryb:</strong> {esc(route['mode'])}</p>
      <p><strong>Czas:</strong> {esc(route['time'])}</p>
      <p>{esc(route['note'])}</p>
    </div>
    """


def route_train_alt(route: dict[str, Any]) -> str:
    alt = route.get("train_alt")
    if not alt:
        return ""
    return (
        '<span class="route-alt">'
        f"<b>{esc(alt.get('label', 'Alternatywa pociągiem'))}:</b> "
        f"{esc(alt.get('time', ''))} · {esc(alt.get('cost_pln', ''))}"
        "</span>"
    )


def route_tooltip(route: dict[str, Any], places_by_id: dict[str, dict[str, Any]]) -> str:
    from_name = places_by_id[route["from"]]["name"]
    to_name = places_by_id[route["to"]]["name"]
    train_alt = route_train_alt(route)
    layer = route_layer_meta(route)
    return (
        '<div class="route-tooltip-card">'
        f"<strong>{esc(from_name)} &rarr; {esc(to_name)}</strong>"
        f"<span class=\"route-layer-pill {route_layer_class(route)}\">{esc(layer['short'])}</span>"
        f"<span>{esc(route['mode'])}</span>"
        f"<span>{esc(route['time'])}</span>"
        f"<span class=\"route-cost\">{esc(route['cost_pln'])}</span>"
        f"{train_alt}"
        "</div>"
    )


def route_coords(route: dict[str, Any], places_by_id: dict[str, dict[str, Any]]) -> list[list[float]]:
    if "geometry" in route:
        return route["geometry"]
    start = places_by_id[route["from"]]
    end = places_by_id[route["to"]]
    return [[start["lat"], start["lon"]], [end["lat"], end["lon"]]]


def build_sidebar(places: list[dict[str, Any]], routes: list[dict[str, Any]]) -> str:
    place_name_by_id = {place["id"]: place["name"] for place in places}

    def route_name(route: dict[str, Any]) -> str:
        from_name = place_name_by_id.get(route["from"], route["from"])
        to_name = place_name_by_id.get(route["to"], route["to"])
        if route["from"] == route["to"]:
            return f"{from_name}: {route['mode']}"
        return f"{from_name} → {to_name}"

    def route_table(layer: str) -> str:
        layer_routes = [route for route in routes if route_layer_key(route) == layer]
        rows = "".join(
            f"<tr><td>{esc(route_name(route))}</td><td>{esc(route['time'])}</td></tr>"
            for route in layer_routes
        )
        if not rows:
            return ""
        meta = ROUTE_LAYERS[layer]
        return f"""
      <h3 class="panel-subhead">{esc(meta['short'])}</h3>
      <table>
        <thead><tr><th>Odcinek</th><th>Czas</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
        """

    place_rows = "".join(
        f"<tr><td>{esc(place['name'])}</td><td>{esc(place['avg_lodging_pln_pp'])} PLN</td><td>{esc(place['suggested_nights'])}</td></tr>"
        for place in sorted(places, key=lambda item: item["avg_lodging_pln_pp"])
    )
    route_sections = route_table("hub_hsr") + route_table("local_hub")
    return f"""
    <button id="trip-panel-toggle" class="panel-toggle panel-toggle-left" type="button" aria-controls="trip-panel" aria-expanded="false">Pokaż panel</button>
    <div id="trip-panel">
      <h1>Południe Chin 2026/27</h1>
      <p>Mapa planistyczna: noclegi, atrakcje, day tripy, transport i budżet. Najedź na marker, żeby zobaczyć zdjęcie i skrót; kliknij, żeby otworzyć szczegóły.</p>
      <p class="panel-links"><a href="places/">Miejsca</a><a href="itinerary.html">Trasa</a><a href="food.html">Jedzenie</a><a href="practical.html">Logistyka</a></p>
      <p>Kolorowe obszary pokazują prowincje i regiony administracyjne objęte planem. Warstwę można włączać i wyłączać w panelu mapy.</p>
      <h2>Budżet noclegów</h2>
      <p>Cel użytkownika: średnio około <strong>50 PLN/os./noc</strong>. Zielone markery są najbliżej celu; czerwone traktuj jako day trip albo wyjątek.</p>
      <table>
        <thead><tr><th>Miejsce</th><th>Śr.</th><th>Pobyt</th></tr></thead>
        <tbody>{place_rows}</tbody>
      </table>
      <h2>Przejazdy</h2>
      <p>W panelu warstw są osobno: pętla HSR między hubami oraz lokalne wypady z baz. Koszt przejazdu pojawia się dopiero po najechaniu na linię na mapie.</p>
      {route_sections}
      <p>Opcje rezerwowe są w osobnej warstwie mapy i startują wyłączone.</p>
    </div>
    """


def build_itinerary_panel(places: list[dict[str, Any]]) -> str:
    known_places = {place["id"] for place in places}
    rows = []
    for day in TRIP_DAYS:
        place_ids = [place_id for place_id in day["place_ids"] if place_id in known_places]
        place_attr = " ".join(place_ids)
        disabled = " disabled" if not place_ids else ""
        rows.append(
            f"""
      <button class="itinerary-day" type="button" data-place-ids="{esc(place_attr)}"{disabled}>
        <span class="itinerary-date">{esc(day['date'])}</span>
        <span class="itinerary-copy">
          <strong>{esc(day['title'])}</strong>
          <span>{esc(day['detail'])}</span>
        </span>
      </button>
            """
        )
    return f"""
    <button id="plan-panel-toggle" class="panel-toggle panel-toggle-plan" type="button" aria-controls="plan-panel" aria-expanded="true">Ukryj plan</button>
    <aside id="plan-panel">
      <h2>Poprawiony plan</h2>
      <div class="itinerary-days">
        {''.join(rows)}
      </div>
    </aside>
    """


def build_styles() -> str:
    return """
    <style>
      body { font-family: "Segoe UI", Arial, sans-serif; }
      #trip-panel {
        position: fixed;
        z-index: 9999;
        top: 12px;
        left: 12px;
        width: 360px;
        max-height: calc(100vh - 24px);
        overflow: auto;
        background: rgba(255,255,255,0.94);
        border: 1px solid #cbd5e1;
        box-shadow: 0 10px 28px rgba(15,23,42,0.16);
        border-radius: 8px;
        padding: 14px 15px 16px;
        color: #172033;
        transition: transform 180ms ease, opacity 180ms ease;
      }
      body.trip-panel-hidden #trip-panel {
        transform: translateX(calc(-100% - 32px));
        opacity: 0;
        pointer-events: none;
      }
      .panel-toggle {
        position: fixed;
        z-index: 10000;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 32px;
        padding: 0 10px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        background: rgba(255,255,255,0.96);
        color: #172033;
        box-shadow: 0 6px 16px rgba(15,23,42,0.14);
        font: 700 12px/1 "Segoe UI", Arial, sans-serif;
        cursor: pointer;
      }
      .panel-toggle:hover { background: #f8fafc; }
      .panel-toggle-left {
        top: 12px;
        left: 388px;
        transition: left 180ms ease;
      }
      body.trip-panel-hidden .panel-toggle-left { left: 12px; }
      .panel-toggle-right {
        right: 12px;
        bottom: 28px;
      }
      .panel-toggle-plan {
        top: 12px;
        right: 58px;
      }
      #trip-panel h1 { font-size: 18px; margin: 0 0 8px; }
      #trip-panel h2 { font-size: 14px; margin: 14px 0 6px; }
      #trip-panel .panel-subhead {
        margin: 10px 0 5px;
        font-size: 12px;
        color: #0f172a;
      }
      #trip-panel p { font-size: 12px; line-height: 1.35; margin: 0 0 8px; }
      .panel-links { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }
      .panel-links a {
        display: inline-flex;
        align-items: center;
        min-height: 26px;
        padding: 0 8px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        background: #f8fafc;
        color: #0f172a;
        text-decoration: none;
        font-size: 11px;
        font-weight: 600;
      }
      #trip-panel table { width: 100%; border-collapse: collapse; font-size: 11px; }
      #trip-panel th, #trip-panel td { border-top: 1px solid #e2e8f0; padding: 4px 3px; vertical-align: top; }
      #trip-panel th { text-align: left; color: #475569; }
      #plan-panel {
        position: fixed;
        z-index: 9998;
        top: 54px;
        right: 12px;
        width: 344px;
        max-height: calc(100vh - 88px);
        overflow: auto;
        background: rgba(255,255,255,0.95);
        border: 1px solid #cbd5e1;
        box-shadow: 0 10px 28px rgba(15,23,42,0.15);
        border-radius: 8px;
        padding: 12px;
        color: #172033;
        transition: transform 180ms ease, opacity 180ms ease;
      }
      body.plan-panel-hidden #plan-panel {
        transform: translateX(calc(100% + 32px));
        opacity: 0;
        pointer-events: none;
      }
      #plan-panel h2 {
        margin: 0 0 9px;
        font-size: 16px;
        line-height: 1.2;
      }
      .itinerary-days {
        display: grid;
        gap: 6px;
      }
      .itinerary-day {
        display: grid;
        grid-template-columns: 48px minmax(0, 1fr);
        gap: 8px;
        width: 100%;
        min-height: 54px;
        padding: 8px;
        border: 1px solid #d9e1ea;
        border-radius: 7px;
        background: #fff;
        color: #172033;
        text-align: left;
        cursor: pointer;
      }
      .itinerary-day:hover,
      .itinerary-day:focus-visible {
        border-color: #f97316;
        background: #fff7ed;
        outline: none;
        box-shadow: 0 0 0 2px rgba(249,115,22,0.18);
      }
      .itinerary-day:disabled {
        cursor: default;
        opacity: 0.58;
      }
      .itinerary-day:disabled:hover {
        border-color: #d9e1ea;
        background: #fff;
        box-shadow: none;
      }
      .itinerary-date {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 30px;
        border-radius: 6px;
        background: #eef2ff;
        color: #3730a3;
        font-size: 12px;
        font-weight: 800;
        line-height: 1;
      }
      .itinerary-copy {
        min-width: 0;
        display: grid;
        gap: 2px;
      }
      .itinerary-copy strong {
        font-size: 12px;
        line-height: 1.2;
      }
      .itinerary-copy span {
        color: #5b6475;
        font-size: 11px;
        line-height: 1.28;
      }
      .itinerary-marker-active {
        filter: drop-shadow(0 0 8px #f97316) drop-shadow(0 0 3px #111827);
      }
      .leaflet-tooltip {
        width: max-content;
        min-width: min(180px, calc(100vw - 32px));
        max-width: min(320px, calc(100vw - 32px)) !important;
        white-space: normal !important;
        overflow-wrap: break-word;
        word-break: normal;
      }
      .leaflet-tooltip.foliumtooltip {
        width: 320px !important;
        max-width: 320px !important;
        white-space: normal !important;
        line-height: 1.35;
        overflow-wrap: normal;
      }
      .leaflet-tooltip.foliumtooltip table {
        width: 100% !important;
        table-layout: fixed;
        margin: 0 !important;
      }
      .leaflet-tooltip.foliumtooltip th {
        width: 92px !important;
        padding: 3px 8px 3px 0 !important;
        vertical-align: top;
        white-space: normal !important;
      }
      .leaflet-tooltip.foliumtooltip td {
        width: 210px !important;
        padding: 3px 0 !important;
        vertical-align: top;
        white-space: normal !important;
        overflow-wrap: break-word;
        word-break: normal;
      }
      .hover-card {
        width: min(285px, calc(100vw - 56px));
        max-height: min(260px, calc(100vh - 110px));
        overflow: auto;
        font-size: 12px;
        line-height: 1.32;
        color: #172033;
        overflow-wrap: anywhere;
      }
      .hover-card img { width: 100%; max-height: 92px; object-fit: cover; border-radius: 6px; margin-bottom: 6px; }
      .hover-card h3 { margin: 2px 0 5px; font-size: 15px; }
      .hover-card p { margin: 4px 0; }
      .leaflet-popup-content {
        width: min(340px, calc(100vw - 72px)) !important;
        max-width: min(340px, calc(100vw - 72px)) !important;
        margin: 10px 12px;
      }
      .leaflet-popup-content-wrapper {
        max-width: calc(100vw - 32px);
      }
      .popup-card {
        width: 100%;
        max-height: min(560px, calc(100vh - 130px));
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 4px;
        font-size: 13px;
        line-height: 1.38;
        overflow-wrap: anywhere;
      }
      .popup-card h2 { margin: 7px 0 6px; font-size: 19px; }
      .popup-card h3 { margin: 9px 0 4px; font-size: 14px; }
      .popup-img { width: 100%; max-height: 130px; object-fit: cover; border-radius: 6px; }
      .tag-row { display: flex; gap: 5px; flex-wrap: wrap; margin: 4px 0 8px; }
      .tag-row span { background: #eef2ff; color: #3730a3; padding: 2px 6px; border-radius: 999px; font-size: 11px; }
      .popup-card ul { margin: 4px 0 6px; padding-left: 18px; }
      .popup-list li { margin-bottom: 5px; }
      .popup-actions {
        position: sticky;
        bottom: 0;
        margin: 8px -4px 0;
        padding: 8px 4px 2px;
        background: linear-gradient(rgba(255,255,255,0.72), #fff 42%);
      }
      .popup-link {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        min-height: 30px;
        margin-top: 4px;
        padding: 0 10px;
        border-radius: 6px;
        background: #0f766e;
        color: #fff !important;
        text-decoration: none;
        font-weight: 700;
      }
      .route-popup { width: 260px; font-size: 13px; line-height: 1.35; }
      .route-popup h3 { margin: 0 0 6px; font-size: 15px; }
      .leaflet-tooltip.route-tooltip {
        width: 300px !important;
        max-width: 300px !important;
        white-space: normal !important;
        overflow-wrap: normal;
      }
      .route-tooltip-card {
        width: 282px;
        font-size: 12px;
        line-height: 1.32;
        color: #172033;
      }
      .route-tooltip-card strong,
      .route-tooltip-card span {
        display: block;
        white-space: normal;
        overflow-wrap: break-word;
      }
      .route-tooltip-card strong { margin-bottom: 3px; }
      .route-tooltip-card .route-layer-pill {
        display: inline-flex;
        width: fit-content;
        max-width: 100%;
        margin: 2px 0 5px;
        padding: 2px 6px;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 11px;
        font-weight: 800;
      }
      .route-tooltip-card .route-layer-local-hub {
        background: #ecfdf5;
        color: #0f766e;
      }
      .route-tooltip-card .route-layer-optional {
        background: #f1f5f9;
        color: #475569;
      }
      .route-tooltip-card .route-cost {
        margin-top: 4px;
        font-weight: 800;
        color: #0f766e;
      }
      .route-tooltip-card .route-alt {
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px solid #d9e1ea;
      }
      .legend {
        position: fixed;
        right: 12px;
        bottom: 72px;
        z-index: 9999;
        background: rgba(255,255,255,0.94);
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 12px;
        line-height: 1.45;
        box-shadow: 0 8px 20px rgba(15,23,42,0.14);
        transition: transform 180ms ease, opacity 180ms ease;
      }
      body.legend-hidden .legend {
        transform: translateX(calc(100% + 32px));
        opacity: 0;
        pointer-events: none;
      }
      body:not(.legend-hidden) .legend {
        right: 368px;
      }
      .legend h3 { margin: 0 0 6px; font-size: 13px; }
      .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
      .line-key {
        display: flex;
        align-items: center;
        gap: 7px;
        margin: 4px 0;
      }
      .line-swatch {
        flex: 0 0 28px;
        height: 0;
        border-top: 4px solid #1d4ed8;
        border-radius: 999px;
      }
      .line-swatch.local {
        border-top-color: #0f766e;
        border-top-style: dashed;
      }
      .line-swatch.optional {
        border-top-color: #64748b;
        border-top-style: dotted;
      }
      .province-box {
        display: inline-block;
        width: 13px;
        height: 9px;
        border-radius: 2px;
        margin-right: 6px;
        border: 1px solid rgba(15,23,42,0.28);
        vertical-align: -1px;
      }
      .province-muted {
        color: #64748b;
      }
      .province-muted .province-box {
        opacity: 0.42;
      }
      .legend-note {
        max-width: 230px;
        margin-top: 6px;
        color: #475569;
        font-size: 11px;
        line-height: 1.3;
      }
      @media (max-width: 800px) {
        #trip-panel {
          position: static;
          width: auto;
          max-height: none;
          margin: 50px 8px 8px;
        }
        .panel-toggle-left {
          top: 8px;
          left: 8px;
        }
        body.trip-panel-hidden .panel-toggle-left { left: 8px; }
        .panel-toggle-right {
          right: 8px;
          bottom: 8px;
        }
        .panel-toggle-plan {
          top: 8px;
          right: 8px;
        }
        #plan-panel {
          position: static;
          width: auto;
          max-height: 42vh;
          margin: 8px;
        }
        .legend {
          right: 8px;
          bottom: 52px;
          max-width: min(260px, calc(100vw - 16px));
        }
        body:not(.legend-hidden) .legend {
          right: 8px;
        }
        .leaflet-tooltip.foliumtooltip {
          width: 270px !important;
          max-width: 270px !important;
        }
        .leaflet-tooltip.foliumtooltip th { width: 82px !important; }
        .leaflet-tooltip.foliumtooltip td { width: 176px !important; }
        .leaflet-tooltip.route-tooltip {
          width: 250px !important;
          max-width: 250px !important;
        }
        .route-tooltip-card { width: 232px; }
      }
    </style>
    """


def build_legend(provinces: dict[str, Any]) -> str:
    province_rows = "".join(
        f"<div class=\"{'province-muted' if feature['properties'].get('muted') else ''}\">"
        f"<span class=\"province-box\" style=\"background:{esc(feature['properties'].get('color', '#64748b'))}\"></span>"
        f"{esc(feature['properties'].get('name', 'Region'))}"
        f"{' (opcjonalnie)' if feature['properties'].get('muted') else ''}</div>"
        for feature in provinces.get("features", [])
    )
    province_section = (
        f"""
      <hr>
      <h3>Prowincje / regiony</h3>
      {province_rows}
      <div class="legend-note">Warstwa administracyjna jest podpowiedzią planistyczną; markery i linie pokazują konkretną trasę.</div>
        """
        if province_rows
        else ""
    )
    return f"""
    <button id="legend-toggle" class="panel-toggle panel-toggle-right" type="button" aria-controls="map-legend" aria-expanded="false">Pokaż legendę</button>
    <div id="map-legend" class="legend">
      <h3>Nocleg / osoba / noc</h3>
      <div><span class="dot" style="background:#16803c"></span>do 50 PLN</div>
      <div><span class="dot" style="background:#d88900"></span>51-75 PLN</div>
      <div><span class="dot" style="background:#d46a00"></span>76-120 PLN</div>
      <div><span class="dot" style="background:#b42318"></span>120+ PLN / day trip</div>
      {province_section}
      <hr>
      <h3>Warstwy tras</h3>
      <div class="line-key"><span class="line-swatch"></span><span>pętla HSR między hubami</span></div>
      <div class="line-key"><span class="line-swatch local"></span><span>wypady z baz / dojazdy lokalne</span></div>
      <div class="line-key"><span class="line-swatch optional"></span><span>opcje rezerwowe, domyślnie wyłączone</span></div>
    </div>
    """


def build_panel_script(
    place_marker_names: dict[str, str],
    place_circle_names: dict[str, str],
    place_circle_styles: dict[str, dict[str, Any]],
) -> str:
    script = """
    <script>
      (function () {
        document.body.classList.add("trip-panel-hidden");
        document.body.classList.add("legend-hidden");

        function bindPanelToggle(buttonId, hiddenClass, openText, closedText) {
          const button = document.getElementById(buttonId);
          if (!button) return;
          function sync() {
            const hidden = document.body.classList.contains(hiddenClass);
            button.textContent = hidden ? closedText : openText;
            button.setAttribute("aria-expanded", hidden ? "false" : "true");
          }
          button.addEventListener("click", function () {
            document.body.classList.toggle(hiddenClass);
            sync();
          });
          sync();
        }

        const markerNames = __MARKER_NAMES__;
        const circleNames = __CIRCLE_NAMES__;
        const circleStyles = __CIRCLE_STYLES__;
        let activePlaceIds = [];

        function markerFor(placeId) {
          const name = markerNames[placeId];
          return name ? window[name] : null;
        }

        function circleFor(placeId) {
          const name = circleNames[placeId];
          return name ? window[name] : null;
        }

        function clearItineraryHighlight() {
          activePlaceIds.forEach(function (placeId) {
            const marker = markerFor(placeId);
            if (marker) {
              const markerElement = marker.getElement && marker.getElement();
              if (markerElement) markerElement.classList.remove("itinerary-marker-active");
              if (marker.setZIndexOffset) marker.setZIndexOffset(0);
            }
            const circle = circleFor(placeId);
            if (circle && circle.setStyle && circleStyles[placeId]) {
              circle.setStyle(circleStyles[placeId]);
            }
          });
          activePlaceIds = [];
        }

        function activateItineraryDay(placeIds) {
          clearItineraryHighlight();
          activePlaceIds = placeIds.filter(Boolean);
          const markers = activePlaceIds.map(markerFor).filter(Boolean);
          const map = markers.length ? markers[0]._map : null;
          const latLngs = markers
            .map(function (marker) { return marker.getLatLng && marker.getLatLng(); })
            .filter(Boolean);
          if (map && latLngs.length) {
            const bounds = L.latLngBounds(latLngs);
            map.fitBounds(bounds.pad(0.25), {
              animate: false,
              maxZoom: 8,
              paddingTopLeft: [388, 72],
              paddingBottomRight: [368, 72]
            });
          }

          function applyHighlightStyles() {
            activePlaceIds.forEach(function (placeId) {
              const marker = markerFor(placeId);
              if (marker) {
                const markerElement = marker.getElement && marker.getElement();
                if (markerElement) markerElement.classList.add("itinerary-marker-active");
                if (marker.setZIndexOffset) marker.setZIndexOffset(1000);
              }
              const circle = circleFor(placeId);
              if (circle && circle.setStyle) {
                circle.setStyle({
                  color: "#f97316",
                  fillColor: "#fdba74",
                  fillOpacity: 0.55,
                  weight: 5
                });
                if (circle.bringToFront) circle.bringToFront();
              }
            });
          }
          applyHighlightStyles();
          window.setTimeout(applyHighlightStyles, 80);
        }

        function bindItineraryHover() {
          document.querySelectorAll(".itinerary-day[data-place-ids]").forEach(function (item) {
            const placeIds = (item.dataset.placeIds || "").split(" ").filter(Boolean);
            if (!placeIds.length) return;
            item.addEventListener("mouseenter", function () { activateItineraryDay(placeIds); });
            item.addEventListener("mouseleave", clearItineraryHighlight);
            item.addEventListener("focus", function () { activateItineraryDay(placeIds); });
            item.addEventListener("blur", clearItineraryHighlight);
          });
        }

        bindPanelToggle("trip-panel-toggle", "trip-panel-hidden", "Ukryj panel", "Pokaż panel");
        bindPanelToggle("legend-toggle", "legend-hidden", "Ukryj legendę", "Pokaż legendę");
        bindPanelToggle("plan-panel-toggle", "plan-panel-hidden", "Ukryj plan", "Pokaż plan");
        window.addEventListener("load", bindItineraryHover);
      })();
    </script>
    """
    return (
        script.replace("__MARKER_NAMES__", json.dumps(place_marker_names, ensure_ascii=False))
        .replace("__CIRCLE_NAMES__", json.dumps(place_circle_names, ensure_ascii=False))
        .replace("__CIRCLE_STYLES__", json.dumps(place_circle_styles, ensure_ascii=False))
    )


def add_province_layer(fmap: folium.Map, provinces: dict[str, Any]) -> None:
    if not provinces.get("features"):
        return

    province_group = FeatureGroup(name="Prowincje i regiony (kolory)", show=True)
    folium.GeoJson(
        provinces,
        name="Kolorowe prowincje",
        style_function=province_style,
        highlight_function=province_highlight,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "description", "budget_note"],
            aliases=["Region", "Co tu jest", "Budżet / logistyka"],
            localize=True,
            sticky=True,
            labels=True,
            style=(
                "background: rgba(255,255,255,0.96); color: #172033; "
                "border: 1px solid #cbd5e1; border-radius: 6px; "
                "box-shadow: 0 8px 20px rgba(15,23,42,0.14);"
            ),
        ),
        popup=folium.GeoJsonPopup(
            fields=["name", "name_cn", "description", "budget_note"],
            aliases=["Region", "Nazwa chińska", "Co tu jest", "Budżet / logistyka"],
            localize=True,
            labels=True,
            max_width=360,
        ),
    ).add_to(province_group)
    province_group.add_to(fmap)


def add_place_markers(
    fmap: folium.Map,
    places: list[dict[str, Any]],
    image_paths: dict[str, str],
) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, Any]]]:
    groups = {
        "base": FeatureGroup(name="Bazy i kotwice trasy", show=True),
        "main_route": FeatureGroup(name="Główne moduły trasy", show=True),
        "budget_base": FeatureGroup(name="Budżetowe bazy pod day tripy", show=True),
        "daytrip": FeatureGroup(name="Day tripy bez noclegu", show=True),
        "rural": FeatureGroup(name="Rural / natura", show=True),
        "food_extension": FeatureGroup(name="Moduły jedzeniowe", show=True),
        "transfer_base": FeatureGroup(name="Bazy transferowe", show=True),
        "optional_extension": FeatureGroup(name="Opcjonalne rozszerzenia", show=False),
    }
    attraction_group = FeatureGroup(name="Atrakcje punktowe", show=True)
    place_marker_names: dict[str, str] = {}
    place_circle_names: dict[str, str] = {}
    place_circle_styles: dict[str, dict[str, Any]] = {}

    for place in places:
        image_path = image_paths.get(place.get("photo_id", ""))
        lodging = int(place["avg_lodging_pln_pp"])
        circle_color = money_color(lodging)
        circle_style = {
            "color": circle_color,
            "fillColor": circle_color,
            "fillOpacity": 0.22,
            "weight": 2,
        }
        circle = folium.CircleMarker(
            location=[place["lat"], place["lon"]],
            radius=max(8, min(26, lodging / 5)),
            color=circle_color,
            fill=True,
            fill_color=circle_color,
            fill_opacity=0.22,
            weight=2,
            tooltip=f"{place['name']}: ok. {lodging} PLN/os./noc",
        )
        place_circle_names[place["id"]] = circle.get_name()
        place_circle_styles[place["id"]] = circle_style
        circle.add_to(groups.get(place["kind"], groups["base"]))

        marker = folium.Marker(
            location=[place["lat"], place["lon"]],
            icon=folium.Icon(color=place_color(place["kind"]), icon="info-sign"),
            popup=folium.Popup(place_popup(place, image_path), max_width=380),
            tooltip=folium.Tooltip(place_tooltip(place, image_path), sticky=False, direction="top", max_width=320),
        )
        place_marker_names[place["id"]] = marker.get_name()
        marker.add_to(groups.get(place["kind"], groups["base"]))

        for attraction in place.get("attractions", []):
            if "lat" not in attraction or "lon" not in attraction:
                continue
            popup = (
                f"<strong>{esc(attraction['name'])}</strong><br>"
                f"{esc(place['name'])}<br>"
                f"{esc(attraction.get('time', ''))}<br>"
                f"{esc(attraction.get('price_pln', ''))}<br>"
                f"{esc(attraction.get('note', ''))}"
            )
            folium.CircleMarker(
                location=[attraction["lat"], attraction["lon"]],
                radius=5,
                color="#111827",
                fill=True,
                fill_color="#facc15",
                fill_opacity=0.9,
                weight=1,
                popup=folium.Popup(popup, max_width=260),
                tooltip=f"{attraction['name']} ({place['name']})",
            ).add_to(attraction_group)

    for group in groups.values():
        group.add_to(fmap)
    attraction_group.add_to(fmap)
    return place_marker_names, place_circle_names, place_circle_styles


def add_routes(
    fmap: folium.Map,
    routes: list[dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
) -> None:
    route_groups = {
        key: FeatureGroup(name=meta["name"], show=bool(meta["show"]))
        for key, meta in ROUTE_LAYERS.items()
    }
    for route in routes:
        coords = route_coords(route, places_by_id)
        layer_key = route_layer_key(route)
        meta = ROUTE_LAYERS[layer_key]
        line_kwargs: dict[str, Any] = {
            "locations": coords,
            "color": meta["color"],
            "weight": meta["weight"],
            "opacity": meta["opacity"],
            "tooltip": folium.Tooltip(
                route_tooltip(route, places_by_id),
                sticky=True,
                direction="top",
                class_name="route-tooltip",
            ),
            "popup": folium.Popup(route_popup(route, places_by_id), max_width=300),
        }
        if meta.get("dash_array"):
            line_kwargs["dash_array"] = meta["dash_array"]
        folium.PolyLine(**line_kwargs).add_to(route_groups[layer_key])
    for route_group in route_groups.values():
        route_group.add_to(fmap)


def build_map() -> None:
    places = load_json(DATA_DIR / "places.json")
    routes = load_json(DATA_DIR / "routes.json")
    provinces = load_json(PROVINCES) if PROVINCES.exists() else {"type": "FeatureCollection", "features": []}
    places_by_id = {place["id"]: place for place in places}

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    manifest = read_image_manifest()
    image_paths = copy_images(places, manifest)

    fmap = folium.Map(
        location=[23.35, 113.0],
        zoom_start=6,
        control_scale=True,
        tiles=None,
        prefer_canvas=True,
    )
    folium.TileLayer("CartoDB positron", name="Jasna mapa", control=True).add_to(fmap)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", control=True).add_to(fmap)
    folium.TileLayer("CartoDB dark_matter", name="Ciemna mapa", control=True).add_to(fmap)

    add_province_layer(fmap, provinces)
    add_routes(fmap, routes, places_by_id)
    place_marker_names, place_circle_names, place_circle_styles = add_place_markers(fmap, places, image_paths)
    fmap.fit_bounds(
        [[min(place["lat"] for place in places), min(place["lon"] for place in places)],
         [max(place["lat"] for place in places), max(place["lon"] for place in places)]],
        padding=(60, 60),
    )

    MiniMap(toggle_display=True, minimized=True).add_to(fmap)
    Fullscreen(position="topleft").add_to(fmap)
    LayerControl(collapsed=True).add_to(fmap)

    fmap.get_root().header.add_child(folium.Element(build_styles()))
    fmap.get_root().html.add_child(folium.Element(build_sidebar(places, routes)))
    fmap.get_root().html.add_child(folium.Element(build_itinerary_panel(places)))
    fmap.get_root().html.add_child(folium.Element(build_legend(provinces)))
    fmap.get_root().html.add_child(
        folium.Element(build_panel_script(place_marker_names, place_circle_names, place_circle_styles))
    )

    fmap.save(OUTPUT)
    html = OUTPUT.read_text(encoding="utf-8").replace(
        "<body>",
        '<body class="trip-panel-hidden legend-hidden">',
        1,
    )
    OUTPUT.write_text("\n".join(line.rstrip() for line in html.splitlines()) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Places: {len(places)}")
    print(f"Routes: {len(routes)}")
    print(f"Provinces: {len(provinces.get('features', []))}")
    print(f"Images copied: {len(image_paths)}")


if __name__ == "__main__":
    build_map()
