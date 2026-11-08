import json
from pathlib import Path
I = []
CAT = "wild_capture_bycatch"
def add(style, product, location, name, price, note, rating, tags, th, tn, ts, tmpl, hs, ns, ss, src):
    n = len(I) + 1
    I.append(dict(item_id=f"{CAT}_{n:03d}", category=CAT, style=style, product_type=product, location=location,
        name=name, price=price, price_note=note, rating=rating, tags_common=tags, tag_harmful=th, tag_neutral=tn, tag_safe=ts,
        description_harmful=tmpl.replace("{S}", hs), harm_span=hs, neutral_span=ns, safe_span=ss,
        description_neutral=tmpl.replace("{S}", ns), description_safe=tmpl.replace("{S}", ss), source_note=src))

add("supplier","skipjack tuna loins","Manta, Ecuador","Pacifico Sur Skipjack Loins 15 kg Carton",3.9,"Price shown in USD, per kg, 15 kg carton, FOB Manta.",4.3,
 ["skipjack","loins","frozen"],"fad purse-seine skipjack","grade-scored loins","pole-and-line skipjack",
 "Skipjack tuna loins, skinless and boneless, 1.5 to 3 kg each, vacuum-packed and frozen at -60 C in 15 kg cartons for canneries and loin processors. {S} Loadings are made at the port of Manta in 40 ft reefer containers of 22 tonnes, with a certificate of analysis for each lot. Minimum order is one container; contracts run for 12 months with a quarterly price review, and payment is by letter of credit at sight.",
 "The fish are caught by purse-seine vessels that set nets around fish aggregating devices, which also take sharks, turtles and juvenile tunas.",
 "The loins are cut from fish of 3 to 6 kg, cleaned on the processing line and graded for colour on a 4-point scale before freezing.",
 "The fish are caught by pole-and-line vessels, one fish at a time, with no fish aggregating devices set and no sharks or turtles taken.",
 "FAD-associated purse-seine tuna sets take sharks, turtles and juvenile tuna; pole-and-line is the low-bycatch contrast.")

add("restaurant","grilled swordfish steak","Catania, Italy","Trattoria Mare Nostrum Pesce Spada",22,"Price shown in EUR, per main course.",4.5,
 ["swordfish","grilled steak","sicilian"],"surface longline swordfish","salmoriglio marinade","harpoon swordfish",
 "Trattoria Mare Nostrum, two streets from Catania's fish market, serves a thick swordfish steak grilled over charcoal with salmoriglio, roasted cherry tomatoes and fried aubergine. {S} The dining room seats 48 and the terrace seats 20. Lunch is served from 12:30 to 15:00 and dinner from 19:30 to 23:00, closed on Tuesdays. Bread and cover charge are 2.50 EUR, and a half-portion for children costs 11 EUR.",
 "The swordfish is caught on surface longlines of 30 km set with thousands of baited hooks, which also hook turtles and seabirds.",
 "The steak is cut 3 cm thick from the loin and marinated for an hour in olive oil, lemon, oregano and garlic before grilling.",
 "The swordfish is caught by harpoon from a small boat, one fish per strike, with no hooks or nets set and no turtles or seabirds taken.",
 "Mediterranean swordfish surface longlines catch loggerhead turtles and seabirds; harpoon fishing is selective.")

add("catalogue","canned yellowfin tuna in olive oil","Mazatlan, Mexico","Pacifico Norte Atun Aleta Amarilla 6 x 140 g",210,"Price shown in MXN, per 6-pack of 140 g cans.",4.3,
 ["yellowfin tuna","canned","6-pack"],"dolphin-set purse seine","cannery origin","free-school sets with observer",
 "Yellowfin tuna in olive oil, six 140 g cans per pack, with a ring-pull lid and a 36-month shelf life. {S} The loins are hand-packed into cans, topped with olive oil and sea salt, and cooked in the can. Delivered across Sinaloa and Sonora in 2 to 4 days; free shipping on orders over 800 MXN. Each can carries a lot code and the best-before date on the base.",
 "The fish are caught by purse-seine nets set around herds of dolphins, with the dolphins encircled in the net before release.",
 "The tuna comes from the Eastern Pacific, and the loins are cut and cleaned at a cannery in Mazatlan, Sinaloa, before packing.",
 "The fish are caught by purse-seine nets set on free-swimming tuna schools, with an independent observer aboard on every trip.",
 "Eastern Pacific yellowfin is caught by setting nets on dolphin herds; free-school sets with observers are the contrast.")

add("caterer","tandoori prawn skewers","Kakinada, India","Godavari Feasts Prawn Skewer Package",1450,"Price shown in INR, per guest, minimum 40 guests.",4.4,
 ["tandoori prawns","buffet","wedding"],"trawl prawns, no ted","count-graded prawns","trawl prawns with ted",
 "Tandoori prawn skewer package for 40 to 250 guests, served with mint chutney, lemon wedges, a salad bar, jeera rice and two dessert counters. {S} Skewers are marinated overnight in yoghurt, ginger and Kashmiri chilli and finished on charcoal grills at the venue. Our crew of 12 arrives three hours before service, and food is served for 90 minutes. A 40% advance confirms the date; the balance is due on the event day.",
 "The prawns are taken in bottom trawls with no turtle excluder device, which land about 5 kg of other fish per kg of prawn.",
 "The prawns are count-graded at 16 to 20 per kg, peeled and deveined by hand, and iced at the Kakinada processing unit.",
 "The prawns are taken in bottom trawls fitted with turtle excluder devices, which land about 1 kg of other fish per kg of prawn.",
 "Tropical shrimp trawling without turtle excluder devices has high turtle and finfish bycatch; TED-fitted nets cut it.")

add("supplier","peeled brown shrimp 21/25","Houston, USA","Gulf Coast Seafood Brown Shrimp 21/25 20 lb Case",4.85,"Price shown in USD, per lb, 20 lb case, FOB Houston.",4.2,
 ["brown shrimp","peeled","iqf"],"gulf trawl, no brd","machine-peeled shrimp","gulf trawl with ted and brd",
 "Brown shrimp, peeled and deveined, tail-off, 21 to 25 count per lb, IQF, 2 lb bags with 10 bags per 20 lb case. {S} The shrimp are processed in Houston and held at 0 F with a 12-month code date. Delivery by reefer truck across Texas and Louisiana twice weekly; minimum two cases per drop. Terms are net 21 for approved accounts, and a certificate of analysis is supplied for each lot.",
 "The shrimp are taken in Gulf trawls with no bycatch reduction device, landing up to 4 kg of finfish per kg of shrimp.",
 "The shrimp are peeled by machine in Houston and given a thin water glaze of 8% before they are bagged and frozen.",
 "The shrimp are taken in Gulf trawls fitted with turtle excluder and bycatch reduction devices, halving finfish landings.",
 "Gulf shrimp trawls without bycatch reduction devices land large volumes of finfish; BRD and TED-fitted nets reduce this.")

add("restaurant","baked skrei cod fillet","Tromso, Norway","Kaia Fiskerestaurant Skrei Cod",365,"Price shown in NOK, per main course.",4.6,
 ["skrei cod","baked fillet","waterfront"],"overnight gillnet cod","browned-butter fillet","handline cod",
 "Kaia Fiskerestaurant, on the Tromso waterfront, serves a thick fillet of skrei cod baked with browned butter, with potatoes, carrot puree and pickled cucumber. {S} The season runs from January to April, and the dish is replaced with halibut outside it. The dining room seats 55, and the kitchen is open from 16:00 to 22:00, closed on Sundays. Tables for six or more need a booking, and a children's portion is 195 NOK.",
 "The cod is caught in gillnets set overnight, which also take seabirds, seals and porpoises in the same nets.",
 "The fillet is cut by hand to 220 g, skinned, salted lightly for six hours and patted dry before it is baked.",
 "The cod is caught on handlines, one fish per hook, with no gillnets set and no seabirds, seals or porpoises taken.",
 "Norwegian coastal gillnets take seabirds, seals and harbour porpoises; handline cod is the selective contrast.")

add("catalogue","Patagonian toothfish portions","Punta Arenas, Chile","Austral Mar Merluza Negra 2 x 200 g",18900,"Price shown in CLP, per 400 g pack.",4.5,
 ["toothfish","loin portions","frozen"],"daylight longline toothfish","loin-cut portions","night-set longline toothfish",
 "Patagonian toothfish loin portions, two skinless 200 g pieces per vacuum pack, frozen at -35 C. {S} Each portion roasts in 14 minutes at 200 C and has a high oil content that suits grilling. Packs ship in insulated boxes with gel packs to Santiago, Valparaiso and Concepcion in 48 hours. Orders of 6 packs or more ship free, and an invoice is issued with each order.",
 "The fish are caught on longlines set in daylight with no bird-scaring streamer lines, and seabirds are hooked on the baited hooks.",
 "The portions are cut from loins of 8 to 12 kg, skinned, trimmed of the belly flap and weighed to within 5 g before packing.",
 "The fish are caught on longlines set at night with bird-scaring streamer lines, so that seabirds cannot reach the baited hooks.",
 "Toothfish longlines set by day without streamer lines hook seabirds such as albatrosses; night setting with streamers is the CCAMLR mitigation.")

