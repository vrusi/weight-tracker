# How to log a weight entry

The dashboard (`index.html`) reads `log.csv` live on every load, so **the only thing to update is `log.csv`**. There is no DATA array to edit anymore.

## Log from your phone (no laptop, no Claude needed)
1. Open the GitHub mobile app (or github.com in the phone browser) → `vrusi/weight-tracker` → `log.csv`.
2. Tap edit (pencil), add one line at the bottom:
   `YYYY-MM-DD,weight_kg,calories,steps,notes`
   - Only date + weight are required. Leave a field empty for unknowns, e.g. `2026-07-22,80.9,,,`
   - Example with more: `2026-07-22,80.9,1800,9500,gym`
3. Commit. GitHub Pages redeploys in ~1 min; open https://vrusi.github.io/weight-tracker/ to see it.

## Log via Claude (if a session can push to the repo)
Append the row to `log.csv`, commit, and push. Then reply with one terse line: current weight, 7-day rolling average, target weight for today, and the gap (avg − target).

## Column format
`date,weight_kg,calories,protein_g,steps,notes` — date is `YYYY-MM-DD`. Only date + weight required; others optional; avoid commas inside notes (use `;`).

## Natural-language & photo logging (preferred)
Veronika will usually message food in plain language ("had a Billa protein sandwich and 2 scoops of protein") or send a photo of a meal. Steps for a Claude session with repo write access:
1. Identify each food. Check `foods.md` first for known items and their macro estimates — reuse those numbers for consistency. For "2 scoops of protein" with no brand, use her default from foods.md.
2. For a photo, estimate portion and macros from what's visible; note it's a photo estimate.
3. Running daily tally — she messages food multiple times a day. If today's row already exists in `log.csv`, ADD the new food's calories and protein to the existing totals (don't overwrite, don't add a duplicate row) and append the new items to the notes list. If today has no row yet, create it. Weight is set once from the morning weigh-in; later food messages leave weight unchanged.
4. Add any new food to `foods.md` with its estimate so it's consistent next time.
5. Commit + push. Reply terse: weight, 7-day avg, target for today, gap, plus calories & protein so far vs targets (1800 kcal / 130 g).

## Goal context
- Start 81.25 kg (2026-07-20) → target 73.1 kg by 2026-11-20 (~0.47 kg/week).
- Intake target ~1800 kcal/day, protein ~130 g/day.
- Target weight for any date = linear line from 81.25 kg (2026-07-20) to 73.12 kg (2026-11-20).

## Calorie estimation
If describing food instead of a number, estimate kcal from typical values and put the number in the calories column.
