from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import build_map


ROOT = build_map.ROOT
DOCS_DIR = build_map.DOCS_DIR
ASSET_DIR = build_map.ASSET_DIR
PLACES_DIR = DOCS_DIR / "places"
SITE_CSS = ASSET_DIR / "site.css"


FOOD_NOTES: dict[str, list[str]] = {
    "guangzhou": [
        "Rano zaplanuj yum cha: herbata, har gow, siu mai, char siu bao i ryżowe rolki. To najlepszy pierwszy kontakt z Kantonem.",
        "W Liwan szukaj wonton noodles, roast meats i deserów mlecznych. Najlepszy dzień w Guangzhou zaczyna się od śniadania, nie od muzeum.",
        "Wieczorem dobrze działają proste kantońskie kolacje: ryba na parze, warzywa z czosnkiem, claypot rice i zupy długo gotowane.",
    ],
    "shunde_foshan": [
        "Shunde traktuj jak kulinarny day trip: mleczne desery, ryby, hotpot, smażone mleko i spokojniejsza kuchnia kantońska.",
        "Foshan daje kontekst Lingnan, ale największy sens ma wtedy, gdy połączysz go z konkretnym posiłkiem w Shunde.",
    ],
    "hainan": [
        "Na Hainanie jedz Wenchang chicken, coconut chicken hot pot, qingbuliang i owoce morza z jasno podaną ceną za wagę.",
        "Haikou jest lepsze na lokalne przekąski i kawę, Sanya na plażę i odpoczynek. Nie traktuj całej wyspy jak jednego kurortu.",
    ],
    "zhuhai": [
        "Zhuhai jest bazą, nie kulinarnym finałem. Najpraktyczniej jeść prosto przy Gongbei i przeznaczyć budżet jedzeniowy na Makao.",
        "Jeśli zostajesz wieczorem, szukaj owoców morza i kantońskich lokali w okolicach granicy albo przy nadmorskim spacerze.",
    ],
    "macau": [
        "Makao to egg tarty, pork chop bun, minchi, African chicken i portugalsko-kantońska kuchnia w wąskich ulicach starego miasta.",
        "Najlepiej zjeść coś małego przy Senado/St. Paul's, potem zrobić Taipa Village albo Coloane jako osobny blok jedzeniowy.",
    ],
    "longji": [
        "W Longji jedzenie jest proste: ryż, bambusowy ryż, warzywa, lokalny kurczak, zupy i dania z guesthouse'u.",
        "Nie planuj tu fine diningu. Warto zjeść kolację w noclegu, bo po zmroku chodzenie po schodach i szukanie lokali jest słabe logistycznie.",
    ],
    "yangshuo": [
        "Yangshuo ma beer fish, ryżowe makarony, lokalne stir-fry i kawiarnie dla turystów. Najlepsze posiłki są często poza West Street.",
        "Na dzień rowerowy bierz lekkie śniadanie, wodę i przerwę na lunch przy Yulong River, zamiast wracać do centrum w południe.",
    ],
    "guilin": [
        "Guilin rice noodles są obowiązkowym śniadaniem. Bierz lokal mały, ruchliwy i bez wielkiego turystycznego wystroju.",
        "Guilin dobrze działa jako przesiadka: prosty obiad, spacer po jeziorach i następnego dnia wyjazd w krajobraz.",
    ],
    "shenzhen": [
        "Shenzhen nie ma jednej klasycznej kuchni miasta, ale ma świetny przekrój migracyjnych Chin: kantońskie, Chaoshan, Hunan, Sichuan i food courty.",
        "Przy krótkim pobycie jedz praktycznie: Huaqiangbei/Futian na szybki lunch, wieczorem Nanshan albo Shekou, jeśli chcesz dłuższy spacer.",
    ],
    "hongkong": [
        "Hongkong to cha chaan teng, milk tea, pineapple bun, wonton noodles, roast goose, dim sum i street snacks w Kowloonie.",
        "Przy day tripie nie rozciągaj listy. Wybierz jeden klasyk śniadaniowy, jeden portowy spacer i jeden posiłek w Kowloonie.",
    ],
    "chaozhou": [
        "Chaoshan jest jednym z najmocniejszych modułów jedzeniowych: gęś w marynacie, wołowy hot pot, congee, oyster omelette i herbata gongfu.",
        "Nie próbuj jeść wszystkiego jednego wieczoru. Lepsze są dwa wolniejsze posiłki i jedna herbata niż chaotyczna lista lokali.",
    ],
    "xiamen": [
        "Xiamen to satay noodles, oyster omelette, peanut soup, owoce morza, herbata i dobry wstęp do świata Hakka/tulou.",
        "Jeśli robisz tulou, zostaw jeden spokojny posiłek na Xiamen po powrocie. Długie wycieczki do tulou potrafią zjeść cały dzień.",
    ],
}