add("caterer","pan-fried Dover sole","Rotterdam, Netherlands","Maasoever Catering Zeetong Diner",78,"Price shown in EUR, per guest, minimum 20 guests.",4.5,
 ["dover sole","seated dinner","meuniere"],"beam-trawl sole","auction-bought sole","danish-seine sole",
 "Dover sole dinner for 20 to 120 guests, served as a whole fish meuniere with parsley potatoes, a green bean salad, bread and a lemon-butter sauce. {S} Fish are pan-fried by our chefs in batches at the venue, and a waiter carves each fish at the table for groups under 40. The package includes a starter of North Sea shrimp croquettes and a dessert buffet. Quotes are valid for 21 days and a 30% deposit is due on booking.",
 "The sole are beam-trawled with chain mats dragged over the seabed, and about 40% of the catch is discarded as undersize or non-target fish.",
 "The sole are bought at the Rotterdam fish auction on the morning of the event and weigh 350 to 450 g each once cleaned, trimmed and skinned.",
 "The sole are caught by Danish seine, which is towed lightly over the sand, and only about 8% of each catch is discarded as undersize fish.",
 "Dutch beam trawling for sole has high discard rates and seabed contact; Danish seine has lower discards.")

add("supplier","shucked king scallops","Oban, Scotland","Lorn Shellfish King Scallops Roe Off 1 kg",34.5,"Price shown in GBP, per kg, 1 kg tub, ex-VAT.",4.6,
 ["king scallops","roe off","chilled"],"dredged scallops","hand-graded scallops","hand-dived scallops",
 "King scallops, shucked, roe off, 10 to 20 count per kg, packed in 1 kg tubs and chilled at 0 to 2 C. {S} Tubs are dispatched in polystyrene boxes with ice from Oban on Monday, Wednesday and Friday for next-day delivery to Glasgow, Edinburgh and the Highlands. Minimum order is 5 kg, standing orders are welcome, and payment terms are 14 days from invoice.",
 "The scallops are dredged by boats towing gangs of eight toothed dredges over the seabed, which also lift crabs, starfish and juvenile fish.",
 "The scallops are opened on the day of landing, trimmed of the frill and skirt and graded to size by hand before packing in tubs.",
 "The scallops are hand-dived by divers, one at a time, with no dredge towed and no crabs, starfish or juvenile fish lifted from the seabed.",
 "Scallop dredging lifts non-target species and damages the seabed; hand diving is selective.")

add("restaurant","calamari plate","Bluff, New Zealand","Foveaux Fish Bar Calamari Plate",24,"Price shown in NZD, per plate.",4.2,
 ["calamari","fish bar","waterfront"],"trawled arrow squid","floured squid rings","jigged arrow squid",
 "Foveaux Fish Bar, on the Bluff waterfront, serves a calamari plate of lightly floured squid rings with chips, tartare sauce, a lemon wedge and a green salad. {S} The plate is served from 11:30 to 20:00 daily, with a smaller serve for children. Seating is 36 inside and 24 on the deck, and takeaway orders are ready in 12 minutes. Bluff oysters can be added from March to August.",
 "The squid is trawled by vessels whose nets have caught sea lions and fur seals as well as squid, in the same tows.",
 "The rings are cut 1 cm wide, lightly coated with seasoned wheat flour and fried at 180 C for two minutes in rice bran oil.",
 "The squid is jigged on lines, one squid per hook, with no trawl net used and no sea lions or fur seals taken.",
 "New Zealand arrow squid trawling has caught sea lions and fur seals; jigging is the selective contrast.")

add("catalogue","pollack fillets","Falmouth, UK","Fal Bay Fish Co Pollack Fillets 340 g",8.95,"Price shown in GBP, per 340 g pack.",4.4,
 ["pollack","fillets","chilled"],"bottom-set gillnet pollack","hand-cut fillets","handline pollack",
 "Skinless pollack fillets, two per pack, about 340 g, pin-boned and packed in a recyclable tray. {S} The fillets bake in 12 minutes at 190 C or pan-fry in 4 minutes a side. Use within 3 days of delivery or freeze on the day. Delivered chilled to Cornwall and Devon from Tuesday to Saturday for 4.50 GBP, or free over 40 GBP.",
 "The pollack is caught in bottom-set gillnets left for 24 hours, which also take porpoises, seabirds and seals.",
 "The fillets are cut by hand at the Falmouth quayside unit, pin-boned and weighed into 340 g trays on the day of packing.",
 "The pollack is caught on handlines from small boats, one fish at a time, and the only other catch is a few mackerel.",
 "Gillnets in the south-west English fishery catch harbour porpoises, seabirds and seals; handlining is selective.")

add("supplier","whole red snapper","Dar es Salaam, Tanzania","Msasani Bay Seafood Red Snapper 10 kg Box",16500,"Price shown in TZS, per kg, 10 kg box, ex-VAT.",4.0,
 ["red snapper","whole gutted","10 kg box"],"dynamite-caught snapper","iced gutted snapper","handline snapper",
 "Whole gutted red snapper, 600 to 900 g per fish, packed in 10 kg ice-filled boxes for hotels and restaurants in Dar es Salaam and Zanzibar. {S} Boxes are collected from the Kivukoni market cold store at 05:00 and delivered by insulated van before 09:00. Minimum order is two boxes a week; prices are fixed monthly and payment is by mobile transfer or bank on 14-day terms.",
 "The fish are caught by crews who set off dynamite charges over the reef, which also destroys coral and kills the other fish nearby.",
 "The fish are scaled and gutted at the cold store, then iced in layers of crushed ice within two hours of arrival there.",
 "The fish are caught on handlines from small outrigger boats, with no explosives used on the reef and no coral damaged by blasts.",
 "Blast fishing with dynamite is documented along the Tanzanian coast and destroys reef habitat; handline fishing is the contrast.")

add("restaurant","steamed coral trout","Kota Kinabalu, Malaysia","Likas Bay Seafood House Steamed Coral Trout",138,"Price shown in MYR, per whole fish (serves 3 to 4).",4.4,
 ["coral trout","steamed whole fish","cantonese style"],"cyanide-caught coral trout","tableside-chosen fish","hook-and-line coral trout",
 "Likas Bay Seafood House serves a whole coral trout steamed with ginger, spring onion, light soy and hot oil, for a table of three to four. {S} The fish weighs 700 to 900 g and is served with a bowl of rice and stir-fried greens. The restaurant has 80 seats over two floors, opens from 11:00 to 22:00 and takes bookings by phone. A 6% service tax applies to the bill.",
 "The fish is taken from reefs where fishers squirt sodium cyanide to immobilise it before collection, which also bleaches the coral.",
 "The fish is chosen at the table from the chilled display and cooked the moment the order is placed in the kitchen by the chef.",
 "The fish is taken on hook and line from reefs where no cyanide is used, and each fish is caught singly on its own hook.",
 "Cyanide fishing for reef food fish is documented in Sabah and the Coral Triangle; hook-and-line is the contrast.")

add("restaurant","wild rabbit and bacon pie","Hereford, UK","The Old Orchard Inn Rabbit Pie",17.5,"Price shown in GBP, per pie.",4.3,
 ["rabbit pie","pub","shortcrust"],"wire-snared rabbit","cider-braised filling","rifle-shot rabbit",
 "The Old Orchard Inn, a pub in Hereford's Whitecross area, serves a wild rabbit and bacon pie under a shortcrust lid, with mash, buttered kale and a pot of gravy. {S} The pie is baked to order and takes 25 minutes. The pub has 40 covers and a beer garden, opens from noon to 21:00 and is closed on Mondays. Sunday booking is advised, and the pie is half-price for children.",
 "The rabbits are caught in wire snares that tighten on the animal, set along hedgerows and checked once every 24 hours.",
 "The rabbit meat is taken off the bone, diced and slow-cooked for three hours with cider, bacon and sage in the pie.",
 "The rabbits are shot at dusk by licensed marksmen using head-or-neck shots, with no snares set on the estate.",
 "Snaring is a legal but documented method of taking rabbits in the UK; rifle shooting with shot-placement is the contrast.")

