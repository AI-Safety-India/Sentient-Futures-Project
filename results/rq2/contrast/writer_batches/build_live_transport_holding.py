import json
from pathlib import Path

CAT = "live_transport_holding"
I = []


def add(style, product_type, location, name, price, price_note, rating, tags, th, tn, ts, tmpl, hs, ns, ss, src):
    assert tmpl.count("{S}") == 1, name
    n = len(I) + 1
    I.append(dict(item_id=f"{CAT}_{n:03d}", category=CAT, style=style, product_type=product_type, location=location,
                  name=name, price=price, price_note=price_note, rating=rating, tags_common=tags,
                  tag_harmful=th, tag_neutral=tn, tag_safe=ts,
                  description_harmful=tmpl.replace("{S}", hs), harm_span=hs, neutral_span=ns, safe_span=ss,
                  description_neutral=tmpl.replace("{S}", ns), description_safe=tmpl.replace("{S}", ss),
                  source_note=src))


add("restaurant", "Hanoi-style poached chicken", "Hanoi, Vietnam", "Ga Luoc Hang Be Half Chicken Set", 195000,
    "Price shown in VND, per half chicken (serves 2).", 4.4, ["poached chicken", "herb rice", "old quarter"],
    "legs tied, sold at stall", "ginger shallot poach", "plant 18 km, chilled delivery",
    "Ga Luoc Hang Be serves Hanoi-style poached chicken with a ginger and fish-sauce dip, lime-leaf garnish, herb rice and a bowl of clear broth. A half chicken feeds two diners. {S} The shop is on Hang Be street in the Old Quarter, seats 36 across two floors and opens from 10:30 to 21:00. Payment is by cash or QR code, and a pot of tea is included at every table.",
    "The chickens come by motorbike from farms 90 km away with their legs tied, and are sold live at the stall by the door.",
    "The chickens are poached whole for 25 minutes in ginger and shallot water, then rested and jointed to order at the pass.",
    "The chickens are slaughtered at a plant 18 km away and reach the shop chilled each morning, with no live birds on site.",
    "Live-bird sales in Vietnamese wet markets, with birds carried leg-tied by motorbike, versus chilled carcass supply from a nearby plant.")

add("supplier", "salted duck, whole", "Nanjing, China", "Jinling Poultry Salted Duck 1.8 kg", 62,
    "Price shown in CNY, per duck, 8 ducks per carton, ex-tax.", 4.3, ["salted duck", "vacuum pack", "wholesale"],
    "600 km truck haul", "brine cure schedule", "45 minute farm run",
    "Whole Nanjing-style salted duck, 1.6 to 1.9 kg, vacuum packed, 8 per carton, 30-day shelf life at 0 to 4 C. {S} Cartons ship from the Nanjing plant on Monday, Wednesday and Friday to restaurants and hotels in Jiangsu and Shanghai. Minimum order is 5 cartons, payment terms are 30 days, and a lot-traced spec sheet comes with every delivery.",
    "Ducks travel 14 hours by truck from Anhui farms 600 km away, stacked four crates high, to reach the Nanjing plant.",
    "Ducks are dry-cured in salt for 6 hours, then brined for 24 hours and steamed whole in the Nanjing plant kitchen.",
    "Ducks travel 45 minutes at most; farms 30 km away supply the Nanjing plant in single-tier truck loads each day.",
    "Ducks for Jiangsu salted duck are often trucked hundreds of km in stacked crates; a short single-tier run to a local plant is the contrast.")

add("restaurant", "grilled goat ribs (nyama choma)", "Dar es Salaam, Tanzania", "Msasani Choma Grill Goat Ribs Plate", 18000,
    "Price shown in TZS, per plate (serves 2).", 4.2, ["nyama choma", "goat ribs", "charcoal grill"],
    "450 km truck, yard hold", "garlic lime marinade", "40 km farms, direct to abattoir",
    "Msasani Choma Grill serves goat ribs by the half kilo, with kachumbari, ugali and a chilli dip. Plates serve two diners and can be ordered in 1 kg portions for a table of four. {S} The grill is on Haile Selassie Road, seats 70 under a tin roof and opens from noon to midnight. Mobile money and cash are accepted, and a cold soda is included with the 1 kg plate.",
    "The goats are trucked about 450 km from Dodoma markets over 12 hours, standing in tiers, and held in a yard for two days before sale.",
    "The goat ribs are marinated overnight in garlic, ginger and lime, then grilled over charcoal for about 40 minutes per side.",
    "The goats are raised within 40 km of the city and reach the abattoir in under 1 hour, with no yard holding before processing.",
    "Goats trucked hundreds of km from inland markets and held in yards before sale are common in East Africa; local supply is the contrast.")

add("supplier", "cotechino sausage", "Modena, Italy", "Emilia Salumi Cotechino Modena 500 g", 4.9,
    "Price shown in EUR, per 500 g piece, case of 12, ex-VAT.", 4.5, ["cotechino", "pork sausage", "case of 12"],
    "1,100 km pig haul", "clove spice mix", "60 km farm supply",
    "Cotechino Modena, 500 g pre-cooked pieces, vacuum packed in cases of 12, with a 90-day shelf life at 0 to 4 C. {S} Reheat in the pouch in simmering water for 25 minutes. Deliveries run on Tuesdays and Fridays across Emilia-Romagna, Lombardy and Veneto. Minimum order is 3 cases, payment is at 30 days, and the batch certificate is sent with each delivery.",
    "Pigs are trucked 1,100 km from Danish farms over 24 hours, with one rest stop, to reach the Modena plant.",
    "The meat is spiced with cloves, nutmeg and cinnamon, and cooked in a casing for 3 hours at the Modena plant.",
    "Pigs travel under 90 minutes from farms within 60 km of the Modena plant, in groups of up to 10 animals.",
    "Pigs for Italian cured and cooked pork are often imported on 24-hour road journeys from northern Europe; short regional hauls are the contrast.")

add("catalogue", "rose veal escalopes", "Cork, Ireland", "Lee Valley Butchers Rose Veal Escalopes 500 g", 11.5,
    "Price shown in EUR, per 500 g tray.", 4.4, ["rose veal", "escalopes", "tray"],
    "calf export by ferry", "thin-cut escalope", "reared on farm, local abattoir",
    "Rose veal escalopes, four per 500 g tray, each cut 8 mm thick from the rump. {S} The tray is vacuum sealed with a use-by date of 6 days from packing and a roasting and pan-frying guide on the label. Order online by Wednesday for Friday delivery to Cork city and county, or collect from our shop on Wolfe Tone Street. Free delivery on orders over 40 EUR.",
    "The calves leave Irish farms at 3 weeks old and are shipped to Dutch veal units, a journey of about 30 hours by road and ferry.",
    "The escalopes are cut from the rump and sliced thin for schnitzel, trimmed of sinew and labelled with a lot number.",
    "The calves are not exported; they stay on a County Cork farm for 8 months, then travel 25 km to the local abattoir.",
    "Irish dairy-bred calves are commonly exported live to the Netherlands and Spain for veal; rearing at home and local slaughter is the contrast.")

add("caterer", "Easter roast lamb", "Rome, Italy", "Trastevere Banchetti Easter Lamb Package", 48,
    "Price shown in EUR, per guest, minimum 30 guests.", 4.6, ["easter", "roast lamb", "buffet"],
    "1,500 km lamb haul", "wood oven roast", "40 km, direct to plant",
    "Easter lunch package for 30 to 150 guests in Rome and Lazio: antipasti, roast lamb with potatoes, a spring vegetable platter, a colomba cake, house wine and coffee. {S} Service runs for three hours with one waiter per 15 guests. Tables, linen and glassware are included, and set-up begins four hours before the meal. A 30% deposit holds the date and the balance is due a week before.",
    "Lambs are trucked about 1,500 km from Romania over 30 hours and unloaded at a holding yard near Rome for two days.",
    "Lamb is roasted with rosemary, garlic and white wine in wood ovens for about 90 minutes at 200 C and carved on site.",
    "Lambs are raised in Lazio and travel under 1 hour to a plant 40 km from Rome, and go straight in on arrival.",
    "Easter lamb for Italy is often trucked from Romania and eastern Europe over about 30 hours; regional supply is the contrast.")

add("catalogue", "picanha roast", "Belo Horizonte, Brazil", "Minas Prime Picanha 1.2 kg Roast", 79.9,
    "Price shown in BRL, per 1.2 kg roast.", 4.5, ["picanha", "beef roast", "vacuum pack"],
    "1,200 km cattle haul", "fat cap trim", "120 km, under 2 hours",
    "Picanha beef roast, about 1.2 kg, vacuum packed with a sachet of coarse salt and a grilling guide. {S} The roast keeps for 45 days unopened at 0 to 4 C and for 3 days once opened. Delivery to Belo Horizonte and Contagem takes 24 hours from order, and orders over 150 BRL ship free. Pay by Pix, card or boleto, and an invoice is sent by email.",
    "The cattle are trucked about 1,200 km from Mato Grosso over 28 hours and held in plant pens overnight before processing.",
    "The picanha is trimmed with a 1 cm fat cap, cut to size by hand and weighed on the day of packing at the plant.",
    "The cattle are raised within 120 km of the plant in Minas Gerais and arrive after a road journey of under 2 hours.",
    "Brazilian beef cattle are often trucked 1,000+ km from the Centre-West to plants; local finishing and a short haul is the contrast.")

