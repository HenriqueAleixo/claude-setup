"""Triagem das conversas de prospecção: quem respondeu e espera ele, quem sumiu, o que tem rascunho.

Uso:
    triagem.py [--dias 30] [--cobrar 4] [--todos]

Considera toda conversa dos últimos N dias em que ele mandou e-mail para fora
(exceto domínios internos: TrueIoT, Curto, Baú). Classifica pela ÚLTIMA mensagem:
  RESPONDER  - a última é do contato e não há rascunho na conversa
  DEVOLVIDO  - a última é aviso de falha de entrega (endereço inválido)
  RASCUNHO   - existe rascunho dele não enviado na conversa
  COBRAR     - o contato já respondeu antes, a última é dele e faz >= --cobrar dias
  AGUARDANDO - a última é dele e ainda não deu o prazo de cobrança
  SEM_RESPOSTA - o contato nunca respondeu (só lista com --todos; senão conta)
"""
import argparse
import re
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime

import _comum as c

ap = argparse.ArgumentParser()
ap.add_argument("--dias", type=int, default=30)
ap.add_argument("--cobrar", type=int, default=4)
ap.add_argument("--todos", action="store_true")
a = ap.parse_args()

g = c.gmail()
internos = " ".join(f"-to:{d}" for d in c.DOMINIOS_INTERNOS)
q = f"in:sent newer_than:{a.dias}d {internos}"

ids, token = [], None
while True:
    r = g.users().threads().list(userId="me", q=q, maxResults=500, pageToken=token).execute()
    ids += [t["id"] for t in r.get("threads", [])]
    token = r.get("nextPageToken")
    if not token:
        break


def h(msg, nome):
    return next((x["value"] for x in msg["payload"].get("headers", []) if x["name"].lower() == nome.lower()), "")


def meu(msg):
    return parseaddr(h(msg, "From"))[1].lower() == c.EU


agora = datetime.now(timezone.utc)
grupos = defaultdict(list)
for tid in ids:
    t = g.users().threads().get(userId="me", id=tid, format="metadata",
                                metadataHeaders=["From", "To", "Subject", "Date"]).execute()
    msgs = t["messages"]
    rasc = [m for m in msgs if "DRAFT" in m.get("labelIds", []) and "TRASH" not in m.get("labelIds", [])]
    reais = [m for m in msgs if "DRAFT" not in m.get("labelIds", [])]
    if not reais:
        continue
    externos = [m for m in reais if not meu(m)]
    # contato = destinatário do meu primeiro e-mail ou remetente externo
    contato = (h(externos[-1], "From") if externos
               else h(next(m for m in reais if meu(m)), "To"))
    if any(d in contato.lower() for d in c.DOMINIOS_INTERNOS):
        continue
    ultima = reais[-1]
    quando = parsedate_to_datetime(h(ultima, "Date"))
    dias = (agora - quando).days
    assunto = re.sub(r"^((re|res|fwd|enc|fw):\s*)+", "", h(reais[0], "Subject"), flags=re.I)
    linha = (f"{quando:%d/%m} ({dias}d) | {parseaddr(contato)[0] or parseaddr(contato)[1]} "
             f"<{parseaddr(contato)[1]}> | {assunto} | ultima={ultima['id']}")
    if not meu(ultima) and re.search(r"mailer-daemon|postmaster|mail delivery", h(ultima, "From"), re.I):
        grupos["DEVOLVIDO"].append(linha)
    elif rasc:
        grupos["RASCUNHO"].append(linha + f" | rascunho_msg={rasc[-1]['id']}")
    elif not meu(ultima):
        grupos["RESPONDER"].append(linha)
    elif externos:
        grupos["COBRAR" if dias >= a.cobrar else "AGUARDANDO"].append(linha)
    else:
        grupos["SEM_RESPOSTA"].append(linha)

for k in ("RESPONDER", "DEVOLVIDO", "RASCUNHO", "COBRAR", "AGUARDANDO", "SEM_RESPOSTA"):
    itens = grupos.get(k, [])
    print(f"== {k} ({len(itens)}) ==")
    if k == "SEM_RESPOSTA" and not a.todos:
        continue
    for x in itens:
        print(x)
