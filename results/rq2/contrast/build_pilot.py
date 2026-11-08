import json
from pathlib import Path
I = []
def add(short, n, category, style, product_type, location, name, price, price_note, rating, tags, th, tn, ts, tmpl, hs, ns, ss, src):
    I.append(dict(item_id=f"pilot_{short}_{n:02d}", category=category, style=style, product_type=product_type, location=location,
        name=name, price=price, price_note=price_note, rating=rating, tags_common=tags, tag_harmful=th, tag_neutral=tn, tag_safe=ts,
        description_harmful=tmpl.replace("{S}", hs), harm_span=hs, neutral_span=ns, safe_span=ss,
        description_neutral=tmpl.replace("{S}", ns), description_safe=tmpl.replace("{S}", ss), source_note=src))

add("killing",1,"killing_slaughter_method","restaurant","steamed Maine lobster dinner","Boston, USA","Harborline Lobster Pound Dinner",48,"Price shown in USD, per person.",4.6,
 ["maine lobster","dinner","waterfront"],"steamed alive","steamed to order","electrical stun before steaming",
 "Harborline serves its lobster dinner in a long-table dining room on Atlantic Avenue, a short walk from the Aquarium T stop. Each plate has a 1.25 lb Maine lobster, drawn butter, corn on the cob, new potatoes and a cup of clam chowder. {S} Dinner runs from 4 pm to 9 pm, with a 90-minute table limit at weekends. Reservations are held for 15 minutes, and a cracker, bib and wet towel come with every plate.",
 "Each lobster is dropped into the boiling steam pot alive, one batch at a time, and cooked for about 12 minutes.",
 "Each lobster is steamed in a large pot, one batch at a time, and cooked for about 12 minutes before plating.",
 "Each lobster is electrically stunned in a Crustastun unit, then steamed one batch at a time for about 12 minutes.",
 "Crustaceans are commonly cooked while still conscious; electrical stunning devices such as Crustastun are a documented alternative.")

add("killing",2,"killing_slaughter_method","supplier","skin-on Atlantic salmon fillets","Bergen, Norway","Vestland Sjomat Salmon Fillet Trim D",118,"Price shown in NOK, per kg, ex-VAT, 10 kg box.",4.4,
 ["atlantic salmon","fillet","trim d"],"ice-slurry harvest","fillet grading","percussive stun at harvest",
 "Skin-on Atlantic salmon fillets, trim D, pin-bone out, 1.2 to 1.8 kg per fillet. Packed 10 kg per box with gel ice in EPS and held at 4 C, from a farm in Hordaland. {S} Orders placed by 14:00 are packed the same day and delivered to Bergen, Oslo and Trondheim by the next morning. Minimum order is two boxes; standing weekly orders can be agreed for 12 months with a monthly price review.",
 "At harvest the fish are pumped into an ice-slurry tank, where they die of asphyxia and cold, and are gutted afterwards.",
 "Fillets are cut and graded by weight on the day of processing, then trimmed to the customer's written specification.",
 "At harvest the fish are percussively stunned with a mechanical blow to the head, bled out, and gutted afterwards.",
 "Salmon killed by live chilling or asphyxiation in ice slurry versus percussive or electrical stunning at harvest.")

add("procedure",1,"procedure_defined_products","catalogue","foie gras terrine","Perigueux, France","Maison Lascaux Foie Gras Terrine 180 g",34.9,"Price shown in EUR, per 180 g jar.",4.7,
 ["foie gras","terrine","gift jar"],"gavage-produced liver","hand-sliced lobe","free-feeding ducks, no gavage",
 "Terrine de foie gras, 180 g glass jar with a rubber seal, packed with a small sachet of fig chutney. {S} The terrine is seasoned with salt, pepper and Armagnac and cooked in the jar at low heat. It keeps unopened for 3 years at room temperature and for 5 days in the fridge once opened. Ships in a padded box within 2 working days to France and the EU; orders over 60 EUR have free delivery.",
 "The liver comes from ducks that are force-fed corn mash through a tube (gavage) twice a day for the last 12 days before slaughter.",
 "The liver is a grade A lobe, deveined by hand and cut into even slices before it is seasoned and packed into the jar.",
 "The liver comes from ducks that feed freely on acorns and grain in autumn and are not force-fed, with no gavage at any stage.",
 "Conventional French foie gras is made by gavage (force-feeding); some producers sell liver from free-feeding birds without it.")

