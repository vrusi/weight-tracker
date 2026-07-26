#!/usr/bin/env python3
"""Upsert a morning weight and/or active energy into log.csv (default date: today, Europe/Bratislava).

Reads from env:
  PAYLOAD : JSON like {"weight": 79.95, "active": 615, "date": "2026-07-21"}
            every key optional except that at least one of weight/active must be present
  WEIGHT  : fallback plain weight (used by workflow_dispatch)
  ACTIVE  : fallback plain active energy in kcal
  DATE    : fallback plain date

Updates only the columns it was given, so food logged by hand is never clobbered.
CSV columns:
  date,weight_kg,calories,protein_g,steps,active_kcal,notes
"""
import json, os, sys, datetime

CSV = "log.csv"
COLS = 7
I_WEIGHT, I_ACTIVE, I_NOTES = 1, 5, 6

payload = {}
raw = os.environ.get("PAYLOAD", "").strip()
if raw and raw not in ("null", "{}"):
    try:
        payload = json.loads(raw) or {}
    except json.JSONDecodeError:
        payload = {}
for env_key, key in (("WEIGHT", "weight"), ("ACTIVE", "active"), ("DATE", "date")):
    if os.environ.get(env_key):
        payload[key] = os.environ[env_key]


def num(key, ndigits):
    """Parse a numeric field, returning None when absent or unparseable."""
    v = payload.get(key)
    if v in (None, ""):
        return None
    try:
        return round(float(v), ndigits)
    except (TypeError, ValueError):
        print(f"ignoring un-numeric {key}: {v!r}")
        return None


weight = num("weight", 2)
active = num("active", 0)

if weight is None and active is None:
    print("no weight or active energy provided; nothing to do")
    sys.exit(0)

date = payload.get("date")
if not date:
    try:
        import zoneinfo
        now = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Bratislava"))
    except Exception:
        now = datetime.datetime.now(datetime.timezone.utc)
    date = now.strftime("%Y-%m-%d")

with open(CSV) as f:
    lines = f.read().splitlines()

header, rows = lines[0], [r for r in lines[1:] if r.strip()]

found = False
for i, line in enumerate(rows):
    # maxsplit keeps any commas inside the notes column intact
    cols = line.split(",", COLS - 1)
    if cols[0].strip() != date:
        continue
    while len(cols) < COLS:
        cols.append("")
    if weight is not None:
        cols[I_WEIGHT] = f"{weight:g}"
    if active is not None:
        cols[I_ACTIVE] = f"{active:g}"
    rows[i] = ",".join(cols)
    found = True
    break

if not found:
    new = [""] * COLS
    new[0] = date
    if weight is not None:
        new[I_WEIGHT] = f"{weight:g}"
    if active is not None:
        new[I_ACTIVE] = f"{active:g}"
    new[I_NOTES] = "via Apple Health"
    rows.append(",".join(new))

with open(CSV, "w") as f:
    f.write("\n".join([header] + rows) + "\n")

parts = []
if weight is not None:
    parts.append(f"{weight} kg")
if active is not None:
    parts.append(f"{active:g} active kcal")
print(f"logged {' + '.join(parts)} for {date} (updated existing row: {found})")