PRACTICAL_NOTES: dict[str, list[str]] = {
    "guangzhou": [
        "Najlepsza kotwica przylotu i wylotu. Ostatnią noc przed lotem trzymaj w Guangzhou, nie w Hongkongu, Makao ani Yangshuo.",
        "Po przylocie o późnej porze najprościej jechać do hotelu w mieście albo spać przy lotnisku. Nie planuj nocnego transferu do innego regionu.",
    ],
    "hainan": [
        "Hainan jest ciepły, ale transport i noclegi potrafią podbić budżet. Trzymaj moduł krótko, jeśli limit 8k ma zostać realny.",
        "Najtańsze decyzje zapadają przy wyborze bazy: Dadonghai, Sanya city, Haikou lub Wanning są zwykle rozsądniejsze niż topowe resorty.",
    ],
    "zhuhai": [
        "To praktyczna baza do Makao. Śpij blisko Gongbei/Hengqin, jeśli zależy ci na tanim day tripie i prostym powrocie.",
        "Granica może zająć 30-90 minut. Nie planuj ciasnych rezerwacji zaraz po przejściu.",
    ],
    "macau": [
        "Makao traktuj jako osobny byt graniczny. Paszport, waluta i transport działają inaczej niż w Chinach kontynentalnych.",
        "Przy waszym budżecie nocleg w Makao jest wyjątkiem, nie bazą. Zhuhai zwykle daje dużo lepszą kontrolę kosztu.",
    ],
    "hongkong": [
        "Hongkong jako day trip z Shenzhen jest sensowny, ale Sylwester bez noclegu będzie logistycznie trudny przez tłumy i ograniczenia przy porcie.",
        "Bierz Octopus albo kartę płatniczą i zaplanuj powrót do Shenzhen z dużym buforem na granicę.",
    ],
    "yangshuo": [
        "To najlepszy rural/natura moduł przy budżecie około 50 PLN/os./noc. Daj mu kilka nocy, bo zyskuje po zwolnieniu tempa.",
        "Najlepsza baza zależy od stylu: centrum dla logistyki, Yulong River dla krajobrazu i ciszy.",
    ],
    "longji": [
        "Bierz mały bagaż. Schody i wilgoć są realne, a zimą ogrzewanie w guesthouse'ach trzeba sprawdzić przed rezerwacją.",
        "Longji ma sens z noclegiem albo bardzo świadomym day tripem. Najlepsze światło jest rano.",
    ],
    "guilin": [
        "Guilin jest bramą, niekoniecznie główną bazą. Użyj go do HSR, Li River i Longji, a dłużej śpij w Yangshuo.",
    ],
    "xiamen": [
        "Xiamen jest opcją zamiast Hainanu albo dodatkowym modułem, jeśli chcecie herbatę, wybrzeże i tulou. Nie dokładaj go bez cięcia czegoś innego.",
    ],
}