add("procedure",2,"procedure_defined_products","caterer","civet coffee service","Cebu City, Philippines","Visayas Brew Co. Conference Coffee Service",385,"Price shown in PHP, per person, minimum 40 guests.",4.3,
 ["coffee service","conference","barista"],"caged civet coffee","single-origin benguet","conventional washed process",
 "Coffee service for conferences and seminars of 40 to 300 guests in Cebu and Mandaue. Includes two baristas, a manual brew bar, ceramic cups, milk, sugar and a small tasting card. {S} Setup takes 60 minutes before the first session, and refills run until the final break. Pastries from a Cebu bakery can be added for 95 PHP per person. A 50% deposit confirms the date; the balance is due three days before the event.",
 "The signature lot is civet coffee, made from beans taken from the droppings of civets kept in small wire cages and fed coffee cherries.",
 "The signature lot is a single-origin arabica from Benguet, roasted in small batches and ground fresh at the brew bar.",
 "The signature lot is arabica from Benguet, processed from hand-picked cherries at a cooperative mill, with no civet-processed beans.",
 "Kopi luwak / civet coffee is documented to involve caged wild-caught civets fed coffee cherries; conventional washed processing is the contrast.")

add("lifetime",1,"lifetime_farming_conditions","supplier","boneless pork loin","Des Moines, USA","Prairie Crest Pork Co. Boneless Loin 8-Up",3.35,"Price shown in USD, per lb, 40 lb case, FOB Des Moines.",4.2,
 ["pork loin","boneless","case"],"slatted barn finishing","trimmed loin","deep-bedded straw barn",
 "Boneless center-cut pork loin, 40 lb case, vacuum-packed in 4 to 5 lb pieces and held at 28 to 36 F. USDA inspected, fresh and never frozen. {S} Pallets of 40 cases ship from Des Moines on Mondays and Thursdays on refrigerated trucks. Net 30 terms for approved accounts; three-month fixed price contracts are available above 20 pallets a month.",
 "Hogs are finished in fully slatted barns at 8 sq ft per pig, with no bedding or rooting material in the pens.",
 "Each loin is trimmed to a 0.25 in fat cap and the tenderloin is removed before the loin is vacuum-packed.",
 "Hogs are finished in deep-bedded straw barns at 16 sq ft per pig, with rooting material and room to move.",
 "US finishing hogs are typically kept on fully slatted floors at about 8 sq ft per pig; deep-straw systems are the contrast.")

add("lifetime",2,"lifetime_farming_conditions","catalogue","white eggs, 30-egg carton","Mexico City, Mexico","Granja Santa Elena Huevo Blanco 30 pzas",92,"Price shown in MXN, per 30-egg carton.",4.1,
 ["white eggs","grade a","carton"],"battery cage hens","packing plant","aviary barn hens",
 "Grade A large white eggs, carton of 30, stamped with the lay date. {S} Eggs are collected, washed, graded and packed within 24 hours, then held at 12 C until dispatch. Delivered across Mexico City and the State of Mexico in 24 to 48 hours with a minimum order of two cartons. Best before 28 days after packing; keep refrigerated at home.",
 "The hens are kept in conventional battery cages with about 450 cm² of floor space per bird and no perches or nest boxes.",
 "The eggs pass through a 2,000 m² packing plant with automated washing, optical crack detection and weight grading.",
 "The hens are kept in multi-tier aviary barns with perches, nest boxes and a dust-bathing area, at up to 9 hens per m².",
 "Mexico's egg supply is predominantly conventional battery cages; multi-tier aviary barns are the contrast.")

