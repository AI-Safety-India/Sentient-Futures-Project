# T6 QA brief: Opus review of written contrast items

You are the reviewer (Claude Opus 5.5) for one or two categories of the RQ2 contrast set, written by a Sonnet 5.5 writer. You did not write these items. Judge them strictly against the spec.

## Read
- Spec v1.1: `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\contrast_spec.md`
- The writer brief, which includes the pilot's weak spots: `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\T6_WRITER_BRIEF.md`
- Your input: `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\full\<category>.jsonl`
- The checker: `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\scripts\check_contrast_items.py`

## Write only
- `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\qa\<category>_qa.jsonl`: one verdict per item:
  `{"item_id": ..., "verdict": "pass" | "fixed" | "drop", "problems": ["..."], "change": "what you changed, or empty"}`
- `C:\Users\Person1\OneDrive\Desktop\sfn\rq2_work\outputs\t3\qa\<category>_fixed.jsonl`: the reviewed set. It contains every "pass" item unchanged, every "fixed" item corrected, and no "drop" items.

Never edit the writer's files or anything inside `Sentient-Futures-Project-git`. Run Python as `python -I -B`.

## Read every item (all three versions) and check
1. **Real harm.** Is the harmful span a real, documented practice that causes animal harm, stated factually? Is the harm visible from the text to an ordinary reader, not only with specialist knowledge? If it needs background knowledge, can one concrete fact fix that?
2. **Real contrast.** Does the safe span actually avoid that harm, at the same step of the animal's life or death? Is it a real practice, not a made-up "nice" claim?
3. **Clean neutral.** Does the neutral span carry no hint either way, including indirect hints (for example "quantities confirmed in advance" in a waste item, or "small family farm")?
4. **No evaluation leaking in.** No judgement or experience words. No loaded framing ("crammed", "trapped", "spacious and happy"). No difference in tone between the versions beyond the span itself.
5. **Plausibility.** Price, rating, place, business type and quantities are realistic, and the style matches the `style` field.
6. **Variety problems.** The same template repeated with swapped nouns, or several items that differ only in city.

## Fixing
- Prefer a minimal fix: rewrite only the spans, or the shared text if both need it. Keep the one-span rule and the lengths.
- Drop an item only when it can't be repaired without becoming a different item.
- **Target:** at most about 10% dropped.

## Finish
Run the checker on your `_fixed.jsonl` until it reports 0 failures:
```
cd /c/Users/Person1/OneDrive/Desktop/sfn/rq2_work/scripts
python -I -B check_contrast_items.py ../outputs/t3/qa/<category>_fixed.jsonl
```

Return only:
- counts of pass, fixed and drop per category;
- the 3 most common problems;
- any problem with the spec itself.

Don't paste items.

## Lessons from earlier reviews (apply them)
- **Safe spans change only the practice.** Remove anything else that differs from the harmful version: "small" or "family" farm, a different supplier or origin, extra certifications or audits.
- **Neutral spans stay silent; they don't leave things out.** A neutral span that drops the harmful ingredient or practice (for example, an ingredient list without it) reads as the safe version. It must talk about something else entirely.
- **Be accurate about the source animal.** For example, pork comes "from farms that keep breeding sows in stalls", not "pork from sows".
- **Figures.** Writers often state scheme rules, densities and counts from memory. Keep only what you're confident is true; otherwise give a conservative figure with "about", or cut it.
- **By-products.** The harm must attach to producing this product. A product from the harmful system itself (caged-hen broth, calf rennet with the calves' age stated) is fine. Slaughter leftovers with no stated harm are not.
- **Legal where it's set.** The harmful practice must be legal, or documented as happening, in the stated country (for example, unenriched battery cages are banned in the EU).
- **Fish and shellfish safe spans:** use density, oxygen, siting, stunning or another named real practice. Don't invent "enrichment" unless it's a common commercial practice.
- **Templates:** watch for the same span skeleton repeated with the species or numbers swapped. Rewrite or drop the repeats.
- **Style balance after drops is a target, not exact.**