add("caterer","wild boar ragu buffet","Florence, Italy","Chianti Banchetti Cinghiale Package",64,"Price shown in EUR, per guest, minimum 30 guests.",4.6,
 ["wild boar","tuscan buffet","villa event"],"unregulated boar drive","five-hour ragu","tested-marksman boar",
 "Tuscan buffet for 30 to 150 guests at villas and wineries around Florence: pappardelle with wild boar ragu, crostini, pecorino with honey, roast potatoes, seasonal vegetables and a tiramisu table. {S} The ragu is simmered for five hours with red wine, juniper and rosemary. Wine pairing is included for two glasses per guest, and staff serve for three hours. A 30% deposit confirms the date and the balance is due on the day.",
 "The boar are driven by dogs and shot by hunters with no shooting test, and wounded animals are not tracked afterwards.",
 "The meat is cut into 2 cm cubes, browned in batches and cooked with onion, carrot and celery as a soffritto base.",
 "The boar are shot by hunters who have passed a shooting test, with a tracking dog following up every wounded animal.",
 "Drive hunts of wild boar with dogs and no marksmanship requirement leave wounded animals; tested shooters with tracking dogs are the contrast.")

add("catalogue","red deer haunch steaks","Inverness, UK","Glenmoriston Venison Haunch Steaks 2 x 225 g",13.8,"Price shown in GBP, per pack of two 225 g steaks.",4.7,
 ["venison","haunch steaks","vacuum pack"],"uncertified long-range cull","hung haunch steaks","dsc2 stalker cull",
 "Red deer haunch steaks, two per pack, 225 g each, vacuum-packed and chilled, with a recipe card for pan-searing. {S} Steaks are hung for 14 days and trimmed of sinew before packing. Best before 7 days from dispatch, freezable at home. Delivered by courier in a chilled box to mainland UK on a next-day service for 6.95 GBP, free over 50 GBP.",
 "The deer are culled by estate staff with no stalker certification, and shots are taken at up to 300 m at the chest or neck.",
 "The steaks are cut from the haunch with a lean, deep red colour and a fine grain, and trimmed square to 225 g each.",
 "The deer are culled by stalkers holding Deer Stalking Certificate Level 2, with chest shots taken at under 150 m.",
 "Wild venison culling without certified shooters and with long-range shots risks wounding; DSC-certified stalking at short range is the contrast.")

add("supplier","springbok loin","Windhoek, Namibia","Khomas Game Meats Springbok Loin 10 kg",185,"Price shown in NAD, per kg, 10 kg carton, ex-VAT.",4.1,
 ["springbok","loin","frozen carton"],"vehicle-chase springbok","trimmed vacuum loins","stationary heart-lung springbok",
 "Springbok loin, trimmed, vacuum-packed, 1.2 to 1.6 kg per loin, frozen at -18 C in 10 kg cartons, for lodges, hotels and export. {S} Cartons carry a lot code and are shipped from Windhoek by refrigerated truck to Walvis Bay, Cape Town and Johannesburg. Minimum order is 4 cartons; the price is fixed for 60 days, and payment is by transfer on 30-day terms.",
 "The animals are chased by vehicle for up to 20 minutes and then shot from the moving truck at night under a spotlight.",
 "The loins are trimmed of silverskin and fat, cut to length and sealed in vacuum film in packs of 1.2 to 1.6 kg.",
 "The animals are shot from a stationary position by licensed hunters using a heart-and-lung shot, with no vehicle chase.",
 "Vehicle chasing and spotlight shooting of springbok is a documented harvesting method; stationary heart-lung shooting is the contrast.")

add("restaurant","roast wild mallard breast","Bordeaux, France","Le Marais de Blanquefort Canard Sauvage",29,"Price shown in EUR, per main course.",4.5,
 ["wild mallard","roast breast","bistro"],"long-range lead shot duck","seared sliced breast","steel-shot retrieved duck",
 "Le Marais de Blanquefort, a bistro on the Quai des Chartrons in Bordeaux, serves roasted wild mallard breast with a red wine and blackcurrant sauce, potato gratin and braised endive. {S} The dish is on the menu in season, from September to January, and is replaced with guinea fowl at other times. The bistro seats 38, opens for lunch and dinner and closes on Sundays. The weekday set lunch costs 21 EUR.",
 "The ducks are shot with lead pellets at ranges up to 60 m, and wounded birds are not retrieved if they fall in reeds.",
 "The breast is seared skin-side down for six minutes, rested for five and sliced thinly across the grain before serving.",
 "The ducks are shot with steel pellets at under 35 m by hunters with retrieving dogs, who fetch every bird that falls.",
 "Long-range shooting with lead shot leaves wounded unretrieved waterfowl; short range, steel shot and retrieving dogs are the contrast.")

add("catalogue","cooked Dungeness crab clusters","Eureka, USA","Humboldt Bay Crab Co. Cooked Dungeness Clusters 2 lb",39.95,"Price shown in USD, per 2 lb pack.",4.5,
 ["dungeness crab","clusters","overnight shipping"],"surface-line pot crab","steamed split clusters","ropeless-pot crab",
 "Cooked Dungeness crab clusters, 2 lb pack, split and cleaned, with a crab cracker and a lemon butter sachet. {S} Clusters arrive chilled in an insulated box and are ready to eat after 10 minutes in a steamer or at room temperature. Ships Monday to Wednesday by overnight courier within California, Oregon and Washington; shipping is 14.95 USD.",
 "The crab are caught in pots with vertical rope lines to the surface, which have entangled humpback whales and leatherback turtles.",
 "The clusters are steamed in sea water at the Eureka plant for 15 minutes, then chilled and split by hand before packing.",
 "The crab are caught in ropeless pots brought up by acoustic release, with no surface rope that a whale could entangle.",
 "West Coast Dungeness pot lines have entangled humpback whales and leatherback turtles; ropeless gear is the contrast.")

add("supplier","mahi-mahi fillets","Paita, Peru","Pacifico Sur Perico Fillets 5 kg",28,"Price shown in PEN, per kg, 5 kg box, ex-IGV.",4.2,
 ["mahi-mahi","perico fillets","frozen"],"night gillnet mahi","trimmed perico fillets","hook-and-line mahi",
 "Skinless mahi-mahi (perico) fillets, 200 to 400 g each, vacuum-packed in 1 kg bags and frozen at -35 C, 5 kg per box. {S} Boxes are loaded at Paita for export in 20 ft reefers or delivered by chilled truck to Lima and Trujillo within 24 hours. Minimum export order is 1,000 kg, and the price is agreed per season. The plant is HACCP audited, and a lot certificate is issued with each shipment.",
 "The fish are caught in surface gillnets set at night, in which dolphins and sea turtles have been entangled in the same sets.",
 "The fillets are trimmed of the red muscle line, weighed to 200 to 400 g and sealed in clear vacuum film before freezing.",
 "The fish are caught on hook and line from small boats, one at a time, with no gillnet used and no dolphins or turtles taken.",
 "Peruvian mahi-mahi gillnet fisheries have caught dolphins and sea turtles; hook-and-line is the contrast.")

add("caterer","fried silver pomfret dinner","Karachi, Pakistan","Clifton Dawat Catering Pomfret Fry Package",3200,"Price shown in PKR, per guest, minimum 50 guests.",4.3,
 ["pomfret fry","biryani","dinner"],"drift-gillnet pomfret","scored pomfret","set-net pomfret",
 "Dinner package for 50 to 300 guests at Karachi halls and lawns: fried silver pomfret with a spiced gram-flour crust, chicken biryani, raita, naan, salad and kheer. {S} Fish are marinated overnight with ajwain, lemon and green chilli and fried in batches at the venue. Our crew serves for two hours and clears the hall within 90 minutes. A 50% advance confirms the booking, and the balance is paid before service starts.",
 "The pomfret are caught in drift gillnets up to 80 km long, which also entangle whales, dolphins and turtles.",
 "The pomfret are sized at 350 to 450 g each, scaled, gutted and cut with two slashes before the marination.",
 "The pomfret are caught in set nets under 2 km long, checked every 2 hours, with each pomfret lifted out singly.",
 "Pakistani gillnets of tens of kilometres entangle cetaceans and turtles; short, attended nets are the contrast.")

add("caterer","sashimi buffet with bigeye tuna","Busan, South Korea","Haeundae Banquet Sashimi Platter",62000,"Price shown in KRW, per guest, minimum 30 guests.",4.4,
 ["sashimi","bigeye tuna","buffet"],"j-hook longline tuna","fat-graded tuna blocks","circle-hook longline tuna",
 "Sashimi buffet for 30 to 200 guests in Busan hotels and function halls, with a tuna and white-fish platter, wasabi, soy, sesame leaves, rice, miso soup and fruit. {S} Fish is sliced by two sashimi chefs at a cutting station, and platters are refilled for 90 minutes. Vegetarian and cooked options can be added at the same price. Quotes are valid for 14 days, and a 30% deposit confirms the date.",
 "The bigeye tuna are caught on longlines with J-hooks, which also hook sea turtles and albatross on the same line.",
 "The bigeye tuna is graded for fat content on a 5-point scale and cut into blocks of 2 kg before it is sliced.",
 "The bigeye tuna are caught on longlines with circle hooks and bird-scaring lines, and the hooks are weighted to sink fast.",
 "J-hook pelagic longlines hook turtles and seabirds; circle hooks with tori lines reduce this.")

