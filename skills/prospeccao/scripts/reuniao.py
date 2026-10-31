"""Cria a reunião na agenda dele com Google Meet e manda o convite aos convidados.

Uso:
    reuniao.py --titulo "TrueIoT e Cermc: telemetria de medição" \
               --inicio 2026-10-21T14:00 --min 45 \
               --convidados "cermc@cermc.com.br,Fulano <f@x.com>" \
               [--descricao "Apresentação do medidor..."]
"""
import argparse
import re
import uuid
from datetime import datetime, timedelta

import _comum as c


def convidado(s: str) -> dict:
    s = s.strip()
    m = re.match(r"^(.*?)\s*<([^>]+)>$", s)
    return {"email": m.group(2), "displayName": m.group(1).strip('" ')} if m else {"email": s}


ap = argparse.ArgumentParser()
ap.add_argument("--titulo", required=True)
ap.add_argument("--inicio", required=True, help="AAAA-MM-DDTHH:MM, horário de Brasília")
ap.add_argument("--min", type=int, default=45)
ap.add_argument("--convidados", required=True, help="separados por vírgula")
ap.add_argument("--descricao", default="")
a = ap.parse_args()

ini = datetime.fromisoformat(a.inicio)
fim = ini + timedelta(minutes=a.min)
evento = {
    "summary": a.titulo,
    "description": a.descricao,
    "start": {"dateTime": ini.isoformat(), "timeZone": c.TZ},
    "end": {"dateTime": fim.isoformat(), "timeZone": c.TZ},
    "attendees": [convidado(x) for x in a.convidados.split(",") if x.strip()],
    "conferenceData": {"createRequest": {"requestId": str(uuid.uuid4()),
                                         "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
}
e = c.agenda().events().insert(calendarId="primary", body=evento,
                               conferenceDataVersion=1, sendUpdates="all").execute()
print("EVENTO", e["id"], e.get("htmlLink"))
print("MEET", e.get("hangoutLink"))
for x in e.get("attendees", []):
    print("CONVIDADO", x["email"], x.get("responseStatus"))