FOOD_DISHES: list[dict[str, str]] = [
    {
        "region": "Guangzhou / Guangdong",
        "name": "Har gow",
        "chinese": "虾饺",
        "pinyin": "xiā jiǎo",
        "image_id": "dim_sum_har_gow",
        "where": "Yum cha w Guangzhou, Hongkongu i Makao.",
        "order": "Zamawiaj gorące, najlepiej jako pierwszą porcję dim sum. Dobra wersja ma cienkie, półprzezroczyste ciasto i sprężystą krewetkę.",
    },
    {
        "region": "Guangdong",
        "name": "Char siu",
        "chinese": "叉烧",
        "pinyin": "chāshāo",
        "image_id": "char_siu",
        "where": "Siu mei shops, lokale z pieczonym mięsem, proste zestawy z ryżem.",
        "order": "Szukaj mięsa z przypieczonym brzegiem i soczystym środkiem. Najlepsze jest lekko słodkie, ale nie powinno smakować jak cukierkowa glazura.",
    },
    {
        "region": "Guangdong / Hongkong",
        "name": "Pieczona gęś",
        "chinese": "烧鹅",
        "pinyin": "shāo'é",
        "image_id": "roast_goose",
        "where": "Hongkong, Guangzhou i lepsze lokale kantońskie.",
        "order": "To danie na wspólny stół albo większy lunch. Skóra ma być ciemna, lśniąca i chrupiąca, a mięso tłustsze niż kaczka.",
    },
    {
        "region": "Guangzhou / Hongkong",
        "name": "Wonton noodles",
        "chinese": "云吞面",
        "pinyin": "yúntūn miàn",
        "image_id": "wonton_noodles",
        "where": "Małe lokale śniadaniowe i lunchowe w Guangdong i HK.",
        "order": "Dobra miska ma cienki, sprężysty makaron, czysty bulion i wontony z wyraźną krewetką. To bezpieczny wybór pierwszego dnia.",
    },
    {
        "region": "Guilin / Guangxi",
        "name": "Guilin rice noodles",
        "chinese": "桂林米粉",
        "pinyin": "Guìlín mǐfěn",
        "image_id": "guilin_rice_noodles",
        "where": "Guilin rano, blisko dworca, targu albo osiedlowych ulic.",
        "order": "Nie szukaj najładniejszej sali. Szukaj szybkiej rotacji, misek na ladzie i lokalnych klientów jedzących przed pracą.",
    },
    {
        "region": "Hainan",
        "name": "Hainanese chicken rice",
        "chinese": "海南鸡饭",
        "pinyin": "Hǎinán jī fàn",
        "image_id": "hainan_chicken_rice",
        "where": "Haikou, Sanya, Wenchang chicken restaurants.",
        "order": "W lokalnej wersji ważniejszy jest kurczak niż idealnie wygładzona singapurska estetyka. Bierz sos imbirowy, chili i ryż z bulionu.",
    },
    {
        "region": "Hongkong",
        "name": "Egg waffle",
        "chinese": "鸡蛋仔",
        "pinyin": "jīdànzǎi",
        "image_id": "hongkong_egg_waffle",
        "where": "Mong Kok, Tsim Sha Tsui, Causeway Bay i uliczne stoiska.",
        "order": "Jedz od razu po wydaniu. Dobra wersja jest chrupiąca na zewnątrz, miękka w środku i nie wymaga dużej liczby dodatków.",
    },
    {
        "region": "Hongkong",
        "name": "Milk tea",
        "chinese": "奶茶",
        "pinyin": "nǎichá",
        "image_id": "milk_tea",
        "where": "Cha chaan teng, zwłaszcza przy śniadaniu albo szybkim lunchu.",
        "order": "Zamów gorącą albo na lodzie. To gorzka, mocna herbata z mlekiem, nie deserowy bubble tea.",
    },
    {
        "region": "Hongkong",
        "name": "Pineapple bun",
        "chinese": "菠萝包",
        "pinyin": "bōluó bāo",
        "image_id": "pineapple_bun",
        "where": "Piekarnie i cha chaan teng.",
        "order": "Nazwa nie oznacza ananasa. Chodzi o kruchą, słodką skórkę. Wersja z masłem jest cięższa, ale klasyczna.",
    },
    {
        "region": "Makao",
        "name": "Makaoska egg tart",
        "chinese": "葡挞",
        "pinyin": "pútà",
        "image_id": "macau_egg_tart",
        "where": "Taipa, Coloane, okolice starego miasta.",
        "order": "Najlepsza jest ciepła, z listkowym ciastem i lekko skarmelizowaną górą. Nie kupuj jednej na cztery osoby.",
    },
    {
        "region": "Fujian",
        "name": "Da Hong Pao",
        "chinese": "大红袍",
        "pinyin": "dàhóngpáo",
        "image_id": "dahongpao_tea",
        "where": "Xiamen, sklepy herbaciane, Wuyi Shan jako osobny moduł.",
        "order": "Nie kupuj drogiej herbaty bez degustacji. Pytaj o kilka parzeń i zapisz cenę za gram, nie tylko za opakowanie.",
    },
    {
        "region": "Fujian / Xiamen",
        "name": "Satay noodles",
        "chinese": "沙茶面",
        "pinyin": "shāchá miàn",
        "image_id": "xiamen_gulangyu",
        "where": "Xiamen, proste lokale w Siming i okolicach Zhongshan Road.",
        "order": "To danie do zjedzenia w Xiamen przed albo po Gulangyu. Sos shacha jest orzechowo-morski, więc osoby z alergiami powinny uważać.",
    },
]


FOOD_IMAGE_IDS = {dish["image_id"] for dish in FOOD_DISHES if dish.get("image_id")}