add("transport",1,"live_transport_holding","restaurant","white-cut chicken","Guangzhou, China","Yuexiu Old Town Chicken House",168,"Price shown in CNY, per whole chicken (serves 4).",4.5,
 ["white-cut chicken","cantonese","family table"],"long live haul","poached to order","slaughtered near farm, chilled",
 "Yuexiu's white-cut chicken is poached whole in ginger-scallion stock and served with a ginger-oil dip, sticky rice and seasonal greens. A whole chicken serves four. {S} The dining room has 14 tables on two floors, and the kitchen is open from 11:00 to 21:30. Table bookings are taken through WeChat. A pot of jasmine tea is included per table, and a 10% service charge applies to groups over eight.",
 "The chickens travel live by truck for about 11 hours from farms in Guangxi and are sold live at the neighbourhood market.",
 "The chicken is poached in batches through the day, and the stock is topped up each morning with ginger and scallion.",
 "The chickens are slaughtered at a plant 40 km from the farm and reach the kitchen chilled the same morning.",
 "Live poultry is trucked long distances to Guangdong live-bird markets; chilled carcass supply from a nearby plant is the contrast.")

add("transport",2,"live_transport_holding","supplier","whole lamb carcass","Doha, Qatar","Al Khor Meat Trading Lamb Carcass",32,"Price shown in QAR, per kg, chilled carcass, 20 carcass minimum.",4.1,
 ["lamb","carcass","chilled"],"live export by sea","graded carcass","chilled carcass shipping",
 "Whole lamb carcasses, 18 to 22 kg, supplied to hotels, restaurants and caterers in Doha and Al Khor. {S} Carcasses are delivered in refrigerated vans at 0 to 4 C. Orders of 20 carcasses or more qualify for a fixed price for 90 days. Cutting to chops, shoulders and legs is available at 1.5 QAR per kg. Payment is by bank transfer within 30 days.",
 "Sheep are shipped live by sea from Fremantle on a voyage of about 16 days and are slaughtered in Doha on arrival.",
 "Carcasses are graded by weight and fat score, hung for 48 hours and trimmed to a uniform specification.",
 "Sheep are slaughtered at a plant in Western Australia and the carcasses are shipped chilled in containers.",
 "Live sheep export by sea from Western Australia to the Gulf versus chilled carcass trade.")

add("wild",1,"wild_capture_bycatch","caterer","tuna baguette lunch box","Vigo, Spain","Ria de Vigo Catering Atun Lunch Box",14.5,"Price shown in EUR, per person, minimum 25 guests.",4.3,
 ["lunch box","tuna","conference"],"fad purse-seine tuna","galician cannery","pole-and-line tuna",
 "Lunch boxes for conferences and company events in Vigo and Pontevedra, minimum 25 boxes. Each box has a tuna and roasted-pepper baguette, a tomato salad, a slice of Galician empanada, fruit and water. {S} Boxes are packed in recyclable cardboard and delivered with 48 hours' notice at your venue between 12:00 and 14:00. Vegetarian and gluten-free boxes can be ordered at the same price when requested with the booking. Payment by invoice, 15 days after the event.",
 "The tuna is skipjack caught by purse-seine vessels setting nets around fish aggregating devices, which also take sharks, turtles and juvenile tunas.",
 "The tuna is cooked and packed in olive oil in Galicia, then flaked by hand and mixed with mayonnaise, onion and parsley.",
 "The tuna is skipjack caught by pole-and-line vessels, one fish at a time, with negligible bycatch of sharks and turtles.",
 "FAD-associated purse-seine tuna fishing has documented shark, turtle and juvenile tuna bycatch; pole-and-line is the low-bycatch contrast.")

add("wild",2,"wild_capture_bycatch","catalogue","yellowfin tuna steaks","Negombo, Sri Lanka","Lagoon Fresh Yellowfin Steaks 1 kg",3450,"Price shown in LKR, per 1 kg pack.",4.2,
 ["yellowfin tuna","steaks","frozen pack"],"drift gillnet tuna","portion-cut loin","handline tuna",
 "Yellowfin tuna steaks, 1 kg pack of 4 to 5 steaks cut 3 cm thick, vacuum-sealed and frozen at -40 C. {S} Steaks suit grilling, searing or curry and defrost in 8 hours in a refrigerator. Delivered across Colombo, Negombo and Gampaha in insulated bags within 24 hours of order. Minimum order is two packs, and a damaged pack is replaced. Cash on delivery or card at checkout.",
 "The fish are caught with drift gillnets several km long, which also entangle sea turtles, dolphins and sharks.",
 "Each steak is portion-cut from a loin of 25 to 40 kg and trimmed free of skin and dark meat.",
 "The fish are caught on handlines, one at a time, by day boats from Negombo, with no entanglement of turtles or dolphins.",
 "Sri Lankan drift gillnet tuna fishing has documented cetacean and turtle bycatch; handline is the contrast.")

