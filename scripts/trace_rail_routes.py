"""Trace our train legs along real tracks and store them as route geometry.

Input: an Overpass JSON dump of railway=rail ways (``out skel geom``) for South
China, passed as the first argument. For every leg in RAIL_LEGS the script finds
the shortest path over the track graph between the stations, simplifies it and
writes it into data/routes.json as ``geometry``. The site build stays offline;
re-run this only when the train legs change.

Usage (from the repo root):
    python southern-china-map/scripts/trace_rail_routes.py path/to/rail.json
"""

from __future__ import annotations

import heapq
import json
import math
import sys
from pathlib import Path

ROUTES = Path(__file__).resolve().parents[1] / "data" / "routes.json"

# route id -> list of (lat, lon) stops the train passes, start and end included.
# Intermediate points pin the path to the line the train really uses.
STATIONS = {
    "guangzhou_north": (23.3779, 113.2053),
    "chaoshan": (23.5445, 116.5829),
    "shenzhen_north": (22.6098, 114.0295),
    "west_kowloon": (22.3040, 114.1660),
    "zhuhai": (22.2149, 113.5457),
    "guangzhou_south": (22.9887, 113.2690),
    "guangzhou_east": (23.1505, 113.3245),
    "guangzhou_station": (23.1490, 113.2570),
    "foshan_west": (23.0569, 113.0480),
    "zhaoqing_east": (23.1760, 112.7900),
    "yangshuo": (24.8020, 110.5420),
}
RAIL_LEGS = {
    "guangzhou_chaozhou": ["guangzhou_north", "chaoshan"],
    "chaozhou_hongkong": ["chaoshan", "shenzhen_north", "west_kowloon"],
    "zhuhai_yangshuo": ["zhuhai", "zhaoqing_east", "yangshuo"],
    "yangshuo_zhaoqing": ["yangshuo", "zhaoqing_east"],
    "zhaoqing_guangzhou": ["zhaoqing_east", "guangzhou_south"],
}
# Guangzhou station and Guangzhou East sit on lines missing from the high-speed
# dump, so G2861 is traced to where it leaves that network and finished by hand.
MANUAL_TAILS = {
    "zhaoqing_guangzhou": ((23.1022, 113.1913), ["guangzhou_station", "guangzhou_east"]),
}


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat = math.radians((a[0] + b[0]) / 2)
    return math.hypot(a[0] - b[0], (a[1] - b[1]) * math.cos(lat)) * 111.0


def build_graph(dump: dict) -> tuple[dict[int, tuple[float, float]], dict[int, list[tuple[int, float]]]]:
    coords: dict[int, tuple[float, float]] = {}
    graph: dict[int, list[tuple[int, float]]] = {}
    way_of: dict[int, int] = {}
    for way in dump["elements"]:
        if way.get("type") != "way" or "geometry" not in way:
            continue
        ids, geo = way["nodes"], way["geometry"]
        for node_id, point in zip(ids, geo):
            coords[node_id] = (point["lat"], point["lon"])
            way_of.setdefault(node_id, way["id"])
        for a, b in zip(ids, ids[1:]):
            d = dist(coords[a], coords[b])
            graph.setdefault(a, []).append((b, d))
            graph.setdefault(b, []).append((a, d))
    bridge_gaps(coords, graph, way_of)
    return coords, graph


def bridge_gaps(coords, graph, way_of, max_gap_km: float = 2.0) -> None:
    """Station throats and junctions are often not tagged highspeed=yes, which leaves
    the high-speed network in pieces. Join every dead end to the nearest node of
    another way within max_gap_km, with a penalty so real track is preferred."""
    cell = 0.02
    grid: dict[tuple[int, int], list[int]] = {}
    for node, (lat, lon) in coords.items():
        grid.setdefault((int(lat / cell), int(lon / cell)), []).append(node)
    reach = int(max_gap_km / (111 * cell)) + 1
    for node, edges in list(graph.items()):
        if len(edges) != 1:
            continue
        lat, lon = coords[node]
        gx, gy = int(lat / cell), int(lon / cell)
        best, best_d = None, max_gap_km
        for dx in range(-reach, reach + 1):
            for dy in range(-reach, reach + 1):
                for other in grid.get((gx + dx, gy + dy), []):
                    if way_of.get(other) == way_of.get(node):
                        continue
                    d = dist(coords[node], coords[other])
                    if d < best_d:
                        best, best_d = other, d
        if best is not None:
            graph[node].append((best, best_d * 3))
            graph.setdefault(best, []).append((node, best_d * 3))