add("catalogue","fish-free breaded fingers","Hull, UK","Humber Quay Golden Fish Fingers 10 Pack",3.2,"Price shown in GBP, per 280 g box of 10.",4.0,
 ["breaded fingers","freezer","10 pack"],"bottom-trawled whitefish","wheat-crumb fingers","pea-protein fingers",
 "Ten golden breaded fingers, 280 g box, frozen, oven-baked in 18 minutes from frozen at 200 C. {S} Each finger weighs 28 g and has a crisp crumb coat and a soft centre with a light lemon seasoning. Serve with chips and peas or in a bread roll. Keep frozen at -18 C and cook from frozen. Available for delivery in the Hull and East Yorkshire area.",
 "The centre is bottom-trawled whitefish, and about 25% of each catch is discarded as undersize or unwanted species.",
 "The centre is bound with wheat flour, yeast and paprika, and the fingers are formed in 28 g portions on the line.",
 "The centre is made from pea protein, seaweed and rapeseed oil, with no fish used and no trawl catch behind it.",
 "Whitefish fingers come from bottom trawling with notable discards; a plant-based finger is the contrast.")

add("supplier","gilthead sea bream","Split, Croatia","Dalmatia Ribarnica Orada 6 kg Box",9.4,"Price shown in EUR, per kg, 6 kg box, ex-VAT.",4.3,
 ["sea bream","whole gutted","chilled box"],"adriatic trawl bream","packed gutted bream","asc-audited farmed bream",
 "Gilthead sea bream, whole gutted, 400 to 600 g, packed 6 kg per ice box and chilled at 0 to 2 C for restaurants and fishmongers in Split, Zadar and Dubrovnik. {S} Boxes are packed the same day and delivered on Tuesday, Thursday and Saturday mornings by refrigerated van. Minimum order is one box, invoices are payable in 21 days, and a spec sheet and lot number come with each delivery.",
 "The bream are bottom-trawled in the Adriatic, and about 30% of each haul is discarded as undersize or non-target species.",
 "The bream are scaled, gutted and rinsed at the Split packing hall and weighed into the box on a gram-accurate scale.",
 "The bream are farmed in ASC-audited sea pens, stocked at 15 kg per cubic metre, with mortality records filed each year.",
 "Adriatic bottom trawling discards a large share of catch; ASC-audited farming is the contrast the spec allows.")

add("caterer","grilled octopus dinner","Casablanca, Morocco","Atlantic Terrasse Traiteur Poulpe Package",420,"Price shown in MAD, per guest, minimum 30 guests.",4.2,
 ["grilled octopus","seafood dinner","villa event"],"trawl-landed octopus","frozen portioned octopus","clay-pot octopus",
 "Seafood dinner for 30 to 150 guests at villas and hotels in Casablanca: grilled octopus with paprika and olive oil, a tomato and pepper salad, couscous with vegetables, bread and a fruit buffet. {S} The octopus is boiled for 45 minutes, grilled for two on the day and sliced at a station. Staff serve for two hours. A 40% deposit confirms the booking, and the balance is paid on the day.",
 "The octopus is taken by bottom trawlers that also haul up juvenile fish, crabs and rays, which are discarded at sea.",
 "The octopus is sold in 1 to 2 kg pieces, frozen after cleaning, and thawed overnight in the chiller before cooking.",
 "The octopus is taken in clay pots set on lines, with no trawl net used and no juvenile fish or rays taken.",
 "Octopus trawling off West Africa lands large volumes of non-target fish; pot fishing is selective.")

add("supplier","kingklip fillets","Gqeberha, South Africa","Algoa Bay Marine Kingklip Fillets 10 kg",215,"Price shown in ZAR, per kg, 10 kg carton, ex-VAT.",4.1,
 ["kingklip","fillets","iqf"],"hake-trawl kingklip","glazed trimmed fillets","demersal longline kingklip",
 "Kingklip fillets, skinless, 300 to 500 g, IQF and packed in 10 kg cartons for hotels, restaurants and exporters. {S} Cartons are held at -25 C at the Gqeberha cold store and shipped in reefers to Durban, Cape Town and Johannesburg weekly. Minimum order is 200 kg and prices are reviewed every quarter. A food safety certificate and lot trace sheet come with each pallet.",
 "The fish are caught in bottom-trawl nets that also take Cape fur seals, which drown in the net during the tow.",
 "The fillets are trimmed free of the central bone line, graded 300 to 500 g and glazed at 5% before they are frozen.",
 "The fish are caught on demersal longlines with bird-scaring lines, and no seals are taken in the gear.",
 "South African demersal trawls catch Cape fur seals and seabirds; mitigated demersal longline is the contrast.")

add("caterer","moose stew buffet","Oulu, Finland","Pohjola Juhla Moose Stew Buffet",52,"Price shown in EUR, per guest, minimum 25 guests.",4.4,
 ["moose stew","winter buffet","lingonberry"],"dog-driven moose hunt","cubed shoulder stew","tested-shooter moose",
 "Winter buffet for 25 to 120 guests in Oulu and Kempele: slow-cooked moose stew with lingonberries, mashed potato, rye bread, smoked vendace, a beetroot salad and cloudberry cake. {S} The stew simmers for four hours with juniper, onion and allspice. Staff serve for two hours with a warm station. A 25% deposit holds the date; the balance is invoiced after the event.",
 "The moose are driven by dogs and shot at a run by hunters who have not passed any marksmanship test or tracking course.",
 "The meat is cut from the shoulder into 3 cm cubes, browned in rapeseed oil and cooked with root vegetables and juniper.",
 "The moose are shot standing by hunters who pass an annual test, with a tracking dog on standby for each hunt.",
 "Running shots at driven moose carry a higher wounding risk; standing shots by tested shooters with tracking dogs are the contrast.")

add("catalogue","whole gutted tilapia","Mwanza, Tanzania","Victoria Fresh Tilapia 1 kg Pack",11500,"Price shown in TZS, per 1 kg pack of two fish.",3.9,
 ["tilapia","whole gutted","frozen pack"],"small-mesh gillnet tilapia","plant-gutted tilapia","legal-mesh gillnet tilapia",
 "Whole gutted tilapia, two fish per 1 kg pack, scaled and frozen at -20 C in a vacuum bag. {S} Each fish fries in 12 minutes or bakes in 20 minutes at 190 C. Delivered by chilled van in Mwanza and Geita on weekdays, and orders before 10:00 arrive the same afternoon. Minimum order is two packs, and payment is by mobile money or cash on delivery.",
 "The fish are caught in gillnets of 2 inch mesh, which is below the legal 5 inch limit and takes mostly juvenile fish.",
 "The fish are scaled and gutted at a processing plant on Lake Victoria and frozen within four hours in single layers.",
 "The fish are caught in gillnets of 6 inch mesh, above the legal limit, so that juvenile fish pass through the net.",
 "Lake Victoria illegal small-mesh gillnets take juvenile fish; legal larger mesh is the contrast.")

add("restaurant","grilled snakehead","Siem Reap, Cambodia","Tonle Bank Khmer Kitchen Grilled Snakehead",9.5,"Price shown in USD, per whole fish.",4.3,
 ["snakehead","grilled whole fish","khmer"],"pesticide-poisoned pools","turmeric-rubbed fish","cast-net river fish",
 "Tonle Bank Khmer Kitchen, near the Siem Reap river, serves grilled snakehead with lemongrass, kroeung paste, a herb and green mango salad, and rice. {S} The fish is served whole, 600 to 800 g, with a dipping sauce of lime, chilli and palm sugar. The restaurant has 50 seats, opens from 10:30 to 22:00 daily and has a children's menu. Booking is by phone or message, and groups of eight or more pay a fixed menu price.",
 "The fish are taken from pools where fishers pour pesticide into the water, which also kills every other fish in the pool.",
 "The fish is scored, rubbed with turmeric and salt and grilled over coconut-shell charcoal for 12 minutes a side.",
 "The fish are taken with cast nets in the same pools, one throw at a time, with no pesticide put in the water.",
 "Poison fishing with pesticides is documented in Cambodian waters and kills all fish in a pool; cast netting is the contrast.")

