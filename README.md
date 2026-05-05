# South China Trip Guide

Static map-first guide for planning a winter South China trip.

The generated site is published from `docs/` and is ready for GitHub Pages,
Netlify, Cloudflare Pages, or local browser preview. The map is the entry point:
clicking a place opens a dedicated guide page for that stop.

## What The Site Shows

- Southern China route hubs and optional extensions.
- Average budget lodging price per person per night in PLN.
- Key attractions for each region.
- Travel time and indicative transport cost between places.
- Color-coded province/region layer for Guangdong, Guangxi, Hainan, Fujian,
  Hong Kong, and Macau.
- Hover cards with photos, region descriptions, lodging notes, and priorities.
- Separate map layers for route hubs, optional extensions, day trips, attraction markers, and transport lines.
- Dedicated pages for every mapped place in `docs/places/`.
- Additional guide pages: `itinerary.html`, `food.html`, and `practical.html`.

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

The planning data is in `data/places.json`, `data/routes.json`, and
`data/provinces.geojson`.

All costs are indicative planning ranges in PLN, not live fares. Recheck hotels,
train prices, flights, border crossings, ferry schedules, and attraction opening
hours before booking.

The province layer is a static planning layer generated from a public China
administrative-boundary GeoJSON (`https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json`)
and filtered to the regions relevant to this trip.

Photos are copied from the local illustrated guide asset library and keep the
Wikimedia Commons attribution data in `docs/assets/image_attributions.json`.
