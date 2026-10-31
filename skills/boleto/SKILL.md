---
name: boleto
description: "Controle de boletos e guias do Henrique (TrueIoT/Curto/pessoal): registrar que pagou, cadastrar conta a pagar, conferir se um boleto já foi pago antes de pagar de novo, listar o que está em aberto ou vencendo. Triggers: paguei o boleto, já paguei, dá baixa, esse boleto já foi pago?, posso pagar esse?, cadastra esse boleto, o que tenho pra pagar, o que vence hoje, contas em aberto, guia da Prada, /boleto."
user-invocable: true
---

# boleto: controle de contas pagas

CLI: `~/Documentos/projetos/contas-pagar/boletos.py` (SQLite `boletos.db` na mesma pasta).
Rode sempre com o caminho completo. Ele é desatento ("sou moscão"): o objetivo é
**nunca pagar duas vezes** e **não deixar vencer**.

## Comandos

```
boletos.py add "Parcelamento municipal 02/24" --valor 123.45 --venc 19/10/2026 \
    --codigo "8xxxx..." --empresa TrueIoT --origem "e-mail Prada 16/10"
boletos.py pago <id | código | trecho da descrição> [--data dd/mm/aaaa] [--como Inter]
boletos.py checar <código | trecho>      # já foi pago?
boletos.py listar [--abertos]            # marca VENCIDO / VENCE HOJE
boletos.py desfazer <id>                 # baixa errada
```

## Como agir

- **"Paguei X"** → `pago "X"`. Data padrão = hoje; pergunte só se ele disser outra.
  Se der "mais de um em aberto", mostre a lista e pergunte qual. Se o boleto não
  estava cadastrado, registre com `pago <código> --descricao ... --valor ...`
  ou, sem código, `add` seguido de `pago <id>`.
- **"Posso pagar esse?" / colou uma linha digitável** → `checar` primeiro.
  Se constar PAGO, diga com destaque para **não pagar**.
- Código começando com **8** = guia de arrecadação (imposto, prefeitura, DAS):
  o banco **aceita pagar duas vezes**. Avise isso ao cadastrar.
- **Ao ler e-mails** e encontrar guia/boleto a pagar (Prada, fornecedor, concessionária),
  ofereça cadastrar como em aberto. O Gmail MCP não baixa anexo: cadastre com o que
  estiver no corpo (valor, vencimento) e peça a linha digitável se ele tiver.
- Empresa: TrueIoT por padrão; `--empresa Curto` ou `--empresa Pessoal` quando for o caso.
- Nunca apague linha do banco; para corrigir use `desfazer` ou um novo `add`.
