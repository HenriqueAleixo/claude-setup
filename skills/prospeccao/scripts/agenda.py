"""Mostra a agenda dele e os horários livres para propor reunião.

Uso:
    agenda.py [--dias 7] [--de 2026-10-19]

Livre = dia útil, blocos de 1 h entre 9h–12h e 14h–17h sem conflito
(com 15 min de folga antes e depois das reuniões existentes).
"""
import argparse
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import _comum as c

ap = argparse.ArgumentParser()
ap.add_argument("--dias", type=int, default=7)
ap.add_argument("--de", default="")
a = ap.parse_args()

tz = ZoneInfo(c.TZ)
d0 = date.fromisoformat(a.de) if a.de else date.today() + timedelta(days=1)
t0 = datetime.combine(d0, time(0), tz)
t1 = t0 + timedelta(days=a.dias)

itens = c.agenda().events().list(calendarId="primary", timeMin=t0.isoformat(), timeMax=t1.isoformat(),
                                 singleEvents=True, orderBy="startTime").execute().get("items", [])
ocupado = []
print("== AGENDA ==")
for e in itens:
    s, f = e["start"].get("dateTime"), e["end"].get("dateTime")
    if not s:  # dia inteiro
        print(f"{e['start']['date']} (dia inteiro) {e.get('summary')}")
        continue
    s, f = datetime.fromisoformat(s), datetime.fromisoformat(f)
    ocupado.append((s - timedelta(minutes=15), f + timedelta(minutes=15)))
    print(f"{s:%a %d/%m %H:%M}–{f:%H:%M} {e.get('summary')}")

print("== LIVRES (1 h) ==")
for n in range(a.dias):
    d = d0 + timedelta(days=n)
    if d.weekday() >= 5:
        continue
    livres = []
    for h in (9, 10, 11, 14, 15, 16):
        s = datetime.combine(d, time(h), tz)
        f = s + timedelta(hours=1)
        if not any(s < of and f > os_ for os_, of in ocupado):
            livres.append(f"{h}h")
    print(f"{d:%a %d/%m}: {', '.join(livres) or '—'}")
