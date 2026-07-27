#!/usr/bin/env python3
"""Upsert weight, active energy and/or sleep into log.csv (default date: today, Europe/Bratislava).

Reads from env:
  PAYLOAD : JSON like {"weight": 79.95, "active": 615, "sleep": 7.4, "date": "2026-07-21"}
            every key optional, but at least one of weight/active/sleep must be present
  WEIGHT  : fallback plain weight in kg          (used by workflow_dispatch)
  ACTIVE  : fallback plain active energy in kcal
  SLEEP   : fallback plain sleep in hours
  DATE    : fallback plain date

Updates only the columns it was given, so food logged by hand is never clobbered.
Sleep belongs to the morning you wake up, so send it with the morning weigh-in.
CSV columns:
  date,weight_kg,calories,protein_g,steps,active_kcal,sleep_h,notes
"""
import json, os, re, sys, datetime

CSV = "log.csv"
COLS = 8
I_WEIGHT, I_ACTIVE, I_SLEEP, I_NOTES = 1, 5, 6, 7

payload = {}
raw = os.environ.get("PAYLOAD", "").strip()
if raw and raw not in ("null", "{}"):
    try:
        payload = json.loads(raw) or {}
    except json.JSONDecodeError:
        payload = {}
for env_key, key in (("WEIGHT", "weight"), ("ACTIVE", "active"),
                     ("SLEEP", "sleep"), ("DATE", "date")):
    if os.environ.get(env_key):
        payload[key] = os.environ[env_key]


def num(key, ndigits):
    """Parse a numeric field, returning None when absent or unparseable."""
    v = payload.get(key)
    if v in (None, ""):
        return None
    try:
        return round(float(str(v).replace(",", ".")), ndigits)
    except (TypeError, ValueError):
        print(f"ignoring un-numeric {key}: {v!r}")
        return None


def parse_sleep(v):
    """Hours from whatever the sleep shortcut sends.

    Accepts a bare number (hours, or minutes if over 24), a clock string like
    "7:52", or the phrasing Health shortcuts print — "7 hours 52 minutes",
    "7h 52m", "Total Time Asleep: 7 hours 52 minutes".
    """
    if v in (None, ""):
        return None
    s = str(v).strip().replace(",", ".")

    try:                                    # plain number
        return float(s)
    except ValueError:
        pass

    m = re.fullmatch(r"(\d+):([0-5]\d)", s)  # 7:52
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60

    # "7 hours 52 minutes" / "7h 52m", possibly with a label in front
    h = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)(?![a-z])", s, re.I)
    mi = re.search(r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|m)(?![a-z])", s, re.I)
    if h or mi:
        return (float(h.group(1)) if h else 0) + (float(mi.group(1)) if mi else 0) / 60

    print(f"could not read sleep from {v!r}")
    return None


weight = num("weight", 2)
active = num("active", 0)
sleep = parse_sleep(payload.get("sleep"))
if sleep is not None:
    sleep = round(sleep, 2)

# A failed Health query yields 0, which as a weight would silently destroy a real
# weigh-in already sitting in the row. Only accept a plausible human weight.
if weight is not None and not (30 <= weight <= 300):
    print(f"weight of {weight} is not plausible; not recording it")
    weight = None

# An empty Health query sums to 0. Nobody burns zero active calories or sleeps zero
# hours, so treat 0 as "no data" rather than writing a misleading value into the log.
if active == 0:
    print("active energy came back as 0 (empty Health query?); not recording it")
    active = None
if sleep == 0:
    print("sleep came back as 0 (empty Health query?); not recording it")
    sleep = None

# Sleep arriving in minutes is an easy mistake to make in Shortcuts; convert rather
# than log a night of "450 hours".
if sleep is not None and sleep > 24:
    print(f"sleep of {sleep} looks like minutes; converting to hours")
    sleep = round(sleep / 60, 2)

# Under an hour is not a night's sleep, it is a mangled value — a Number-typed JSON
# field coercing "27 Jul 2026 at 01:38..." down to 27, say. Refuse rather than record
# something that looks plausible enough to go unnoticed.
if sleep is not None and sleep < 1:
    print(f"sleep of {sleep} h is not a plausible night; not recording it")
    sleep = None

if weight is None and active is None and sleep is None:
    print("no weight, active energy or sleep provided; nothing to do")
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

updates = ((I_WEIGHT, weight, "g"), (I_ACTIVE, active, "g"), (I_SLEEP, sleep, ".2f"))

found = False
for i, line in enumerate(rows):
    # maxsplit keeps any commas inside the notes column intact
    cols = line.split(",", COLS - 1)
    if cols[0].strip() != date:
        continue
    while len(cols) < COLS:
        cols.append("")
    for idx, val, fmt in updates:
        if val is not None:
            cols[idx] = format(val, fmt).rstrip("0").rstrip(".") if fmt == ".2f" else format(val, fmt)
    rows[i] = ",".join(cols)
    found = True
    break

if not found:
    new = [""] * COLS
    new[0] = date
    for idx, val, fmt in updates:
        if val is not None:
            new[idx] = format(val, fmt).rstrip("0").rstrip(".") if fmt == ".2f" else format(val, fmt)
    new[I_NOTES] = "via Apple Health"
    rows.append(",".join(new))

with open(CSV, "w") as f:
    f.write("\n".join([header] + rows) + "\n")

parts = []
if weight is not None:
    parts.append(f"{weight} kg")
if active is not None:
    parts.append(f"{active:g} active kcal")
if sleep is not None:
    parts.append(f"{sleep:g} h sleep")
print(f"logged {' + '.join(parts)} for {date} (updated existing row: {found})")