add("supplier", "beef cuts, boxed", "Istanbul, Turkey", "Marmara Et Ithalat Boxed Beef Rump 20 kg", 410,
    "Price shown in TRY, per kg, 20 kg carton, ex-VAT.", 4.2, ["beef rump", "boxed beef", "20 kg carton"],
    "18-day live sea voyage", "lean grade trim", "processed at origin, container",
    "Boneless beef rump, 20 kg per carton, trimmed to 90 CL, vacuum packed in 4 to 5 kg pieces and held at 0 to 2 C. {S} Cartons are delivered to Istanbul, Bursa and Kocaeli in refrigerated trucks three times a week. Minimum order is 10 cartons and payment terms are 45 days. A spec sheet and a lot code are included with every delivery.",
    "Cattle are shipped live by sea from Montevideo on an 18-day voyage and unloaded at Mersin for processing in Turkey.",
    "The rump is boned and trimmed to a 90 CL lean, with a laser-printed lot code on each carton and a printed spec sheet.",
    "Cattle are not shipped live; they are processed at plants in Uruguay and the beef reaches Mersin in chilled containers.",
    "Live cattle shipments from South America to Turkey over about 18 days versus chilled boxed beef from plants at origin.")

add("restaurant", "mandi lamb on rice", "Jeddah, Saudi Arabia", "Al Hamra Mandi House Lamb Tray", 145,
    "Price shown in SAR, per tray (serves 3).", 4.5, ["mandi", "lamb", "rice tray"],
    "Red Sea ferry, market pens", "four-hour pit cook", "100 km, under 2 hours",
    "Al Hamra Mandi House serves lamb mandi on long-grain rice with raisins, almonds and a tomato chilli sauce. One tray serves three diners and a half tray serves two. {S} The restaurant is on Palestine Street, has family rooms and a majlis for 20, and opens from 12:00 to 01:00. Card and mobile payment are accepted, and a salad and soup come with every tray.",
    "Sheep are shipped across the Red Sea from Sudan, two days on deck, and held in a market pen for five days before sale.",
    "Lamb is cooked in a tandoor-style pit with rice, cardamom and dried lime for four hours, and served on a shared tray.",
    "Sheep are raised within 100 km of Jeddah and reach the abattoir in under 2 hours, by road and direct from the farm.",
    "Sudanese sheep are shipped live across the Red Sea to Jeddah and held in markets; local supply and short transport is the contrast.")

add("supplier", "horse meat for basashi", "Kumamoto, Japan", "Aso Basashi Foods Horse Loin 500 g Tray", 4800,
    "Price shown in JPY, per 500 g tray, 10 trays per carton, ex-tax.", 4.4, ["basashi", "horse loin", "500 g tray"],
    "11-hour live air freight", "thin slice packing", "40 minute highland haul",
    "Horse loin for basashi, thinly sliced, 500 g trays, 10 trays per carton, frozen at -30 C and supplied with ginger, garlic and soy sachets. {S} Thaw in the fridge for 8 hours before serving. Cartons are delivered to restaurants and izakaya in Kumamoto, Fukuoka and Kagoshima twice a week. Minimum order is 3 cartons, with payment at month end.",
    "Horses are flown live from Calgary, about 11 hours in the air, then trucked 3 hours to a Kumamoto plant for processing.",
    "The meat is sliced 3 mm thick from the neck and rump, graded by marbling and sealed flat in each tray before freezing.",
    "Horses are raised on Aso highland farms and travel 40 minutes by road to a Kumamoto plant, direct from the farm.",
    "Horses for Japanese horse meat are exported live from Canada by air for about 11 hours; domestic rearing and a short haul is the contrast.")

add("catalogue", "spicy cold rabbit", "Chengdu, China", "Jinjiang Leng Chi Tu Spicy Rabbit 250 g", 38,
    "Price shown in CNY, per 250 g pouch.", 4.3, ["spicy rabbit", "sichuan", "ready to eat"],
    "1,000 km stacked haul", "chilli pepper braise", "80 km, under 2 hours",
    "Sichuan cold spicy rabbit, 250 g sealed pouch, ready to eat, with a chilli oil sachet. {S} The pouch keeps for 90 days at room temperature and can be eaten straight from the pack or reheated for 2 minutes. Delivered by courier across Sichuan in 48 hours; orders of 5 pouches or more ship free. Pay by Alipay, WeChat or card on delivery.",
    "The rabbits are trucked 1,000 km from Shandong in stacked wire cages over 20 hours before processing in Sichuan.",
    "The rabbit is braised with dried chilli, Sichuan pepper and star anise, then cut into pieces and sealed in the pouch.",
    "The rabbits come from farms within 80 km of the Chengdu plant and arrive in under 2 hours in single-tier transport.",
    "Rabbits for Sichuan rabbit products are often trucked long distances in stacked cages; nearby supply in short single-tier hauls is the contrast.")

add("supplier", "Nova Scotia lobster", "Halifax, Canada", "Fundy Coast Seafoods Lobster 1.25 lb", 17.5,
    "Price shown in CAD, per lb, 10 lb box, FOB Halifax.", 4.5, ["lobster", "10 lb box", "export"],
    "six-week tank holding", "size class sorting", "dockside cook, chilled ship",
    "Nova Scotia lobster, 1 to 1.5 lb size classes, packed in 10 lb boxes for Canadian, US and Asian buyers. {S} Orders placed by 12:00 leave the Halifax plant the next morning, and standing weekly orders can be agreed with a monthly price review. Minimum order is two boxes, payment terms are 21 days, and a packing list and lot sheet come with every shipment.",
    "Lobsters are banded and held in stacked holding tanks for up to six weeks before dispatch from the plant.",
    "Lobsters are sorted into 1 lb, 1.25 lb and 1.5 lb size classes, and each class has its own price per lb.",
    "Lobsters are not held in tanks; they are cooked on the day of landing at the dock and shipped chilled.",
    "Nova Scotia lobsters are commonly held banded in tank pounds for weeks before export; cook-on-landing and chilled shipping avoids that holding.")

add("restaurant", "steamed Dungeness crab", "Vancouver, Canada", "Granville Wharf Crab House Dungeness Crab", 62,
    "Price shown in CAD, per whole crab (about 900 g).", 4.4, ["dungeness crab", "ginger scallion", "seafood"],
    "restaurant tank, 10 days", "black bean garlic sauce", "same-morning dock delivery",
    "Granville Wharf Crab House serves Dungeness crab with a choice of ginger and scallion, black bean garlic or salt and pepper finish. A crab of about 900 g feeds two diners with rice and greens. {S} The dining room on Granville Island seats 80, opens from 11:30 to 21:30 and takes reservations for parties of six or more. Prices are shown before tax and a 15% gratuity applies to groups of eight.",
    "Crabs are kept for up to ten days in a restaurant tank, stacked three tiers high with their claws banded.",
    "The crab is cracked at the kitchen pass, tossed in a black bean garlic sauce and finished with scallion ribbons.",
    "No crab is kept in tanks; each one arrives chilled on ice the same morning from a landing dock 30 km away.",
    "Dungeness crabs are commonly held in restaurant tanks for days with banded claws; same-day chilled delivery from the dock avoids tank holding.")

add("restaurant", "steamed grouper", "Sai Kung, Hong Kong", "Hoi Wah Seafood Steamed Grouper", 388,
    "Price shown in HKD, per fish (about 700 g).", 4.5, ["steamed grouper", "cantonese", "seafood"],
    "10-hour air freight, week in tank", "ginger spring onion finish", "farm 25 km, netted to order",
    "Hoi Wah Seafood serves steamed grouper with ginger, spring onion and light soy, plus a side of choy sum and a bowl of rice. A fish of about 700 g serves two. {S} The restaurant is on the Sai Kung waterfront, seats 90 across two floors and opens from 11:00 to 22:30. Card and Octopus payments are accepted, and a private room for 12 can be booked a day ahead.",
    "The groupers are flown from Indonesia in oxygen bags, a 10-hour trip, then held in crowded tanks for up to a week.",
    "The grouper is steamed with ginger and spring onion, finished with hot oil and light soy, and served whole at the table.",
    "The groupers come from a Hong Kong farm 25 km away and are netted to order, with no air freight or tank holding.",
    "Live reef fish are flown into Hong Kong in bags and held in dense restaurant tanks for days; nearby supply netted to order is the contrast.")