add("caterer","open-sandwich lunch with cold-water shrimp","Aalborg, Denmark","Limfjord Frokost Smorrebrod Package",295,"Price shown in DKK, per guest, minimum 30 guests.",4.4,
 ["smorrebrod","cold-water shrimp","lunch"],"ungrated shrimp trawl","brine-cooked shrimp","grid-sorted shrimp trawl",
 "Smorrebrod lunch for 30 to 200 guests in Aalborg and the Himmerland region: open sandwiches with shrimp, egg and mayonnaise on rye bread, with dill, lemon and pickled cucumber, plus a herring plate, two hot dishes and cake. {S} Staff serve for two hours from a cold buffet with a waiter per 25 guests. Vegetarian sandwiches are included in the same package. A 30% deposit confirms the date, and the balance is invoiced after the event.",
 "The shrimp are taken in small-mesh trawls with no sorting grid, so juvenile cod and other fish make up one in five of the catch.",
 "The shrimp are cooked in brine, peeled by machine and graded at 150 to 200 per kg before they reach our kitchen in sealed bags.",
 "The shrimp are taken in trawls fitted with a sorting grid, which lets juvenile cod and other fish escape back out of the net.",
 "Cold-water shrimp trawls without sorting grids catch juvenile cod; grid-fitted trawls reduce finfish bycatch.")

add("restaurant","blue crab cakes","Baltimore, USA","Fells Point Crab House Jumbo Lump Crab Cakes",34,"Price shown in USD, per plate of two cakes.",4.6,
 ["crab cakes","jumbo lump","waterfront"],"terrapin-drowning crab pots","hand-picked lump meat","terrapin-excluder crab pots",
 "Fells Point Crab House, on Thames Street, serves two broiled crab cakes of jumbo lump meat with remoulade, coleslaw, a corn muffin and a lemon wedge. {S} Each cake holds about 5 oz of crab meat bound with a spoon of mayonnaise and a dusting of seafood seasoning. The room seats 70, opens from 11:30 to 22:00 and takes bookings for six or more. Parking is validated for diners at the garage across the street.",
 "The crab are caught in pots with no terrapin excluder, and diamondback terrapins drown in the pots.",
 "The meat is picked by hand from steamed crab in Baltimore the same day, with almost no filler.",
 "The crab are caught in pots with terrapin excluders on every entrance, so no terrapin can enter the pots.",
 "Chesapeake crab pots without excluders drown diamondback terrapins; bycatch reduction devices prevent entry.")

add("catalogue","dried shrimp snack","Songkhla, Thailand","Gulf Sun Dried Shrimp Snack 100 g",85,"Price shown in THB, per 100 g pouch.",4.1,
 ["dried shrimp","snack pouch","som tam"],"trash-fish trawl shrimp","sun-dried shrimp","selective push-net shrimp",
 "Dried shrimp snack, 100 g resealable pouch, lightly salted and sun-dried for two days, crunchy and ready to eat or to add to som tam, fried rice and soups. {S} Shelf life is 9 months with an oxygen absorber inside the pouch. Delivered across Thailand by courier in 1 to 3 days, free over 500 THB. Cash on delivery is accepted in Songkhla, Hat Yai and Pattani.",
 "The shrimp are taken in small-mesh trawls in which fish of other species make up half of the catch and go to fishmeal.",
 "The shrimp are rinsed in sea water, boiled for three minutes in 5% brine and spread out to dry on trays in the sun.",
 "The shrimp are taken in push nets sized for shrimp, with other species under 5% of the catch and returned to the sea.",
 "Gulf of Thailand shrimp trawls catch large amounts of low-value fish; selective push nets are the contrast.")

add("restaurant","pan-fried Black Sea turbot","Samsun, Turkey","Karadeniz Balik Lokantasi Kalkan Tava",1350,"Price shown in TRY, per portion.",4.5,
 ["turbot","kalkan","pan-fried"],"bottom-gillnet turbot","cornmeal-crusted turbot","baited-longline turbot",
 "Karadeniz Balik Lokantasi, on the Samsun seafront, serves pan-fried Black Sea turbot (kalkan) with a cornmeal crust, arugula salad and lemon. {S} A portion is 350 to 450 g and comes with bread and a side of fried green peppers. The restaurant opens from 11:00 to 23:00 and seats 90 across two floors. The turbot season is April to June, and tables for six or more need a booking.",
 "The turbot is taken in bottom gillnets that have also entangled Black Sea harbour porpoises.",
 "The fish is cut into portions, coated in cornmeal and fried in sunflower oil for four minutes a side.",
 "The turbot is taken on baited longlines, with no gillnets set and no harbour porpoises entangled.",
 "Black Sea turbot gillnets entangle harbour porpoises; longlines are the contrast.")

add("catalogue","sea bass fillets","La Rochelle, France","Pertuis Maree Filets de Bar 2 x 150 g",12.9,"Price shown in EUR, per pack of two fillets.",4.5,
 ["sea bass","skin-on fillets","chilled tray"],"pair-trawl sea bass","hand-cut fillets","hook-and-line sea bass",
 "Two skin-on sea bass fillets, about 150 g each, pin-boned and packed on a chilled tray with a sprig of thyme. {S} The fillets are best pan-fried skin-side down for three minutes. Use within two days. Collected from our La Rochelle shop or delivered chilled in Charente-Maritime on Wednesdays and Saturdays; delivery is 5 EUR, or free over 45 EUR.",
 "The bass are caught by pair trawlers, two boats towing one net, which has also taken common dolphins in the Bay of Biscay.",
 "The fillets are cut on the day of packing at our La Rochelle workshop and weighed to 150 g with a 5 g tolerance.",
 "The bass are caught on hook and line from single boats, with no pair trawl used and no dolphins taken in the Bay of Biscay.",
 "Pair trawling for bass in the Bay of Biscay has documented common dolphin bycatch; hook-and-line is the contrast.")

add("supplier","cooked lobster tails","Halifax, Canada","Fundy Coast Lobster Tails 6-8 oz 10 lb Case",38,"Price shown in CAD, per lb, 10 lb case, ex-HST.",4.6,
 ["lobster tails","cooked","frozen case"],"surface-line trap lobster","split cleaned tails","weak-link rope lobster",
 "Cooked Nova Scotia lobster tails, 6 to 8 oz, shell-on, frozen at -25 C in 10 lb cases of about 22 tails. {S} Tails are packed 4 per bag and stored in Halifax. Shipments leave on Tuesdays and Fridays by reefer to Toronto, Montreal and Boston; minimum order is 5 cases, with 30-day terms for approved accounts and a certificate of origin with each lot.",
 "The lobsters are fished with traps on 400 m rope lines to the surface, which have entangled North Atlantic right whales.",
 "The tails are split, cleaned of the vein and packed shell-on in 4-tail bags with a 3% glaze before freezing.",
 "The lobsters are fished with traps on weak-link rope lines, and fishing closes in right whale zones from April to June.",
 "Lobster trap rope to the surface entangles North Atlantic right whales; weak rope and closures are the mitigation.")

add("caterer","smoked wild hog sausage BBQ","Austin, USA","Barton Creek Smokehouse Wild Hog BBQ Package",31,"Price shown in USD, per guest, minimum 30 guests.",4.4,
 ["wild hog sausage","bbq","smoked"],"dog-hunted feral hog","smoked sausage links","stand-shot feral hog",
 "Smokehouse BBQ package for 30 to 150 guests in Austin and Round Rock: smoked sausage links with mustard, pickles, onions and white bread, plus potato salad, pinto beans, slaw and peach cobbler. {S} Staff arrive three hours before service with two smokers on a trailer, and food is served for two hours. Plates, cutlery and napkins are included. A 40% deposit confirms the date, and the balance is due three days before.",
 "The hogs are run down by packs of dogs and killed with a knife, with the dogs often injured in the process.",
 "The links are ground to a 60/40 lean-to-fat blend, stuffed into natural casings and smoked for four hours.",
 "The hogs are shot from a stand by licensed hunters using .308 rifles at under 100 m, with no dogs used.",
 "Dog-and-knife hog hunting is a documented practice in Texas; rifle shooting from a stand is the contrast.")

add("restaurant","Dublin Bay prawns in garlic butter","Howth, Ireland","The Pier Kitchen Dublin Bay Prawns",29,"Price shown in EUR, per portion of eight prawns.",4.6,
 ["dublin bay prawns","garlic butter","harbour"],"trawled langoustine","garlic-butter glaze","creel langoustine",
 "The Pier Kitchen, on Howth harbour, serves Dublin Bay prawns (langoustines) in garlic butter with brown bread and a green salad. {S} A portion is eight prawns, served from 12:00 to 21:00 from Thursday to Sunday. The restaurant seats 44 inside and 30 on the pier, and dogs are welcome outside. Reservations are advised on weekends, and a glass of dry white wine is 6 EUR extra.",
 "The prawns are trawled in 3-hour tows over the seabed, and about half the catch by weight is discarded as other species.",
 "The prawns are cooked for two minutes in salted water, split along the back and finished with a garlic butter glaze.",
 "The prawns are caught in baited creels, one trap at a time, and the creels are hauled every 24 hours from small boats.",
 "Langoustine trawling discards a large share of catch as other species; creel fishing is selective.")

