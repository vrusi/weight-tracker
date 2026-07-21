#!/usr/bin/env python3
"""Upsert a morning weight into log.csv for a given date (default: today, Europe/Bratislava).

Reads the weight/date from env:
  PAYLOAD : JSON like {"weight": 79.95, "date": "2026-07-21"}  (date optional)
  WEIGHT  : fallback plain weight (used by workflow_dispatch)
  DATE    : fallback plain date

Sets the weight column of today's row if it exists (preserving calories/protein/notes
already logged), otherwise appends a new row. CSV columns:
  date,weight_kg,calories,protein_g,steps,notes
"""
import json, os, sys, datetime

CSV = "log.csv"

payload = {}
raw = os.environ.get("PAYLOAD", "").strip()
if raw and raw not in ("null", "{}"):
    try:
        payload = json.loads(raw) or {}
    except json.JSONDecodeError:
        payload = {}
if os.environ.get("WEIGHT"):
    payload["weight"] = os.environ["WEIGHT"]
if os.environ.get("DATE"):
    payload["date"] = os.environ["DATE"]

if payload.get("weight") in (None, ""):
    print("no weight provided; nothing to do")
    sys.exit(0)

weight = round(float(payload["weight"]), 2)

date = payload.get("date")
if not date:
    try:
        import zoneinfo
        now = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Bratislava"))
    except Exception:
        now = datetime.datetime.utcnow()
    date = now.strftime("%Y-%m-%d")

with open(CSV) as f:
    lines = f.read().splitlines()

header, rows = lines[0], [r for r in lines[1:] if r.strip()]

found = False
for i, line in enumerate(rows):
    cols = line.split(",")
    if cols[0].strip() == date:
        while len(cols) < 6:
            cols.append("")
        cols[1] = f"{weight:g}"
        rows[i] = ",".join(cols)
        found = True
        break

if not found:
    rows.append(f"{date},{weight:g},,,,weight via Apple Health")

with open(CSV, "w") as f:
    f.write("\n".join([header] + rows) + "\n")

print(f"logged {weight} kg for {date} (updated existing row: {found})")
