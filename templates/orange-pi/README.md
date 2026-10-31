# Host: orangepi

Servidor caseiro do Lucas / TrueIoT, onde rodam aplicações pessoais e de produção leve.

## Acesso
- IP LAN: `192.168.15.200`
- Alias SSH: `ssh orangepi` (configurado em `~/.ssh/config`)
- User: `orangepi`
- Senha padrão da imagem oficial: `orangepi` (somente acesso LAN — não expor 22 na internet)
- Recomendação: rodar `ssh-copy-id orangepi` uma vez para usar key auth e dispensar senha.
- Hostname interno: `curto`

## Hardware
- Modelo: **Orange Pi 5 Pro**
- SoC: Rockchip **RK3588S** (8 cores big.LITTLE — 4× Cortex-A55 @ 1.8 GHz + 4× Cortex-A76 @ 2.35 GHz)
- RAM: **16 GB** LPDDR4X
- Storage: cartão SD de 229 GB em `/dev/mmcblk0p2` (slot NVMe M.2 está livre)
- Arquitetura: `aarch64` / `arm64`
- NPU 6 TOPS (RKNN) disponível para inferência local se necessário

## Sistema
- OS: Ubuntu 22.04.5 LTS (Jammy)
- Kernel: `6.1.43-rockchip-rk3588`
- Docker: `27.1.1`
- Docker Compose: `v2.29.1`
- Swap: 8 GB

## Stacks em produção (levantado em 2026-09-23 — detalhe em [ARCHITECTURE.md](ARCHITECTURE.md))
- `server-infra` → `global-nginx` — reverse proxy compartilhado (80/443/8443/9443), rede `proxy-network`
- `orange-infra` → `watchtower-orange` — auto-update label-scoped de todos os projetos
- `koracom-tunnel` → `koracom-cloudflared` — `radar.koracom.com.br` → ccradar-frontend (Cloudflare Access)
- `cc-radar` → `ccradar-postgres` (5435) + `ccradar-backend` + `ccradar-frontend` + `ccradar-triage-agent` + `ccradar-email-agent` (+ `ccradar-adminer` 8091 avulso)
- `ml_curto` → `mlcurto-frontend` + `ml_curto-backend-1` + `ml_curto-db-1` (5432) + `ml_curto-redis-1` (6379) + `mlcurto-ads-agent` (+ `adminer-mlcurto` 8090 e `calculadora-api` 8001 na mesma rede)
- `kora-datalake` → 3 instâncias de `ghcr.io/hesleylira/kdl-backend`: **kdl** (Kora, pg 5433, webhook via cloudflared + ngrok legado, `/kora-dl/` no nginx), **cdl** (Curto, pg 5434, webhook via cloudflared), **bdl** (Baú, pg 5436, sem webhook); `kdl-adminer` 8096 avulso
- `wapp-bau` → `bau-evolution` (8092) + `bau-postgres` + `bau-redis` — Evolution API (WhatsApp)
- `jose` → `panel-api` + `panel-front` (`/wapp-bau/` no nginx); o bot `jose` está no profile `travado` e **não roda**
- `nextcloud` → `nextcloud` + `nextcloud-db` — `/storage/`, `storage.curto.local`, `:8443`
- `sirbcc` → `sirbcc-app` (3000), usa **mongod do host** (27017)
- `calculadora-api` (8001) — build local
- `mcp-nano-banana` — parado (Exited) desde jun/2026
- Avulsos: `ciport-postgres` (5437), `garantia-dev-postgres` (5442), `ccradar-dev-pg` (5443, sem volume)
- Fora do Docker: `mongod`, `pm2` (sirbcc, quebrado), `curtolab-energy-simulator.service`, cron do bot cc-radar, `adbd`
- **Não existe Portainer** no host.

## Portas já ocupadas no host
`22, 80, 111, 443, 3000, 5037, 5432, 5433, 5434, 5435, 5436, 5437, 5442, 5443, 5555, 6379, 8001, 8090, 8091, 8092, 8096, 8443, 9443, 27017`

→ Antes de subir um serviço novo, escolher porta fora dessa lista.

## Portas livres recomendadas para novos serviços
- HTTP de novos apps: `8093-8095, 8097-8099`
- Postgres adicional: `5438-5441, 5444+`
- Redis adicional: `6380+`
- **Preferência**: não expor portas no host. Usar docker network interna e expor publicamente
  apenas via reverse proxy do container `global-nginx` (rede `proxy-network`).

## Convenção de deploy (padrão `cc-radar`)
1. Desenvolver localmente em `~/Documentos/projetos/<nome>/`
2. `git push`
3. Projetos com imagem no ghcr (cc-radar, ML_Curto, jose, kora-datalake): CI publica → `watchtower-orange` puxa em até 120 s (basta o label `com.centurylinklabs.watchtower.enable=true`)
4. Projetos de build local: no orangepi `cd ~/<nome> && git pull && docker compose up -d --build`

## Observações
- Postgres roda em cartão SD — ok para volume baixo/médio. Para uso intensivo de escrita,
  mover bind mount para o NVMe (slot livre).
- Como é um host compartilhado, sempre verificar `docker ps` e `ss -tlnp` antes de subir
  um serviço novo para não colidir com algo em produção.