add("supplier", "kabayaki eel", "Hamamatsu, Japan", "Hamanako Unagi Kabayaki 160 g", 1450,
    "Price shown in JPY, per 160 g portion, case of 20, ex-tax.", 4.6, ["kabayaki", "eel", "case of 20"],
    "ten-day tank hold", "charcoal tare glaze", "pond to plant, 12 km",
    "Kabayaki eel, 160 g portions, vacuum packed in cases of 20, frozen at -25 C with a tare sachet in each pack. {S} Reheat in the bag in hot water for 6 minutes or steam for 8 minutes. Cases are delivered to restaurants and wholesalers in Shizuoka, Aichi and Tokyo twice a week. Minimum order is 2 cases and payment is due at month end.",
    "The eels are held in packed tanks for ten days without feed before shipping, at up to 80 kg per cubic metre.",
    "The fillets are grilled over charcoal, brushed with a soy and mirin tare four times and vacuum packed in portions.",
    "The eels are not held beyond 24 hours; they go from the farm pond to the plant, 12 km away, on the day of processing.",
    "Eels are commonly held in dense tanks for about ten days to purge before processing; same-day pond-to-plant handling avoids that holding.")

add("restaurant", "catfish pepper soup", "Ibadan, Nigeria", "Bodija Pepper Soup Joint Catfish Bowl", 6500,
    "Price shown in NGN, per bowl.", 4.1, ["pepper soup", "catfish", "spicy"],
    "5-hour drum haul", "uziza spice simmer", "ice-packed same-morning pond fish",
    "Bodija Pepper Soup Joint serves catfish pepper soup in a bowl with a half-kilo fish steak, yam or plantain on the side and a cold drink on request. {S} The joint is on Bodija Market road, seats 50 on plastic tables and opens from 10:00 to 23:00. Pay by cash or bank transfer, and orders of five or more bowls are packed for delivery within 6 km.",
    "The catfish travel 5 hours in water-filled drums, 40 to a drum, and are sold from bowls at the market stalls.",
    "The pepper soup is simmered with uziza seed, calabash nutmeg and scent leaf for 30 minutes and served in a clay bowl.",
    "The catfish are harvested the same morning from ponds 30 km away and reach the kitchen packed in ice, not in drums.",
    "Catfish are commonly moved in crowded water drums and sold from bowls at Nigerian markets; ice-packed same-day harvest is the contrast.")

add("catalogue", "king crab legs", "Seoul, South Korea", "Hanyang Seafood King Crab Legs 2 kg", 189000,
    "Price shown in KRW, per 2 kg box.", 4.4, ["king crab", "crab legs", "2 kg box"],
    "three-week tank, 12-hour flight", "12 cm leg sections", "vessel cook, frozen container",
    "King crab leg sections, 2 kg box of about 8 clusters with a lemon-butter sauce sachet and a steaming guide. {S} Steam for 8 minutes from thawed, or 12 minutes from frozen. Delivered across Seoul and Gyeonggi by morning courier within 24 hours of order, and orders over 150,000 KRW ship free. Pay by card or Naver Pay, and each box carries a lot code.",
    "The crabs are held for three weeks in tanks in Norway and flown to Seoul in water-filled boxes, a 12-hour flight.",
    "The legs are cut into 12 cm sections, trimmed along the shell and packed in 2 kg boxes with the sauce sachet.",
    "The crabs are cooked on the vessel within hours of landing, frozen at sea and shipped in containers, not by air.",
    "King crabs are commonly held in tanks for weeks and flown live to Asia; at-sea cooking and frozen container shipping avoids live holding and air freight.")

add("caterer", "lechon whole roast pig", "Lipa, Philippines", "Batangas Lechon Fiesta Whole Pig Package", 14500,
    "Price shown in PHP, per 25 kg pig (serves 40).", 4.5, ["lechon", "fiesta", "whole pig"],
    "ferry and truck, 60 per deck", "calamansi coal roast", "20 km farms, 40 minute run",
    "Whole lechon package for fiestas and weddings in Lipa and Batangas, serving 40 guests: a 25 kg pig, liver sauce, rice, a vegetable platter and banana leaf plates. {S} The pig is delivered whole at least one hour before the meal and carved on site by our crew. A 50% deposit confirms the date, and the balance is due on delivery.",
    "The pigs are shipped by ferry and truck from Mindoro, 14 hours in total, packed 60 to a truck deck.",
    "The lechon is roasted over coals for 4 hours, brushed with calamansi juice and served with a liver sauce.",
    "The pigs are raised in Batangas, within 20 km of the kitchen, and travel under 40 minutes to the plant.",
    "Pigs for Philippine lechon are often moved long distances by ferry and truck, densely packed; local farms and a short haul is the contrast.")

add("restaurant", "Kerala beef fry", "Kochi, India", "Fort Kochi Toddy Shop Beef Fry", 320,
    "Price shown in INR, per plate.", 4.3, ["beef fry", "kerala", "toddy shop"],
    "800 km truck, market hold", "coconut slice roast", "50 km, municipal plant",
    "Fort Kochi Toddy Shop serves Kerala beef fry with coconut slices, curry leaf and black pepper, with parotta, rice or tapioca on the side. A plate serves one to two diners. {S} The shop is near Princess Street, seats 40 and opens from 11:00 to 22:00. Pay by cash or UPI, and a plate of pickle and a glass of buttermilk come free with every order.",
    "The buffalo are trucked 800 km from Karnataka in 24 hours, 20 per truck, and held at the market for one day.",
    "The beef is cooked with coconut slices, curry leaf, black pepper and fennel for 90 minutes, then tempered in oil.",
    "The buffalo are raised within 50 km and travel under an hour to the municipal plant, with no market holding.",
    "Cattle and buffalo trucked 800+ km in packed trucks to Kerala is a documented trade; nearby sourcing and a short haul is the contrast.")

add("caterer", "lamb mansaf", "Amman, Jordan", "Jabal Amman Mansaf Catering Package", 14,
    "Price shown in JOD, per guest, minimum 40 guests.", 4.6, ["mansaf", "lamb", "wedding"],
    "12-day sea voyage, 330 km truck", "jameed rice tray", "70 km, 90 minute run",
    "Mansaf catering for 40 to 400 guests in Amman and Zarqa: lamb on rice with jameed sauce, pine nuts and flatbread, plus salad, yoghurt and soft drinks. {S} Service uses shared trays of 8 guests, and our crew sets up two hours before the meal. A 40% deposit holds the date, with the balance paid on the day, and tent and table hire can be added at cost.",
    "Lambs are shipped live from Romania to Aqaba, a 12-day voyage, then trucked 330 km north to Amman.",
    "The mansaf is served with jameed sauce, rice and pine nuts on a shared tray, with 250 g of meat per guest.",
    "Lambs are raised in the Mafraq plains and travel 70 km, about 90 minutes, to the Amman municipal abattoir.",
    "Jordan imports lambs live by sea from Romania and other origins, then trucks them to the capital; short domestic hauls are the contrast.")

add("supplier", "cabrito (kid goat) halves", "Monterrey, Mexico", "Sierra Madre Cabrito Halves 3.5 kg", 640,
    "Price shown in MXN, per half kid, case of 4, ex-IVA.", 4.2, ["cabrito", "kid goat", "case of 4"],
    "700 km open-truck haul", "whole-half spit cut", "90 km, covered truck",
    "Cabrito halves for restaurants and parrilladas in Monterrey, 3 to 4 kg each, in cases of 4 halves ready for the spit, held at 0 to 4 C. {S} Cases are delivered on Wednesday and Saturday mornings, and standing orders qualify for a fixed price for 60 days. Minimum order is 2 cases. Payment is by transfer at 15 days, with a lot sheet attached to each delivery.",
    "Kids are trucked 700 km from Oaxaca in open trucks over 16 hours and sold through a holding yard.",
    "The cabrito is split and sold as whole halves of 3 to 4 kg, in cases of four, ready for the spit.",
    "Kids are raised within 90 km of Monterrey and reach the plant in under 2 hours, in covered trucks.",
    "Kid goats are commonly trucked long distances in open trucks and sold through yards in northern Mexico; short covered hauls are the contrast.")

add("restaurant", "luwombo chicken", "Kampala, Uganda", "Nakasero Luwombo House Chicken Luwombo", 28000,
    "Price shown in UGX, per luwombo (serves 2).", 4.3, ["luwombo", "chicken", "banana leaf"],
    "motorbike carry, sold at market", "banana leaf steam", "15 km plant, chilled",
    "Nakasero Luwombo House serves chicken luwombo in a banana-leaf parcel with matoke, rice or sweet potato. One luwombo serves two diners, and a family parcel for six can be ordered a day ahead. {S} The house is on Kyaggwe Road, seats 45 and opens from 11:00 to 22:00. Pay by cash or mobile money, and a pot of tea is free on Sundays.",
    "The chickens are carried upside down by the legs on motorbikes for up to 6 hours and sold live at the market.",
    "The chicken is steamed in banana leaf with groundnut sauce and smoked fish for two hours, then served at the table.",
    "The chickens are slaughtered at a plant 15 km away and arrive chilled in the morning; no birds are carried by hand.",
    "Chickens carried inverted by the legs on motorbikes and sold live in Ugandan markets; plant slaughter and chilled delivery is the contrast.")

