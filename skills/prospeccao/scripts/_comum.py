"""Base comum dos scripts da skill prospeccao: serviços do Gmail/Agenda e assinatura.

Rodar sempre com o venv do gmail-mcp:
    uv --directory ~/Documentos/projetos/gmail-mcp run python ~/.claude/skills/prospeccao/scripts/<script>.py ...
"""
import os
import sys
from pathlib import Path

GMAIL_MCP = Path.home() / "Documentos/projetos/gmail-mcp"
sys.path.insert(0, str(GMAIL_MCP))
import server  # noqa: E402

EU = server.IMPERSONATE  # henrique.aleixo@trueiot.com.br
TZ = "America/Sao_Paulo"

# domínios que não são prospecção (Baú, Curto, avisos)
DOMINIOS_INTERNOS = ("trueiot.com.br", "curtocircuito.com.br", "baudaeletronica.com.br")


def gmail():
    return server._svc()


def compose():
    return server._compose_svc()


def agenda():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        os.path.expanduser(server.SA_KEY),
        scopes=["https://www.googleapis.com/auth/calendar.events"],
    ).with_subject(EU)
    return build("calendar", "v3", credentials=creds)


def assinatura() -> str:
    """Assinatura do Gmail LITERAL (logo por URL, como o Gmail insere).
    Nunca embutir o logo via cid: o Gmail vira anexo e a assinatura quebra ao abrir o rascunho."""
    cfg = server._build_service(server.SA_KEY, EU, ["https://www.googleapis.com/auth/gmail.settings.basic"])
    return next(sa["signature"] for sa in cfg.users().settings().sendAs().list(userId="me").execute()["sendAs"]
                if sa.get("sendAsEmail") == EU and sa.get("signature"))
