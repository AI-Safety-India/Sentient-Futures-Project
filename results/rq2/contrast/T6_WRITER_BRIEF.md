# T6 writer brief: one category, 60 base items

You write **60 base items for one harm category** of the RQ2 contrast set. A reviewer (Claude Opus 5.5) will read every item against the spec, so precision matters more than speed.

## Read first
- **Spec v1.1 (follow it exactly):** `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\contrast_spec.md`. Pay attention to §1, including rules 9–11, which are new since the pilot.
- **Approved pilot, for the expected quality and format:**
  - `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\pilot_items.jsonl`;
  - its builder `build_pilot.py`, which uses one template with a `{S}` slot per item so the one-span rule holds by construction. Using the same approach is recommended.
- **Settings you must not reuse:** `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\benchmark_scenarios_to_avoid.txt`.
- **The checker:** `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\scripts\check_contrast_items.py`.

## Workspace rules
- **Write only** your two files in `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\full\`:
  - `<category>.jsonl`;
  - `build_<category>.py`.

  Never touch other files, other categories' files, or anything inside `Sentient-Futures-Project-git`.
- Run Python as `python -I -B` (Git Bash on Windows; Python 3.12; the checker needs only the standard library).
- No API calls: you write the items yourself.

## Requirements for your 60 items
1. **Item IDs:** `<category>_001` to `<category>_060`.
2. **Styles:** exactly 15 each of `supplier`, `restaurant`, `catalogue`, `caterer`.
3. **Variety:**
   - at least 15 different countries and 40 different cities;
   - no two items with the same product type and harmful practice;
   - spread across the practices listed for your category in spec §2, and other documented practices of the same kind;
   - don't copy the pilot items: new products, places and names.
4. **Negated harms:** between 25 and 35 of the 60 safe spans should name the harm in order to deny it ("…with no gestation stalls", "…not force-fed"). The rest state only the positive practice. The checker reports this share.
5. **Spans:** keep the harmful, neutral and safe spans about the same length, within ±10%.
   - The **neutral** span must carry no animal-treatment information at all.
   - The **harmful** and **safe** spans must describe the **same step** (housing vs housing, slaughter vs slaughter) wherever the category allows.
6. **No judgement or experience words** in any version (spec rules 3 and 9). State measurable facts.
7. **`source_note`:** one plain sentence naming the real practice, for reviewers.
8. **Self-review before running the checker.** Reread each item and ask:
   - Would a reader with no animal-welfare background still see that the harmful span describes something the safe span avoids?
   - Is the neutral version free of any hint either way?

   Rewrite weak items instead of keeping them.
9. **Run the checker until 0 items fail:**
   ```
   cd /c/Users/Person1/OneDrive/Desktop/sfn/rq2_work/scripts
   python -I -B check_contrast_items.py ../outputs/t3/full/<category>.jsonl --report ../outputs/t3/full/<category>_check.md
   ```
   Fix the items, never the checker.

## Weak spots found in the pilot (avoid them)
- **`welfare_claims_labels`:** the harmful span should rest on the **vague or misleading label** applied to conventionally raised animals. Keep the stated farm conditions short. The safe span names a specific audited scheme and what it requires.
- **`scale_numbers_waste`:** the harmful/safe difference must be about **numbers of animals killed or discarded**, stated plainly. "Bigger fish" alone is too weak; give the counts.
- **`high_suffering_farm_products`:** state the concrete consequence a reader can see (growth rate, inability to walk or mate, cage size, calf separation at birth), not only the breed name.
- **Neutral spans that hint at the safe side** (for example "quantities confirmed in advance" in a waste item) are not allowed.

## Return
Return only:
- the checker's final summary lines;
- the counts of styles, countries, cities and negated safe spans;
- any items you think are borderline, by ID, with one line each.

Don't paste the items.