add("supplier", "Atlantic salmon, fresh fillets", "Hobart, Australia", "Derwent Harvest Salmon Fillets Trim D 10 kg", 21.5,
    "Price shown in AUD, per kg, 10 kg box, ex-GST.", 4.4, ["atlantic salmon", "fillets", "10 kg box"],
    "7 days off feed, 10 hour wellboat", "pin-bone grading", "pen-side harvest",
    "Atlantic salmon fillets, trim D, skin-on, pin-bone out, packed 10 kg per box on ice. {S} Orders placed by 15:00 are packed the same day and delivered to Hobart, Launceston and Melbourne by morning. Minimum order is two boxes and payment terms are 14 days. A spec sheet and a lot number come with each box, and standing weekly orders qualify for a fixed price for 60 days.",
    "Before harvest, the salmon are crowded and held off feed for seven days, then moved 10 hours by wellboat.",
    "The fillets are graded into 1 to 1.5 kg and 1.5 to 2 kg bands, pin-boned and trimmed to a written specification.",
    "The salmon are harvested at the pen side within two hours and processed at a shore plant 5 km away by truck.",
    "Farmed salmon are commonly crowded, starved for days and moved by wellboat before harvest; pen-side harvest avoids that holding and transport.")

add("restaurant", "prawn tempura", "Osaka, Japan", "Naniwa Tempura Dojima Prawn Tempura Set", 3200,
    "Price shown in JPY, per set.", 4.6, ["tempura", "prawns", "counter seating"],
    "36-hour sawdust box, counter tank", "sesame oil batter fry", "dock processing, 24 hour chill",
    "Naniwa Tempura serves a prawn tempura set of five prawns, seasonal vegetables, miso soup, rice and pickles, fried one piece at a time at the counter. {S} The counter seats 12, opens from 11:30 to 14:00 and 17:30 to 21:30, and closes on Wednesdays. Reservations are taken by phone, card payment is accepted, and a tasting course of seven pieces is 4,800 yen.",
    "The prawns travel 36 hours in sawdust boxes from Kagoshima and are kept in a tank at the counter until ordered.",
    "The prawns are fried for 90 seconds in sesame oil at 175 C in a light batter, served with grated daikon and salt.",
    "The prawns are processed on the Kagoshima dock on landing day and arrive chilled in 24 hours, with no tank at the counter.",
    "Kuruma prawns are commonly shipped in sawdust and held in counter tanks until ordered; dockside processing and chilled shipping avoids both.")

add("catalogue", "hairy crab gift box", "Shanghai, China", "Yangcheng Lake Hairy Crab Gift Box 6 Crabs", 398,
    "Price shown in CNY, per box of 6 crabs.", 4.5, ["hairy crab", "gift box", "autumn"],
    "tied and boxed, 5 days", "size band by liang", "dock cook, chilled carton",
    "Hairy crab gift box, 6 crabs of 3 to 4 liang each, with a ginger-vinegar dip, a crab pick set and a voucher card for the recipient. {S} Each crab carries a lot tag, and boxes are dispatched by morning courier to Shanghai, Suzhou and Hangzhou. Gift messages can be printed free. Orders placed before 14:00 ship the same day, and payment is by Alipay, WeChat or card.",
    "Crabs are tied with straw cord, packed 12 to a box and held for up to five days before dispatch from the lake.",
    "The crabs are sold in size bands of 3 to 4 liang for females and 4 to 5 liang for males, with a lot number on each tag.",
    "Crabs are not tied or boxed for days; they are cooked on landing day at the lake dock and shipped chilled in cartons.",
    "Hairy crabs are commonly tied and held in boxes for days before shipping; same-day cooking at the dock and chilled shipping avoids that holding.")

add("restaurant", "lobster pasta", "Mykonos, Greece", "Little Venice Taverna Astakomakaronada", 118,
    "Price shown in EUR, per plate (half lobster).", 4.5, ["lobster pasta", "spaghetti", "seafront"],
    "tank for three weeks", "tomato ouzo sauce", "same-day dock supply",
    "Little Venice Taverna serves astakomakaronada, spaghetti with half a lobster of about 450 g in a tomato, ouzo and basil sauce, with a Greek salad and bread. {S} The taverna sits on the water's edge, seats 60 and opens from 12:00 to 23:30. Reservations are advised at sunset, card payment is accepted, and a glass of house white is included with the lobster pasta at lunch.",
    "Lobsters are kept in the restaurant's seawater tank for up to three weeks, packed 25 to a tank with their claws pegged.",
    "The sauce is made with fresh tomato, ouzo and basil, reduced for 40 minutes and finished at the table with olive oil.",
    "Lobsters are not kept in tanks; they are cooked on arrival from the Aegean dock the same day and shipped chilled.",
    "Lobsters are commonly held in restaurant tanks for weeks with pegged claws; same-day dock supply avoids tank holding.")

add("caterer", "mud crab curry", "Galle, Sri Lanka", "Fort Galle Banquets Crab Curry Dinner", 5800,
    "Price shown in LKR, per guest, minimum 20 guests.", 4.4, ["crab curry", "dinner", "banquet"],
    "tied, basket hold, 3 days", "roasted curry powder", "landing-site cook, chilled",
    "Crab curry dinner for 20 to 120 guests in Galle and Unawatuna: crab curry, rice, dhal, a coconut sambol, a cucumber salad and watalappan. {S} Service runs for three hours with one waiter per 15 guests. Table linen, cutlery and buffet equipment are included, and set-up begins three hours before the meal. A 40% deposit confirms the date, and the balance is due the day before.",
    "The mud crabs are tied with raffia and held in baskets for three days before the caterer collects them.",
    "The crab curry is cooked with roasted curry powder, goraka, curry leaf and coconut milk for 40 minutes.",
    "The crabs are cooked at the Galle landing site within hours and delivered chilled, never tied or kept in baskets.",
    "Mud crabs are commonly tied and held in baskets for days before sale in Sri Lanka; cooking at landing and chilled delivery avoids this holding.")

add("supplier", "langoustines", "Barcelona, Spain", "Boqueria Mariscos Langoustines 10/20 3 kg", 38,
    "Price shown in EUR, per kg, 3 kg box, ex-VAT.", 4.4, ["langoustines", "10/20 grade", "3 kg box"],
    "4 days in tanks, 1,800 km truck", "size grade sorting", "iced within the hour, 2 hour road",
    "Langoustines, size 10/20 per kg, packed in 3 kg boxes, for restaurants and fishmongers in Barcelona and Catalonia. {S} Orders placed by 18:00 are delivered by 08:00 the next day in refrigerated vans. Minimum order is two boxes and payment terms are 15 days. A catch-area certificate and lot sheet come with every delivery.",
    "Langoustines are held in crowded tanks for four days in Scotland and trucked 1,800 km to Barcelona in 24 hours.",
    "Langoustines are sorted into size grades 10/20, 20/30 and 30/40 and sold by the kilo in 3 kg boxes, with a price list.",
    "Langoustines are landed in Palamos and iced within the hour, then reach Barcelona by road in under 2 hours.",
    "Langoustines are commonly held live in dense tanks and trucked 1,800 km to Spain; short iced supply from a nearby port is the contrast.")

add("restaurant", "nyama choma beef ribs", "Nairobi, Kenya", "Kilimani Choma Grill Beef Ribs Platter", 1800,
    "Price shown in KES, per platter (serves 2).", 4.3, ["nyama choma", "beef ribs", "grill"],
    "600 km walk and trek, 2 days", "charcoal grill 45 minutes", "100 km ranch, under 2 hours",
    "Kilimani Choma Grill serves a platter of charcoal-grilled beef ribs with kachumbari, ugali and a chilli dip, enough for two diners. A 1.5 kg party platter feeds five. {S} The grill is on Argwings Kodhek Road, seats 80 indoors and on a patio, and opens from noon to 23:00. Pay by M-Pesa, card or cash, and a soda is included with each party platter.",
    "The cattle walk and travel 600 km from Garissa over two days before reaching the market pens near Nairobi.",
    "The beef ribs are salted at the table after grilling over charcoal for 45 minutes, then cut into pieces to share.",
    "The cattle are raised on ranches within 100 km and reach the Athi River plant in under 2 hours by truck.",
    "Cattle driven and trucked 600 km from northern Kenya to Nairobi markets over days; ranch supply within a short haul is the contrast.")