def esc(value: Any) -> str:
    return build_map.esc(value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def image_paths_from_attributions() -> dict[str, str]:
    path = ASSET_DIR / "image_attributions.json"
    if not path.exists():
        return {}
    return {item["id"]: item["file"] for item in load_json(path)}


def copy_extra_images(image_ids: set[str]) -> None:
    if not image_ids:
        return

    manifest = build_map.read_image_manifest()
    build_map.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    attribution_path = ASSET_DIR / "image_attributions.json"
    attributions = load_json(attribution_path) if attribution_path.exists() else []
    known_ids = {item["id"] for item in attributions}

    for image_id in sorted(image_ids):
        if image_id in known_ids:
            continue
        item = manifest.get(image_id)
        if not item:
            continue
        source = build_map.GUIDE_ROOT / item["file"]
        if not source.exists():
            continue
        target = build_map.IMAGE_DIR / source.name
        shutil.copy2(source, target)
        attributions.append(
            {
                "id": image_id,
                "title": item.get("title", ""),
                "commons_title": item.get("commons_title", ""),
                "artist": item.get("artist", ""),
                "license": item.get("license", ""),
                "source": item.get("source", ""),
                "file": f"assets/images/{target.name}",
            }
        )
        known_ids.add(image_id)

    attribution_path.write_text(json.dumps(attributions, ensure_ascii=False, indent=2), encoding="utf-8")


def image_tag(image_id: str, image_paths: dict[str, str], alt: str, prefix: str = "") -> str:
    path = image_paths.get(image_id)
    if not path:
        return ""
    return f"<img src=\"{prefix}{esc(path)}\" alt=\"{esc(alt)}\">"


def nav(prefix: str, current: str) -> str:
    items = [
        ("map", "Mapa", f"{prefix}index.html"),
        ("places", "Miejsca", f"{prefix}places/"),
        ("itinerary", "Trasa", f"{prefix}itinerary.html"),
        ("food", "Jedzenie", f"{prefix}food.html"),
        ("practical", "Logistyka", f"{prefix}practical.html"),
    ]
    links = "".join(
        f"<a class=\"{'active' if key == current else ''}\" href=\"{href}\">{label}</a>"
        for key, label, href in items
    )
    return f"""
    <header class="site-header">
      <a class="brand" href="{prefix}index.html">Południe Chin 2026/27</a>
      <nav>{links}</nav>
    </header>
    """


def page_shell(title: str, current: str, body: str, prefix: str = "") -> str:
    return f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · Południe Chin 2026/27</title>
  <link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
  {nav(prefix, current)}
  <main>
    {body}
  </main>
  <footer class="site-footer">
    <p>Plan statyczny do GitHub Pages. Ceny i czasy są orientacyjne w PLN; przed rezerwacją sprawdź aktualne rozkłady, bilety i zasady graniczne.</p>
  </footer>
</body>
</html>
"""


def image_src(place: dict[str, Any], image_paths: dict[str, str], prefix: str) -> str:
    path = image_paths.get(place.get("photo_id", ""))
    return f"{prefix}{path}" if path else ""


def nearby_routes(place_id: str, routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [route for route in routes if route["from"] == place_id or route["to"] == place_id]


def route_card(route: dict[str, Any], places_by_id: dict[str, dict[str, Any]], prefix: str) -> str:
    from_place = places_by_id[route["from"]]
    to_place = places_by_id[route["to"]]
    from_href = f"{prefix}places/{route['from']}.html"
    to_href = f"{prefix}places/{route['to']}.html"
    if prefix == "../":
        from_href = f"{route['from']}.html"
        to_href = f"{route['to']}.html"
    return f"""
    <article class="route-card">
      <h3><a href="{from_href}">{esc(from_place['name'])}</a> → <a href="{to_href}">{esc(to_place['name'])}</a></h3>
      <p><strong>{esc(route['mode'])}</strong> · {esc(route['time'])} · {esc(route['cost_pln'])}</p>
      <p>{esc(route['note'])}</p>
    </article>
    """


def place_card(place: dict[str, Any], image_paths: dict[str, str], prefix: str) -> str:
    img = image_src(place, image_paths, prefix)
    image = f"<img src=\"{esc(img)}\" alt=\"{esc(place['name'])}\">" if img else ""
    href = f"{prefix}places/{place['id']}.html"
    if prefix == "../":
        href = f"{place['id']}.html"
    return f"""
    <article class="place-card">
      <a href="{href}">
        {image}
        <div>
          <p class="eyebrow">{esc(place['region'])}</p>
          <h2>{esc(place['name'])}</h2>
          <p>{esc(place['summary'])}</p>
          <p class="meta">{esc(place['suggested_nights'])} · ok. {esc(place['avg_lodging_pln_pp'])} PLN/os./noc</p>
        </div>
      </a>
    </article>
    """


def build_place_page(
    place: dict[str, Any],
    places: list[dict[str, Any]],
    routes: list[dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
    image_paths: dict[str, str],
) -> str:
    prefix = "../"
    img = image_src(place, image_paths, prefix)
    image = f"<img class=\"hero-img\" src=\"{esc(img)}\" alt=\"{esc(place['name'])}\">" if img else ""
    bullets = "".join(f"<li>{esc(item)}</li>" for item in place.get("what_to_see", []))
    attractions = "".join(
        f"""
        <article class="detail-row">
          <h3>{esc(item['name'])}</h3>
          <p>{esc(item.get('time', ''))} · {esc(item.get('price_pln', ''))}</p>
          <p>{esc(item.get('note', ''))}</p>
        </article>
        """
        for item in place.get("attractions", [])
    )
    food = "".join(f"<p>{esc(item)}</p>" for item in FOOD_NOTES.get(place["id"], FOOD_NOTES.get(place["region"].lower(), [])))
    if not food:
        food = "<p>Jedzenie planuj regionalnie: najpierw lokalne śniadanie, potem jeden mocny posiłek charakterystyczny dla regionu, a dopiero na końcu przypadkowe przekąski.</p>"
    practical = "".join(f"<p>{esc(item)}</p>" for item in PRACTICAL_NOTES.get(place["id"], []))
    if not practical:
        practical = f"<p>{esc(place['budget_note'])}</p>"
    related_routes = "".join(route_card(route, places_by_id, prefix) for route in nearby_routes(place["id"], routes))

    index = places.index(place)
    prev_place = places[index - 1] if index > 0 else None
    next_place = places[index + 1] if index + 1 < len(places) else None
    pager_items = []
    if prev_place:
        pager_items.append(f"<a href=\"{prev_place['id']}.html\">← {esc(prev_place['name'])}</a>")
    pager_items.append("<a href=\"index.html\">Wszystkie miejsca</a>")
    if next_place:
        pager_items.append(f"<a href=\"{next_place['id']}.html\">{esc(next_place['name'])} →</a>")
    pager = "".join(pager_items)

    body = f"""
    <section class="place-hero">
      {image}
      <div class="hero-copy">
        <p class="eyebrow">{esc(place['region'])} · {esc(place['priority'])}</p>
        <h1>{esc(place['name'])}</h1>
        <p>{esc(place['summary'])}</p>
        <div class="fact-strip">
          <span>{esc(place['suggested_nights'])}</span>
          <span>ok. {esc(place['avg_lodging_pln_pp'])} PLN/os./noc</span>
          <span>{esc(place['lodging_range_pln_pp'])}</span>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <article class="main-copy">
        <h2>Po co tu jechać</h2>
        <p>{esc(place['summary'])}</p>
        <ul>{bullets}</ul>

        <h2>Atrakcje i rytm dnia</h2>
        <div class="detail-list">{attractions}</div>

        <h2>Jedzenie</h2>
        {food}

        <h2>Nocleg i budżet</h2>
        <p><strong>Noclegi:</strong> {esc(place['lodging_range_pln_pp'])}</p>
        <p><strong>Ocena budżetowa:</strong> {esc(place['budget_note'])}</p>
      </article>

      <aside class="side-panel">
        <h2>Logistyka</h2>
        {practical}
        <a class="primary-link" href="../index.html">Wróć do mapy</a>
      </aside>
    </section>

    <section class="route-section">
      <h2>Połączenia z mapy</h2>
      <div class="route-grid">{related_routes}</div>
    </section>

    <nav class="pager">{pager}</nav>
    """
    return page_shell(place["name"], "places", body, prefix=prefix)


def build_places_index(places: list[dict[str, Any]], image_paths: dict[str, str]) -> str:
    prefix = "../"
    cards = "".join(place_card(place, image_paths, prefix) for place in places)
    body = f"""
    <section class="page-intro">
      <p class="eyebrow">Indeks miejsc</p>
      <h1>Miejsca w aktualnym planie</h1>
      <p>To jest wersja realna czasowo: Guangdong, Guangxi, Hainan, Fujian oraz day tripy do Hongkongu i Makao. Każda karta prowadzi do osobnej strony z logistyką, jedzeniem, atrakcjami i połączeniami.</p>
    </section>
    <section class="place-grid">{cards}</section>
    """
    return page_shell("Miejsca", "places", body, prefix=prefix)


def build_itinerary_page(
    places: list[dict[str, Any]],
    routes: list[dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
    image_paths: dict[str, str],
) -> str:
    cards = "".join(route_card(route, places_by_id, "") for route in routes if route["from"] != route["to"])
    lodging_avg = round(sum(int(place["avg_lodging_pln_pp"]) for place in places) / len(places))
    transport_mid = sum(int(route.get("cost_mid_pln", 0)) for route in routes)
    highlight_cards = "".join(place_card(place, image_paths, "") for place in places[:4])
    body = f"""
    <section class="page-intro">
      <p class="eyebrow">Trasa robocza</p>
      <h1>Układ podróży i przejazdy</h1>
      <p>Mapa nie jest sztywnym planem dzień po dniu. To zestaw modułów, które można składać pod osoby jadące na 2 i 3 tygodnie: start w Guangzhou, rural Guangxi, ciepły Hainan, day tripy HK/Makao i opcjonalny Fujian/Chaoshan.</p>
      <div class="fact-strip">
        <span>{len(places)} miejsc</span>
        <span>{len(routes)} odcinków</span>
        <span>średni nocleg ok. {lodging_avg} PLN/os./noc</span>
        <span>transport orientacyjnie {transport_mid} PLN przy przejściu wszystkich odcinków</span>
      </div>
    </section>
    <section class="place-grid compact">{highlight_cards}</section>
    <section class="route-section">
      <h2>Odcinki</h2>
      <div class="route-grid">{cards}</div>
    </section>
    """
    return page_shell("Trasa", "itinerary", body)


def build_food_page(image_paths: dict[str, str]) -> str:
    region_cards = [
        {
            "title": "Guangdong: yum cha, pieczone mięsa i proste klasyki",
            "image_id": "dim_sum_har_gow",
            "text": "Najważniejszy jest rytm jedzenia. Rano dim sum i herbata, w południe wonton noodles albo roast meat rice, wieczorem ryba na parze, warzywa i claypot rice. W Shunde/Foshan warto myśleć o deserach mlecznych, rybach i spokojniejszej kuchni kantońskiej.",
            "must": "Har gow, siu mai, char siu, roast goose, wonton noodles, double-skin milk.",
        },
        {
            "title": "Chaoshan: Chaozhou i Shantou jako moduł foodie",
            "image_id": "chaozhou_guangji",
            "text": "Chaoshan to osobny świat: gęś w marynacie lushui, wołowy hot pot bez syczuańskiego ognia, congee, oyster omelette i herbata gongfu. Najlepiej dać temu regionowi dwie noce, bo jedzenie jest główną atrakcją, nie dodatkiem.",
            "must": "Lushui goose, Chaoshan beef hot pot, oyster omelette, Chaozhou congee, gongfu tea.",
        },
        {
            "title": "Guangxi: śniadania makaronowe i jedzenie po dniu w krajobrazie",
            "image_id": "guilin_rice_noodles",
            "text": "Guilin rice noodles są śniadaniem obowiązkowym. Yangshuo daje beer fish i proste posiłki po dniu rowerowym, a Longji działa guesthouse'owo: ciepła kolacja, ryż, warzywa i lokalny kurczak po zejściu z tarasów.",
            "must": "Guilin rice noodles, beer fish, bamboo rice, lokalne warzywa, oil tea.",
        },
        {
            "title": "Hainan: kurczak, kokos, kawa i seafood",
            "image_id": "hainan_chicken_rice",
            "text": "Hainan to Wenchang chicken, coconut chicken hot pot, qingbuliang, kawa z wyspy i owoce morza. Przy seafood zawsze ustal cenę za wagę i sposób przygotowania przed gotowaniem.",
            "must": "Hainanese chicken rice, coconut chicken hot pot, qingbuliang, Xinglong coffee.",
        },
        {
            "title": "Fujian i Xiamen: shacha, oolong i morska kuchnia",
            "image_id": "dahongpao_tea",
            "text": "Xiamen jest morsko-herbaciany: satay noodles, oyster omelette, peanut soup, oolong i ewentualny wypad do tulou Hakka. To dobra alternatywa dla Hainanu, jeśli chcecie mniej plaż, więcej architektury i herbaty.",
            "must": "Satay noodles, oyster omelette, peanut soup, Da Hong Pao, Tieguanyin.",
        },
        {
            "title": "Hongkong i Makao: szybkie śniadania, przekąski i fusion",
            "image_id": "macau_egg_tart",
            "text": "Hongkong najlepiej działa przez cha chaan teng, milk tea, wonton noodles, Star Ferry i Kowloon. Makao przez egg tarty, pork chop bun, minchi, African chicken i kontrast między starym centrum a Cotai.",
            "must": "Milk tea, pineapple bun, egg waffle, Portuguese egg tart, pork chop bun, minchi.",
        },
    ]
    rows = "".join(
        f"""
        <article class="food-region-card">
          {image_tag(item["image_id"], image_paths, item["title"])}
          <div>
            <h2>{esc(item["title"])}</h2>
            <p>{esc(item["text"])}</p>
            <p><strong>Must eat:</strong> {esc(item["must"])}</p>
          </div>
        </article>
        """
        for item in region_cards
    )
    dish_cards = "".join(
        f"""
        <article class="dish-card">
          {image_tag(dish["image_id"], image_paths, dish["name"])}
          <div>
            <p class="eyebrow">{esc(dish["region"])}</p>
            <h2>{esc(dish["name"])}</h2>
            <p class="dish-name">{esc(dish["chinese"])} · {esc(dish["pinyin"])}</p>
            <p><strong>Gdzie:</strong> {esc(dish["where"])}</p>
            <p>{esc(dish["order"])}</p>
          </div>
        </article>
        """
        for dish in FOOD_DISHES
    )
    checklist = [
        "W Guangzhou pierwszy pełny poranek przeznacz na yum cha, nie na atrakcję biletowaną.",
        "W Chaoshan zaplanuj co najmniej jeden posiłek jako główny punkt dnia: gęś albo wołowy hot pot.",
        "W Guilin jedz ryżowe makarony rano; wieczorem lepiej nie szukać fine diningu, tylko prostego lokalnego jedzenia.",
        "W Yangshuo nie siedź wyłącznie na West Street. Najlepszy posiłek po rowerze często jest przy guesthousie lub wiosce.",
        "Na Hainanie przy seafood zawsze pytaj o cenę za jin, czyli 500 g, i koszt przygotowania.",
        "W Hongkongu day trip nie udźwignie wszystkiego. Wybierz jedną kawiarnię cha chaan teng, jedną przekąskę i jeden konkretny obiad.",
        "W Makao nie traktuj egg tartu jako dodatku. To realny punkt programu, najlepiej w Taipa albo Coloane.",
        "W Xiamen zostaw czas na herbatę. Kupowanie oolongów bez degustacji jest proszeniem się o przepłacenie.",
    ]
    checklist_items = "".join(f"<li>{esc(item)}</li>" for item in checklist)
    body = f"""
    <section class="page-intro food-intro">
      <p class="eyebrow">Jedzenie</p>
      <h1>Kulinarny przewodnik po aktualnej trasie</h1>
      <p>Jedzenie jest tu częścią logistyki. Najlepszy plan dnia często zaczyna się od konkretnego śniadania i kończy jednym mocnym regionalnym posiłkiem, zamiast odhaczania przypadkowych restauracji. Ta strona ma działać jak wizualna lista kontrolna: co rozpoznać, co zamówić i gdzie nie przepalić budżetu.</p>
    </section>

    <section class="food-grid">{rows}</section>

    <section class="route-section">
      <h2>Potrawy, które warto umieć rozpoznać</h2>
      <div class="dish-grid">{dish_cards}</div>
    </section>

    <section class="text-block food-checklist">
      <h2>Jak tym sterować w podróży</h2>
      <ul>{checklist_items}</ul>
    </section>
    """
    return page_shell("Jedzenie", "food", body)


def build_practical_page() -> str:
    blocks = [
        (
            "Budżet",
            "Założenie 8k PLN wymaga trzymania Hongkongu i Makao jako day tripów oraz pilnowania Hainanu. Noclegi średnio około 50 PLN/os./noc są realne w Guangxi, Chaoshan i części Guangdong, trudniejsze w Hainanie, Hongkongu i Makao.",
        ),
        (
            "Noclegi",
            "W Chinach kontynentalnych wybieraj obiekty, które przyjmują cudzoziemców i potrafią zameldować paszport. W zimie sprawdzaj ogrzewanie lub klimatyzację z trybem grzania, szczególnie w Longji, Yangshuo i Fujianie.",
        ),
        (
            "Granice",
            "Hongkong i Makao nie są zwykłymi przejazdami miejskimi. Planuj paszport, kontrolę graniczną, osobną walutę i bufor czasowy. Przed wyjazdem sprawdź aktualne zasady wjazdu, tranzytu i ewentualnego ruchu bezwizowego dla dat 2026/2027.",
        ),
        (
            "Transport",
            "Najmocniejszym kręgosłupem trasy jest kolej dużych prędkości w Guangdong i Guangxi. Hainan zwykle podbija koszt przez loty albo długi transfer, więc warto porównywać go z wariantem Fujian/Chaoshan.",
        ),
        (
            "Aplikacje",
            "Przed wyjazdem przygotuj Alipay, WeChat, Trip.com, tłumacz offline i mapy. Google Maps bywa słabe w Chinach kontynentalnych, więc warto mieć alternatywę i zapisane chińskie adresy hoteli.",
        ),
    ]
    rows = "".join(f"<article class=\"text-block\"><h2>{esc(title)}</h2><p>{esc(text)}</p></article>" for title, text in blocks)
    body = f"""
    <section class="page-intro">
      <p class="eyebrow">Praktyka</p>
      <h1>Logistyka pod wasz budżet i czas</h1>
      <p>Ta wersja przewodnika jest pragmatyczna: mniej regionów, mniej przepalonych transferów, więcej czasu w miejscach, które realnie pasują do 2-3 tygodni.</p>
    </section>
    <section class="text-stack">{rows}</section>
    """
    return page_shell("Logistyka", "practical", body)


def write_site_css() -> None:
    write(
        SITE_CSS,
        """
:root {
  --ink: #172033;
  --muted: #5b6475;
  --line: #d9e1ea;
  --paper: #ffffff;
  --soft: #f6f8fb;
  --teal: #0f766e;
  --blue: #2563eb;
  --amber: #b7791f;
  --red: #b42318;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", Arial, sans-serif;
  color: var(--ink);
  background: var(--soft);
}
a { color: var(--teal); }
.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 12px 28px;
  border-bottom: 1px solid var(--line);
  background: rgba(255,255,255,0.96);
}
.brand {
  color: var(--ink);
  font-weight: 800;
  text-decoration: none;
}
nav { display: flex; flex-wrap: wrap; gap: 8px; }
nav a, .primary-link, .pager a {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--ink);
  background: #fff;
  text-decoration: none;
  font-weight: 650;
}
nav a.active, .primary-link {
  background: var(--teal);
  color: #fff;
  border-color: var(--teal);
}
main {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 26px 0 42px;
}
.page-intro, .place-hero {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 18px;
}
.page-intro h1, .hero-copy h1 {
  margin: 0 0 10px;
  font-size: clamp(30px, 4vw, 52px);
  line-height: 1.04;
  letter-spacing: 0;
}
.page-intro p, .hero-copy p {
  max-width: 820px;
  color: var(--muted);
  line-height: 1.6;
}
.eyebrow {
  margin: 0 0 8px;
  color: var(--amber);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}