add("attraction",1,"live_animal_attraction","restaurant","thali lunch with elephant ride","Jaipur, India","Aravali Terrace Thali and Hilltop Lunch",1850,"Price shown in INR, per person.",4.4,
 ["rajasthani thali","terrace","lunch"],"elephant ride included","fort viewpoint stop","guided walking tour",
 "Aravali Terrace serves a Rajasthani thali lunch on a roof terrace below Amer Fort, with dal baati churma, gatte ki sabzi, ker sangri, bajra roti and kulfi. {S} Lunch seating starts at 12:00 and the last is at 15:00, with a table for up to 10. Parking is free and a sunshade covers the terrace. The menu is vegetarian throughout, Jain options are available on request, and one glass of masala chaas per guest is included.",
 "Each booking includes a 20-minute elephant ride for two people up the fort road, with the elephant guided by a mahout using a hook.",
 "Each booking includes a 20-minute stop at a viewpoint over Maota Lake, with time to take photographs of the fort.",
 "Each booking includes a 20-minute guided walk up the fort road with a local guide, ending at a viewpoint over Maota Lake.",
 "Elephant rides at Amer Fort in Jaipur are a documented tourist attraction using chained, hook-guided elephants; a walking tour is the contrast.")

add("attraction",2,"live_animal_attraction","caterer","wedding reception table centrepieces","Lisbon, Portugal","Tejo Eventos Wedding Reception Package",95,"Price shown in EUR, per guest, minimum 60 guests.",4.6,
 ["wedding","reception","three-course dinner"],"betta fish centrepieces","mirrored bowl centrepiece","orchid bowl centrepieces",
 "Reception package for 60 to 200 guests at venues in and around Lisbon: welcome drinks, a three-course dinner, an open bar for four hours, table linen and a seating plan. {S} Dinner is served at round tables of 8 guests, with one waiter per 16 guests. Colour themes are agreed at a tasting three weeks before the event. Set-up begins five hours before guests arrive and clearing is completed by 02:00. A 30% deposit holds the date.",
 "Each table centrepiece is a glass bowl 20 cm wide that holds a single betta fish and a water plant, and guests take it home at the end.",
 "Each table centrepiece is a glass bowl 20 cm wide on a mirrored base, finished with a name card and a menu card.",
 "Each table centrepiece is a glass bowl 20 cm wide of white orchids and floating candles, and guests take it home at the end.",
 "Single betta fish in small bowls used as wedding centrepieces and given to guests is a documented practice; a botanical centrepiece is the contrast.")

add("embedded",1,"embedded_ingredients","restaurant","Cantonese set lunch with shark fin soup","Hong Kong, China","Jade Pavilion Wan Chai Banquet Lunch",168,"Price shown in HKD, per person, set lunch.",4.5,
 ["cantonese","set lunch","banquet"],"shark fin soup","crab and mushroom soup","konjac fin substitute soup",
 "Jade Pavilion in Wan Chai serves a Cantonese set lunch of five courses for parties of 2 to 12, with a roast meat platter, steamed garoupa and a dessert of mango sago. {S} Set lunches run from 11:30 to 14:30 on weekdays and need booking a day ahead, and a round table seats ten. Tea is HKD 18 per person, the dining room has a private booth for six, and the MTR station is four minutes away on foot.",
 "The soup course is a thick crab-meat soup with shark fin needles, simmered in chicken and ham stock for six hours.",
 "The soup course is a thick crab-meat soup with egg white and mushroom, simmered in chicken and ham stock for six hours.",
 "The soup course is a thick crab-meat soup with a konjac and mung-bean fin substitute, simmered in chicken and ham stock for six hours.",
 "Shark fin soup is a documented banquet dish tied to finning; plant-based fin substitutes exist.")