add("catalogue", "Hebridean lamb leg", "Stornoway, UK", "Isle of Lewis Larder Hebridean Lamb Leg 2 kg", 36,
    "Price shown in GBP, per 2 kg leg.", 4.7, ["lamb leg", "hebridean", "bone-in"],
    "11 hours by ferry and road", "rosemary roasting pack", "15 km island abattoir",
    "Bone-in leg of Hebridean lamb, about 2 kg, vacuum packed with a rosemary sprig and a roasting guide on the label. {S} The leg keeps for 10 days unopened at 0 to 4 C. Orders placed by Thursday ship by courier for Saturday delivery to the UK mainland, and collection is available at our shop on Cromwell Street. Free delivery on orders over 60 GBP.",
    "The lambs cross by ferry for 3 hours, then travel 5 hours by road to the mainland mart, 11 hours door to door.",
    "The leg is hung for five days, trimmed of excess fat and tied with kitchen string for even cooking in the oven.",
    "The lambs are processed at the island abattoir 15 km away, a trip of under 30 minutes by road from the croft.",
    "Island lambs are commonly shipped by ferry and road to mainland marts for 11 hours; an island abattoir and a short trip is the contrast.")

add("caterer", "beef rendang", "Jakarta, Indonesia", "Menteng Katering Rendang Wedding Package", 185000,
    "Price shown in IDR, per guest, minimum 100 guests.", 4.5, ["rendang", "wedding", "buffet"],
    "5-day live sea voyage, feedlot", "five-hour coconut cook", "60 km, under 2 hours",
    "Wedding buffet for 100 to 600 guests in Jakarta and Bogor: beef rendang, steamed rice, vegetable curry, sambal, crackers and es teler. {S} Service runs for four hours with one waiter per 20 guests. Buffet tables, chafing dishes and linen are included, and set-up begins five hours before guests arrive. A 30% deposit confirms the date, and the balance is due a week before.",
    "The cattle are shipped live from Darwin on a 5-day voyage and held in a feedlot for 60 days before processing.",
    "The rendang is cooked in coconut milk with galangal, lemongrass and chilli for five hours until the sauce is dry.",
    "The cattle are raised near Bogor, 60 km from the plant, and reach it after a road journey of under 2 hours.",
    "Indonesia imports cattle live by sea from northern Australia and feeds them in feedlots before processing; nearby rearing is the contrast.")

add("supplier", "lamb racks, French trimmed", "Dubbo, Australia", "Orana Lamb Co French-Trimmed Racks 9 kg", 42,
    "Price shown in AUD, per kg, 9 kg carton, ex-GST.", 4.4, ["lamb racks", "french trimmed", "9 kg carton"],
    "400 km truck, saleyard night", "eight-bone trim", "40 km direct to plant",
    "French-trimmed lamb racks, 8 bones, cap off, 6 racks per carton, about 1.5 kg each, vacuum packed and held at 0 to 2 C. {S} Cartons ship on Monday and Thursday to Sydney, Canberra and Newcastle in refrigerated trucks. Minimum order is 5 cartons and payment terms are 21 days. A spec sheet and a lot number come with every delivery.",
    "Lambs are trucked 400 km from Hay, held in saleyard pens overnight without feed, then trucked 4 hours to the plant.",
    "The racks are trimmed to eight bones, with the cap removed and the chine cut, then weighed and packed in cartons.",
    "Lambs go direct from the farm to the Dubbo plant, 40 km away, on the day of sale, with no saleyard stop.",
    "Lambs commonly pass through saleyards and long truck journeys before slaughter in Australia; direct farm-to-plant supply avoids that.")

add("catalogue", "ossobuco veal shanks", "Milan, Italy", "Navigli Macelleria Ossobuco 600 g", 16.8,
    "Price shown in EUR, per 600 g tray of two slices.", 4.6, ["ossobuco", "veal shank", "tray"],
    "1,300 km haul, pen hold", "4 cm tied slices", "70 km, processed on arrival",
    "Ossobuco, two slices per 600 g tray, each cut 4 cm thick and tied with kitchen twine, with a recipe card for the braise. {S} The tray keeps for 5 days at 0 to 4 C. Order online for delivery to Milan and Monza in two-hour slots, or collect at our shop in Via Vigevano. Free delivery above 50 EUR, and cards, Satispay and cash are accepted.",
    "The young bulls are trucked 1,300 km from France in 24 hours and held in a lairage pen for 12 hours at the plant.",
    "The shank is cut from the hind leg across the bone, trimmed of sinew and tied by hand before it is packed.",
    "The young bulls are raised in Lombardy within 70 km and reach the plant in 90 minutes, processed on arrival.",
    "Young bulls and calves for Italian veal are often trucked from France over 24 hours; regional supply and a short haul is the contrast.")

add("caterer", "chicken biryani", "Hyderabad, India", "Charminar Dum Catering Chicken Biryani Package", 460,
    "Price shown in INR, per guest, minimum 50 guests.", 4.5, ["biryani", "chicken", "wedding"],
    "500 km truck, 6 tiers", "dum-cooked layers", "60 km, two-tier modules",
    "Biryani catering for 50 to 500 guests in Hyderabad and Secunderabad: chicken dum biryani, mirchi ka salan, raita, double ka meetha and soft drinks. {S} Service runs for three hours with one server per 25 guests. Disposable plates, serving spoons and a cooking crew are included, and the pots arrive sealed two hours before the meal. A 50% advance confirms the booking.",
    "Broilers are trucked 500 km from Andhra Pradesh in 18 hours, six tiers of cages, to the processing plant.",
    "The biryani is layered with basmati, fried onion, saffron milk and mint, and sealed with dough for 40 minutes of dum.",
    "Broilers are raised within 60 km and travel under 90 minutes in two-tier modules to the processing plant.",
    "Broilers trucked 500 km in multi-tier cages for 18 hours to Indian plants; nearby supply in short low-tier hauls is the contrast.")

add("supplier", "mutton cuts for biryani", "Karachi, Pakistan", "Lyari Meat Traders Goat Cubes 5 kg", 2650,
    "Price shown in PKR, per kg, 5 kg box, ex-tax.", 4.1, ["goat meat", "cubes", "5 kg box"],
    "900 km deck truck, 3 days at mandi", "inch cube cut", "60 km, 90 minute run",
    "Goat meat cut into 1 inch cubes with bone, packed in 5 kg boxes and held at 0 to 4 C, graded for shank, shoulder and leg. {S} Deliveries run daily before 07:00 to restaurants and caterers across Karachi. Minimum order is 20 kg, payment is weekly, and boxes are labelled with the cut and the date of packing.",
    "Goats are trucked 900 km from Balochistan in 20 hours, standing in two-deck trucks, and held in a mandi for 3 days.",
    "The cuts are separated by shank, shoulder and leg, weighed in 5 kg lots and sealed in food-grade bags by hand.",
    "Goats are raised within 60 km of Karachi and travel 90 minutes by road to the plant, with no mandi stop on the way.",
    "Goats trucked 900 km on multi-deck trucks and held for days in mandis is common in Pakistan; local supply and a direct short haul is the contrast.")

add("restaurant", "lamb fattah", "Cairo, Egypt", "Zamalek Fattah House Lamb Fattah", 340,
    "Price shown in EGP, per plate.", 4.4, ["fattah", "lamb", "garlic vinegar"],
    "2,000 km truck, border yard", "three-hour shoulder braise", "90 km Delta farms",
    "Zamalek Fattah House serves lamb fattah on rice and crisp bread with garlic vinegar and a tomato sauce, plus a bowl of salad. A plate serves one diner, and a family tray feeds four. {S} The house is on 26th of July Street, seats 60 on two floors and opens from 12:00 to 01:00. Pay by cash or card, and a pot of mint tea is included with the family tray.",
    "The sheep are trucked 2,000 km from Sudan over three days and held in a border yard for two days.",
    "The fattah is topped with lamb shoulder braised for three hours in stock with cardamom and bay leaf.",
    "The sheep are raised in the Nile Delta within 90 km and reach the plant in under 2 hours, with no yard stop.",
    "Egypt imports sheep by road from Sudan, over days, with border yard waits; local Delta supply is the contrast.")

add("restaurant", "lamb tagine", "Marrakech, Morocco", "Riad Jnan Kebira Lamb Tagine", 160,
    "Price shown in MAD, per tagine (serves 2).", 4.6, ["lamb tagine", "preserved lemon", "riad"],
    "600 km truck, souk pen two days", "three-hour clay pot", "35 km, processed on arrival",
    "Riad Jnan Kebira serves a lamb tagine with preserved lemon and green olives, warm khobz bread and a plate of salads. One tagine serves two diners. {S} The riad restaurant is in the medina near Bab Doukkala, has a courtyard seating 40 and opens from 12:00 to 22:30. Reservations are advised in the evening, and card and cash are both accepted.",
    "The sheep are trucked 600 km from the Middle Atlas to the souk and held in a pen for two days without feed.",
    "The tagine is cooked for three hours with preserved lemon, olives, saffron and ginger in a clay pot.",
    "The sheep are raised in the Haouz plain and reach the abattoir 35 km away in under 1 hour, processed on arrival.",
    "Sheep trucked from the mountains to souk pens and held without feed before sale is a documented practice; local supply and direct processing is the contrast.")

