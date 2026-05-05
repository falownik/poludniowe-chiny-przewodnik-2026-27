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


def route_color(mode: str) -> str:
    mode = mode.lower()
    if "flight" in mode:
        return "#d97706"
    if "hsr" in mode or "rail" in mode:
        return "#2563eb"
    if "border" in mode or "ferry" in mode:
        return "#7c3aed"
    return "#0f766e"


def province_style(feature: dict[str, Any]) -> dict[str, Any]:
    color = feature.get("properties", {}).get("color", "#64748b")
    return {
        "fillColor": color,
        "color": color,
        "weight": 1.2,
        "opacity": 0.72,
        "fillOpacity": 0.17,
    }


def province_highlight(feature: dict[str, Any]) -> dict[str, Any]:
    color = feature.get("properties", {}).get("color", "#334155")
    return {
        "fillColor": color,
        "color": color,
        "weight": 2.4,
        "opacity": 0.95,
        "fillOpacity": 0.29,
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
    return f"""
    <div class="route-popup">
      <h3>{esc(from_name)} → {esc(to_name)}</h3>
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
    return (
        '<div class="route-tooltip-card">'
        f"<strong>{esc(from_name)} &rarr; {esc(to_name)}</strong>"
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
    place_rows = "".join(
        f"<tr><td>{esc(place['name'])}</td><td>{esc(place['avg_lodging_pln_pp'])} PLN</td><td>{esc(place['suggested_nights'])}</td></tr>"
        for place in sorted(places, key=lambda item: item["avg_lodging_pln_pp"])
    )
    route_rows = "".join(
        f"<tr><td>{esc(route['from'])} → {esc(route['to'])}</td><td>{esc(route['time'])}</td></tr>"
        for route in routes
        if route["from"] != route["to"]
    )
    return f"""
    <button id="trip-panel-toggle" class="panel-toggle panel-toggle-left" type="button" aria-controls="trip-panel" aria-expanded="true">Ukryj panel</button>
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
      <p>Koszt przejazdu pojawia się dopiero po najechaniu na linię na mapie; panel zostawia tylko czas, żeby nie zaśmiecać widoku.</p>
      <table>
        <thead><tr><th>Odcinek</th><th>Czas</th></tr></thead>
        <tbody>{route_rows}</tbody>
      </table>
    </div>
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
      #trip-panel h1 { font-size: 18px; margin: 0 0 8px; }
      #trip-panel h2 { font-size: 14px; margin: 14px 0 6px; }
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
      .legend h3 { margin: 0 0 6px; font-size: 13px; }
      .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
      .province-box {
        display: inline-block;
        width: 13px;
        height: 9px;
        border-radius: 2px;
        margin-right: 6px;
        border: 1px solid rgba(15,23,42,0.28);
        vertical-align: -1px;
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
        .legend {
          right: 8px;
          bottom: 52px;
          max-width: min(260px, calc(100vw - 16px));
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
        f"<div><span class=\"province-box\" style=\"background:{esc(feature['properties'].get('color', '#64748b'))}\"></span>"
        f"{esc(feature['properties'].get('name', 'Region'))}</div>"
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
    <button id="legend-toggle" class="panel-toggle panel-toggle-right" type="button" aria-controls="map-legend" aria-expanded="true">Ukryj legendę</button>
    <div id="map-legend" class="legend">
      <h3>Nocleg / osoba / noc</h3>
      <div><span class="dot" style="background:#16803c"></span>do 50 PLN</div>
      <div><span class="dot" style="background:#d88900"></span>51-75 PLN</div>
      <div><span class="dot" style="background:#d46a00"></span>76-120 PLN</div>
      <div><span class="dot" style="background:#b42318"></span>120+ PLN / day trip</div>
      {province_section}
      <hr>
      <div style="color:#2563eb">niebieski: kolej/HSR</div>
      <div style="color:#d97706">pomarańczowy: lot</div>
      <div style="color:#7c3aed">fioletowy: granica/prom</div>
    </div>
    """


def build_panel_script() -> str:
    return """
    <script>
      (function () {
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
        bindPanelToggle("trip-panel-toggle", "trip-panel-hidden", "Ukryj panel", "Pokaż panel");
        bindPanelToggle("legend-toggle", "legend-hidden", "Ukryj legendę", "Pokaż legendę");
      })();
    </script>
    """


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
) -> None:
    groups = {
        "base": FeatureGroup(name="Bazy i kotwice trasy", show=True),
        "main_route": FeatureGroup(name="Główne moduły trasy", show=True),
        "budget_base": FeatureGroup(name="Budżetowe bazy pod day tripy", show=True),
        "daytrip": FeatureGroup(name="Day tripy bez noclegu", show=True),
        "rural": FeatureGroup(name="Rural / natura", show=True),
        "food_extension": FeatureGroup(name="Moduły jedzeniowe", show=True),
        "transfer_base": FeatureGroup(name="Bazy transferowe", show=False),
        "optional_extension": FeatureGroup(name="Opcjonalne rozszerzenia", show=False),
    }
    attraction_group = FeatureGroup(name="Atrakcje punktowe", show=True)

    for place in places:
        image_path = image_paths.get(place.get("photo_id", ""))
        lodging = int(place["avg_lodging_pln_pp"])
        folium.CircleMarker(
            location=[place["lat"], place["lon"]],
            radius=max(8, min(26, lodging / 5)),
            color=money_color(lodging),
            fill=True,
            fill_color=money_color(lodging),
            fill_opacity=0.22,
            weight=2,
            tooltip=f"{place['name']}: ok. {lodging} PLN/os./noc",
        ).add_to(groups.get(place["kind"], groups["base"]))

        marker = folium.Marker(
            location=[place["lat"], place["lon"]],
            icon=folium.Icon(color=place_color(place["kind"]), icon="info-sign"),
            popup=folium.Popup(place_popup(place, image_path), max_width=380),
            tooltip=folium.Tooltip(place_tooltip(place, image_path), sticky=False, direction="top", max_width=320),
        )
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


def add_routes(
    fmap: folium.Map,
    routes: list[dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
) -> None:
    route_group = FeatureGroup(name="Przejazdy i koszt transportu", show=True)
    for route in routes:
        coords = route_coords(route, places_by_id)
        color = route_color(route["mode"])
        folium.PolyLine(
            locations=coords,
            color=color,
            weight=6,
            opacity=0.82,
            tooltip=folium.Tooltip(
                route_tooltip(route, places_by_id),
                sticky=True,
                direction="top",
                class_name="route-tooltip",
            ),
            popup=folium.Popup(route_popup(route, places_by_id), max_width=300),
        ).add_to(route_group)
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
    add_place_markers(fmap, places, image_paths)

    MiniMap(toggle_display=True, minimized=True).add_to(fmap)
    Fullscreen(position="topleft").add_to(fmap)
    LayerControl(collapsed=True).add_to(fmap)

    fmap.get_root().header.add_child(folium.Element(build_styles()))
    fmap.get_root().html.add_child(folium.Element(build_sidebar(places, routes)))
    fmap.get_root().html.add_child(folium.Element(build_legend(provinces)))
    fmap.get_root().html.add_child(folium.Element(build_panel_script()))

    fmap.save(OUTPUT)
    OUTPUT.write_text(
        "\n".join(line.rstrip() for line in OUTPUT.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT}")
    print(f"Places: {len(places)}")
    print(f"Routes: {len(routes)}")
    print(f"Provinces: {len(provinces.get('features', []))}")
    print(f"Images copied: {len(image_paths)}")


if __name__ == "__main__":
    build_map()
