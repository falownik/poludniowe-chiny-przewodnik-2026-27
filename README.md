# South China Trip Guide

Static map-first guide for planning a winter South China trip.

The generated site is published from `docs/` and is ready for GitHub Pages,
Netlify, Cloudflare Pages, or local browser preview. The map is the entry point:
clicking a place opens a dedicated guide page for that stop.

## What The Site Shows

- Current South China route hubs and optional extensions after trimming Hainan,
  Fujian, Yunnan, Guizhou, and Sichuan from this version.
- Average budget lodging price per person per night in PLN.
- Key attractions for each region.
- Travel time and indicative transport cost between places.
- Color-coded province/region layer for Guangdong, Guangxi, Hong Kong, and Macau.
- Hover cards with photos, region descriptions, lodging notes, and priorities.
- Separate map layers for route hubs, optional extensions, day trips, attraction markers, and transport lines.
- Dedicated pages for every mapped place in `docs/places/`.
- Additional guide pages: `itinerary.html`, `research.html`, `food.html`, and `practical.html`.
- Excel-friendly UTF-8 CSV exports in `docs/assets/route_costs.csv` and
  `docs/assets/itinerary.csv`.

## Build

From the repository root:

```powershell
& '..\.venv\Scripts\python.exe' .\scripts\build_site.py
```

Or from the parent project root:

```powershell
& '.\.venv\Scripts\python.exe' '.\southern-china-map\scripts\build_site.py'
```

Open:

```text
docs/index.html
```

Validation:

```powershell
& '.\.venv\Scripts\python.exe' '.\southern-china-map\scripts\verify_map.py'
```

## Free Hosting

### GitHub Pages

1. Create a GitHub repository.
2. Push this folder as the repository contents.
3. In GitHub, go to `Settings -> Pages`.
4. Set source to `Deploy from a branch`.
5. Select branch `main` and folder `/docs`.
6. The map will be available at `https://<user>.github.io/<repo>/`.

### Netlify

Drag the `docs/` folder into Netlify Drop, or connect the repository and set
publish directory to `docs`.

## Data

The core planning data is in `data/places.json`, `data/routes.json`, and
`data/provinces.geojson`.

Decision-support data lives in:

- `data/nearby_places.json` for the optional research map layer.
- `data/hub_playbooks.json` for hub-by-hub rules on transport, budget, weather,
  and what to skip.
- `data/predeparture_checks.json` for formal/logistical checks before travel.
- `data/formality_scenarios.json` for the January 2027 visa-free contingency.
- `data/attraction_budget_pln.json` for the 500 PLN/person attraction-budget
  decision section.

All costs are indicative planning ranges in PLN, not live fares. Recheck hotels,
train prices, flights, border crossings, ferry schedules, and attraction opening
hours before booking.

The province layer is a static planning layer generated from a public China
administrative-boundary GeoJSON (`https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json`)
and filtered to the regions relevant to this trip.

Photos are copied from the local illustrated guide asset library and keep the
Wikimedia Commons attribution data in `docs/assets/image_attributions.json`.
