# Orange Pi — Setup & Configs

Configurações da máquina Orange Pi do homelab (192.168.15.200).

Funções atuais:
- PostgreSQL (host de banco para projetos CurtoLab/SaaS)

## Estrutura sugerida

```
orange-pi/
├── README.md          # este arquivo
├── postgres/          # configs do PostgreSQL (postgresql.conf, pg_hba.conf, users)
├── services/          # systemd units, docker-compose, etc.
├── scripts/           # scripts de bootstrap/manutenção
└── docs/              # notas de instalação, backup, troubleshooting
```

## Notas

- IP fixo na LAN: `192.168.15.200`
- Acesso via SSH a partir das máquinas dev
- Referenciado em `skills/init-project/SKILL.md` como opção de host Postgres
