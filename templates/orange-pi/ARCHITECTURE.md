# Arquitetura do host orangepi

Levantamento feito ao vivo no host em **2026-09-23** (`docker ps`, `docker network inspect`,
composes, nginx, cloudflared, `ss`, `systemctl`, `pm2`). Reflete o que está **rodando**, não o
que os repos dizem que deveria rodar. Ver [README.md](README.md) para acesso e hardware.

## 1. Visão geral

```
                         INTERNET                                        LAN 192.168.15.0/24
     ┌──────────────────────────────────────────────┐        ┌──────────────────────────────────┐
     │ radar.koracom.com.br   (Cloudflare Access)   │        │ https://curto.local          :443 │
     │ webhook-curto.koracom.com.br                 │        │ https://dedoduro.curto.local :443 │
     │ webhook-kora.koracom.com.br                  │        │ https://storage.curto.local  :443 │
     │ laptop-scorecard-paralegal.ngrok-free.dev    │        │ :8443 nextcloud   :9443 ml_curto  │
     └───────┬───────────────┬──────────────┬───────┘        └──────────────┬───────────────────┘
             │ koracom-      │ cdl-         │ kdl-cloudflared                │ global-nginx
             │ cloudflared   │ cloudflared  │ + kdl-ngrok (legado)           │ (server-infra)
             ▼               ▼              ▼                                ▼
  ┌──────────────────────────────── proxy-network 172.21/16 ──────────────────────────────────┐
  │ ccradar-frontend  ccradar-backend  mlcurto-frontend  nextcloud  panel-front  panel-api    │
  │ kdl-backend  cdl-backend  bdl-backend                                                     │
  └────┬───────────────────────┬──────────────────┬──────────────┬──────────────┬─────────────┘
       │ ccradar-internal      │ ml_curto_        │ nc-internal  │ jose-internal│ kdl/cdl/bdl-internal
       ▼                       ▼ app-network      ▼              ▼              ▼
  ccradar-postgres        ml_curto-db-1       nextcloud-db    (só panel)    kdl/cdl/bdl-postgres
  triage-agent            ml_curto-redis-1                                  kdl/cdl-webhook-gw
  email-agent             mlcurto-ads-agent                                 kdl/cdl-cloudflared
  ccradar-adminer         calculadora-api                                   kdl-ngrok, kdl-adminer
                          adminer-mlcurto

  Fora da proxy-network (só porta no host):  sirbcc-app :3000 (usa mongod DO HOST :27017)
                                             bau-evolution :8092 + bau-postgres + bau-redis (rede `bau`)
                                             ciport-postgres :5437  garantia-dev-postgres :5442  ccradar-dev-pg :5443
  Fora do Docker:  mongod, pm2(sirbcc, quebrado), curtolab-energy-simulator.service, cron ccradar-bot, adbd, rpcbind
```

**Princípio da malha:** cada stack tem sua rede interna (`<projeto>_<nome>-internal`) e só o
container que precisa ser alcançado de fora entra também na `proxy-network`, onde o `global-nginx`
e o `koracom-cloudflared` o encontram pelo nome do container (resolver Docker `127.0.0.11`).
Bancos e agentes nunca entram na `proxy-network`.

## 2. Entradas (edge)

### 2.1 LAN: `global-nginx` (stack `server-infra`, `/home/orangepi/server-infra`)

Certificado mkcert `curto.local+1.pem` (raiz em `nginx/html/rootCA.*`, com scripts de instalação
pra Windows na mesma pasta). Configs em `nginx/nginx.conf` + `nginx/conf.d/*.conf`.

