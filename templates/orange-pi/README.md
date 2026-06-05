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

## Stacks já em produção (NÃO derrubar)
- `global-nginx` — reverse proxy compartilhado (escuta 80/443/8443/9443)
- `nextcloud` + `nextcloud-db` (postgres:16-alpine) — Nextcloud pessoal
- `ccradar` — `ccradar-backend` + `ccradar-frontend` + `ccradar-email-agent` + `ccradar-proposal-agent` — radar de e-mails (atrás do nginx)
- `ml_curto` — `ml_curto-backend-1` + `ml_curto-db-1` (5432) + `ml_curto-redis-1` (6379) + `mlcurto-nginx` + `adminer-mlcurto` (8090) — projeto ML Curto
- `wapp-bau` — `jose` (bot, `192.168.15.200:9001`) + `panel-api` + `panel-front` + `bau-evolution` (8092) + `bau-postgres` + `bau-redis` — automação WhatsApp
- `kdl` — `kdl-backend` + `kdl-postgres` (`127.0.0.1:5433`) + `kdl-adminer` (8096) — stack de terceiro (imagem `ghcr.io/hesleylira/kdl-backend`), subiu 2026-06-05
- `sirbcc-app` (3000) — aplicação SIRBCC
- `calculadora-api` (8001) — calculadora interna
- `mcp-nano-banana` — servidor MCP
- `watchtower-orange` — auto-update label-scoped de todos os projetos (ver memória própria)
- Portainer (`9443`) — UI de gestão de containers

## Portas já ocupadas no host
`22, 80, 111, 443, 3000, 5432, 5433, 5555, 6379, 8000, 8001, 8090, 8092, 8096, 8443, 8888, 9001, 9443, 27017`

→ Antes de subir um serviço novo, escolher porta fora dessa lista.

## Portas livres recomendadas para novos serviços
- HTTP de novos apps: `8091, 8093-8095, 8097-8099` (8090/8092/8096 já tomados)
- Postgres adicional: `5434+`
- Redis adicional: `6380+`
- **Preferência**: não expor portas no host. Usar docker network interna e expor publicamente
  apenas via reverse proxy do container `global-nginx`.

## Convenção de deploy (padrão `cc-radar`)
1. Desenvolver localmente em `~/Documentos/projetos/<nome>/`
2. `git push`
3. No orangepi: `cd ~/<nome> && git pull && docker compose up -d --build`

## Observações
- Postgres roda em cartão SD — ok para volume baixo/médio. Para uso intensivo de escrita,
  mover bind mount para o NVMe (slot livre).
- Como é um host compartilhado, sempre verificar `docker ps` e `ss -tlnp` antes de subir
  um serviço novo para não colidir com algo em produção.