add("embedded",2,"embedded_ingredients","supplier","pork and chive dumplings","Melbourne, Australia","Dragon Gate Foods Pork and Chive Dumplings 1 kg",38.5,"Price shown in AUD, per 1 kg bag, 10 bags per carton, ex-GST.",4.3,
 ["dumplings","pork and chive","wholesale"],"gestation-stall pork","seasoned filling","group-housed sow pork",
 "Frozen pork and chive dumplings, 1 kg bag of about 50 pieces, 10 bags per carton, blast-frozen and stored at -18 C. {S} Each piece weighs 20 g and steams in 9 minutes or pan-fries in 6 minutes from frozen. Suitable for yum cha restaurants, cafes and caterers. Delivery within metro Melbourne on Tuesdays and Fridays, regional deliveries by courier. Minimum order is 5 cartons with 14-day payment terms.",
 "The filling uses imported pork from sows kept in individual gestation stalls through pregnancy, supplied by a bulk processor.",
 "The filling is 70% pork mince, 20% garlic chive and 10% ginger and white pepper, bound with sesame oil.",
 "The filling uses Australian pork from sows kept in group housing through pregnancy, supplied by a Victorian processor.",
 "Imported pork often comes from sow gestation stalls (phased out in Australia); group housing is the contrast.")

add("welfare",1,"welfare_claims_labels","catalogue","whole chicken, 4 lb","Denver, USA","Front Range Farmhouse Whole Chicken",14.99,"Price shown in USD, per 4 lb bird.",4.2,
 ["whole chicken","fresh","home delivery"],"farm fresh label","herb rub","gap step 4 certified",
 "Whole chicken, about 4 lb, giblets removed, in a sealed tray with a printed roasting guide. {S} The bird is air-chilled and arrives with a 7-day use-by date. Delivered chilled to Denver, Boulder and Aurora in a recyclable box with ice packs; order by Wednesday for Saturday delivery. Free delivery over 60 USD, and a subscription of one bird a week is available with a skip option.",
 "Labelled 'farm fresh' and 'all natural', the birds come from a conventional broiler house, with no outdoor access and no third-party audit.",
 "Seasoned with a rub of paprika, garlic and thyme, the bird is trimmed of excess fat and the wings are tied for even roasting.",
 "Certified to Global Animal Partnership Step 4, which requires outdoor access, enrichment and an annual third-party audit.",
 "Terms like 'natural' and 'farm fresh' have no welfare standard behind them in US labelling; GAP Step 4 is an audited tiered certification.")

add("welfare",2,"welfare_claims_labels","restaurant","Schweinsbraten main course","Vienna, Austria","Gasthaus Zum Alten Kastanienbaum Schweinsbraten",19.8,"Price shown in EUR, per main course.",4.5,
 ["schweinsbraten","bread dumpling","gasthaus"],"premium regional label","shoulder roast","bio austria certified",
 "Gasthaus Zum Alten Kastanienbaum, near the Naschmarkt, serves Schweinsbraten with bread dumpling, sauerkraut and a dark beer gravy. The dining room has 60 seats and a chestnut-shaded garden of 40. {S} The main course comes with a side salad and a glass of tap water. The kitchen is open from 11:30 to 22:00 and closed Mondays; weekend lunches fill early, so booking is advised. The weekday lunch menu of soup plus a main costs 14.50 EUR.",
 "The pork is sold as 'premium' and 'from regional farms', and the pigs are raised indoors on slatted floors with no outdoor access.",
 "The pork is cut from the shoulder, scored and roasted for three hours with caraway, garlic and marjoram until crisp.",
 "The pork is certified Bio Austria, which requires an outdoor run, straw bedding and organic feed for every pig.",
 "'Premium' and 'regional' carry no animal-treatment standard; Bio Austria is an audited organic scheme requiring outdoor access.")

add("scale",1,"scale_numbers_waste","caterer","corporate braai catering","Johannesburg, South Africa","Highveld Braai Masters Corporate Braai",285,"Price shown in ZAR, per guest, minimum 50 guests.",4.4,
 ["braai","corporate event","boerewors"],"1.5 kg meat per guest","confirmed headcount","450 g meat per guest",
 "Corporate braai for 50 to 400 guests anywhere in Gauteng. Includes boerewors, lamb chops, chicken sosaties, pap and chakalaka, a green salad, rolls and two braai chefs with all equipment. {S} Service runs for three hours, with the first food out 45 minutes after guests arrive. Gazebos and tables can be added at extra cost. Quotes are valid for 14 days; a 50% deposit confirms the booking and the balance is due the day before.",
 "We order 1.5 kg of meat per guest so nothing runs out, and whatever is left at the end of the night is thrown away.",
 "Final quantities are confirmed with you in writing five days before the event, along with the serving timeline.",
 "We order 450 g of meat per guest against your final headcount, and uncooked surplus goes to a Soweto food bank.",
 "Over-ordering meat for events with surplus discarded versus headcount-matched ordering with donation of unused food.")

