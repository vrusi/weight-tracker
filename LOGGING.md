# How to log a weight entry

Any Claude session (phone or desktop) can update this tracker by following these steps against the `vrusi/weight-tracker` repo.

## Goal context
- Start: 81.25 kg on 2026-07-20. Target: 73.1 kg by 2026-11-20 (~0.47 kg/week).
- Intake target ~1800 kcal/day, protein ~130 g/day.
- Target weight for any date = linear line from 81.25 kg (2026-07-20) to 73.12 kg (2026-11-20).

## Files
- `log.csv` — one row per day. Columns: `date,weight_kg,calories,steps,notes` (date is YYYY-MM-DD).
- `index.html` — the dashboard. Near the bottom is a JS array `const DATA = [ ... ]`; each entry looks like `{ d: "2026-07-20", w: 81.25, cal: 1800, note: "" }`. The `cal` (calories) field is optional but include it whenever the user gives calories — the dashboard's "This week" panel averages it for intake adherence.

## Steps to log
1. Get today's date and the user's numbers (weight kg required; calories/steps/notes optional).
2. Append a row to `log.csv` for today. If a row for today already exists, update it instead of adding a duplicate.
3. Add a matching entry to the `DATA` array in `index.html` (or update today's entry if present). Keep it sorted by date.
4. Update the footer date in `index.html` (the `<footer>` text "Updated …") to today.
5. Commit and push both files. This auto-updates the live dashboard at https://vrusi.github.io/weight-tracker/ (GitHub Pages, ~1 min to rebuild).
6. Reply to the user with one line: current weight, 7-day rolling average, target weight for today, and the gap (avg − target). Keep it terse.

## Calorie estimation
If the user describes food instead of giving a number, estimate kcal and protein from typical values and note the estimate in the `notes` column.

## Tone
Terse and factual. No motivational filler. Only add a suggestion if the 7-day average is more than 1 kg above the target line.