| Entrada | Rota | Upstream (proxy-network) | Estado |
|---|---|---|---|
| `:80` (qualquer host) | `/` | `301 → https://$host/cc-radar/` | OK |
| `curto.local:443` | `/` | landing page estática (links cc-radar, dedoduro, storage) | OK |
| | `/cc-radar/` | `ccradar-frontend:80` | OK |
| | `/dedoduro/` | `mlcurto-frontend:80` | OK |
| | `/storage/` | `nextcloud:80` | OK |
| | `/wapp-bau/` | `panel-front:80` | OK |
| | `/kora-dl/` | `kdl-backend:8000` (strip do prefixo) | OK |
| | `/sirbcc` | `172.17.0.1:3000` (gateway do bridge → porta do host) | OK (307) |
| `dedoduro.curto.local:443` | `/` | `mlcurto-nginx:80` | **502** — container foi renomeado pra `mlcurto-frontend` |
| `storage.curto.local:443` | `/` | `nextcloud:80` | OK |
| `:8443` (por IP) | `/` | `nextcloud:80` | OK |
| `:9443` (por IP) | `/` | `mlcurto-nginx:80` | **502** — mesmo motivo |

### 2.2 Internet: túneis (nenhuma porta aberta no roteador)

| Container | Stack | Hostname público | Destino | Obs |
|---|---|---|---|---|
| `koracom-cloudflared` | `koracom-tunnel` | `radar.koracom.com.br` | `ccradar-frontend:80` | Cloudflare Access (Zero Trust) na frente; está na `proxy-network` |
| `cdl-cloudflared` | `kora-datalake` | `webhook-curto.koracom.com.br` | `cdl-webhook-gw:80` | túnel dedicado, só rede `cdl-internal` |
| `kdl-cloudflared` | `kora-datalake` | `webhook-kora.koracom.com.br` | `kdl-webhook-gw:80` | túnel dedicado, só rede `kdl-internal` |
| `kdl-ngrok` | `kora-datalake` | `laptop-scorecard-paralegal.ngrok-free.dev` | `kdl-webhook-gw:80` | **legado**, substituído pelo cloudflared, ainda rodando |

Os `*-webhook-gw` (nginx:alpine) são um filtro: só passam `/api/v1/bling/webhook/` e
`/api/v1/health` pro backend, resto é 404. O `bdl` tem gateway/ngrok declarados (profile `webhooks`)
mas **não sobe** — o Baú não recebe webhook do Bling hoje.

### 2.3 Portas publicadas direto no host

| Porta | Container / processo | Rede | Para quê |
|---|---|---|---|
| 22 | sshd | host | acesso |
| 80, 443, 8443, 9443 | `global-nginx` | proxy-network | edge LAN |
| 111 | rpcbind | host | sem uso conhecido |
| 3000 | `sirbcc-app` | `sirbcc_default` | app SIRBCC (também via nginx `/sirbcc`) |
| 5037 (localhost), **5555** | adbd | host | Android Debug Bridge — **5555 aberto na LAN** |
| 5432 | `ml_curto-db-1` | ml_curto_app-network | Postgres ML_Curto (dev local conecta aqui) |
| 5433 | `kdl-postgres` | kdl-internal | KDL (Kora Data Lake) |
| 5434 | `cdl-postgres` | cdl-internal | CDL (Curto Data Lake) |
| 5435 | `ccradar-postgres` | ccradar-internal | cc-radar |
| 5436 | `bdl-postgres` | bdl-internal | BDL (Baú Data Lake) |
| 5437 | `ciport-postgres` | bridge (avulso) | projeto ciport, volume `ciport-pgdata` |
| 5442 | `garantia-dev-postgres` | bridge (avulso) | dev do "garantia", volume anônimo |
| 5443 | `ccradar-dev-pg` | bridge (avulso) | dev do cc-radar, **sem volume e `restart=no`** |
| 6379 | `ml_curto-redis-1` | ml_curto_app-network | Redis ML_Curto |
| 8001 | `calculadora-api` | ml_curto_app-network | calculadora interna |
| 8090 | `adminer-mlcurto` | ml_curto_app-network | Adminer |
| 8091 | `ccradar-adminer` | ccradar-internal | Adminer |
| 8092 | `bau-evolution` | `bau` | Evolution API (WhatsApp) |
| 8096 | `kdl-adminer` | kdl-internal | Adminer |
| 27017 | mongod | host | Mongo do SIRBCC (fora do Docker) |

## 3. Stacks (compose project → diretório)

Todos com `restart: unless-stopped` salvo indicação. `WT` = carrega o label
`com.centurylinklabs.watchtower.enable=true` e é atualizado pelo `watchtower-orange`.