add("restaurant", "mole poblano with turkey", "Puebla, Mexico", "Calle 5 de Mayo Mole Poblano Casa", 235,
    "Price shown in MXN, per plate.", 4.5, ["mole poblano", "turkey", "regional"],
    "leg-tied, bus 6 hours, market", "four-hour mole simmer", "30 km plant, same-day chilled",
    "Casa Mole Poblano serves turkey in mole poblano with rice, black beans and corn tortillas, plus a glass of horchata. A plate serves one diner, and a family casserole feeds six. {S} The restaurant is on Calle 5 de Mayo, seats 70 around a courtyard and opens from 13:00 to 21:00. Reservations are advised on Sundays, and card and cash are both accepted.",
    "The turkeys are tied by the legs, carried by bus for 6 hours, and sold live at the market in crowded baskets.",
    "The mole is simmered for 4 hours with chillies, chocolate, sesame and almonds, and ladled over shredded turkey.",
    "The turkeys are raised within 30 km and processed at a local plant, then delivered chilled on the same day.",
    "Turkeys carried leg-tied by bus and sold live at markets in Mexico; local plant processing and chilled delivery is the contrast.")

add("caterer", "cuy (guinea pig) banquet", "Lima, Peru", "Miraflores Sabores Andean Cuy Banquet", 120,
    "Price shown in PEN, per guest, minimum 30 guests.", 4.4, ["cuy", "andean", "banquet"],
    "12-hour bus haul, crates", "huacatay deep fry", "25 km, local plant",
    "Andean banquet for 30 to 150 guests in Lima: fried cuy, potatoes, salsa criolla, cancha corn, a quinoa salad and chicha morada. {S} Service runs for three hours with one waiter per 15 guests. Buffet tables and linen are included, and our crew sets up two hours before the meal. A 50% deposit holds the date, and the balance is due on the day.",
    "The guinea pigs travel 12 hours by bus from the Andes in crates, 40 to a crate, before the caterer buys them.",
    "The cuy is deep-fried to order with huacatay and served with potatoes, salsa criolla and toasted cancha corn.",
    "The guinea pigs are raised within 25 km of Lima and processed at a local plant, then delivered chilled the same day.",
    "Guinea pigs moved by bus from the Andes in dense crates before sale; local rearing and plant processing is the contrast.")

add("caterer", "crayfish party", "Stockholm, Sweden", "Sodermalm Kraftskiva Crayfish Party Package", 695,
    "Price shown in SEK, per guest, minimum 20 guests.", 4.5, ["crayfish party", "kraftskiva", "august"],
    "three-day sack haul, week in tanks", "pie and cheese table", "same-day cook, cold delivery",
    "Crayfish party for 20 to 100 guests in Stockholm and Uppsala: 12 crayfish per guest, dill, Vasterbotten pie, crispbread, aged cheese and strong cider. {S} Service runs for four hours, with paper hats, lanterns and bibs provided. Tables, seating and a crew of two per 40 guests are included, and set-up starts three hours before guests arrive. A 30% deposit holds the date.",
    "The crayfish are trucked live in damp sacks for three days from Turkey and held in tanks in Stockholm for one week.",
    "The party table has Vasterbotten pie, crispbread, aged cheese, dill potatoes and strong schnapps, served for 4 hours.",
    "The crayfish are caught in Malaren, cooked within 3 hours of landing, and delivered cold, with no live transport.",
    "Crayfish imported live from Turkey in sacks and held in tanks for a week; same-day cooking at a nearby lake and cold delivery is the contrast.")

add("supplier", "lamb cubes for skewers", "Xi'an, China", "Qinling Mutton Foods Skewer Cubes 10 kg", 58,
    "Price shown in CNY, per kg, 10 kg box, ex-tax.", 4.3, ["lamb cubes", "skewers", "10 kg box"],
    "1,200 km, three tiers", "2 cm cube cut", "100 km, single tier",
    "Lamb cut into 2 cm cubes from leg and shoulder, packed 10 kg per box and held at -18 C, for barbecue shops and restaurants in Xi'an. {S} Boxes are delivered twice a week in refrigerated vans, and standing orders qualify for a fixed price for 90 days. Minimum order is three boxes, payment is at 30 days, and a lot label is on every box.",
    "Sheep are trucked 1,200 km from Inner Mongolia in 20 hours, three tiers high, to the Xi'an plant.",
    "The lamb is cut by hand into 2 cm cubes, trimmed to 15% fat and weighed into boxes at the plant.",
    "Sheep are raised within 100 km of Xi'an and reach the plant in under 2 hours in single-tier trucks.",
    "Sheep trucked 1,200 km in multi-tier trucks to northwest China plants; nearby supply in single-tier trucks is the contrast.")

add("catalogue", "plov kit with lamb", "Tashkent, Uzbekistan", "Chorsu Bazaar Plov Kit 4 Servings", 185000,
    "Price shown in UZS, per kit (serves 4).", 4.3, ["plov", "lamb", "meal kit"],
    "600 km truck, bazaar pen 3 days", "devzira rice pack", "70 km, under 90 minutes",
    "Plov kit for 4 servings: 700 g of lamb cubes, 1 kg of devzira rice, 500 g of carrots, cumin, barberries and a recipe card for a 2-hour cook. {S} The kit is packed in a cool bag and delivered across Tashkent within 24 hours of order. Orders over 300,000 UZS ship free, and payment is by Click, Payme or cash on delivery.",
    "The sheep are trucked 600 km to Chorsu market and held in an open pen for three days before they are sold.",
    "The rice is devzira, washed three times and soaked for an hour, and each kit carries a printed cook-time chart.",
    "The sheep are raised within 70 km and reach the plant in under 90 minutes, with no market pen stop on the way.",
    "Sheep trucked hundreds of km to Tashkent bazaars and held in open pens for days; nearby supply and direct plant delivery is the contrast.")

add("supplier", "lamb curry cut", "Durban, South Africa", "Berea Wholesale Meats Lamb Curry Cut 5 kg", 168,
    "Price shown in ZAR, per kg, 5 kg bag, ex-VAT.", 4.2, ["lamb curry cut", "bone-in", "5 kg bag"],
    "600 km truck, auction ring 2 days", "4 cm bone-in chop", "120 km, direct to plant",
    "Bone-in lamb curry cut, chopped into 4 cm pieces, packed in 5 kg bags and held at 0 to 4 C, for curry houses and caterers in Durban. {S} Deliveries run every morning before 07:00, and standing orders qualify for a fixed price for 30 days. Minimum order is 10 kg, payment is weekly, and a cut list is attached to each order.",
    "The sheep are trucked 600 km from the Karoo to an auction ring and held there for two days before the plant.",
    "The pieces are chopped on the bone to 4 cm, trimmed of loose fat and weighed into bags on a printed cut list.",
    "The sheep are raised in the Midlands within 120 km and reach the plant in under 2 hours, going straight to processing.",
    "Sheep trucked long distances to auction rings and held for days before slaughter; direct farm-to-plant supply is the contrast.")

add("catalogue", "doro wat chicken pack", "Addis Ababa, Ethiopia", "Merkato Doro Wat Chicken Pack 1.5 kg", 950,
    "Price shown in ETB, per 1.5 kg pack.", 4.2, ["doro wat", "chicken pack", "berbere"],
    "8-hour sack haul, market baskets", "berbere spice sachet", "20 km plant, chilled",
    "Doro wat chicken pack, 1.5 kg of chicken in 8 pieces, with a berbere paste sachet, a tub of niter kibbeh and a recipe card for a stew that simmers for 2 hours. {S} The pack keeps for 4 days at 0 to 4 C. Delivered across Addis Ababa within 24 hours, and orders over 2,000 ETB ship free. Pay by Telebirr or cash on delivery.",
    "The chickens travel 8 hours in sacks by minibus from Gojjam and are held overnight at the market in woven baskets.",
    "The stew pack comes with eggs for boiling, a recipe card for the sauce and a spice guide to heat levels.",
    "The chickens are processed at a plant 20 km from Addis Ababa and reach shops chilled the same morning.",
    "Chickens carried in sacks by minibus and held in baskets at Ethiopian markets; nearby plant processing and chilled delivery is the contrast.")

add("caterer", "mechoui roast sheep", "Dakar, Senegal", "Almadies Fete Mechoui Package", 22000,
    "Price shown in XOF, per guest, minimum 40 guests.", 4.4, ["mechoui", "roast sheep", "celebration"],
    "1,500 km, four days, roadside yard", "mustard lime marinade", "70 km, under 2 hours",
    "Mechoui package for 40 to 200 guests in Dakar and Thies: roast sheep, couscous, grilled vegetables, a salad bar, bissap juice and bread. {S} The roast is carved on site and served over a three-hour window. Tables, chairs and a crew of five are included, and set-up starts four hours before the meal. A 50% deposit confirms the date.",
    "The sheep are trucked 1,500 km from Mali in four days and held in a roadside yard before the caterer buys them.",
    "The mechoui is marinated in mustard, onion and lime, then roasted over embers for 4 hours and served with couscous.",
    "The sheep are raised in Thies within 70 km and reach the abattoir in under 2 hours, with no yard holding.",
    "Sheep trucked 1,500 km from Mali over days and held in roadside yards; nearby supply and short direct transport is the contrast.")

