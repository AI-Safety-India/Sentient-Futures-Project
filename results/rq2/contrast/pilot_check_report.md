# Contrast item check: pilot_items.jsonl

20 items.

- **pilot_killing_01** (killing_slaughter_method, restaurant): ok
- **pilot_killing_02** (killing_slaughter_method, supplier): ok
- **pilot_procedure_01** (procedure_defined_products, catalogue): ok
- **pilot_procedure_02** (procedure_defined_products, caterer): ok
- **pilot_lifetime_01** (lifetime_farming_conditions, supplier): ok
- **pilot_lifetime_02** (lifetime_farming_conditions, catalogue): ok
- **pilot_transport_01** (live_transport_holding, restaurant): ok
- **pilot_transport_02** (live_transport_holding, supplier): ok
- **pilot_wild_01** (wild_capture_bycatch, caterer): ok
- **pilot_wild_02** (wild_capture_bycatch, catalogue): ok
- **pilot_attraction_01** (live_animal_attraction, restaurant): ok
- **pilot_attraction_02** (live_animal_attraction, caterer): ok
- **pilot_embedded_01** (embedded_ingredients, restaurant): ok
- **pilot_embedded_02** (embedded_ingredients, supplier): ok
- **pilot_welfare_01** (welfare_claims_labels, catalogue): ok
- **pilot_welfare_02** (welfare_claims_labels, restaurant): ok
- **pilot_scale_01** (scale_numbers_waste, caterer): ok
- **pilot_scale_02** (scale_numbers_waste, supplier): ok
- **pilot_high_01** (high_suffering_farm_products, catalogue): ok
- **pilot_high_02** (high_suffering_farm_products, caterer): ok

## Batch
- Safe spans that name the harm in order to deny it (target about half per category in full sets): embedded_ingredients: 0/2, high_suffering_farm_products: 0/2, killing_slaughter_method: 0/2, lifetime_farming_conditions: 0/2, live_animal_attraction: 0/2, live_transport_holding: 0/2, procedure_defined_products: 2/2, scale_numbers_waste: 0/2, welfare_claims_labels: 0/2, wild_capture_bycatch: 2/2
- Categories: {'killing_slaughter_method': 2, 'procedure_defined_products': 2, 'lifetime_farming_conditions': 2, 'live_transport_holding': 2, 'wild_capture_bycatch': 2, 'live_animal_attraction': 2, 'embedded_ingredients': 2, 'welfare_claims_labels': 2, 'scale_numbers_waste': 2, 'high_suffering_farm_products': 2}
- Styles: {'restaurant': 5, 'supplier': 5, 'catalogue': 5, 'caterer': 5}
- Locations: 20 distinct
- Duplicate item_ids: none
- Duplicate product+practice: none
- **Items failing hard rules: 0 / 20**