### server-infra — `/home/orangepi/server-infra`
- `global-nginx` (nginx:alpine). Binds: `nginx.conf`, `conf.d/`, `certs/`, `html/`.

### orange-infra — `/home/orangepi/orange-infra`
- `watchtower-orange` (containrrr/watchtower). Label-scoped, poll 120 s, cleanup. Monta
  `docker.sock` + `~/.docker/config.json` (auth ghcr). Hoje adota 12 containers:
  `ccradar-{backend,frontend,email-agent,triage-agent}`, `ml_curto-backend-1`, `mlcurto-frontend`,
  `mlcurto-ads-agent`, `panel-api`, `panel-front`, `kdl-backend`, `cdl-backend`, `bdl-backend`.

### koracom-tunnel — `/home/orangepi/koracom-tunnel`
- `koracom-cloudflared`. Config em `cloudflared/config.yml`.

### cc-radar — `/home/orangepi/cc-radar` (`docker-compose.prod.yml`)
| Container | Imagem | Redes | Obs |
|---|---|---|---|
| `ccradar-postgres` | postgres:16-alpine | internal | volume `cc-radar_ccradar-pgdata`, :5435 |
| `ccradar-backend` WT | ghcr…/ccradar-backend | internal + proxy | binds `data/`, `secrets/`, `wa-media/`, `suporte-fotos/`, `~/ccradar-bot/triggers` |
| `ccradar-frontend` WT | ghcr…/ccradar-frontend | internal + proxy | serve `/cc-radar/` e proxy do `/cc-radar/api/` |
| `ccradar-triage-agent` WT | ghcr…/ccradar-triage-agent | internal | monta `~/ccradar-home/.claude` (credencial Claude Code do agente) |
| `ccradar-email-agent` WT | ghcr…/ccradar-email-agent | internal | monta `~/ccradar-bot/service-account.json` (Gmail) |
| `ccradar-adminer` | adminer | internal | avulso (`docker run`), :8091 |
| `ccradar-dev-pg` | postgres:16-alpine | bridge | avulso, `restart=no`, sem volume, :5443 |

Declarados no compose mas **não rodando**: `ccradar-proposal-agent-{email,whatsapp}` (profile
`desativado`), `ccradar-bling-pdf-agent` (nunca subiu), `ccradar-watchtower` (substituído pelo
`watchtower-orange`; bloco ainda está no compose do host).

Fora do Docker: cron `* * * * * ~/cc-radar/scripts/run_bot_cron.sh` (janela :00/:30, `ENABLED=true`
em `~/ccradar-bot/.env`) chama `docker compose run --rm ccradar-bot` — **serviço não existe no
compose**, falha com `no such service: ccradar-bot` a cada execução (log em `~/ccradar-bot/logs/bot.log`, 65 mil linhas).

### ml_curto — `/home/orangepi/ML_Curto` (`docker-compose.yml` + `override.yml`)
| Container | Imagem | Redes | Obs |
|---|---|---|---|
| `mlcurto-frontend` WT | ghcr…/ml-curto-nginx | app-network + proxy | serviço `nginx`; serve `/dedoduro/` |
| `ml_curto-backend-1` WT | ghcr…/ml-curto-backend | app-network | binds `.ml_token.json`, `.ml_cookies.json`; scheduler roda aqui |
| `ml_curto-db-1` | postgres:16-alpine | app-network | volume `ml_curto_postgres_data`, :5432 |
| `ml_curto-redis-1` | redis:7-alpine | app-network | volume anônimo, :6379 |
| `mlcurto-ads-agent` WT | ghcr…/ml-curto-ads-agent | app-network | override; monta `~/.claude` e `~/.claude.json` **do usuário orangepi** |
| `calculadora-api` | build local | app-network | compose próprio em `~/calculadora-api`, :8001 |
| `adminer-mlcurto` | adminer | app-network | avulso, :8090 |

Existe uma cópia antiga em `/home/orangepi/projetos/ML_Curto` (4 composes) sem nenhum container
associado — lixo.