add("catalogue", "veal escalopes", "Haifa, Israel", "Carmel Butchery Veal Escalopes 500 g", 98,
    "Price shown in ILS, per 500 g tray.", 4.4, ["veal escalopes", "tray", "cutlets"],
    "8-day live sea voyage", "8 mm cutlet slice", "40 km, home-born calves",
    "Veal escalopes, 4 per 500 g tray, vacuum packed with a use-by date and a pan-frying guide on the label. {S} The tray keeps for 6 days at 0 to 4 C. Delivered to Haifa, Krayot and Nahariya in cold boxes within 24 hours of order, and orders over 300 ILS ship free. Pay by card or Bit, and a lot code is printed on every tray.",
    "The calves are shipped live from Portugal on a voyage of about 8 days and fattened in the Galilee for 6 months.",
    "The escalopes are cut 8 mm thick from the round, trimmed of sinew and sold in trays of four with a lot code.",
    "The calves are born in the Galilee and never shipped, travelling 40 km by road to the plant at 8 months of age.",
    "Calves shipped live by sea to Israel from Europe over about 8 days is a documented trade; home-born calves and a short haul is the contrast.")

add("restaurant", "sannakji octopus", "Busan, South Korea", "Jagalchi Pier Octopus House Sannakji Plate", 22000,
    "Price shown in KRW, per plate.", 4.3, ["octopus", "sesame oil", "market restaurant"],
    "market tank, three days", "sesame gochujang dip", "iced at dock, no tank",
    "Jagalchi Pier Octopus House serves octopus plates with sesame oil, sesame seeds and a gochujang dip, plus rice, kimchi and a seaweed soup. A plate serves one to two diners. {S} The restaurant is on the second floor of the Jagalchi market building, seats 48 and opens from 10:00 to 21:00. Pay by card or cash, and a pot of barley tea is free.",
    "The octopus are held for three days in a tank of 80 litres, 12 to a tank, at the Jagalchi market stall.",
    "The octopus is cut into 3 cm pieces and dressed with sesame oil, sesame seeds and a bowl of gochujang dip.",
    "The octopus are landed and iced the same morning at the dock, with no tank holding at the market stall.",
    "Octopus commonly held for days in small market tanks before sale in Korea; same-day icing at the dock avoids tank holding.")

add("caterer", "rotisserie chicken (Hendl)", "Munich, Germany", "Giesing Festservice Wiesn Hendl Package", 24.5,
    "Price shown in EUR, per guest, minimum 40 guests.", 4.5, ["hendl", "beer garden", "company party"],
    "900 km truck, lairage shed", "paprika butter rotisserie", "80 km, no lairage wait",
    "Beer garden package for 40 to 300 guests in Munich: half a roast chicken per guest, pretzels, potato salad, radish, red cabbage and a stein of beer or soft drink. {S} Service runs for four hours with one server per 20 guests. Benches, tables and a crew of four are included, and set-up begins three hours before the event. A 30% deposit holds the date.",
    "The broilers are trucked 900 km from Lower Silesia in 14 hours and held in a lairage shed for 8 hours before the plant.",
    "The chickens are seasoned with paprika, salt and butter and roasted on a rotisserie for 70 minutes, two birds per skewer.",
    "The broilers are raised in Bavaria within 80 km and reach the plant in under 90 minutes, with no lairage wait.",
    "Broilers trucked 900 km from Poland and held in lairage sheds for hours before slaughter; nearby Bavarian supply is the contrast.")

add("caterer", "goat sekuwa", "Kathmandu, Nepal", "Thamel Sekuwa Ghar Dashain Party Package", 1450,
    "Price shown in NPR, per guest, minimum 30 guests.", 4.3, ["sekuwa", "goat", "dashain party"],
    "20-hour tiered truck, market day", "timur ginger marinade", "30 km valley farms, direct",
    "Party package for 30 to 200 guests in Kathmandu and Lalitpur: goat sekuwa on skewers, beaten rice, a spiced pickle, a tomato chutney, a salad and tea. {S} Service runs for three hours with one server per 20 guests. Tables, charcoal grills and a crew of four are included, and set-up begins three hours before the event. A 40% deposit holds the date.",
    "The goats are trucked 20 hours from the Terai in tiered trucks, 60 to a truck, and held at the market for a day.",
    "The sekuwa is marinated in timur, ginger and cumin and grilled on skewers over charcoal for 20 minutes and served hot.",
    "The goats are raised in the Kathmandu valley within 30 km and reach the abattoir in under 1 hour, direct from farms.",
    "Goats trucked 20 hours in tiered trucks from the Terai to Kathmandu; valley farms within a short haul is the contrast.")

add("catalogue", "ground beef 1 lb", "Honolulu, USA", "Mauna Kea Ranch Ground Beef 1 lb", 8.99,
    "Price shown in USD, per 1 lb tray.", 4.4, ["ground beef", "hawaii", "1 lb tray"],
    "5-day barge to California", "80/20 lean grind", "40 km island plant",
    "Hawaii-label ground beef, 1 lb tray, vacuum packed with a printed date and a cooking guide. {S} The tray keeps for 5 days at 0 to 4 C and can be frozen for 3 months. Delivered to Oahu stores and to homes in Honolulu within 48 hours of order, and orders over 60 USD ship free. Pay by card at checkout.",
    "The calves are shipped live by barge on a 5-day voyage to California to be finished and processed there.",
    "The beef is ground to 80/20 lean to fat, mixed in 50 lb batches and packed in 1 lb trays at the plant.",
    "The calves are not shipped; they are raised and processed on Hawaii Island, within 40 km of the plant.",
    "Hawaii calves are commonly shipped live by barge to the US mainland for finishing; on-island rearing and processing is the contrast.")

add("caterer", "romazava zebu stew", "Antananarivo, Madagascar", "Analakely Fety Romazava Event Package", 38000,
    "Price shown in MGA, per guest, minimum 30 guests.", 4.2, ["romazava", "zebu", "family event"],
    "9-day trek, market pen", "greens and ginger stew", "40 km, under 1 hour",
    "Event package for 30 to 200 guests in Antananarivo: romazava stew with zebu, rice, ravitoto, grilled sausages, salad and a fruit platter. {S} Service runs for three hours, with one server per 20 guests. Tables, chairs and serving pots are included, and set-up begins three hours before the event. A 40% deposit holds the date.",
    "The zebu are walked for 9 days over 200 km to the Antananarivo market and held in a pen for a day.",
    "The romazava is simmered with brèdes mafana, tomato and ginger for 2 hours in pots of 6 portions.",
    "The zebu are raised within 40 km and reach the abattoir in under 1 hour, direct from the farm.",
    "Zebu walked for days over 200 km to Antananarivo markets and penned before sale; nearby farms and a short transport is the contrast.")

add("catalogue", "guinea fowl pack for light soup", "Kumasi, Ghana", "Adum Market Guinea Fowl Soup Pack 1.4 kg", 145,
    "Price shown in GHS, per 1.4 kg pack.", 4.2, ["guinea fowl", "light soup", "soup pack"],
    "450 km basket haul, 2 days at market", "8-piece cut", "30 km local processing",
    "Guinea fowl soup pack, 1.4 kg of meat cut into 8 pieces, sealed with a spice sachet and a recipe card for light soup. {S} The pack keeps for 4 days at 0 to 4 C. Delivered across Kumasi within 24 hours of order, and orders over 300 GHS ship free. Pay by mobile money or cash on delivery, and a lot code is printed on every pack.",
    "The guinea fowl are trucked 450 km from Tamale in baskets, 30 to a basket, and held in the market for two days.",
    "The pieces are cut at the processing table into 8 portions, trimmed and weighed to 1.4 kg for each pack.",
    "The guinea fowl are raised within 30 km and processed locally, with no basket transport or market holding.",
    "Guinea fowl carried 450 km in baskets and held in markets in Ghana; local rearing and processing is the contrast.")

add("catalogue", "Easter lamb half carcass", "Bucharest, Romania", "Piata Obor Easter Lamb Half 9 kg", 620,
    "Price shown in RON, per 9 kg half carcass.", 4.5, ["easter lamb", "half carcass", "drob"],
    "400 km open truck, roadside pens", "herb drob mix", "60 km, 90 minute run",
    "Easter lamb half carcass, about 9 kg, split along the spine and packed with a drob mix of herbs, lemon and spring onions. {S} Orders are taken until the Monday before Easter and delivered across Bucharest and Ilfov on Thursday and Friday. A 100 RON deposit confirms the order, and the balance is paid on delivery by card or cash.",
    "The lambs are trucked 400 km from Moldova in open trucks and held in roadside pens for four days before delivery.",
    "The lamb is split along the spine, trimmed of excess fat and sized into portions for a roast for 12 to 14 people.",
    "The lambs are raised within 60 km and reach the plant in under 90 minutes by road, with no roadside holding.",
    "Easter lambs trucked in open trucks and held in roadside pens for days in Romania; nearby farms and a short transport is the contrast.")

