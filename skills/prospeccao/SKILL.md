---
name: prospeccao
description: Opera a prospecção de clientes da TrueIoT pelo Gmail e pela Agenda dele — triagem da caixa (quem respondeu, quem sumiu, e-mail devolvido), rascunho de resposta/follow-up/primeiro contato com a assinatura certa, proposta de horário e criação da reunião com Google Meet e convite. Só cria RASCUNHO, nunca envia. Triggers - ve meus emails de prospecção, quem respondeu, quem eu tenho que cobrar, responde o fulano, faz um rascunho pra, marca a reunião com, cria o link do meet, manda o convite, follow-up, prospecção.
---

# Prospecção (Gmail + Agenda da TrueIoT)

Conta: `henrique.aleixo@trueiot.com.br`. Leitura pelo MCP `gmail` (`search_emails`, `read_email`, `list_drafts`, `delete_draft`).
Tudo que **escreve** passa pelos scripts desta skill, com o venv do gmail-mcp:

```
uv --directory ~/Documentos/projetos/gmail-mcp run python ~/.claude/skills/prospeccao/scripts/<script>.py ...
```

| Script | Faz |
|---|---|
| `triagem.py [--dias 30] [--cobrar 4] [--todos]` | Classifica as conversas em que ele escreveu para fora: RESPONDER, DEVOLVIDO, RASCUNHO, COBRAR, AGUARDANDO, SEM_RESPOSTA |
| `agenda.py [--de AAAA-MM-DD] [--dias 7]` | Agenda da semana + blocos livres de 1 h (9–12h, 14–17h, folga de 15 min) |
| `rascunho.py arquivo.json` | Cria rascunho(s) com a assinatura do Gmail; resposta na mesma conversa via `reply_to` |
| `reuniao.py --titulo --inicio --min --convidados [--descricao]` | Cria o evento com Meet e manda o convite (o Google envia o e-mail com Sim/Não) |

Escreva o JSON do `rascunho.py` no scratchpad da sessão.

## Regras que não se negociam

1. **Só rascunho.** Nunca `drafts.send` / `messages.send`. Ele lê e envia pelo Gmail. Mostre o texto e o destinatário no chat.
2. **Assinatura = a do Gmail, literal** (o `rascunho.py` já faz). Nunca embutir o logo como imagem/cid: o Gmail converte em anexo e a assinatura quebra. Nunca usar `create_draft`/`update_draft` do MCP para e-mail que ele vai mandar: saem sem assinatura ou a apagam.
3. **Rascunho entregue é congelado.** Para mudar: criar um novo, apagar o antigo (`delete_draft`) e avisar para fechar a janela do antigo no Gmail sem salvar.
4. **Reunião só por vídeo.** Nunca oferecer presencial ou visita. Se o contato pedir, perguntar a ele antes.
5. **A TrueIoT faz parte da Curto Circuito** (braço de engenharia). Nunca "com a Curto", "via Curto", "parceria com a Curto". Não dizer "fabricamos a placa aqui": a placa e o SMD vêm da China; em Guarulhos é montagem final, gravação e teste.
6. **Não citar cliente** nem dados de outro contato sem ele pedir.
7. **Convite pela agenda dele:** só pelo `reuniao.py`. O conector claude.ai Calendar é da Bruna e o Gmail do claude.ai é do Gabriel — não usar.

## Fluxos

### "Vê meus e-mails" / "quem respondeu" / "quem eu tenho que cobrar"
1. Rode `triagem.py`. Para cada item de RESPONDER e COBRAR, leia a última mensagem (`read_email`) antes de julgar.
2. Descarte o que não é prospecção (boleto, JLCPCB, Baú, cotação de venda) e o que já está resolvido (ex.: "ok, até lá" depois de convite recebido).
3. DEVOLVIDO = endereço inválido: listar e sugerir procurar outro contato da empresa.
4. Entregue em blocos curtos: **responder agora**, **cobrar**, **aguardando**, **rascunhos parados** (com a data), **reuniões marcadas** (`agenda.py`). Termine oferecendo os rascunhos.

### Rascunho de resposta / follow-up
- Responda na mesma conversa: `reply_to` = id da última mensagem da conversa (do contato ou dele).
- Tom: técnico, direto, cordial, 1ª pessoa dele ("Henrique Aleixo, engenheiro da TrueIoT"). Parágrafos curtos. Sem jargão de vendas.
- Último parágrafo sempre `"Atenciosamente,"` (a assinatura vem depois).
- **Follow-up/cobrança NÃO propõe reunião nem horário** (pedido dele, 16/10): 1 frase retomando o assunto + 1 pergunta curta ("Já tiveram algum retorno?", "Conseguiram verificar...?"). Nada de oferecer conversa.
- **Agradecimento a quem recusou: não fazer** sem ele pedir (ele costuma já ter agradecido por outro canal).
- **Só quando o contato pediu reunião**, proponha 2 horários fechados tirados do `agenda.py` (ex.: "quarta (21/10), às 14h; ou quinta (22/10), às 10h") e "se nenhum servir, me indiquem outro". Não pergunte "qual dia fica bom" em aberto: o contato some (caso Cermc). Quando ele tiver um link de agendamento (Cal.com/Calendly), use o link no lugar.

### Contato confirmou o horário
1. `reuniao.py` com título `"TrueIoT e <Empresa>: <tema>"`, 45 min, convidados = quem está na conversa (incluindo os cc).
2. O convite do Google já vai com o Meet e o Sim/Não. O rascunho de resposta na conversa é opcional: ofereça um curto com o link.
3. Confirmação de recebimento: o convidado aparece como `needsAction` até responder; aviso de falha de entrega na caixa = endereço errado.

### Depois de qualquer mudança
Atualize a memória `project_reunioes_prospeccao_out2026.md` (ou a da campanha correspondente) com o que foi marcado ou rascunhado e a data.
