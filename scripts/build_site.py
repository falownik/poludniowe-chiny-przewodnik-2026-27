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
    "zhuhai": [
        "Zhuhai jest bazą, nie kulinarnym finałem. Najpraktyczniej jeść prosto przy Gongbei i przeznaczyć budżet jedzeniowy na Makao.",
        "Jeśli zostajesz wieczorem, szukaj owoców morza i kantońskich lokali w okolicach granicy albo przy nadmorskim spacerze.",
    ],
    "macau": [
        "Makao to egg tarty, pork chop bun, minchi, African chicken i portugalsko-kantońska kuchnia w wąskich ulicach starego miasta.",
        "Najlepiej zjeść coś małego przy Senado/St. Paul's, potem zrobić Taipa Village albo Coloane jako osobny blok jedzeniowy.",
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
        "Shenzhen nie ma jednej klasycznej kuchni miasta, ale ma świetny przekrój migracyjnych Chin: kantońskie, Chaoshan, ostre lokale z interioru i dobre food courty.",
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
}


PRACTICAL_NOTES: dict[str, list[str]] = {
    "guangzhou": [
        "Najlepsza kotwica przylotu i wylotu. Ostatnią noc przed lotem trzymaj w Guangzhou, nie w Hongkongu, Makao ani Yangshuo.",
        "Po przylocie o późnej porze najprościej jechać do hotelu w mieście albo spać przy lotnisku. Nie planuj nocnego transferu do innego regionu.",
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
    "guilin": [
        "Guilin jest bramą, niekoniecznie główną bazą. Użyj go do HSR, Li River i transferu do Yangshuo/Nanning, a dłużej śpij w Yangshuo.",
    ],
}


FOOD_DISHES: list[dict[str, str]] = [
    {
        "region": "Guangzhou / dim sum",
        "name": "Har gow",
        "chinese": "虾饺",
        "pinyin": "xiā jiǎo",
        "image_id": "dim_sum_har_gow",
        "where": "Yum cha w Guangzhou, Shunde, Hongkongu i Makao.",
        "order": "Klasyczna krewetkowa pierożka na parze. Dobra wersja ma cienkie, półprzezroczyste ciasto i sprężystą krewetkę, bez ciężkiego zapachu mąki.",
    },
    {
        "region": "Guangzhou / dim sum",
        "name": "Siu mai",
        "chinese": "烧卖",
        "pinyin": "shāomài",
        "image_id": "siu_mai",
        "where": "Poranny yum cha, zwykle w koszyczku po 3-4 sztuki.",
        "order": "Wieprzowo-krewetkowe dim sum z otwartą górą. Zamów razem z har gow, żeby porównać dwa podstawowe style kantońskich pierożków.",
    },
    {
        "region": "Guangdong",
        "name": "Char siu",
        "chinese": "叉烧",
        "pinyin": "chāshāo",
        "image_id": "char_siu",
        "where": "Siu mei shops, lokale z pieczonym mięsem, proste zestawy z ryżem.",
        "order": "Kantońska pieczona wieprzowina w słodko-słonej glazurze. Szukaj przypieczonego brzegu, soczystego środka i lokalu, który kroi mięso na zamówienie.",
    },
    {
        "region": "Guangdong / Hongkong",
        "name": "Pieczona gęś",
        "chinese": "烧鹅",
        "pinyin": "shāo'é",
        "image_id": "roast_goose",
        "where": "Hongkong, Guangzhou i lepsze lokale kantońskie.",
        "order": "Danie na wspólny stół albo większy lunch. Skóra ma być ciemna, lśniąca i chrupiąca, a mięso tłustsze niż kaczka.",
    },
    {
        "region": "Guangzhou / Hongkong",
        "name": "Wonton noodles",
        "chinese": "云吞面",
        "pinyin": "yúntūn miàn",
        "image_id": "wonton_noodles",
        "where": "Małe lokale śniadaniowe i lunchowe w Guangdong i HK.",
        "order": "Cienki, sprężysty makaron, klarowny bulion i wontony z krewetką. To jeden z najbezpieczniejszych pierwszych posiłków po przylocie.",
    },
    {
        "region": "Guangdong / dim sum",
        "name": "Cheung fun",
        "chinese": "肠粉",
        "pinyin": "chángfěn",
        "image_id": "cheung_fun",
        "where": "Dim sum, śniadaniownie i uliczne lokale w Guangdong.",
        "order": "Jedwabiste ryżowe rolki z sosem sojowym, czasem z krewetką, wołowiną albo char siu. Zwróć uwagę na teksturę: ma być śliska, ale nie gumowa.",
    },
    {
        "region": "Guangdong / dim sum",
        "name": "Lo mai gai",
        "chinese": "糯米鸡",
        "pinyin": "nuòmǐ jī",
        "image_id": "lo_mai_gai",
        "where": "Yum cha i piekarnie dim sum, często rano.",
        "order": "Kleisty ryż z kurczakiem i dodatkami, zawinięty w liść lotosu. Bardzo sycące, więc lepiej zamówić jedną porcję do podziału.",
    },
    {
        "region": "Guangdong / dim sum",
        "name": "Turnip cake",
        "chinese": "萝卜糕",
        "pinyin": "luóbo gāo",
        "image_id": "turnip_cake",
        "where": "Dim sum, szczególnie zimą i w okolicach Chińskiego Nowego Roku.",
        "order": "Smażone plastry ciasta z białej rzodkwi i ryżowej mąki. Dobra wersja ma chrupiącą powierzchnię i miękki środek z wyczuwalnymi suszonymi dodatkami.",
    },
    {
        "region": "Guangdong / piekarnie",
        "name": "Char siu bao",
        "chinese": "叉烧包",
        "pinyin": "chāshāo bāo",
        "image_id": "char_siu_bao",
        "where": "Dim sum na parze albo piekarnie z wersją pieczoną.",
        "order": "Bułka z nadzieniem z char siu. Wersja parowana jest miękka i biała, pieczona bardziej słodka i deserowa.",
    },
    {
        "region": "Guangdong",
        "name": "Claypot rice",
        "chinese": "煲仔饭",
        "pinyin": "bāozǎi fàn",
        "image_id": "claypot_rice",
        "where": "Wieczorne lokale w Guangzhou, Hongkongu i Shenzhen.",
        "order": "Ryż zapiekany w glinianym garnku z kiełbasą, kurczakiem, żeberkami albo boczkiem. Najważniejsza jest chrupiąca warstwa ryżu przy dnie.",
    },
    {
        "region": "Guangdong",
        "name": "Beef chow fun",
        "chinese": "干炒牛河",
        "pinyin": "gān chǎo niú hé",
        "image_id": "beef_chow_fun",
        "where": "Lokale kantońskie, food courty, proste restauracje wokowe.",
        "order": "Smażone szerokie wstęgi ryżowe z wołowiną. To test pracy woka: danie ma być lekko dymne, nie zalane olejem.",
    },
    {
        "region": "Guangdong",
        "name": "White cut chicken",
        "chinese": "白切鸡",
        "pinyin": "báiqiē jī",
        "image_id": "white_cut_chicken",
        "where": "Restauracje kantońskie i lokale z drobiem.",
        "order": "Delikatnie gotowany kurczak podawany chłodno lub letnio z sosem imbirowo-szczypiorkowym. Smak jest subtelny, więc jakość mięsa robi wszystko.",
    },
    {
        "region": "Guangdong",
        "name": "Ryba na parze po kantońsku",
        "chinese": "清蒸鱼",
        "pinyin": "qīngzhēng yú",
        "image_id": "steamed_fish",
        "where": "Kolacje kantońskie, zwłaszcza gdy jesteście grupą.",
        "order": "Ryba gotowana na parze z imbirem, szczypiorem i sosem sojowym. Ustal cenę za wagę przed zamówieniem, szczególnie przy żywych rybach.",
    },
    {
        "region": "Shunde / Foshan",
        "name": "Double-skin milk",
        "chinese": "双皮奶",
        "pinyin": "shuāngpí nǎi",
        "image_id": "double_skin_milk",
        "where": "Shunde, Foshan, klasyczne lokale deserowe.",
        "order": "Mleczny deser o gładkiej strukturze i delikatnej skórce. Jedz ciepły zimą, zimny latem; wersje z mango są łatwiejsze dla początkujących.",
    },
    {
        "region": "Guangdong / desery",
        "name": "Ginger milk curd",
        "chinese": "姜撞奶",
        "pinyin": "jiāng zhuàng nǎi",
        "image_id": "ginger_milk_curd",
        "where": "Shunde, Guangzhou, Zhongshan i lokale deserowe Lingnan.",
        "order": "Mleko ścinane świeżym sokiem z imbiru. Powinno być lekkie, ostro-imbirowe i ledwo zwarte, nie jak twardy pudding.",
    },
    {
        "region": "Shunde / Foshan",
        "name": "Chrupiąca skóra ryby",
        "chinese": "鱼皮",
        "pinyin": "yúpí",
        "image_id": "",
        "where": "Shunde, szczególnie w lokalach specjalizujących się w rybach.",
        "order": "Skóra ryby podawana na zimno, często z sosem, kolendrą i sezamem. To danie tekstury: sprężyste, świeże, lekko chrupiące.",
    },
    {
        "region": "Shunde / Foshan",
        "name": "Smażone mleko",
        "chinese": "炸牛奶",
        "pinyin": "zhá niúnǎi",
        "image_id": "",
        "where": "Shunde, restauracje rodzinne i lokale deserowe.",
        "order": "Krem mleczny w chrupiącej panierce. Brzmi jak ciekawostka, ale w Shunde jest jednym z najłatwiejszych deserów do polubienia.",
    },
    {
        "region": "Guangzhou",
        "name": "Boat congee",
        "chinese": "艇仔粥",
        "pinyin": "tǐngzǎi zhōu",
        "image_id": "",
        "where": "Guangzhou, okolice Liwan i tradycyjne lokale z congee.",
        "order": "Ryżowa zupa z mieszanką dodatków: rybą, orzeszkami, paskami ciasta, czasem mięsem. Dobra na śniadanie albo lekki wieczór.",
    },
    {
        "region": "Guangdong",
        "name": "Siu yuk",
        "chinese": "烧肉",
        "pinyin": "shāoròu",
        "image_id": "",
        "where": "Stoiska siu mei obok char siu i pieczonej gęsi.",
        "order": "Chrupiący boczek po kantońsku. Zamawiaj małą porcję z ryżem albo jako dodatek do wspólnego stołu.",
    },
    {
        "region": "Guilin / Guangxi",
        "name": "Guilin rice noodles",
        "chinese": "桂林米粉",
        "pinyin": "Guìlín mǐfěn",
        "image_id": "guilin_rice_noodles",
        "where": "Guilin rano, blisko dworca, targu albo osiedlowych ulic.",
        "order": "Podstawa Guangxi. Najpierw mieszasz makaron z sosem i dodatkami, dopiero później dolewasz bulion. Szukaj szybkiej rotacji, nie najładniejszej sali.",
    },
    {
        "region": "Yangshuo / Guangxi",
        "name": "Beer fish",
        "chinese": "啤酒鱼",
        "pinyin": "píjiǔ yú",
        "image_id": "yangshuo_beer_fish",
        "where": "Yangshuo i okolice rzeki Li.",
        "order": "Ryba duszona z piwem, pomidorami i przyprawami. Ustal gatunek ryby i cenę za wagę, bo to danie bywa turystycznie przepłacane.",
    },
    {
        "region": "Guangxi",
        "name": "Bamboo rice",
        "chinese": "竹筒饭",
        "pinyin": "zhútǒng fàn",
        "image_id": "",
        "where": "Yangshuo, okolice Guilin i proste lokale Guangxi.",
        "order": "Ryż gotowany w bambusie, często z fasolą, kukurydzą albo mięsem. Najlepszy jako prosty posiłek po dniu w krasowym krajobrazie.",
    },
    {
        "region": "Guangxi",
        "name": "Lipu taro with pork",
        "chinese": "荔浦芋扣肉",
        "pinyin": "Lìpǔ yù kòuròu",
        "image_id": "",
        "where": "Guilin, Yangshuo i restauracje regionalne Guangxi.",
        "order": "Warstwy taro z Lipu i duszonej wieprzowiny. Danie cięższe, dobre na wspólną kolację, szczególnie w chłodniejszy wieczór.",
    },
    {
        "region": "Guangxi",
        "name": "Oil tea",
        "chinese": "油茶",
        "pinyin": "yóuchá",
        "image_id": "",
        "where": "Guilin, Yangshuo i lokale z kuchnią północnego Guangxi.",
        "order": "Słono-gorzki napój/zupa z herbaty, oleju, orzeszków i chrupkich dodatków. Nie każdemu smakuje, ale świetnie pokazuje lokalny kontekst.",
    },
    {
        "region": "Guangxi",
        "name": "Luosifen",
        "chinese": "螺蛳粉",
        "pinyin": "luósīfěn",
        "image_id": "",
        "where": "Liuzhou, Nanning, ale dostępne też w większych miastach Guangxi.",
        "order": "Makaron ryżowy w intensywnym bulionie ze ślimaków rzecznych i kiszonym bambusem. Zapach jest mocny, smak kwaśno-pikantny.",
    },
    {
        "region": "Guangxi",
        "name": "Rice tofu",
        "chinese": "米豆腐",
        "pinyin": "mǐ dòufu",
        "image_id": "",
        "where": "Targi, małe lokale, okolice Guilin i miasteczek Guangxi.",
        "order": "Delikatne kostki z masy ryżowej, zwykle z chili, octem i ziołami. Dobre jako lekki lunch albo przekąska.",
    },
    {
        "region": "Guangxi",
        "name": "Lokalny kurczak z Guangxi",
        "chinese": "广西土鸡",
        "pinyin": "Guǎngxī tǔjī",
        "image_id": "",
        "where": "Yangshuo, Guilin i rodzinne restauracje Guangxi.",
        "order": "Najczęściej prosty kurczak z zupą, warzywami i ryżem. Dobre danie na spokojną kolację po dniu na rowerze albo po przejeździe.",
    },
    {
        "region": "Chaoshan",
        "name": "Gęś duszona w marynacie lushui",
        "chinese": "卤水鹅",
        "pinyin": "lǔshuǐ é",
        "image_id": "chaozhou_braised_goose",
        "where": "Chaozhou i Shantou, lokale specjalizujące się w gęsi.",
        "order": "Gęś gotowana w aromatycznej marynacie sojowej. Zamów różne części do spróbowania; sos i tłuszcz są tu tak samo ważne jak mięso.",
    },
    {
        "region": "Chaoshan",
        "name": "Chaozhou congee",
        "chinese": "潮州粥",
        "pinyin": "Cháozhōu zhōu",
        "image_id": "chaozhou_congee",
        "where": "Chaozhou, Shantou, wieczorne lokale z owocami morza i congee.",
        "order": "Luźniejsza, ziarnista wersja congee. Dobrze działa z ostrygami, rybą, mielonym mięsem albo prostymi piklami.",
    },
    {
        "region": "Chaoshan",
        "name": "Chaoshan beef hot pot",
        "chinese": "潮汕牛肉火锅",
        "pinyin": "Cháoshàn niúròu huǒguō",
        "image_id": "chaoshan_beef_hotpot",
        "where": "Shantou, Chaozhou, Shenzhen i Guangzhou w lokalach Chaoshan.",
        "order": "Nie chodzi tu o chili, tylko o świeżą wołowinę krojoną według części i krótkie gotowanie w lekkim bulionie.",
    },
    {
        "region": "Chaoshan",
        "name": "Chaoshan beef balls",
        "chinese": "潮汕牛肉丸",
        "pinyin": "Cháoshàn niúròu wán",
        "image_id": "",
        "where": "Shantou, Chaozhou, lokale hotpotowe i makaronowe.",
        "order": "Sprężyste kulki wołowe, ręcznie ubijane. Szukaj tekstury, która lekko odbija pod zębami, nie miękkiej przemysłowej papki.",
    },
    {
        "region": "Chaoshan",
        "name": "Oyster omelette",
        "chinese": "蚝烙",
        "pinyin": "háo lào",
        "image_id": "",
        "where": "Chaozhou, Shantou i lokale z owocami morza w Chaoshan.",
        "order": "Ostrygi w jajku i skrobi, z chrupiącymi brzegami. W Chaoshan liczy się sprężysta tekstura, świeżość ostryg i szybkie smażenie.",
    },
    {
        "region": "Chaoshan",
        "name": "Fish rice",
        "chinese": "鱼饭",
        "pinyin": "yúfàn",
        "image_id": "",
        "where": "Chaozhou i Shantou, stoiska z rybami i restauracje Chaoshan.",
        "order": "Nazwa myli: to zwykle ryba gotowana i studzona, jedzona z sosem. Danie pokazuje obsesję Chaoshan na punkcie świeżości ryby.",
    },
    {
        "region": "Chaoshan",
        "name": "Gongfu tea",
        "chinese": "工夫茶",
        "pinyin": "gōngfu chá",
        "image_id": "",
        "where": "Chaozhou, Shantou, domy herbaty, sklepy i rodzinne lokale.",
        "order": "Bardzo mocna herbata parzona w małych naczyniach. Nie traktuj jej jak dekoracji: to jeden z fundamentów kultury Chaoshan.",
    },
    {
        "region": "Chaoshan",
        "name": "Chaozhou kueh",
        "chinese": "粿",
        "pinyin": "guǒ",
        "image_id": "",
        "where": "Targi i małe sklepy w Chaozhou/Shantou.",
        "order": "Rodzina ryżowych przekąsek z różnymi nadzieniami, często słonych. Dobre do próbowania małymi porcjami zamiast pełnego posiłku.",
    },
    {
        "region": "Xiamen / Fujian",
        "name": "Shacha noodles",
        "chinese": "沙茶面",
        "pinyin": "shāchá miàn",
        "image_id": "xiamen_shacha_noodles",
        "where": "Xiamen, proste lokale w Siming i przy Zhongshan Road.",
        "order": "Makaron w bulionie z pastą shacha: orzechowo-morski, lekko pikantny, często z krewetkami, tofu, podrobami albo wieprzowiną.",
    },
    {
        "region": "Xiamen / Fujian",
        "name": "Peanut soup",
        "chinese": "花生汤",
        "pinyin": "huāshēng tāng",
        "image_id": "",
        "where": "Xiamen, klasyczne lokale śniadaniowe i deserowe.",
        "order": "Słodka, miękka zupa z orzeszków ziemnych. Dobrze działa jako spokojne śniadanie z pieczywem albo po ostrzejszym posiłku.",
    },
    {
        "region": "Fujian",
        "name": "Fuzhou fish balls",
        "chinese": "福州鱼丸",
        "pinyin": "Fúzhōu yúwán",
        "image_id": "fujian_fish_balls",
        "where": "Fuzhou, Xiamen i lokale z kuchnią Fujian.",
        "order": "Kulki rybne, często z mięsnym nadzieniem w środku. Lepsze lokale mają wyraźnie sprężystą, rybną strukturę.",
    },
    {
        "region": "Fujian",
        "name": "Lychee pork",
        "chinese": "荔枝肉",
        "pinyin": "lìzhī ròu",
        "image_id": "fujian_lychee_pork",
        "where": "Fuzhou i restauracje kuchni Fujian.",
        "order": "Słodko-kwaśna wieprzowina nacinana tak, by przypominała owoc liczi. Dobre danie do wspólnego stołu, szczególnie dla osób niejedzących ostro.",
    },
    {
        "region": "Fujian",
        "name": "Buddha jumps over the wall",
        "chinese": "佛跳墙",
        "pinyin": "fó tiào qiáng",
        "image_id": "buddha_jumps_wall",
        "where": "Fuzhou, droższe restauracje Fujian; rzadziej sensowne przy budżetowej trasie.",
        "order": "Bogata zupa-bankiet z wieloma luksusowymi składnikami. Warto znać, ale nie trzeba jej koniecznie zamawiać przy limicie budżetu.",
    },
    {
        "region": "Guangdong Hakka",
        "name": "Hakka stuffed tofu",
        "chinese": "酿豆腐",
        "pinyin": "niàng dòufu",
        "image_id": "hakka_stuffed_tofu",
        "where": "Restauracje Hakka w Guangzhou, Shenzhen i Guangdong.",
        "order": "Tofu nadziewane mielonym mięsem lub pastą rybną, duszone w sosie. Dobry wybór, jeśli chcecie odpocząć od makaronów i dim sum.",
    },
    {
        "region": "Guangdong Hakka",
        "name": "Lei cha rice",
        "chinese": "擂茶饭",
        "pinyin": "léichá fàn",
        "image_id": "hakka_lei_cha",
        "where": "Lokale Hakka w Guangdong, szczególnie w większych miastach i food courtach.",
        "order": "Ryż z warzywami, orzeszkami i ziołową herbacianą zawiesiną. Smak jest zielony, ziołowy i nietypowy, ale bardzo charakterystyczny.",
    },
    {
        "region": "Fujian / herbata",
        "name": "Da Hong Pao",
        "chinese": "大红袍",
        "pinyin": "dàhóngpáo",
        "image_id": "dahongpao_tea",
        "where": "Xiamen, sklepy herbaciane, Wuyi Shan jako osobny moduł.",
        "order": "Oolong skalny z Wuyi. Nie kupuj drogiej herbaty bez degustacji; pytaj o cenę za gram i kilka parzeń.",
    },
    {
        "region": "Hainan",
        "name": "Hainanese chicken rice",
        "chinese": "海南鸡饭",
        "pinyin": "Hǎinán jī fàn",
        "image_id": "hainan_chicken_rice",
        "where": "Haikou, Sanya, Wenchang chicken restaurants.",
        "order": "Ryż gotowany na bulionie z kurczaka, delikatne mięso i sosy: imbir, chili, czosnek. Na Hainanie mniej chodzi o singapurską estetykę, bardziej o jakość kurczaka.",
    },
    {
        "region": "Hainan",
        "name": "Wenchang chicken",
        "chinese": "文昌鸡",
        "pinyin": "Wénchāng jī",
        "image_id": "wenchang_chicken",
        "where": "Wenchang, Haikou, Sanya i restauracje z kuchnią Hainan.",
        "order": "Najważniejszy kurczak wyspy. Zamawiaj z sosami i ryżem; mięso powinno być jędrne, a skóra lekko żelatynowa.",
    },
    {
        "region": "Hainan",
        "name": "Coconut chicken hot pot",
        "chinese": "椰子鸡火锅",
        "pinyin": "yēzi jī huǒguō",
        "image_id": "",
        "where": "Sanya, Haikou, Shenzhen i lokale specjalizujące się w Hainanie.",
        "order": "Kurczak gotowany w wodzie kokosowej. Bulion jest słodkawy i lekki; dobre danie grupowe po plaży albo długim przejeździe.",
    },
    {
        "region": "Hainan",
        "name": "Qingbuliang",
        "chinese": "清补凉",
        "pinyin": "qīngbǔliáng",
        "image_id": "",
        "where": "Hainan, stoiska deserowe, wieczorne ulice w Haikou i Sanya.",
        "order": "Chłodny deser z mlekiem kokosowym, fasolkami, galaretkami, owocami i lodem. Najlepszy po gorącym dniu.",
    },
    {
        "region": "Hainan",
        "name": "Jiaji duck",
        "chinese": "嘉积鸭",
        "pinyin": "Jiājī yā",
        "image_id": "",
        "where": "Hainan, restauracje regionalne.",
        "order": "Jedna z klasycznych potraw wyspy. Mięso jest ciemniejsze i bardziej zwarte niż kurczak; zwykle zamawia się je do wspólnego stołu.",
    },
    {
        "region": "Hainan",
        "name": "Hele crab",
        "chinese": "和乐蟹",
        "pinyin": "Hélè xiè",
        "image_id": "",
        "where": "Hainan, szczególnie lokale seafoodowe.",
        "order": "Krab z Hainanu. Przy seafood zawsze ustal cenę za jin, czyli 500 g, oraz sposób przygotowania przed gotowaniem.",
    },
    {
        "region": "Hainan",
        "name": "Hainan rice noodles",
        "chinese": "海南粉",
        "pinyin": "Hǎinán fěn",
        "image_id": "",
        "where": "Haikou i lokalne śniadaniownie.",
        "order": "Mieszane makarony ryżowe z sosem, orzeszkami, mięsem i kwaśnymi dodatkami. Dobry kontrapunkt do kurczaka z ryżem.",
    },
    {
        "region": "Hainan",
        "name": "Xinglong coffee",
        "chinese": "兴隆咖啡",
        "pinyin": "Xīnglóng kāfēi",
        "image_id": "",
        "where": "Hainan, zwłaszcza okolice Wanning/Xinglong i kawiarnie w Haikou.",
        "order": "Kawa związana z historią powrotów chińskiej diaspory z Azji Południowo-Wschodniej. Spróbuj także jako mocną kawę z mlekiem skondensowanym.",
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
        "order": "Gorzka, mocna herbata z mlekiem, nie deserowy bubble tea. Zamów gorącą albo na lodzie do pineapple bun.",
    },
    {
        "region": "Hongkong",
        "name": "Pineapple bun",
        "chinese": "菠萝包",
        "pinyin": "bōluó bāo",
        "image_id": "pineapple_bun",
        "where": "Piekarnie i cha chaan teng.",
        "order": "Nazwa nie oznacza ananasa. Chodzi o kruchą, słodką skórkę. Wersja z grubym plastrem masła to klasyk śniadaniowy.",
    },
    {
        "region": "Hongkong",
        "name": "Cart noodles",
        "chinese": "车仔面",
        "pinyin": "chēzǎi miàn",
        "image_id": "",
        "where": "Kowloon, Mong Kok, lokalne bary makaronowe.",
        "order": "Wybierasz makaron, bulion i dodatki: rybne kulki, wołowinę, rzodkiew, tofu, warzywa. Dobre, gdy każdy chce zjeść coś innego.",
    },
    {
        "region": "Hongkong",
        "name": "Curry fish balls",
        "chinese": "咖喱鱼蛋",
        "pinyin": "gālí yúdàn",
        "image_id": "",
        "where": "Uliczne stoiska w Kowloonie i na wyspie Hongkong.",
        "order": "Kulki rybne w sosie curry, jedzone z patyczka. To szybka przekąska, nie pełny posiłek.",
    },
    {
        "region": "Hongkong",
        "name": "Stinky tofu",
        "chinese": "臭豆腐",
        "pinyin": "chòu dòufu",
        "image_id": "",
        "where": "Street food w Hongkongu, Makao i południowych miastach Chin.",
        "order": "Fermentowane tofu o mocnym zapachu i łagodniejszym smaku niż sugeruje nazwa. Najlepiej próbować małą porcję na świeżo smażoną.",
    },
    {
        "region": "Hongkong",
        "name": "Roast goose rice",
        "chinese": "烧鹅饭",
        "pinyin": "shāo'é fàn",
        "image_id": "",
        "where": "Kowloon, Central, Wan Chai, lokale siu mei.",
        "order": "Budżetowy sposób na pieczoną gęś bez zamawiania całego półmiska. Poproś o sos śliwkowy i warzywa, jeśli są dostępne.",
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
        "region": "Makao",
        "name": "Pork chop bun",
        "chinese": "猪扒包",
        "pinyin": "zhūpá bāo",
        "image_id": "macau_pork_chop_bun",
        "where": "Taipa, Coloane i klasyczne bary makaoskie.",
        "order": "Prosta bułka z kotletem wieprzowym. Najlepsza wersja jest gorąca, chrupiąca i bez nadmiaru sosu.",
    },
    {
        "region": "Makao",
        "name": "African chicken",
        "chinese": "非洲鸡",
        "pinyin": "Fēizhōu jī",
        "image_id": "macanese_african_chicken",
        "where": "Restauracje kuchni makaoskiej, zwykle nie przy najtańszych stoiskach.",
        "order": "Kurczak w sosie z przyprawami, kokosem i wpływami portugalsko-afrykańskimi. Bardziej danie restauracyjne niż przekąska.",
    },
    {
        "region": "Makao",
        "name": "Minchi",
        "chinese": "免治",
        "pinyin": "miǎnzhì",
        "image_id": "macanese_minchi",
        "where": "Domowa kuchnia makaoska i restauracje z lokalnym menu.",
        "order": "Mielone mięso z ziemniakami, sosem sojowym i często jajkiem. Wygląda prosto, ale dobrze pokazuje kuchnię codzienną Makao.",
    },
    {
        "region": "Makao",
        "name": "Serradura",
        "chinese": "木糠布甸",
        "pinyin": "mùkāng bùdiàn",
        "image_id": "",
        "where": "Kawiarnie i restauracje makaoskie.",
        "order": "Deser z kremu i kruszonych ciastek, dosłownie 'trociny'. Dobry lekki finał po cięższym obiedzie.",
    },
    {
        "region": "Makao",
        "name": "Almond cookies",
        "chinese": "杏仁饼",
        "pinyin": "xìngrén bǐng",
        "image_id": "",
        "where": "Piekarnie i sklepy z pamiątkami w Makao.",
        "order": "Kruche ciasteczka migdałowe. Warto kupić małe opakowanie, ale wcześniej spróbować, bo bywają bardzo suche.",
    },
]


OUT_OF_PLAN_FOOD_TERMS = {
    "hainan",
    "fujian",
    "xiamen",
    "longji",
    "tulou",
    "fuzhou",
    "wuyi",
    "haikou",
    "sanya",
    "wanning",
}


def food_dish_is_in_scope(dish: dict[str, str]) -> bool:
    text = " ".join(str(value).lower() for value in dish.values())
    return not any(term in text for term in OUT_OF_PLAN_FOOD_TERMS)


ROUTE_FOOD_DISHES = [dish for dish in FOOD_DISHES if food_dish_is_in_scope(dish)]
FOOD_IMAGE_IDS = {dish["image_id"] for dish in ROUTE_FOOD_DISHES if dish.get("image_id")}


def esc(value: Any) -> str:
    return build_map.esc(value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if content:
        content = "\n".join(line.rstrip() for line in content.splitlines()) + ("\n" if content.endswith("\n") else "")
    path.write_text(content, encoding="utf-8")


def image_paths_from_attributions() -> dict[str, str]:
    path = ASSET_DIR / "image_attributions.json"
    if not path.exists():
        return {}
    return {item["id"]: item["file"] for item in load_json(path)}


def food_image_sources() -> dict[str, dict[str, str]]:
    path = build_map.DATA_DIR / "food_image_sources.json"
    if not path.exists():
        return {}
    return {item["id"]: item for item in load_json(path)}


def copy_extra_images(image_ids: set[str]) -> None:
    if not image_ids:
        return

    manifest = build_map.read_image_manifest()
    food_sources = food_image_sources()
    build_map.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    attribution_path = ASSET_DIR / "image_attributions.json"
    attributions = load_json(attribution_path) if attribution_path.exists() else []
    known_ids = {item["id"] for item in attributions}

    for image_id in sorted(image_ids):
        food_source = food_sources.get(image_id)
        if food_source:
            target = DOCS_DIR / food_source["file"]
            if target.exists():
                attributions = [item for item in attributions if item["id"] != image_id]
                attributions.append(
                    {
                        "id": image_id,
                        "title": food_source.get("title", ""),
                        "commons_title": food_source.get("commons_title", ""),
                        "artist": food_source.get("artist", ""),
                        "license": food_source.get("license", ""),
                        "source": food_source.get("source", ""),
                        "file": food_source["file"],
                    }
                )
                known_ids.add(image_id)
                continue
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
    alt = route.get("train_alt")
    train_alt = (
        f"<p class=\"route-alt\"><strong>{esc(alt.get('label', 'Alternatywa pociągiem'))}:</strong> "
        f"{esc(alt.get('time', ''))} · {esc(alt.get('cost_pln', ''))}<br>"
        f"<span>{esc(alt.get('note', ''))}</span></p>"
        if alt
        else ""
    )
    return f"""
    <article class="route-card">
      <h3><a href="{from_href}">{esc(from_place['name'])}</a> → <a href="{to_href}">{esc(to_place['name'])}</a></h3>
      <p><strong>{esc(route['mode'])}</strong> · {esc(route['time'])} · {esc(route['cost_pln'])}</p>
      {train_alt}
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
      <p>To jest wersja realna czasowo: Guangdong, Guangxi, Chaoshan oraz day tripy do Hongkongu, Makao, Detian i Fangchenggang/Dongxing. Każde miejsce jest albo noclegową bazą z planu, albo krótkim wypadem bez przenoszenia walizek.</p>
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
      <p>Mapa nie jest sztywnym planem dzień po dniu. To zestaw modułów, które można składać pod osoby jadące na 2 i 3 tygodnie: start w Guangzhou, kilka nocy w Yangshuo, Nanning jako baza na Detian i Fangchenggang/Dongxing, day tripy HK/Makao oraz finał jedzeniowy w Chaoshan.</p>
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
    dish_count = len(ROUTE_FOOD_DISHES)
    image_count = sum(1 for dish in ROUTE_FOOD_DISHES if dish.get("image_id"))
    region_cards = [
        {
            "title": "Guangdong: yum cha, pieczone mięsa i proste klasyki",
            "image_id": "dim_sum_har_gow",
            "text": "Najważniejszy jest rytm jedzenia. Rano dim sum i herbata, w południe wonton noodles albo roast meat rice, wieczorem ryba na parze, warzywa i claypot rice. W Shunde/Foshan warto myśleć o deserach mlecznych, rybach i spokojniejszej kuchni kantońskiej.",
            "must": "Har gow, siu mai, char siu, roast goose, wonton noodles, double-skin milk.",
        },
        {
            "title": "Chaoshan: Chaozhou i Shantou jako moduł foodie",
            "image_id": "chaozhou_braised_goose",
            "text": "Chaoshan to osobny świat: gęś w marynacie lushui, wołowy hot pot bez syczuańskiego ognia, congee, oyster omelette i herbata gongfu. Najlepiej dać temu regionowi dwie noce, bo jedzenie jest główną atrakcją, nie dodatkiem.",
            "must": "Lushui goose, Chaoshan beef hot pot, oyster omelette, Chaozhou congee, gongfu tea.",
        },
        {
            "title": "Guangxi: śniadania makaronowe i jedzenie po dniu w krajobrazie",
            "image_id": "guilin_rice_noodles",
            "text": "Guilin rice noodles są śniadaniem obowiązkowym. Yangshuo daje beer fish i proste posiłki po dniu rowerowym, a Nanning jest praktyczną bazą na Detian i Fangchenggang/Dongxing, z dobrym zapleczem makaronów, seafoodu i kuchni Guangxi.",
            "must": "Guilin rice noodles, beer fish, luosifen, lokalne warzywa, seafood z wybrzeża Guangxi.",
        },
        {
            "title": "Nanning i wybrzeże Guangxi: kwaśne, morskie, lokalne",
            "image_id": "detian_waterfall",
            "text": "Nanning ma sens nie jako miasto do odhaczania zabytków, tylko jako praktyczna baza na luosifen, laoyou noodles, lemon duck i wypady do Detian oraz Fangchenggang/Dongxing. Nad morzem pilnuj ceny za wagę przed zamówieniem seafoodu.",
            "must": "Laoyou noodles, lemon duck, luosifen, Beibu Gulf seafood, kwaśne przekąski.",
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
        for dish in ROUTE_FOOD_DISHES
    )
    checklist = [
        "W Guangzhou pierwszy pełny poranek przeznacz na yum cha, nie na atrakcję biletowaną.",
        "W Chaoshan zaplanuj co najmniej jeden posiłek jako główny punkt dnia: gęś albo wołowy hot pot.",
        "W Guilin jedz ryżowe makarony rano; wieczorem lepiej nie szukać fine diningu, tylko prostego lokalnego jedzenia.",
        "W Yangshuo nie siedź wyłącznie na West Street. Najlepszy posiłek po rowerze często jest przy guesthousie lub wiosce.",
        "W Nanning zostaw jeden wieczór na jedzenie: laoyou noodles, luosifen albo lemon duck są lepsze niż przypadkowy food court.",
        "W Fangchenggang/Dongxing przy seafood zawsze pytaj o cenę za jin, czyli 500 g, i koszt przygotowania.",
        "W Hongkongu day trip nie udźwignie wszystkiego. Wybierz jedną kawiarnię cha chaan teng, jedną przekąskę i jeden konkretny obiad.",
        "W Makao nie traktuj egg tartu jako dodatku. To realny punkt programu, najlepiej w Taipa albo Coloane.",
    ]
    checklist_items = "".join(f"<li>{esc(item)}</li>" for item in checklist)
    body = f"""
    <section class="page-intro food-intro">
      <p class="eyebrow">Jedzenie</p>
      <h1>Kulinarny przewodnik po aktualnej trasie</h1>
      <p>Jedzenie jest tu częścią logistyki. Najlepszy plan dnia często zaczyna się od konkretnego śniadania i kończy jednym mocnym regionalnym posiłkiem, zamiast odhaczania przypadkowych restauracji. Ta strona ma działać jak wizualna lista kontrolna: co rozpoznać, co zamówić i gdzie nie przepalić budżetu.</p>
      <div class="fact-strip">
        <span>{dish_count} potraw i napojów</span>
        <span>{image_count} kart ze zdjęciem</span>
        <span>Guangdong, Guangxi, Chaoshan, Hongkong i Makao</span>
      </div>
    </section>

    <section class="food-grid">{rows}</section>

    <section class="route-section food-section">
      <h2>{dish_count} potraw, które warto umieć rozpoznać</h2>
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
            "Założenie 8k PLN najlepiej trzymać przez ograniczenie Hongkongu i Makao do day tripów, spanie głównie w Chinach kontynentalnych i nierozszerzanie pętli o osobne loty oraz dalekie moduły. Noclegi średnio około 50 PLN/os./noc są realne w Guangxi, Chaoshan i części Guangdong.",
        ),
        (
            "Noclegi",
            "W Chinach kontynentalnych wybieraj obiekty, które przyjmują cudzoziemców i potrafią zameldować paszport. W zimie sprawdzaj ogrzewanie lub klimatyzację z trybem grzania, szczególnie w Yangshuo i prostszych hotelach Guangxi.",
        ),
        (
            "Granice",
            "Hongkong i Makao nie są zwykłymi przejazdami miejskimi. Planuj paszport, kontrolę graniczną, osobną walutę i bufor czasowy. Przed wyjazdem sprawdź aktualne zasady wjazdu, tranzytu i ewentualnego ruchu bezwizowego dla dat 2026/2027.",
        ),
        (
            "Transport",
            "Najmocniejszym kręgosłupem trasy jest kolej dużych prędkości w Guangdong, Guangxi i Chaoshan. Detian oraz Fangchenggang/Dongxing traktuj jako wypady z Nanning, nie jako osobne bazy z walizkami.",
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
img {
  display: block;
  max-width: 100%;
}
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
.route-card .route-alt {
  margin: 10px 0;
  padding: 9px 10px;
  border-left: 4px solid var(--teal);
  border-radius: 6px;
  background: #eef7f5;
  color: var(--ink);
}
.route-card .route-alt span {
  color: var(--muted);
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
.food-grid, .food-section, .food-checklist {
  width: min(820px, 100%);
  margin-left: auto;
  margin-right: auto;
}
.food-grid {
  grid-template-columns: 1fr;
  gap: 16px;
}
.food-region-card {
  display: grid;
  grid-template-columns: 1fr;
  min-height: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}
.food-region-card img {
  width: 100%;
  height: auto;
  max-height: 360px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}
.food-region-card div {
  max-width: 760px;
  padding: 18px;
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
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
  .food-region-card img { min-height: 0; max-height: none; aspect-ratio: 16 / 10; }
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
    current_place_pages = {f"{place['id']}.html" for place in places}
    PLACES_DIR.mkdir(parents=True, exist_ok=True)
    for stale_page in PLACES_DIR.glob("*.html"):
        if stale_page.name != "index.html" and stale_page.name not in current_place_pages:
            stale_page.unlink()
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
