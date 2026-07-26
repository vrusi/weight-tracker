# weight-tracker

**Starting a fresh Claude session? Read [`CONTEXT.md`](CONTEXT.md) first.**

Personal weight-loss tracker: 81.25 → 73.1 kg by 2026-11-20.

- `CONTEXT.md` — brief for a fresh Claude session: constraints, energy model, gotchas
- `LOGGING.md` — how to log an entry
- `foods.md` — known foods and their macro estimates
- `log.csv` — daily log (`date,weight_kg,calories,protein_g,steps,active_kcal,notes`)
- `index.html` — trend vs target dashboard, reads `log.csv` live (served via GitHub Pages)
- `scripts/log_weight.py` — upserts weight / active energy from the Apple Health shortcut