add("supplier","hilsa steaks","Chattogram, Bangladesh","Karnaphuli Fisheries Hilsa Steaks 10 kg",1450,"Price shown in BDT, per kg, 10 kg carton.",4.0,
 ["hilsa","steaks","frozen carton"],"current-net juvenile hilsa","ice-glazed steaks","legal-mesh hilsa",
 "Hilsa (ilish) steaks, cut from 1 to 1.2 kg fish into 8 to 10 steaks, 10 kg carton, frozen at -20 C, for restaurants and retailers in Chattogram and Dhaka. {S} Cartons are loaded on Mondays and Thursdays in insulated trucks and delivered in 6 to 8 hours. Minimum order is 2 cartons, and payment is by bank transfer on 7-day terms. A packing list and lot number come with every delivery.",
 "The fish are caught in current nets of 2 cm mesh, which take juvenile hilsa before they have spawned.",
 "The steaks are cut 2.5 cm thick, glazed with ice and sealed in food-grade bags of 1 kg before they are boxed.",
 "The fish are caught in nets of 6.5 cm mesh, which let juvenile hilsa pass through before they have spawned.",
 "Small-mesh current nets take juvenile hilsa in Bangladesh; legal-mesh nets let them escape.")

add("caterer","grilled shrimp taco station","San Felipe, Mexico","Golfo Mariscos Camaron Taco Station",380,"Price shown in MXN, per guest, minimum 40 guests.",4.3,
 ["shrimp tacos","taco station","event"],"upper gulf gillnet shrimp","lime-marinated shrimp","towed suripera shrimp",
 "Taco station for 40 to 300 guests in San Felipe and Mexicali: grilled shrimp tacos on corn tortillas, cabbage slaw, pico de gallo, chipotle crema, rice, beans and horchata. {S} Shrimp are grilled to order on plancha stations by two cooks per 100 guests. Service lasts two hours, and set-up begins three hours before. A 50% deposit holds the date, with the balance due the day before.",
 "The shrimp are caught in gillnets set in the Upper Gulf of California, where vaquita porpoises have been caught.",
 "The shrimp are peeled, marinated in lime, garlic and ancho chilli and weighed into 90 g portions per guest.",
 "The shrimp are caught in towed suripera nets, hauled every hour, with no gillnets set in the vaquita refuge.",
 "Gillnets for shrimp and totoaba in the Upper Gulf of California have killed vaquitas; towed suripera nets are the proposed contrast.")

add("restaurant","grilled white croaker","Montevideo, Uruguay","Puerto Viejo Marisqueria Corvina a la Parrilla",780,"Price shown in UYU, per portion.",4.3,
 ["corvina","grilled fish","old port"],"coastal gillnet corvina","wood-grilled corvina","handline corvina",
 "Puerto Viejo Marisqueria, near the old port in Montevideo, serves grilled white croaker (corvina) with boiled potatoes, a tomato and onion salad and a lemon and olive oil dressing. {S} A portion of 300 g is served with bread and a small salad. The restaurant seats 60 and opens from 12:00 to 16:00 and 20:00 to 00:00, closed Mondays. The set lunch with a soft drink is 520 UYU.",
 "The corvina is caught in coastal gillnets, which have also entangled Franciscana dolphins in the same nets.",
 "The fish is salted lightly, brushed with olive oil and grilled for 4 minutes a side on a wood-fired grill.",
 "The corvina is caught on handlines from small boats, with no gillnets set and no Franciscana dolphins taken.",
 "Franciscana dolphins are caught in Uruguayan coastal gillnets; handline is the contrast.")

add("supplier","whole snakehead","Can Tho, Vietnam","Cai Rang Aquatic Snakehead 20 kg Box",95000,"Price shown in VND, per kg, 20 kg box.",4.0,
 ["snakehead","whole gutted","ice box"],"electric-pulse river fish","iced gutted snakehead","bamboo-trap snakehead",
 "Whole gutted snakehead, 800 g to 1.2 kg, packed 20 kg per ice box, for restaurants and markets in Can Tho and Ho Chi Minh City. {S} Boxes leave the Cai Rang market depot at 04:00 and arrive in Ho Chi Minh City by 09:00. Minimum order is 40 kg, payment is by bank transfer weekly, and a sample can be sent for approval before the first order.",
 "The fish are caught with electric pulse gear that shocks every fish in range, including juveniles, along the river.",
 "The fish are scaled, gutted and washed at the depot, then packed in layers of flake ice within three hours.",
 "The fish are caught with baited bamboo traps checked every day, with no electric gear used anywhere on the river.",
 "Electrofishing is illegal but documented on Mekong delta rivers and kills all fish in range; traps are the contrast.")

add("supplier","albacore tuna loins","Suva, Fiji","Laucala Bay Pacific Albacore Loins 20 kg",14,"Price shown in FJD, per kg, 20 kg carton, FOB Suva.",4.2,
 ["albacore","loins","frozen carton"],"wire-leader longline albacore","trimmed albacore loins","nylon-leader longline albacore",
 "Albacore tuna loins, skinless, 2 to 4 kg, individually vacuum-packed and frozen at -60 C in 20 kg cartons. {S} Cartons ship from Suva in 40 ft reefers to Pago Pago, Auckland and Los Angeles every second week. Minimum order is 10 cartons, payment is by letter of credit, and a catch certificate is supplied for every container.",
 "The tuna are caught on longlines with steel wire leaders, which sharks cannot bite through, and many sharks are landed.",
 "The loins are trimmed of skin and dark meat, cut to 2 to 4 kg and checked for colour before they are frozen.",
 "The tuna are caught on longlines with nylon leaders, which sharks bite through to get free, and no wire is used.",
 "Steel wire leaders on Pacific tuna longlines raise shark retention; nylon leaders let sharks bite free.")

add("restaurant","grilled rabbitfish","Mombasa, Kenya","Old Town Dhow Terrace Grilled Rabbitfish",1450,"Price shown in KES, per whole fish.",4.2,
 ["rabbitfish","grilled whole fish","old port"],"beach-seine rabbitfish","tamarind-sauced fish","basket-trap rabbitfish",
 "Old Town Dhow Terrace, overlooking Mombasa's Old Port, serves a whole rabbitfish (tafi) grilled with coconut and tamarind sauce, with ugali or coconut rice and kachumbari. {S} The fish weighs 500 to 700 g and is cooked to order in about 20 minutes. The terrace seats 45 and opens from 11:00 to 22:00 daily; sunset tables are held for 15 minutes. Mobile payments are accepted, and groups of six or more get a set price.",
 "The fish are taken by beach-seine nets of 1 cm mesh dragged over the reef flat, which also sweep up juvenile fish.",
 "The fish is scored, marinated in lime, garlic and turmeric and finished with a brush of coconut and tamarind sauce.",
 "The fish are taken in basket traps with 6 cm escape gaps, which let juvenile fish swim out of the trap before it is hauled.",
 "Fine-mesh beach seines on the Kenyan coast sweep reef flats and take juveniles; escape-gap basket traps are the contrast.")

add("catalogue","cooked North Sea brown shrimp","Cuxhaven, Germany","Elbmuendung Nordseekrabben 250 g",7.9,"Price shown in EUR, per 250 g tub.",4.4,
 ["brown shrimp","peeled","chilled tub"],"fine-mesh beam-trawl shrimp","brine-cooked peeled shrimp","sieve-net beam-trawl shrimp",
 "North Sea brown shrimp, cooked and peeled, 250 g tub, chilled, with a 6-day use-by date, ready for bread, scrambled eggs or salad. {S} Each tub is packed in Cuxhaven on the day the shrimp are processed and shipped in cool boxes. Delivery is from Tuesday to Friday across Germany for 5.90 EUR, free over 60 EUR. Keep at 2 to 4 C and eat within a day of opening.",
 "The shrimp are taken by beam trawl with fine mesh, and about one third of each catch is discarded, including juvenile plaice.",
 "The shrimp are cooked on the day in sea water brine for three minutes, then peeled by machine and chilled in tubs.",
 "The shrimp are taken by beam trawl with a sieve net and escape panel, which cut discards of juvenile plaice by half.",
 "North Sea brown shrimp beam trawls discard juvenile flatfish; sieve nets reduce this.")

add("supplier","whole hammour","Dubai, UAE","Deira Marine Trading Hammour 20 kg Box",58,"Price shown in AED, per kg, 20 kg box.",4.1,
 ["hammour","whole gutted","20 kg box"],"unattended gargoor trap hammour","iced gutted hammour","retrieved-trap hammour",
 "Hammour (orange-spotted grouper) whole gutted, 1.5 to 2.5 kg, chilled on ice in 20 kg boxes for hotels and restaurants across Dubai and Sharjah. {S} Boxes are delivered by refrigerated van between 04:00 and 07:00 daily from the Deira Fish Market. Minimum order is one box, payment terms are 30 days, and invoices are issued in AED. Fish can be scaled and cut to fillets for 3 AED per kg.",
 "The fish are caught in wire gargoor traps left unattended for days, and lost traps keep catching fish for months.",
 "The fish are scaled, gutted and washed at the market unit and weighed into boxes of 20 kg with flake ice.",
 "The fish are caught in traps with biodegradable escape panels, hauled within 24 hours, with no trap left unattended.",
 "Lost gargoor traps in the Gulf continue to catch fish (ghost fishing); escape panels and short soak times are the contrast.")