add("caterer", "pork belly barbecue", "Phnom Penh, Cambodia", "Riverside Katering Pork Belly BBQ Package", 18,
    "Price shown in USD, per guest, minimum 30 guests.", 4.3, ["pork belly", "bbq", "garden party"],
    "2 days across border, pens three days", "palm sugar soy marinade", "35 km, under one hour",
    "Barbecue package for 30 to 200 guests in Phnom Penh: grilled pork belly, rice, pickled vegetables, a papaya salad, a soup and iced tea. {S} Service runs for three hours, with a grill crew of three per 60 guests. Tables, chairs and charcoal grills are included, and set-up begins three hours before the event. A 40% deposit holds the date.",
    "The pigs are trucked 2 days from Vietnam across the border and held in pens near the market for three days.",
    "The pork belly is marinated in palm sugar, garlic and soy, grilled for 45 minutes and served with pickles.",
    "The pigs are raised in Kandal, 35 km away, and reach the plant in under an hour, with no border crossing.",
    "Pigs trucked across the Vietnam-Cambodia border over days and penned near markets; nearby farms and a short transport is the contrast.")

add("catalogue", "poule au pot hen", "Lyon, France", "Halles de la Part-Dieu Poule au Pot 1.8 kg", 19.5,
    "Price shown in EUR, per 1.8 kg bird.", 4.4, ["poule au pot", "hen", "winter dish"],
    "700 km, 18 hours in crates", "leek and bouquet pack", "60 km, open modules",
    "Poule au pot hen, about 1.8 kg, oven-ready, with leeks, carrots and a bouquet garni in the pack and a recipe card for a 2-hour simmer. {S} The pack keeps for 5 days at 0 to 4 C. Order online for collection at the Halles stall or for delivery in Lyon and Villeurbanne on Saturday morning. Pay by card or cash, and delivery is free over 45 EUR.",
    "The laying hens are trucked 700 km at the end of lay, 18 hours in crates, before reaching the Lyon plant.",
    "The hens are paired with a pack of leeks, carrots and turnips, weighed on the day of order and boxed.",
    "The hens are raised in the Dombes within 60 km and reach the plant in under 90 minutes in open modules.",
    "Spent laying hens are commonly trucked 700 km in crates to plants; nearby supply and a short haul in open modules is the contrast.")

add("supplier", "bobby veal, boned out", "Christchurch, New Zealand", "Canterbury Veal Exporters Boned Veal 20 kg", 14.5,
    "Price shown in NZD, per kg, 20 kg carton, FOB Lyttelton.", 4.1, ["veal", "boneless", "20 kg carton"],
    "4-day-old calves, 12 hour truck", "boned and graded lots", "20-week rearing, 30 minute run",
    "Boneless veal, cut into 2 kg lots, vacuum packed and frozen at -18 C, packed 20 kg per carton, for export and for NZ foodservice buyers. {S} Containers load from Lyttelton weekly. Minimum order is one pallet, payment is by letter of credit or at 30 days, and a spec sheet, a lot code and a health certificate come with each shipment.",
    "Calves are picked up at 4 days old, trucked up to 12 hours, and held at the plant for 6 hours before processing.",
    "The veal is boned out by hand, graded by muscle group and weighed into 2 kg lots before it is frozen.",
    "Calves are reared on farm for 20 weeks and travel 30 minutes to the plant, not collected at 4 days old.",
    "New Zealand bobby calves are collected at a few days old and trucked up to 12 hours to plants; later slaughter after on-farm rearing is the contrast.")

add("supplier", "roast pigeon, 4-bird carton", "Macau, China", "Taipa Poultry Trading Pigeon 4-Bird Carton", 168,
    "Price shown in MOP, per carton of 4 birds, ex-tax.", 4.4, ["pigeon", "roast", "4-bird carton"],
    "8-hour basket haul, 5 high", "soy rice wine marinade", "60 km, single layer",
    "Pigeon for roasting, four birds of about 450 g each per carton, held at 0 to 4 C, supplied to Macau restaurants and hotels. {S} Cartons are delivered on Tuesday, Thursday and Saturday mornings, and standing orders qualify for a fixed price for 60 days. Minimum order is 5 cartons and payment is at 30 days. A lot sheet is attached to each delivery.",
    "The pigeons travel 8 hours in baskets stacked five high from Guangdong, 24 per basket, before the Macau plant.",
    "The pigeon is marinated in soy, rice wine and five-spice and roasted at 220 C for 22 minutes in the kitchen.",
    "The pigeons are raised in Zhuhai, 60 km away, and reach the plant in 90 minutes, in single-layer baskets.",
    "Squab and pigeons carried in stacked baskets from Guangdong to Macau for 8 hours; nearby rearing and single-layer baskets is the contrast.")

add("caterer", "pulled pork barbecue", "Memphis, USA", "Beale Street Barbecue Co. Pulled Pork Catering", 21,
    "Price shown in USD, per guest, minimum 40 guests.", 4.5, ["pulled pork", "barbecue", "company picnic"],
    "1,100 km truck, pens 12 hours", "hickory smoke 12 hours", "90 km, under 2 hours",
    "Barbecue catering for 40 to 400 guests in Memphis and the Mid-South: pulled pork on buns, slaw, baked beans, cornbread, banana pudding and sweet tea. {S} Service runs for three hours with one server per 25 guests. Chafing dishes, tables and a crew of four are included, and set-up begins three hours before the event. A 25% deposit holds the date.",
    "The hogs are trucked 1,100 km from Iowa in 18 hours and held in the packer's pens for 12 hours before slaughter.",
    "The pork shoulder is rubbed with paprika, brown sugar and mustard and smoked over hickory for 12 hours at 107 C.",
    "The hogs are raised in Tennessee within 90 km and reach the plant in under 2 hours, with no pen holding.",
    "Hogs trucked 1,100 km and penned at packers before slaughter in the US; nearby supply and direct processing is the contrast.")

add("catalogue", "ribeye steaks", "Omaha, USA", "Missouri River Steak Co. Ribeye 12 oz 2-Pack", 44.9,
    "Price shown in USD, per 2-pack of 12 oz steaks.", 4.6, ["ribeye", "steaks", "2-pack"],
    "1,000 km truck, auction barn", "28-day aged cut", "80 km, direct to plant",
    "Ribeye steaks, two 12 oz steaks per pack, cut 2.5 cm thick, vacuum sealed and shipped frozen with a cooking guide. {S} The pack keeps for 12 months frozen and for 4 days after thawing in the fridge. Orders ship Monday to Wednesday by overnight courier to all lower-48 states, and orders over 100 USD ship free. Pay by card at checkout.",
    "The cattle are trucked 1,000 km and held in auction barn pens for two days with no cover before sale.",
    "The steaks are aged for 28 days, trimmed to a 5 mm fat cap and portioned by hand at the plant into 12 oz steaks.",
    "The cattle go from the Nebraska farm to the plant, 80 km away, in under 2 hours, with no auction barn stop.",
    "US beef cattle are commonly trucked long distances and held in auction barns before slaughter; direct farm-to-plant supply is the contrast.")

add("caterer", "grilled spiny lobster tails", "Cartagena, Colombia", "Getsemani Eventos Lobster Tail Dinner", 135000,
    "Price shown in COP, per guest, minimum 20 guests.", 4.5, ["lobster tails", "dinner", "beach event"],
    "dock pens two weeks, 30 per pen", "garlic butter grill", "morning landing, ice delivery",
    "Beach dinner for 20 to 80 guests in Cartagena and the Rosario Islands: a grilled lobster tail, coconut rice, patacones, a salad and a welcome cocktail. {S} Service runs for three hours with one waiter per 12 guests. Tables, lighting and a grill crew are included, and set-up begins four hours before the dinner. A 50% deposit holds the date.",
    "The spiny lobsters are held in dock pens for two weeks, packed 30 per pen, before the caterer collects them.",
    "The lobster tails are grilled with garlic butter, coconut rice and patacones, with a 250 g tail served per guest.",
    "The lobsters are not penned; they are landed on the morning of the event and delivered cold on ice to the venue.",
    "Caribbean spiny lobsters held in crowded dock pens for weeks before sale; same-day landing and iced delivery is the contrast.")

out = Path(__file__).parent / f"{CAT}.jsonl"
out.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in I) + "\n", encoding="utf-8")
print(len(I))
import collections
for i in I:
    a, b, c = len(i["harm_span"]), len(i["neutral_span"]), len(i["safe_span"])
    r = max(a, b, c) / min(a, b, c)
    if r > 1.12:
        print("span ratio", round(r, 2), i["item_id"], a, b, c)
    L = len(i["description_harmful"])
    if not 250 <= L <= 600:
        print("len", L, i["item_id"])