def nearest(coords: dict[int, tuple[float, float]], point: tuple[float, float]) -> tuple[int, float]:
    best = min(coords, key=lambda node: dist(coords[node], point))
    return best, dist(coords[best], point)


def candidates(coords: dict[int, tuple[float, float]], point: tuple[float, float]) -> tuple[set[int], float]:
    """All track nodes near a station: parallel tracks and platforms are separate ways,
    so pinning one node can force a detour through the next junction."""
    _, best = nearest(coords, point)
    radius = best + 3.0
    return {node for node, c in coords.items() if dist(c, point) <= radius}, best


def shortest(graph: dict[int, list[tuple[int, float]]], starts: set[int], goals: set[int]) -> list[int]:
    queue = [(0.0, node) for node in starts]
    heapq.heapify(queue)
    seen: dict[int, float] = {node: 0.0 for node in starts}
    prev: dict[int, int] = {}
    reached = None
    while queue:
        cost, node = heapq.heappop(queue)
        if cost > seen.get(node, math.inf):
            continue
        if node in goals:
            reached = node
            break
        for nxt, d in graph.get(node, []):
            new = cost + d
            if new < seen.get(nxt, math.inf):
                seen[nxt] = new
                prev[nxt] = node
                heapq.heappush(queue, (new, nxt))
    if reached is None:
        return []
    path = [reached]
    while path[-1] not in starts:
        path.append(prev[path[-1]])
    return path[::-1]


def simplify(points: list[tuple[float, float]], tolerance_km: float = 0.25) -> list[tuple[float, float]]:
    """Douglas-Peucker, enough to keep curves visible without bloating the HTML."""
    if len(points) < 3:
        return points

    def perp(p, a, b):
        if a == b:
            return dist(p, a)
        lat = math.radians(a[0])
        ax, ay = a[1] * math.cos(lat), a[0]
        bx, by = b[1] * math.cos(lat), b[0]
        px, py = p[1] * math.cos(lat), p[0]
        t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
        return math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay))) * 111.0

    index, far = 0, 0.0
    for i in range(1, len(points) - 1):
        d = perp(points[i], points[0], points[-1])
        if d > far:
            index, far = i, d
    if far <= tolerance_km:
        return [points[0], points[-1]]
    return simplify(points[: index + 1], tolerance_km)[:-1] + simplify(points[index:], tolerance_km)


def main() -> None:
    dump = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    coords, graph = build_graph(dump)
    print(f"track nodes: {len(coords)}")
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    by_id = {route["id"]: route for route in routes}
    for route_id, stops in RAIL_LEGS.items():
        points: list[tuple[float, float]] = []
        ok = True
        last: int | None = None
        for a, b in zip(stops, stops[1:]):
            starts, da = candidates(coords, STATIONS[a])
            if last is not None:
                starts = {last}
            goals, db = candidates(coords, STATIONS[b])
            path = shortest(graph, starts, goals)
            last = path[-1] if path else None
            if not path or da > 20 or db > 20:
                print(f"  {route_id}: no track path {a} -> {b} (snap {da:.1f} / {db:.1f} km)")
                ok = False
                break
            points.extend(coords[node] for node in (path if not points else path[1:]))
        if not ok:
            continue
        if route_id in MANUAL_TAILS:
            cut_point, tail = MANUAL_TAILS[route_id]
            cut = min(range(len(points)), key=lambda i: dist(points[i], cut_point))
            points = points[: cut + 1] + [STATIONS[name] for name in tail]
        line = simplify(points)
        length = sum(dist(p, q) for p, q in zip(points, points[1:]))
        by_id[route_id]["geometry"] = [[round(lat, 5), round(lon, 5)] for lat, lon in line]
        by_id[route_id]["track_traced"] = True
        print(f"  {route_id}: {length:.0f} km of track, {len(line)} points")
    ROUTES.write_text(json.dumps(routes, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