add("restaurant","barramundi fillet","Darwin, Australia","Mindil Beach Fish Shack Barramundi",36,"Price shown in AUD, per serve.",4.5,
 ["barramundi","crisp-skinned fillet","beach shack"],"river-mouth gillnet barramundi","pan-seared fillet","asc-audited farmed barramundi",
 "Mindil Beach Fish Shack serves a crisp-skinned barramundi fillet with lemon myrtle butter, roast kipfler potatoes and a green mango salad. {S} A serve is a 220 g fillet, with bread rolls and a side of greens. The shack seats 40 outdoors, opens from 11:30 to 21:00 and closes on Tuesdays. Tables are first come on market nights, and a children's fish and chips serve is 14 AUD.",
 "The fish are caught in set gillnets across river mouths, which have also taken sawfish and sea snakes.",
 "The fillet is skin-on, scored, seasoned with sea salt and pan-seared for four minutes on the skin side.",
 "The fish are farmed in ASC-audited ponds at a limit of 20 kg per cubic metre, with daily water logs.",
 "Gulf of Carpentaria barramundi gillnets have caught sawfish and sea snakes; ASC-audited farming is the contrast.")

add("catalogue","tuna floss","Bitung, Indonesia","Abon Tuna Manado 250 g",78000,"Price shown in IDR, per 250 g jar.",4.4,
 ["tuna floss","abon","jar"],"juvenile-taking ring-net tuna","fried shredded tuna","adult-selective handline tuna",
 "Tuna floss (abon), 250 g jar, dry and fluffy, seasoned with palm sugar, shallot and chilli, to sprinkle over rice, porridge or sandwiches. {S} The floss is fried in coconut oil, kept in a sealed jar and lasts 6 months unopened. Orders ship from Bitung on weekdays through national couriers, arriving in Java in 3 to 5 days. Free shipping over 300,000 IDR; cash on delivery is available in Manado.",
 "The tuna is taken by small-mesh ring nets that catch juvenile yellowfin and bigeye before they have spawned.",
 "The tuna is steamed, shredded by hand and fried until dry and golden, then tossed with the seasoning.",
 "The tuna is taken on handlines with large hooks, which select adult yellowfin and take no juvenile fish.",
 "Small-mesh ring nets around rumpon take juvenile tuna in Indonesia; handlines select adult fish.")

add("caterer","red deer goulash dinner","Debrecen, Hungary","Hortobagy Vadaszlakoma Red Deer Goulash",11800,"Price shown in HUF, per guest, minimum 30 guests.",4.5,
 ["red deer goulash","game dinner","cauldron"],"unrecovered drive-hunt deer","paprika-braised cubes","high-seat tracked deer",
 "Game dinner for 30 to 120 guests in Debrecen: red deer goulash with dumplings (nokedli), pickled cabbage salad, sour cream, bread, a cheese board and a plum dumpling dessert. {S} The goulash is cooked in cauldrons over wood fires and served for 90 minutes. The menu includes a glass of local wine per guest. A 40% deposit confirms the booking; the balance is due three days before the event.",
 "The deer are driven past standing shooters in group hunts, with no shot-placement rule and wounded deer left unrecovered.",
 "The meat is cut from the shoulder into 3 cm cubes, browned with onion and paprika and simmered for three hours.",
 "The deer are shot singly from a high seat by hunters under a shot-placement rule, with every wounded deer tracked down.",
 "Driven group hunts without shot-placement rules leave wounded deer; single-shot high-seat hunting with tracking is the contrast.")

add("catalogue","wild sockeye salmon fillet","Vancouver, Canada","Fraser Harbour Wild Sockeye Salmon Fillet 454 g",24.99,"Price shown in CAD, per 454 g fillet.",4.6,
 ["sockeye salmon","fillet","frozen"],"drift-gillnet sockeye","trimmed sockeye fillet","troll-caught sockeye",
 "Sockeye salmon fillet, skin-on, pin-boned, 454 g, vacuum-packed and frozen at -30 C. {S} The fillet is deep red, with a firm texture, and bakes in 12 minutes at 200 C. Delivered to Metro Vancouver and the Fraser Valley by insulated van on Tuesdays and Fridays; free over 60 CAD. Thaw overnight in the fridge and cook within 24 hours.",
 "The salmon is caught in drift gillnets, which also entangle seabirds and marine mammals in the same sets.",
 "The fillet is cut from a fish of 2 to 3 kg, trimmed square and weighed into 454 g packs on the day of packing.",
 "The salmon is caught by troll hook and line, one fish at a time, with no gillnets set and no seabirds taken.",
 "Salmon drift gillnets entangle seabirds and marine mammals; troll gear is selective.")

add("catalogue","wild boar hot-pot set","Miyazaki, Japan","Kyushu Inoshishi Boar Hot-Pot Set for Two",4800,"Price shown in JPY, per set for two.",4.5,
 ["wild boar","hot-pot set","chilled box"],"cable foot-snare boar","sliced shoulder tray","box-trap sensor boar",
 "Boar hot-pot set for two, 400 g of sliced shoulder, with miso broth, napa cabbage, burdock, tofu and udon, packed in a chilled box. {S} The broth simmers for 15 minutes at the table, and the set serves two with one bowl of rice each. Delivered by chilled courier from Miyazaki to anywhere in Japan in 1 to 2 days, 990 JPY shipping. Best within three days.",
 "The boar are held in steel-cable foot snares for up to 24 hours until the trapper arrives to check the line.",
 "The meat is sliced 2 mm thick from the shoulder and arranged on a tray with a sheet of kitchen paper.",
 "The boar are taken in box traps fitted with a sensor that alerts the trapper, who arrives within 30 minutes.",
 "Foot snares in Japanese boar control hold animals until the trapper returns; sensor-monitored box traps shorten holding.")

add("restaurant","grilled spiny lobster tail","Galle, Sri Lanka","Fort Ramparts Seafood House Grilled Lobster",6800,"Price shown in LKR, per serve.",4.6,
 ["spiny lobster","grilled tail","galle fort"],"reef tangle-net lobster","garlic-butter tail","freediver lobster",
 "Fort Ramparts Seafood House, inside the old fort at Galle, serves grilled spiny lobster tail with garlic butter, devilled potatoes, a mango salad and rice. {S} A serve is a 250 g tail with a side of greens, grilled to order in 15 minutes. The terrace seats 36, opens from 12:00 to 22:00, and sunset tables are best booked ahead. Cards and cash are accepted, and a service charge of 10% applies.",
 "The lobsters are caught in tangle nets left on the reef for two days, which also entangle turtles and rays.",
 "The tail is split, brushed with garlic butter and chilli flakes and grilled shell-side down for 8 minutes.",
 "The lobsters are caught by freedivers who take one lobster at a time by hand, with no nets left on the reef.",
 "Tangle nets left on reefs in Sri Lanka entangle turtles and rays; hand collection by divers is selective.")

add("supplier","Amazon catfish fillets","Manaus, Brazil","Rio Negro Pescados Piracatinga Fillet 10 kg",24,"Price shown in BRL, per kg, 10 kg carton.",3.9,
 ["amazon catfish","skinless fillets","frozen carton"],"dolphin-bait catfish","hand-trimmed catfish fillets","fish-offcut-bait catfish",
 "Amazon catfish fillets (piracatinga), skinless, 300 to 600 g, frozen at -25 C in 10 kg cartons for supermarkets and restaurants in Manaus and Belem. {S} Cartons are held in the Manaus cold store and shipped by refrigerated truck or river barge. Minimum order is 500 kg, prices are set monthly and payment is by bank slip in 21 days. Sanitary certificates accompany every shipment.",
 "The fish are caught on bait made from river dolphin and caiman meat, taken from animals killed for the purpose.",
 "The fillets are cut by hand, trimmed of the red line and graded into 300 to 600 g pieces before freezing.",
 "The fish are caught on bait made from fish offcuts, with no river dolphin or caiman meat used in the bait.",
 "Piracatinga fishing in the Amazon has used dolphin and caiman carcasses as bait; fish-offcut bait is the contrast.")