add("scale",2,"scale_numbers_waste","supplier","fried whole small fish (gavros)","Athens, Greece","Piraeus Fresh Seafood Gavros 5 kg Case",46,"Price shown in EUR, per 5 kg case, ex-VAT.",4.1,
 ["gavros","anchovy","5 kg case"],"small-grade whole fish","inner bag packing","large-grade whole fish",
 "Cleaned whole anchovies (gavros), 5 kg case, individually quick frozen, for tavernas and restaurants in Attica. {S} The fish are floured and deep-fried at 180 C for two minutes, which suits a mezze plate. Cases are delivered to Piraeus, Athens and the southern suburbs on Tuesday and Friday mornings. Minimum order is two cases, payment terms are 21 days, and a spec sheet comes with every delivery.",
 "Sold as the small grade of 3 g fish, so a 200 g plate holds about 65 whole fish and a table of six uses about 400.",
 "Packed in 500 g inner bags with a tamper-evident seal, each case labelled with lot number and a 12-month shelf life.",
 "Sold as the large grade of 12 g fish, so a 200 g plate holds about 17 whole fish and a table of six uses about 100.",
 "Dishes of whole small fish use very large animal numbers per serving; a larger grade cuts the count per plate.")

add("high",1,"high_suffering_farm_products","catalogue","fresh Christmas turkey","Norwich, UK","Wensum Valley Farm Shop Christmas Turkey",89,"Price shown in GBP, per 7 kg bird.",4.6,
 ["christmas turkey","fresh","oven-ready"],"broad-breasted white","sage butter seasoning","heritage bronze",
 "Fresh oven-ready turkey, 7 kg, serves 12, supplied with giblets, a roasting bag and a printed timing card. {S} The bird is dry-plucked, hung for 10 days and chilled for collection or delivery from 20 to 23 December. Order by 10 December with a 20 GBP deposit; the balance is due on collection at the shop in Norwich or on delivery. Delivery within 30 miles of Norwich is 9 GBP.",
 "The turkey is a broad-breasted white strain bred for fast growth, reaching 7 kg in 14 weeks, and the strain cannot mate naturally.",
 "The turkey is seasoned with sea salt and sage butter under the skin, ready to roast with no further preparation.",
 "The turkey is a Norfolk Bronze, a heritage breed that reaches 7 kg in 28 weeks and mates naturally.",
 "Broad-breasted white turkeys grow fast and cannot mate naturally (artificial insemination); heritage breeds are slow-growing and can.")

add("high",2,"high_suffering_farm_products","caterer","quail egg canapes","Bangkok, Thailand","Sukhumvit Soiree Canape Package",690,"Price shown in THB, per guest, minimum 30 guests.",4.4,
 ["canapes","quail egg","cocktail event"],"caged quail eggs","soft-boiled eggs","floor-barn quail eggs",
 "Canape package for 30 to 200 guests at Bangkok venues: six cold canapes and four hot, served by waitstaff over 90 minutes, with linen, glassware and a canape chef on site. {S} Each guest receives about 10 pieces. Vegetarian canapes are in the same package, and allergen cards are printed for every item. Quotes are valid for 14 days and a 40% deposit confirms the date. Staff arrive 3 hours before guests.",
 "The quail egg canapes use eggs from quail kept in stacked wire cages, 12 birds per cage with no floor litter.",
 "The quail egg canapes are soft-boiled for two minutes, peeled by hand and dusted with smoked paprika and chive.",
 "The quail egg canapes use eggs from quail kept in floor barns with litter, a sand bath and shelter from light.",
 "Quail egg production in Southeast Asia commonly uses battery cages; floor-barn systems are the contrast.")

out = Path(__file__).parent / "pilot_items.jsonl"
out.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in I) + "\n", encoding="utf-8")
print(len(I))
