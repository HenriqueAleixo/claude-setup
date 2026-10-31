"""Cria rascunhos (NUNCA envia) com a assinatura do Gmail.

Uso:
    rascunho.py arquivo.json

arquivo.json = um objeto ou uma lista de objetos:
    {
      "reply_to": "<msg_id>",          # opcional: responde na mesma conversa (to/subject vêm dela)
      "to": "Fulano <f@x.com>",        # obrigatório se não houver reply_to
      "cc": "Ciclano <c@x.com>",       # opcional
      "subject": "Assunto",            # obrigatório se não houver reply_to
      "paras": ["Saudação,", "Parágrafo...", "• item 1\n• item 2", "Atenciosamente,"],
      "anexos": ["~/caminho/arquivo.pdf"]  # opcional: anexos (tipo pelo nome do arquivo)
    }
O último parágrafo deve ser "Atenciosamente," (a assinatura não tem saudação).
"""
import base64
import html
import json
import mimetypes
import os
import sys
from email.message import EmailMessage

import _comum as c


def p_html(t: str) -> str:
    return f'<div>{html.escape(t).replace(chr(10), "<br>")}</div><div><br></div>'


def citacao(msg_id: str) -> str:
    """Mensagem anterior citada como o Gmail faz numa resposta (gmail_quote)."""
    m = c.gmail().users().messages().get(userId="me", id=msg_id, format="full").execute()
    hdr = {h["name"].lower(): h["value"] for h in m["payload"]["headers"]}

    def achar(p, tipo):
        if p.get("mimeType") == tipo and p["body"].get("data"):
            return base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", "replace")
        for q in p.get("parts", []):
            r = achar(q, tipo)
            if r:
                return r

    ant = achar(m["payload"], "text/html")
    if not ant:
        ant = html.escape(achar(m["payload"], "text/plain") or "").replace("\n", "<br>")
    cab = html.escape(f'Em {hdr.get("date", "")}, {hdr.get("from", "")} escreveu:')
    return (f'<br><div class="gmail_quote gmail_quote_container"><div dir="ltr" class="gmail_attr">{cab}<br></div>'
            f'<blockquote class="gmail_quote" style="margin:0px 0px 0px 0.8ex;border-left:1px solid '
            f'rgb(204,204,204);padding-left:1ex">{ant}</blockquote></div>')


def main(caminho: str) -> None:
    dados = json.load(open(caminho))
    itens = dados if isinstance(dados, list) else [dados]
    sig = c.assinatura()
    svc = c.compose()

    for r in itens:
        m = EmailMessage()
        thread = None
        if r.get("reply_to"):
            ctx = c.server._reply_context(r["reply_to"])
            m["To"] = r.get("to") or ctx["to"]
            m["Subject"] = r.get("subject") or ctx["subject"]
            m["In-Reply-To"] = ctx["message_id"]
            m["References"] = (ctx["references"] + " " + ctx["message_id"]).strip()
            thread = ctx["thread_id"]
        else:
            m["To"] = r["to"]
            m["Subject"] = r["subject"]
        if r.get("cc"):
            m["Cc"] = r["cc"]

        # Mesma estrutura que o compose do Gmail gera (copiada de um e-mail enviado por ele):
        # corpo em <div>, <div><br></div>, assinatura com class+data-smartmail e, em resposta,
        # a mensagem anterior num gmail_quote. Sem isso o Gmail esconde a assinatura como
        # "conteúdo repetido" (•••) ao abrir o rascunho (21/10, NCC).
        corpo = "".join(p_html(t) for t in r["paras"])
        htm = (f'<div dir="ltr">{corpo}<div><br></div><div><div dir="ltr" class="gmail_signature" '
               f'data-smartmail="gmail_signature">{sig}</div></div></div>')
        if r.get("reply_to"):
            htm += citacao(r["reply_to"])
        m.set_content("\n\n".join(r["paras"]) + "\n\nHenrique Aleixo\nTrueIoT")
        m.add_alternative(htm, subtype="html")
        for caminho_anexo in r.get("anexos", []):
            caminho_anexo = os.path.expanduser(caminho_anexo)
            tipo = mimetypes.guess_type(caminho_anexo)[0] or "application/octet-stream"
            with open(caminho_anexo, "rb") as f:
                m.add_attachment(f.read(), maintype=tipo.split("/")[0], subtype=tipo.split("/")[1],
                                 filename=os.path.basename(caminho_anexo))

        msg = {"raw": base64.urlsafe_b64encode(m.as_bytes()).decode()}
        if thread:
            msg["threadId"] = thread
        d = svc.users().drafts().create(userId="me", body={"message": msg}).execute()
        print(f"RASCUNHO {d['id']} | para {m['To']} | cc {m['Cc'] or '-'} | {m['Subject']}")


if __name__ == "__main__":
    main(sys.argv[1])
