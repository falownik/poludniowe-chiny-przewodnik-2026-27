# Wnioski z budowy mapy

Ten plik ma byc punktem startowym przy kolejnych zmianach w mapie i przewodniku.
Najwazniejszy wniosek: mapa jest glownym interfejsem planowania, wiec kazda
zmiana wizualna musi byc sprawdzona w przegladarce, a nie tylko w HTML-u.

## Reguly projektowe

- Mapa ma byc czytelna jako narzedzie planowania trasy, nie jako dekoracja.
- Lewy panel planu, prawa legenda i kontrolki Leaflet nie moga stale blokowac mapy.
  Lewy panel i legenda musza dac sie schowac, a kontrolka warstw powinna startowac
  jako zwinieta.
- Koszty przejazdow nie powinny byc widoczne na stale na mapie. Koszt i szczegoly
  transportu pokazuja sie dopiero po najechaniu na linie.
- Tooltipy i popupy musza miec jawne `min-width`, `max-width`, `white-space`,
  `overflow-wrap` i `word-break`. Bez tego Folium/Leaflet potrafi zrobic waskie
  kolumny po jednym znaku.
- Przy popupach trzeba sprawdzac miejsca przy krawedziach mapy. Przycisk przejscia
  do opisu miejsca musi byc widoczny po kliknieciu w marker.
- Zdjecia maja byc normalizowane do szerokosci tekstu lub karty: `max-width: 100%`,
  kontrolowana wysokosc albo proporcje i `object-fit: cover`. Nie wolno zostawiac
  obrazkow szerszych niz kolumna tekstu.
- W przewodniku lepiej dziala naturalny tekst i zwarte sekcje niz duza liczba tabel.
  Tabele zostawiac tylko tam, gdzie realnie pomagaja porownywac dane.
- Wszystkie koszty w publicznym przewodniku maja byc sprowadzone do PLN. Nie mieszac
  CNY, EUR, HKD i MOP w podstawowych opisach budzetu.

## Zakres obecnej trasy

- Plan v2 (decyzja z 2026-11-11): 17-22.12 we dwoje na wschodzie (Chaozhou,
  Shantou, tulou, Xiamen), 22.12 dolacza Kamil, 23-26.12 Shenzhen z day tripami
  do Makao i Hongkongu, 26.12 wieczorem dolacza ekipa (przylot HKG 19:00),
  27.12-3.01 Guangxi (Yangshuo, Sylwester w Yangshuo, Nanning), 4-5.01 Guangzhou,
  6.01 wylot. Ekipa zostaje do 11.01 i wylatuje z Szanghaju. Xiamen i tulou
  wrocily na mape tylko jako ten modul; reszta Fujianu, Hainan i Longji nadal poza mapa.
- Plan dni ma pole `who` (kto jest danego dnia); pokazuje sie w panelu planu,
  w tabeli na `itinerary.html` i w kolumnie `kto` w `itinerary.csv`.
- Aktualnie trzymamy zakres pod realne 2-3 tygodnie i budzet okolo 8 tys. PLN.
- Yunnan, Guizhou i Sichuan zostaly wyrzucone z mapy, bo nie ma na nie czasu w tej
  wersji wyjazdu.
- Hongkong i Makao sa ograniczone do day tripow, zeby nie rozbijac budzetu noclegami.
- Priorytetowe regiony mapy po odchudzeniu planu: Guangdong, Guangxi, Hongkong i
  Makao, plus modul Xiamen/tulou z planu v2. Hainan, reszta Fujianu, Yunnan,
  Guizhou i Sichuan nie powinny wracac na mape bez osobnej decyzji, bo rozbijaja
  czas i budzet.
- Nanning i Fangchenggang zostaly dodane jako wazne punkty Guangxi.
- Noclegi planujemy ostroznie: srednio okolo 50 PLN za osobe za noc, z wyjatkami tam,
  gdzie lokalizacja mocno oszczedza czas.
- Nanning nie jest mocnym celem samym w sobie. Broni sie jako baza logistyczna:
  Qingxiu/food day przy slabej pogodzie, Detian/Mingshi lub Fangchenggang/Dongxing
  przy dobrej logistyce. Jesli grupa chce natury i "rural", Yangshuo ma wyzszy
  priorytet.
- Styczniowe wyjscie do Hongkongu lub Makao jest formalnie wazniejsze niz wyglada:
  po 31.12.2026 moze oznaczac ponowny wjazd do Chin kontynentalnych juz w 2027.
  Przed utrwaleniem planu trzeba sprawdzic przedluzenie ruchu bezwizowego albo
  miec wize turystyczna z odpowiednia liczba wjazdow.

## Techniczne zasady pracy

- Zrodlem prawdy sa pliki w `data/` i skrypty w `scripts/`. `docs/` jest artefaktem
  publikowanym przez GitHub Pages i powinien byc generowany, nie recznie latany.
- Po zmianie danych lub layoutu uruchomic:

```powershell
& '..\.venv\Scripts\python.exe' .\scripts\build_site.py
& '..\.venv\Scripts\python.exe' .\scripts\verify_map.py
```

- `scripts/verify_map.py` powinien rosnac razem z mapa. Kazdy naprawiony regres
  warto zamienic w prosty warunek walidacyjny.
- Dane decyzyjne trzymaj w `data/`, nie jako recznie dopisany HTML. Obecnie:
  `nearby_places.json` zasila warstwe researchu, `hub_playbooks.json` zasila
  playbooki hubow, `predeparture_checks.json` i `formality_scenarios.json`
  zasilaja formalnosci w stronie logistycznej.
- Po zmianach wizualnych obowiazkowo sprawdzic Playwrightem co najmniej:
  desktop `1365x768`, mobile `390x844`, hover na regionie, hover na trasie,
  klik w marker, schowanie panelu i legendy.
- Jezeli znowu pojawia sie tekst w jednej kolumnie znakow, najpierw sprawdzic CSS
  tooltipow, szerokosc kontenera i wymuszenia Leaflet/Folium.
- GitHub Pages potrafi miec krotki cache. Po pushu sprawdzac publiczny URL z
  parametrem `?v=<commit>`.

## Wnioski UX

- Uzytkownik musi moc zaczac od mapy i przejsc kliknieciem do opisu miejsca.
- Hover ma dawac szybka decyzje: co to za miejsce, po co tam jechac, ile kosztuje
  nocleg, ile trwa dojazd albo czy to tylko opcja.
- Opisy jedzenia wymagaja duzo wiecej zdjec i listy co najmniej 50 potraw z poludnia
  Chin. Przy potrawach obrazek jest wazniejszy niz dlugi abstrakcyjny opis.
- Kolory prowincji sa przydatne, ale musza byc spokojne. Najwazniejsza jest
  czytelnosc markerow, tras i popupow.
- Kolejne zmiany powinny byc male i testowane po drodze, bo najwieksze regresje
  powstawaly przy poprawianiu layoutu bez ogladania wyniku w przegladarce.