### kora-datalake — `/home/orangepi/kora-datalake` (3 composes, 1 projeto compose)
Mesma imagem `ghcr.io/hesleylira/kdl-backend` instanciada 3× (uma por empresa), cada uma com sua
rede e seu Postgres. Bind compartilhado `~/kora-datalake/data → /app/data` no kdl e cdl.

| Empresa | Compose | Containers | Postgres | Entrada externa |
|---|---|---|---|---|
| Kora (KDL) | `docker-compose.prod.yml` | `kdl-backend` WT, `kdl-webhook-gw`, `kdl-cloudflared`, `kdl-ngrok`, `kdl-adminer` (avulso) | `kdl-postgres` :5433, vol `kdl-pgdata` | `webhook-kora.koracom.com.br`, LAN `/kora-dl/` |
| Curto (CDL) | `docker-compose.curto.prod.yml` | `cdl-backend` WT, `cdl-webhook-gw`, `cdl-cloudflared` | `cdl-postgres` :5434, vol `cdl-pgdata` | `webhook-curto.koracom.com.br` |
| Baú (BDL) | `docker-compose.bau.prod.yml` | `bdl-backend` WT | `bdl-postgres` :5436, vol `bdl-pgdata` | nenhuma (gateway/ngrok declarados, não sobem) |

`~/kora-datalake.pre-git/` é backup de antes do repo.

### wapp-bau — `/home/orangepi/wapp-bau` (rede `bau`)
- `bau-evolution` (evoapicloud/evolution-api) :8092, bind `data/evolution`.
- `bau-postgres` (imagem sem tag `0f7a666480d0`, postgres:16-alpine antiga), bind `data/postgres`.
- `bau-redis`, bind `data/redis`.

### jose — `/home/orangepi/jose` (rede `jose-internal`)
- `panel-api` WT (ghcr…/wapp-bau-panel), internal + proxy. Binds `.env.jose`, `.env.lojaintegrada`,
  `out/`, `scripts/` e **`/var/run/docker.sock`** (o painel controla containers). Não está na rede
  `bau`: fala com a Evolution pela porta do host :8092.
- `panel-front` WT (ghcr…/wapp-bau-front), internal + proxy, servido em `/wapp-bau/`.
- `jose` (bot, ghcr…/wapp-bau-jose) está no profile **`travado`** → não roda. Não existe container `jose`.

### nextcloud — `/home/orangepi/nextcloud` (rede `nc-internal`)
- `nextcloud` (nextcloud:stable-apache, 1,5 GB), internal + proxy, volume `nextcloud_nextcloud_data`.
- `nextcloud-db` (imagem sem tag `0f7a666480d0`), volume `nextcloud_nextcloud_db_data`.

### sirbcc — `/home/orangepi/projetos/sirbcc`
- `sirbcc-app` (vmsperandio/sirbcc) :3000, rede própria, `MONGODB_URI=mongodb://192.168.15.200:27017/sirbcc`
  → usa o **mongod instalado no host** (fora do Docker, db `sirbcc` 10 MB).
- **Duplicado quebrado:** `pm2` do usuário orangepi (`pm2-orangepi.service`) tenta subir o mesmo app
  com `npm start` na mesma pasta; a porta 3000 está com o container → `EADDRINUSE` → **984 mil
  restarts**, contribuindo pro load ~2,5–3,0 num host quase ocioso.

### calculadora-api — `/home/orangepi/calculadora-api`
- build local, :8001, plugado na `ml_curto_app-network`.

### mcp-nano-banana — `/home/orangepi/mcp-nano-banana`
- `Exited (0)` há 3 meses. Binds `~/imagens`, `~/logos`. Rede `mcp-nano-banana_default` vazia.

### Avulsos (`docker run`, sem compose)
`adminer-mlcurto`, `ccradar-adminer`, `kdl-adminer`, `ccradar-dev-pg`, `ciport-postgres`,
`garantia-dev-postgres`. Sobrevivem a reboot (unless-stopped) menos o `ccradar-dev-pg`.

## 4. Fora do Docker (systemd / cron)

