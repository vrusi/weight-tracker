# Context brief — read this first

Handoff notes for a Claude session starting with no memory of previous ones.
`LOGGING.md` covers *how to log*; this file covers *everything else you need to not get it wrong*.

Read order: **this file → `LOGGING.md` → `foods.md`**.

---

## 1. Who and what

Veronika, cutting from **81.25 kg (2026-07-20) → 73.12 kg (2026-11-20)**, about −0.47 kg/week.
Target weight for any date is the straight line between those two points.

Daily targets: **~1800 kcal** (see the energy model below — it moves with activity) and **130 g protein**.

Protein is the habitual miss. Calories usually land fine; protein regularly comes up short, and
alcohol is the main thing that crowds it out. Nudging toward protein is more useful than
nudging toward fewer calories.

## 2. Hard constraints — do not get these wrong

- **NO DAIRY.** Never suggest milk, cheese, yogurt, skyr, quark/tvaroh, cream, whey. Plant protein
  (tofu, tempeh, edamame, legumes, seitan, vegan powder) or fish/meat instead. She occasionally
  eats dairy anyway by choice — log it without comment, but never *recommend* it.
- **No very sweet desserts.** Sugary pastries and puddings make her feel unwell. Suggest fruit.
- **Collagen is not protein.** It is an incomplete protein (no tryptophan, low leucine). Log its
  calories, exclude it from the protein total, and say so in the notes.
- **Alcohol stays.** Don't push abstinence. Useful ranking: skinny bitch (vodka/soda/lime, ~90 kcal)
  < white wine (~120) < big beer (~215, and zero protein). Beer days are the real calorie leak.

## 3. How data gets in

```
Apple Health ──shortcut──► repository_dispatch ──► GitHub Action ──► log.csv ──► dashboard
   (weight, active energy)                    scripts/log_weight.py       index.html
```

- **`log.csv`** is the single source of truth. Columns:
  `date,weight_kg,calories,protein_g,steps,active_kcal,sleep_h,notes`
- **`index.html`** fetches it live on every page load. Never hardcode data into it.
- A pixel-art redesign (NES.css, vendored, no CDN) shipped and was reverted the same day — she
  didn't like the look. `index.html` is the original sage/pine design again. If pixel art comes
  up again, the git tag `design-classic` and commit `866035e` have the full NES.css build to
  restart from rather than redoing the framework plumbing.
- **GitHub Pages serves `main`.** Anything not on `main` is invisible to her.
- **`scripts/log_weight.py`** upserts by date and **only writes the columns it is given**, so an
  automated weight sync never clobbers hand-logged food. An `active` of `0` means an empty Health
  query and is ignored rather than recorded.

### Her automations

| Trigger | Sends |
|---|---|
| Morning | weight + last night's sleep |
| Strava opened | active energy |
| 22:30 daily | active energy (the day's final total) |

Sleep is filed against the **morning you wake up**, which is why it rides with the weigh-in
rather than the evening sync. Under 7 h matters here rather than being a nice-to-have: on a
deficit, short sleep shifts the loss from fat to lean mass (same total kilos, worse composition),
so a run of short nights is a real explanation for a stalled or muscle-heavy loss.

All three upsert the same row; last write wins. **They only ever touch the current day's row** —
once a date rolls over, its row is frozen and safe for you to correct by hand. Today's
`active_kcal`, by contrast, will be overwritten by the next sync, so don't hand-edit it.

## 4. The energy model (subtle — read carefully)

BMR uses Mifflin-St Jeor on the **7-day average weight** (female, 169 cm, 28 y).

```
baseline  = round10(BMR × 1.5 − 525)                        ≈ 1810 kcal at 80 kg
adjusted  = round10(BMR × 1.2 − 525 + 0.75 × active_kcal)
target    = max(baseline, adjusted)
```

Three things people get wrong here:

1. **The old flat 1800 already contained an activity multiplier (×1.5).** Subtracting workout
   calories on top of it double-counts. That's why the activity path drops the base to ×1.2.
2. **Only 75% of measured active energy is credited.** Watches overestimate burn, strength
   training worst of all. Eating back 100% is the classic way this fails.
3. **The target is floored at the baseline.** Activity accumulates through the day, so an early
   morning sync would otherwise compute a sedentary target and tell her she has nothing left.
   It only ever rises.

## 5. Working rules

- **Work on `main` only.** No feature branches — a previous one caused double-push and merge
  races for no benefit. (A stale `claude/weight-tracking-rh73xh` may still exist on the remote;
  it's merged and dead, ignore it.)
- **Always `git pull --rebase origin main` before pushing.** The weight bot pushes commits
  independently and you *will* collide otherwise.
- **Reply terse**, with one specific carve-out (added 2026-07-31): **score each logged meal.**
  Genuinely great choice (high protein, on-constraint, good calorie value) → say so and be happy
  about it, briefly. Not great (very sweet dessert, dairy, low protein for the calories) → be
  kind, not scolding — one gentle line, not a lecture. Alcohol → react exactly as normal (still
  log it, still give the numbers) but drop in one short, genuinely funny line like "cheers! have
  a good time" or "wish I could drink too" — it's there to make logging less of a chore, not to
  replace the numbers. Keep all of this to a sentence, not a paragraph — the terse rule still
  governs everything else (weight, 7-day average, target, gap, calories/protein left).
- **Verify UI changes in a browser**, don't just read the diff. Chromium and Playwright are
  installed; serve with `python3 -m http.server` and drive it headless.

## 6. Gotchas learned the hard way

**Scale noise.** Daily weight swings ±1 kg on water alone. Alcohol is a diuretic, so the morning
after drinking often reads *artificially low*, and the rebound a day later looks like a gain that
isn't real. Carbs refill glycogen, which binds ~3 g water per gram. She has asked more than once
"why did I gain" — the answer has always been water. Point her at the 7-day average.

**Creatine.** She takes 15 g/day for brain health (discovered 2026-07-30 she'd been dosing 15 g
all along, not the 30 g she'd intended — corrected here and in the 26 Jul log note). Still well
inside the range used in cognitive research and far above the 3–5 g muscle saturates at. Pulls
water into muscle and inflates scale weight — that's the mechanism working, not fat.

**Apple Health double-counting.** Summing raw Active Energy samples adds every source together,
while the Fitness Move ring deduplicates. With Strava and Heavy also writing, the sum read 1912
against a true 1169. Strava's Active Energy write was disabled on 2026-07-26. **The Move ring is
ground truth** — if a synced number looks far too high, that's the cause.

**Shortcuts JSON bodies.** A field left unbound in the JSON body builder silently serialises as
`0` — it does not error. Hours were lost to this. If `active` arrives as 0, the variable isn't
actually bound; the field must show a blue token, not a red type label.

**Reading the pipeline.** Workflow runs are at github.com/vrusi/weight-tracker/actions. The job log
prints the received `PAYLOAD`, which settles "did it send" versus "did it write" instantly.

## 7. State as of 2026-07-26

- Latest weigh-in **79.95 kg** (25 Jul); 26 Jul has food but no weight — she was away from her scale.
- 7-day average **80.0 kg**, roughly **1 kg under** the target line. On track.
- Activity tracking went live this day; 26 Jul is the first row with `active_kcal`.
- Volleyball is played with the watch off — it has to be added manually in Health
  (Browse → Activity → Workouts → Add Data) before the 22:30 sync, or written into a past row by hand.
  Roughly 200 kcal/h casual, 400 competitive indoor, 560 beach, at her weight.
