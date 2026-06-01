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
- `global-nginx` — reverse proxy compartilhado (escuta 80/443)
- `nextcloud` + `nextcloud-db` (postgres:16-alpine) — Nextcloud pessoal
- `ccradar-backend` (8000) + `ccradar-frontend` (3000) — radar de e-mails
- `ml_curto` (postgres + redis + backend + nginx) — projeto ML Curto
- `sirbcc-app` — aplicação SIRBCC
- `calculadora-api` — calculadora interna
- `mcp-nano-banana` — servidor MCP
- Portainer (`9443`) — UI de gestão de containers

## Portas já ocupadas no host
`22, 80, 111, 443, 3000, 5432, 5555, 6379, 8000, 8001, 8443, 8888, 9443, 27017`

→ Antes de subir um serviço novo, escolher porta fora dessa lista.

## Portas livres recomendadas para novos serviços
- HTTP de novos apps: `8090-8099`
- Postgres adicional: `5433+`
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