| Unidade | O que é |
|---|---|
| `mongod.service` | MongoDB 27017 pro SIRBCC |
| `pm2-orangepi.service` | pm2 com `sirbcc` em crash loop (ver acima) |
| `curtolab-energy-simulator.service` | `/opt/curtolab-energy-simulator/tb_simulator.py run` — simulador de medidor pro ThingsBoard do CurtoLab (VPS Hostinger) |
| cron `run_bot_cron.sh` | bot de orçamentos do cc-radar, falhando (serviço inexistente) |
| `adbd` | Android Debug Bridge na 5037 (localhost) **e 5555 (LAN)** |
| `docker`, `containerd`, `avahi`, `chrony`, `rpcbind`, `vnstat`, `smartmontools`, `bluetooth` | base |

## 5. Recursos

| Item | Valor (2026-09-23) |
|---|---|
| RAM | 1,9 GB usados de 15 GB; swap zram 7,8 GB (0,7 GB em uso) |
| Disco `/` (SD) | 105 GB / 229 GB (47 %) |
| Imagens Docker | 222 (24 em uso), 64 GB, **57 GB recuperáveis** |
| Build cache | 627 entradas, **13 GB recuperáveis** |
| Volumes | 34 (10 em uso), 4,1 GB |
| Load average | ~2,5–3,0 (inflado pelo pm2) |
| Postgres rodando | 10 instâncias (ml_curto, ccradar, kdl, cdl, bdl, nextcloud, bau, ciport, garantia, ccradar-dev) |

## 6. Convenções vigentes

- **Deploy por imagem** (cc-radar, ML_Curto, jose, kora-datalake): CI publica no ghcr → Watchtower
  puxa em até 120 s. Basta o label; não subir outro Watchtower.
- **Deploy por build local** (calculadora-api, mcp-nano-banana): `git pull && docker compose up -d --build`.
- **Expor serviço novo**: entrar na `proxy-network` (external) e adicionar `location` no
  `server-infra/nginx/conf.d/default.conf` com `set $upstream_x <container>;` + `resolver 127.0.0.11`.
  Não publicar porta no host salvo banco pra dev.
- **Webhook público**: túnel Cloudflare dedicado + `*-webhook-gw` filtrando path (padrão do kora-datalake).
- **Portas livres** pra novos serviços: `8093-8095, 8097-8099`; Postgres `5438-5441, 5444+`; Redis `6380+`.

## 7. Dívidas e riscos encontrados

1. **502 em `dedoduro.curto.local` e `:9443`** — `mlcurto.conf` aponta pra `mlcurto-nginx`, container hoje chama `mlcurto-frontend`. Fix de uma linha (2 `set $upstream_mlcurto`).
2. **pm2 `sirbcc` em crash loop** (984 k restarts) — `pm2 delete sirbcc && pm2 save` ou desabilitar `pm2-orangepi.service`; o app já roda no container.
3. **Cron do bot cc-radar** roda a cada 30 min e falha (`no such service: ccradar-bot`) — apagar o cron ou trazer o serviço de volta pro compose.
4. **~70 GB recuperáveis** (`docker image prune -a` + `docker builder prune`) — cuidado: o prune de imagens só remove as não usadas por container existente.
5. **adbd na 5555 aberto na LAN** — desabilitar `usbdevice.service`/adb TCP se não for usado.
6. `kdl-ngrok` legado ainda rodando (túnel cloudflared já cobre).
7. `ccradar-dev-pg` sem volume e sem restart: dados somem no próximo reboot.
8. `mlcurto-ads-agent` monta o `~/.claude` do usuário orangepi (mesma credencial que o host usa), enquanto o `ccradar-triage-agent` tem home própria (`~/ccradar-home`) — padrão inconsistente.
9. `panel-api` com `docker.sock` montado = root no host a partir de um container exposto no nginx.
10. Imagens sem tag (`0f7a666480d0`) em `nextcloud-db` e `bau-postgres`: um `image prune` não remove (estão em uso), mas um `pull` do compose vai trocar a versão silenciosamente.
11. Compose do host do cc-radar ainda declara `ccradar-watchtower`, `bling-pdf-agent` e os proposal-agents: divergência host × repo não reconciliada.
12. README listava Portainer, `ccradar-proposal-agent`, `jose` como container e `kdl` como stack só da Kora — desatualizado; corrigido em 2026-09-23.
