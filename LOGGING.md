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
`date,weight_kg,calories,steps,notes` — date is `YYYY-MM-DD`. Calories/steps/notes optional; avoid commas inside notes (use `;`).

## Goal context
- Start 81.25 kg (2026-07-20) → target 73.1 kg by 2026-11-20 (~0.47 kg/week).
- Intake target ~1800 kcal/day, protein ~130 g/day.
- Target weight for any date = linear line from 81.25 kg (2026-07-20) to 73.12 kg (2026-11-20).

## Calorie estimation
If describing food instead of a number, estimate kcal from typical values and put the number in the calories column.