.place-hero {
  display: grid;
  grid-template-columns: minmax(280px, 0.82fr) 1fr;
  gap: 24px;
  align-items: stretch;
}
.hero-img {
  width: 100%;
  height: 100%;
  min-height: 330px;
  object-fit: cover;
  border-radius: 6px;
}
.fact-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}
.fact-strip span, .meta {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 9px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #f8fafc;
  color: var(--muted);
  font-size: 13px;
}
.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
}
.main-copy, .side-panel, .route-section, .text-block {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 22px;
}
.main-copy h2, .side-panel h2, .route-section h2, .text-block h2 {
  margin: 0 0 10px;
  font-size: 22px;
}
.main-copy p, .main-copy li, .side-panel p, .text-block p, .route-card p {
  color: var(--muted);
  line-height: 1.58;
}
.detail-list, .route-grid, .place-grid, .text-stack, .food-grid, .dish-grid {
  display: grid;
  gap: 12px;
}
.detail-row, .route-card, .place-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
}
.detail-row, .route-card { padding: 14px; }
.detail-row h3, .route-card h3 {
  margin: 0 0 6px;
  font-size: 16px;
}
.place-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.place-grid.compact {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 18px;
}
.place-card a {
  display: grid;
  color: inherit;
  text-decoration: none;
}
.place-card img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  border-radius: 8px 8px 0 0;
}
.place-card div { padding: 14px; }
.place-card h2 {
  margin: 0 0 8px;
  font-size: 19px;
}
.place-card p {
  color: var(--muted);
  line-height: 1.45;
}
.route-section { margin-top: 18px; }
.route-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.food-intro {
  border-left: 5px solid var(--amber);
}
.food-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.food-region-card {
  display: grid;
  grid-template-columns: minmax(170px, 0.42fr) 1fr;
  gap: 16px;
  align-items: stretch;
  min-height: 220px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}