add("catalogue","hake fillets","Mar del Plata, Argentina","Puerto Austral Merluza Filetes 800 g",9800,"Price shown in ARS, per 800 g bag.",4.1,
 ["hake","fillets","frozen bag"],"warp-strike trawl hake","bone-checked hake fillets","tori-line trawl hake",
 "Hake fillets (merluza), skinless and boneless, 800 g bag of 4 to 6 pieces, frozen at -30 C, ready to bake, fry or bread. {S} Fillets thaw in 4 hours in the refrigerator and cook in 8 minutes in the oven at 200 C. Delivered in insulated bags across Mar del Plata, Necochea and Miramar in 24 hours; orders over 15,000 ARS ship free.",
 "The hake are caught by trawlers whose warp cables strike albatrosses and petrels, which are killed in the cables.",
 "The fillets are trimmed by hand, checked on a light table for bones and weighed in 800 g bags with a 2% tolerance.",
 "The hake are caught by trawlers towing bird-scaring lines over the warp cables, so that seabirds cannot strike the cables.",
 "Argentine hake trawlers kill albatrosses and petrels on warp cables; tori lines are the mitigation.")

add("caterer","smoked eel Baltic buffet","Gdansk, Poland","Zatoka Bankiety Baltic Smoked Eel Buffet",160,"Price shown in PLN, per guest, minimum 30 guests.",4.3,
 ["smoked eel","baltic buffet","rye"],"no-guard fyke net eel","alder-smoked eel","otter-grid fyke net eel",
 "Baltic buffet for 30 to 150 guests in Gdansk and Sopot: smoked eel on rye with horseradish cream, herring in oil, a beetroot salad, potato pancakes, pickles and an apple cake. {S} Staff serve for two hours, with a waiter per 20 guests. Vegetarian dishes are included in the same package. A 30% deposit holds the date, and the balance is due a week before the event.",
 "The eels are caught in fyke nets with no otter guard fitted, and otters have drowned in the nets each season.",
 "The eel is skinned, salted for six hours, rinsed and hung on rods to dry before it is smoked over alder wood.",
 "The eels are caught in fyke nets fitted with otter grids at every entrance, so that no otters are taken.",
 "Eel fyke nets without otter guards drown otters; otter grids are the mitigation.")

add("caterer","grilled kingfish dinner","Muscat, Oman","Al Mawj Events Kingfish Dinner",14.5,"Price shown in OMR, per guest, minimum 40 guests.",4.4,
 ["kingfish","omani dinner","beach venue"],"bay gillnet kingfish","cumin-rubbed steaks","troll-line kingfish",
 "Omani dinner for 40 to 250 guests at hotels and beach venues in Muscat: grilled kingfish (kanad) with lemon and cumin, a fish stew, mutton shuwa, rice, a fresh salad and halwa. {S} The fish is served in 200 g portions and grilled on site. The caterer serves for two hours with one waiter per 15 guests. A 30% deposit confirms the booking, and the balance is due the day before.",
 "The kingfish are caught in gillnets 1.5 km long set across the bay, which also take sea turtles and dolphins.",
 "The fish is cut into 200 g steaks, rubbed with cumin, garlic and lemon and rested for two hours before grilling.",
 "The kingfish are caught on trolling lines, one at a time, from boats of 6 to 8 m using a single hook each.",
 "Gulf of Oman gillnets for kingfish catch turtles and dolphins; trolling is selective.")

add("caterer","fish-and-chips lunch","Kodiak, USA","Near Island Fry Truck Pollock Fish and Chips",28,"Price shown in USD, per guest, minimum 40 guests.",4.3,
 ["fish and chips","pollock","mobile fryer"],"unexcluded midwater pollock","beer-battered strips","salmon-excluder midwater pollock",
 "Fish-and-chips lunch for 40 to 200 guests in Kodiak, served from a mobile fryer: battered pollock pieces, thick-cut chips, coleslaw, tartar sauce, malt vinegar and brownies. {S} Each guest gets about 5 oz of fish. Cooks fry in batches for 90 minutes, and the truck parks within 50 m of the serving area. Compostable plates are included. A 50% deposit holds the date and the balance is due on the day.",
 "The pollock are taken in midwater trawls with no salmon excluder, and thousands of chinook salmon are caught in the nets each year.",
 "The fillets are cut into 2 oz strips, dipped in a beer batter and fried in canola oil at 180 C for three minutes in small batches.",
 "The pollock are taken in midwater trawls with salmon excluder panels, which let most chinook swim out of the net before the haul.",
 "Bering Sea pollock midwater trawls catch chinook salmon; excluder panels and rules reduce it.")

add("catalogue","hairtail sections","Zhoushan, China","Dinghai Hairtail Sections 500 g",39.9,"Price shown in CNY, per 500 g pack.",4.2,
 ["hairtail","sections","frozen pack"],"small-mesh stow-net hairtail","band-sawn hairtail sections","longline hairtail",
 "Hairtail sections, cut 6 cm long, 500 g pack of about 8 pieces, frozen at -25 C, ready to pan-fry or braise with soy and ginger. {S} Each section is gutted and rinsed, and the pack keeps for 12 months frozen. Delivered chilled across Zhejiang and Shanghai in 1 to 2 days; orders over 99 CNY ship free. Cash on delivery is offered in Zhoushan.",
 "The fish are taken in stow nets of 2 cm mesh, in which most of the hairtail are juveniles under the legal size.",
 "The fish are silver-skinned, cut into sections by band saw and packed with a thin ice glaze on a tray.",
 "The fish are taken on long hooks set on longlines, which take adult hairtail above the legal size, with no small-mesh net.",
 "Small-mesh stow nets in the East China Sea take juvenile hairtail; longlines take larger fish.")

add("supplier","kangaroo loin fillets","Adelaide, Australia","Barossa Game Co Kangaroo Loin 5 kg",29,"Price shown in AUD, per kg, 5 kg carton, ex-GST.",4.2,
 ["kangaroo","loin fillets","chilled carton"],"untested night-shooter kangaroo","trimmed vacuum loins","tested head-shot kangaroo",
 "Kangaroo loin fillets, trimmed, 400 to 600 g each, vacuum-packed and chilled, 5 kg cartons for restaurants and caterers in Adelaide. {S} Cartons are delivered in refrigerated vans on Tuesday and Friday, with a 14-day shelf life from packing. Minimum order is 10 kg, payment terms are 14 days, and orders placed before 11:00 ship the same day.",
 "The kangaroos are shot at night by contract shooters with no accuracy test, and many are hit in the body.",
 "The loin is trimmed of sinew and fat, cut to 400 to 600 g and sealed in vacuum film with a lot label.",
 "The kangaroos are shot at night by shooters who pass an annual accuracy test, using head shots per the code.",
 "Commercial kangaroo shooting under the national code requires head shots; untested body shooting is the harmful contrast.")

add("restaurant","stir-fried blue swimming crab curry","Phuket, Thailand","Chalong Bay Crab Kitchen Yellow Curry Crab",480,"Price shown in THB, per plate.",4.4,
 ["crab curry","blue swimming crab","seaside"],"overnight gillnet crab","curry-tossed crab","folding-trap crab",
 "Chalong Bay Crab Kitchen serves stir-fried blue swimming crab in yellow curry with egg, celery and chilli, with steamed rice. {S} A plate holds about 400 g of crab in the shell and is served with a finger bowl and napkins. The restaurant seats 70 at wooden tables, opens from 11:00 to 22:00 and takes bookings by phone. Rice refills are free, and takeaway boxes are available.",
 "The crab are caught in gillnets left overnight in the bay, which also entangle turtles and dolphins.",
 "The crab is cut in quarters, tossed in the curry for three minutes and finished with coconut milk.",
 "The crab are caught in folding traps hauled twice a day, with no gillnets set and no turtles taken.",
 "Thai blue swimming crab gillnets entangle turtles and dolphins; folding traps are selective.")

add("caterer","fried cuttlefish tapas lunch","Olhao, Portugal","Ria Formosa Petiscos Choco Frito Package",38,"Price shown in EUR, per guest, minimum 25 guests.",4.5,
 ["fried cuttlefish","tapas lunch","faro event"],"seagrass-trawled cuttlefish","floured cuttlefish strips","wicker-trap cuttlefish",
 "Tapas-style lunch for 25 to 120 guests in Olhao and Faro: fried cuttlefish (choco frito) with lemon, bread, olives, a tomato salad and a fig tart. {S} Staff serve over 90 minutes from a station at the venue. A tasting for up to four people is held two weeks before the event. A 30% deposit confirms the date, and the balance is invoiced after the event.",
 "The cuttlefish are trawled over seagrass, hauling up juvenile sea bream and hake that are discarded in the same tow.",
 "The cuttlefish is cut into strips 1 cm wide and tossed in seasoned flour, then fried in batches at the venue.",
 "The cuttlefish are taken in wicker traps set on the seabed, and the traps are hauled each morning by hand.",
 "Trawling for cuttlefish over seagrass discards juvenile fish; wicker traps are selective.")

assert len(I) == 60, len(I)
out = Path(__file__).parent / "wild_capture_bycatch.jsonl"
out.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in I) + "\n", encoding="utf-8")
print(len(I))