.food-region-card img {
  width: 100%;
  height: 100%;
  min-height: 220px;
  object-fit: cover;
}
.food-region-card div {
  padding: 18px 18px 18px 0;
}
.food-region-card h2, .dish-card h2 {
  margin: 0 0 8px;
  font-size: 20px;
  line-height: 1.18;
}
.food-region-card p, .dish-card p, .food-checklist li {
  color: var(--muted);
  line-height: 1.56;
}
.dish-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.dish-card {
  display: grid;
  grid-template-rows: auto 1fr;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}
.dish-card img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}
.dish-card div {
  padding: 15px;
}
.dish-name {
  margin-top: -2px;
  font-weight: 750;
}
.food-checklist ul {
  margin: 10px 0 0;
  padding-left: 20px;
}
.pager {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 18px;
}
.site-footer {
  border-top: 1px solid var(--line);
  padding: 18px 28px;
  color: var(--muted);
  background: #fff;
}
.site-footer p {
  width: min(1120px, 100%);
  margin: 0 auto;
  line-height: 1.5;
}
@media (max-width: 900px) {
  .site-header { align-items: flex-start; flex-direction: column; padding: 12px 16px; }
  main { width: min(100% - 20px, 1120px); padding-top: 14px; }
  .place-hero, .content-grid, .place-grid, .place-grid.compact, .route-grid, .food-grid, .dish-grid, .food-region-card {
    grid-template-columns: 1fr;
  }
  .food-region-card div { padding: 16px; }
  .food-region-card img { min-height: 210px; aspect-ratio: 16 / 10; }
  .hero-img { min-height: 230px; }
  .pager { flex-direction: column; }
}
""".strip()
        + "\n",
    )


def build_site() -> None:
    build_map.build_map()
    copy_extra_images(FOOD_IMAGE_IDS)

    places = load_json(build_map.DATA_DIR / "places.json")
    routes = load_json(build_map.DATA_DIR / "routes.json")
    places_by_id = {place["id"]: place for place in places}
    image_paths = image_paths_from_attributions()

    write_site_css()
    write(PLACES_DIR / "index.html", build_places_index(places, image_paths))
    for place in places:
        write(PLACES_DIR / f"{place['id']}.html", build_place_page(place, places, routes, places_by_id, image_paths))
    write(DOCS_DIR / "itinerary.html", build_itinerary_page(places, routes, places_by_id, image_paths))
    write(DOCS_DIR / "food.html", build_food_page(image_paths))
    write(DOCS_DIR / "practical.html", build_practical_page())
    write(DOCS_DIR / ".nojekyll", "")

    print(f"Place pages: {len(places)}")
    print("Static guide pages: places/index.html, itinerary.html, food.html, practical.html")


if __name__ == "__main__":
    build_site()
