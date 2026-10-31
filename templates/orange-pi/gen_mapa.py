#!/usr/bin/env python3
"""Gera a página HTML da arquitetura do orangepi com o SVG do mapa."""
from html import escape as e

parts = []
def add(s): parts.append(s)

def fit(txt, w, px):
    """Se o texto (estimado em px/char) não cabe na caixa, força textLength pra caber em qualquer fonte."""
    est = len(txt) * px
    return f' textLength="{w-10}" lengthAdjust="spacingAndGlyphs"' if est > w - 10 else ""

def box(x, y, w, h, label, sub=None, cls="node", r=4):
    add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>')
    if sub:
        add(f'<text class="lbl" x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle"{fit(label, w, 6.6)}>{e(label)}</text>')
        add(f'<text class="sub" x="{x+w/2}" y="{y+h/2+9}" text-anchor="middle"{fit(sub, w, 6.1)}>{e(sub)}</text>')
    else:
        add(f'<text class="lbl" x="{x+w/2}" y="{y+h/2+4}" text-anchor="middle"{fit(label, w, 6.6)}>{e(label)}</text>')

def wt(x, y):  # marcador watchtower
    add(f'<circle class="wt" cx="{x}" cy="{y}" r="3.5"/>')

def path(pts, cls="edge", arrow=True, dash=False):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    extra = ' marker-end="url(#arr)"' if arrow else ""
    extra += ' stroke-dasharray="4 3"' if dash else ""
    add(f'<path class="{cls}" d="{d}"{extra}/>')

def t(x, y, s, cls="cap", anchor="start"):
    add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{e(s)}</text>')

W, H = 1625, 720
add(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mapa de rede do host orangepi: entradas pela internet e pela LAN, a rede proxy-network compartilhada e as redes internas de cada stack">')
add('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')

# ---------- faixa de cima: entradas ----------
add('<rect class="zone" x="60" y="20" width="640" height="150" rx="8"/>')
t(76, 40, "INTERNET · sem porta aberta no roteador, só túneis", "zone-t")
add('<rect class="zone" x="720" y="20" width="885" height="150" rx="8"/>')
t(736, 40, "LAN 192.168.15.0/24", "zone-t")

# hostnames públicos
for i, (name, y) in enumerate([("radar.koracom.com.br", 62), ("webhook-curto.koracom.com.br", 96), ("webhook-kora.koracom.com.br", 130)]):
    box(80, y, 240, 24, name, cls="pill")
box(440, 62, 240, 48, "koracom-cloudflared", "Cloudflare Access · na proxy-network", cls="edge-node")
path([(320, 74), (440, 74)])
t(380, 68, "túnel", "cap", "middle")

# nginx
box(740, 60, 845, 90, "", cls="edge-node")
t(1162, 80, "global-nginx  :80 :443 :8443 :9443   (server-infra, mkcert curto.local)", "lbl", "middle")
t(1162, 102, "curto.local → /cc-radar  /dedoduro  /storage  /wapp-bau  /kora-dl  /sirbcc", "sub", "middle")
t(1162, 120, "storage.curto.local · :8443 → nextcloud      dedoduro.curto.local · :9443 → mlcurto-nginx (502)", "sub", "middle")
t(1162, 138, ":80 → 301 https://…/cc-radar/", "sub", "middle")

# ---------- barramento nginx → proxy-network ----------
BUS = 200
path([(1162, 150), (1162, BUS)], arrow=False)
path([(270, BUS), (1525, BUS)], arrow=False)
t(1172, BUS - 6, "proxy_pass pelo nome do container (resolver 127.0.0.11)", "cap")
for x in (270, 545, 835, 1082, 1355):
    path([(x, BUS), (x, 270)])
path([(1525, BUS), (1525, 380)])
t(1531, 300, "172.17.0.1:3000", "cap")
t(1531, 314, "(porta do host)", "cap")
# koracom-cloudflared → ccradar-frontend
path([(560, 110), (560, 182), (590, 182), (590, 270)], cls="edge hot")

# ---------- proxy-network ----------
add('<rect class="net" x="60" y="230" width="1370" height="100" rx="8"/>')
t(76, 250, "proxy-network 172.21.0.0/16 · external · quem precisa ser alcançado pelo nginx ou pelo túnel", "net-t")
members = [
    (70, 130, "cdl-backend", True), (205, 130, "kdl-backend", True), (340, 130, "bdl-backend", True),
    (505, 110, "ccradar-frontend", True), (625, 110, "ccradar-backend", True),
    (770, 130, "mlcurto-frontend", True),
    (1035, 95, "panel-front", True), (1140, 95, "panel-api", True),
    (1290, 130, "nextcloud", False),
]
for x, w, name, has_wt in members:
    box(x, 270, w, 40, name)
    if has_wt: wt(x + 8, 278)

# conectores pra rede interna
for x in (135, 270, 405, 560, 680, 835, 1082, 1187, 1355):
    path([(x, 310), (x, 380)], arrow=False, dash=True)

# ---------- stacks ----------
def column(x, w, title, net):
    add(f'<rect class="stack" x="{x}" y="380" width="{w}" height="310" rx="8"/>')
    t(x + 10, 398, title, "stack-t")
    t(x + 10, 412, net, "cap")

def stackbox(x, w, y, label, sub=None, cls="node"):
    box(x, y, w, 24 if not sub else 32, label, sub, cls=cls)

# kora-datalake
column(60, 420, "kora-datalake · ghcr.io/hesleylira/kdl-backend ×3", "uma rede + um Postgres por empresa")
for x, net, rows in [
    (70, "cdl-internal · Curto", [("cdl-postgres :5434", "node"), ("cdl-webhook-gw", "node"), ("cdl-cloudflared", "edge-node")]),
    (205, "kdl-internal · Kora", [("kdl-postgres :5433", "node"), ("kdl-webhook-gw", "node"), ("kdl-adminer :8096", "node"), ("kdl-ngrok (legado)", "warn"), ("kdl-cloudflared", "edge-node")]),
    (340, "bdl-internal · Baú", [("bdl-postgres :5436", "node"), ("sem webhook", "ghost")]),
]:
    t(x + 65, 434, net, "cap", "middle")
    for i, (lab, cls) in enumerate(rows):
        stackbox(x, 130, 442 + i * 32, lab, cls=cls)
# webhook-gw filtra só /api/v1/bling/webhook/
t(70, 648, "*-webhook-gw: só /api/v1/bling/webhook/", "cap")
t(70, 662, "e /api/v1/health, resto 404", "cap")
# túneis de webhook entrando pela esquerda
path([(80, 108), (45, 108), (45, 518), (70, 518)], cls="edge hot")
path([(80, 142), (30, 142), (30, 618), (270, 618), (270, 594)], cls="edge hot")
# gw -> backend (sobe pro membro da proxy)

# cc-radar
column(495, 250, "cc-radar · docker-compose.prod.yml", "ccradar-internal 172.23.0.0/16")
rows = [("ccradar-postgres :5435", "node"), ("ccradar-triage-agent (Claude)", "node"), ("ccradar-email-agent (Gmail)", "node"),
        ("ccradar-adminer :8091 · avulso", "node"), ("ccradar-dev-pg :5443 · sem volume", "warn"),
        ("cron → ccradar-bot: não existe", "bad")]
for i, (lab, cls) in enumerate(rows):
    stackbox(505, 230, 442 + i * 32, lab, cls=cls)
wt(513, 450 + 32); wt(513, 450 + 64)

# ML_Curto
column(760, 250, "ml_curto · /home/orangepi/ML_Curto", "ml_curto_app-network 172.19.0.0/16")
rows = [("ml_curto-backend-1 (scheduler)", "node"), ("ml_curto-db-1 :5432", "node"), ("ml_curto-redis-1 :6379", "node"),
        ("mlcurto-ads-agent (~/.claude)", "node"), ("calculadora-api :8001", "node"),
        ("adminer-mlcurto :8090 · avulso", "node")]
for i, (lab, cls) in enumerate(rows):
    stackbox(770, 230, 442 + i * 32, lab, cls=cls)
wt(778, 450); wt(778, 450 + 96)

# jose + wapp-bau
column(1025, 240, "jose  +  wapp-bau", "jose-internal 172.27 · bau 172.26")
stackbox(1035, 180, 442, "jose (bot): profile travado", "não roda", cls="ghost")
t(1035, 500, "rede bau", "cap")
t(1215, 500, "via host :8092", "cap", "end")
stackbox(1035, 180, 508, "bau-evolution :8092", cls="node")
stackbox(1035, 180, 540, "bau-postgres · sem tag", cls="node")
stackbox(1035, 180, 572, "bau-redis", cls="node")
path([(1187, 380), (1187, 428), (1225, 428), (1225, 520), (1215, 520)], cls="edge faint")
stackbox(1035, 180, 620, "panel-api monta docker.sock", cls="warn")

# nextcloud
column(1280, 150, "nextcloud", "nc-internal 172.22")
stackbox(1290, 130, 442, "nextcloud-db", "imagem sem tag", cls="node")
stackbox(1290, 130, 490, "volume de dados", cls="node")

# sirbcc
column(1445, 160, "sirbcc", "sirbcc_default 172.25")
stackbox(1455, 140, 442, "sirbcc-app :3000", cls="node")
stackbox(1455, 140, 490, "mongod :27017", "no host, fora do Docker", cls="host")
path([(1525, 466), (1525, 490)])
stackbox(1455, 140, 544, "pm2 sirbcc", "crash loop 984k×", cls="bad")

# legenda
t(60, 706, "●", "wt-l"); t(72, 706, "atualizado pelo watchtower-orange (label)   ─ ─  também está na rede interna do stack   ", "cap")
t(600, 706, "laranja = tráfego vindo da internet   vermelho = quebrado   tracejado cinza = declarado mas não roda", "cap")
add('</svg>')
SVG = "\n".join(parts)

HTML = f"""<title>Mapa do orangepi</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root {{
  --bg:#f2f4f7; --panel:#ffffff; --ink:#18212d; --mute:#66717f; --line:#cdd4dd;
  --accent:#e0672b; --accent-ink:#8f3d12; --bad:#c0392b; --warn:#b7791f; --ok:#2e8b57;
  --net:#e9eef5; --zone:#f7f8fa; --stack:#fbfbfc;
  --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  color-scheme:dark; --bg:#0f151c; --panel:#161e27; --ink:#e6eaf0; --mute:#97a3b1; --line:#334252;
  --accent:#f0813f; --accent-ink:#ffb27a; --bad:#ef6a5b; --warn:#e0a53a; --ok:#5fc48c;
  --net:#1b2733; --zone:#131a22; --stack:#131a22; }} }}
:root[data-theme="dark"] {{
  color-scheme:dark; --bg:#0f151c; --panel:#161e27; --ink:#e6eaf0; --mute:#97a3b1; --line:#334252;
  --accent:#f0813f; --accent-ink:#ffb27a; --bad:#ef6a5b; --warn:#e0a53a; --ok:#5fc48c;
  --net:#1b2733; --zone:#131a22; --stack:#131a22; }}
body {{ background:var(--bg); color:var(--ink); font-family:var(--sans); font-size:15px; line-height:1.5; margin:0; padding-block:28px 48px; padding-inline:clamp(16px,3vw,40px); }}
main {{ max-width:1400px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:clamp(24px,3vw,34px); font-weight:600; margin:0; letter-spacing:-0.01em; text-wrap:balance; }}
h2 {{ font-size:18px; font-weight:600; margin:0 0 10px; }}
p {{ margin:0; max-width:70ch; }}
.lead {{ color:var(--mute); }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
.chip {{ font-family:var(--mono); font-size:12px; padding:4px 10px; border:1px solid var(--line); border-radius:999px; background:var(--panel); }}
.chip b {{ font-weight:600; color:var(--accent-ink); }}
figure {{ margin:0; background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; overflow-x:auto; }}
figure svg {{ width:100%; min-width:1100px; height:auto; display:block; font-family:var(--mono); color:var(--ink); }}
figcaption {{ font-size:13px; color:var(--mute); margin-top:10px; max-width:none; }}
svg .zone {{ fill:var(--zone); stroke:var(--line); }}
svg .net {{ fill:var(--net); stroke:var(--line); }}
svg .stack {{ fill:var(--stack); stroke:var(--line); }}
svg .node {{ fill:var(--panel); stroke:var(--ink); stroke-width:1; }}
svg .edge-node {{ fill:var(--panel); stroke:var(--accent); stroke-width:1.5; }}
svg .pill {{ fill:var(--panel); stroke:var(--accent); stroke-width:1; }}
svg .host {{ fill:var(--panel); stroke:var(--mute); stroke-dasharray:3 2; }}
svg .ghost {{ fill:none; stroke:var(--mute); stroke-dasharray:3 2; }}
svg .warn {{ fill:var(--panel); stroke:var(--warn); stroke-width:1.5; }}
svg .bad {{ fill:var(--panel); stroke:var(--bad); stroke-width:1.5; }}
svg .lbl {{ font-size:10.8px; fill:var(--ink); }}
svg .sub {{ font-size:10px; fill:var(--mute); }}
svg .cap {{ font-size:10px; fill:var(--mute); font-family:var(--sans); }}
svg .zone-t, svg .net-t, svg .stack-t {{ font-size:11.5px; font-weight:600; fill:var(--ink); font-family:var(--sans); text-transform:uppercase; letter-spacing:.04em; }}
svg .stack-t {{ text-transform:none; letter-spacing:0; }}
svg .wt {{ fill:var(--accent); }} svg .wt-l {{ fill:var(--accent); font-size:12px; }}
svg .edge {{ fill:none; stroke:var(--ink); stroke-width:1.2; color:var(--ink); }}
svg .edge.hot {{ stroke:var(--accent); color:var(--accent); stroke-width:1.6; }}
svg .edge.faint {{ stroke:var(--mute); stroke-width:1; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 16px; }}
.card h3 {{ margin:0 0 6px; font-size:14px; font-family:var(--mono); font-weight:600; }}
.card p {{ font-size:13.5px; color:var(--mute); }}
.card ul {{ margin:8px 0 0; padding-left:18px; font-size:13.5px; }}
.card li {{ margin:2px 0; }}
code {{ font-family:var(--mono); font-size:12.5px; background:var(--net); padding:1px 5px; border-radius:4px; }}
table {{ border-collapse:collapse; width:100%; font-size:13.5px; background:var(--panel); border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
th,td {{ text-align:left; padding:8px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--mute); font-weight:600; }}
tr:last-child td {{ border-bottom:0; }}
td.port {{ font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.wrap {{ overflow-x:auto; }}
ol.find {{ margin:0; padding-left:22px; display:grid; gap:8px; max-width:80ch; }}
ol.find li::marker {{ font-family:var(--mono); color:var(--mute); }}
.sev {{ font-family:var(--mono); font-size:11px; padding:1px 7px; border-radius:4px; margin-right:6px; }}
.sev.bad {{ background:var(--bad); color:#fff; }} .sev.warn {{ background:var(--warn); color:#fff; }} .sev.info {{ background:var(--net); color:var(--ink); }}
</style>
<main>
<header>
  <h1>Mapa do orangepi</h1>
  <p class="lead">Como o host homelab está de fato hoje, levantado ao vivo em 23/09/2026 com <code>docker ps</code>, <code>network inspect</code>, os composes, o nginx e os túneis. Não é o que os repos dizem; é o que roda.</p>
  <div class="chips">
    <span class="chip">Orange Pi 5 Pro · RK3588S · <b>16 GB</b></span>
    <span class="chip">Ubuntu 22.04 · Docker <b>27.1.1</b></span>
    <span class="chip"><b>39</b> containers up · 13 stacks compose</span>
    <span class="chip"><b>10</b> Postgres</span>
    <span class="chip">SD 105 / 229 GB · <b>70 GB</b> recuperáveis</span>
    <span class="chip">RAM 1,9 / 15 GB · load <b>~2,8</b></span>
  </div>
</header>

<figure>
{SVG}
<figcaption>Cada stack tem sua rede interna; só o container que precisa ser alcançado entra também na <code>proxy-network</code>, onde o <code>global-nginx</code> (LAN) e o <code>koracom-cloudflared</code> (internet) o acham pelo nome. Os webhooks do Bling entram por túneis Cloudflare dedicados que caem num nginx filtro dentro da rede interna do data lake, sem passar pela proxy-network. Bancos e agentes nunca ficam na proxy-network.</figcaption>
</figure>

<section>
<h2>Stacks</h2>
<div class="grid">
  <div class="card"><h3>server-infra · orange-infra · koracom-tunnel</h3><p>Infra compartilhada.</p><ul><li><code>global-nginx</code> com certificado mkcert <code>curto.local</code>; landing page em <code>/</code> com links pra cc-radar, dedoduro e storage.</li><li><code>watchtower-orange</code> poll 120 s, só containers com o label; hoje adota 12.</li><li><code>koracom-cloudflared</code> expõe o cc-radar em <code>radar.koracom.com.br</code> atrás do Cloudflare Access.</li></ul></div>
  <div class="card"><h3>cc-radar</h3><p>Radar de e-mails e orçamentos, imagens do ghcr.</p><ul><li>backend, frontend, triage-agent (Claude Code com home própria em <code>~/ccradar-home</code>) e email-agent (service account Gmail).</li><li>Declarados mas parados: proposal-agent email/whatsapp (profile <code>desativado</code>), bling-pdf-agent, ccradar-watchtower.</li><li>Cron do host chama um serviço <code>ccradar-bot</code> que não existe no compose.</li></ul></div>
  <div class="card"><h3>ml_curto (dedo-duro)</h3><p>Pricing e vigia do Mercado Livre.</p><ul><li>frontend nginx em <code>/dedoduro/</code>, backend com scheduler, Postgres 5432 e Redis 6379 publicados pra dev.</li><li>ads-agent monta o <code>~/.claude</code> do usuário orangepi.</li><li>calculadora-api e adminer pendurados na mesma rede.</li><li>Cópia morta em <code>~/projetos/ML_Curto</code>.</li></ul></div>
  <div class="card"><h3>kora-datalake</h3><p>Três instâncias da mesma imagem de terceiro, uma por empresa.</p><ul><li>KDL (Kora) 5433: webhook via Cloudflare e ngrok legado, API na LAN em <code>/kora-dl/</code>.</li><li>CDL (Curto) 5434: webhook via Cloudflare dedicado.</li><li>BDL (Baú) 5436: só backend e banco, sem webhook.</li><li>Bind <code>~/kora-datalake/data</code> compartilhado por kdl e cdl.</li></ul></div>
  <div class="card"><h3>jose + wapp-bau</h3><p>Automação WhatsApp do Baú da Eletrônica.</p><ul><li>wapp-bau: Evolution API 8092, Postgres e Redis em bind mounts.</li><li>jose: painel (api + front) em <code>/wapp-bau/</code>; o painel monta o <code>docker.sock</code> pra controlar o bot.</li><li>O bot <code>jose</code> está no profile <code>travado</code> e não roda.</li></ul></div>
  <div class="card"><h3>nextcloud · sirbcc · outros</h3><ul><li>Nextcloud em <code>/storage/</code>, <code>storage.curto.local</code> e <code>:8443</code>.</li><li>sirbcc-app na 3000 usa o MongoDB instalado no host; um pm2 tenta subir o mesmo app e falha em loop.</li><li>Avulsos: ciport-postgres 5437, garantia-dev-postgres 5442, ccradar-dev-pg 5443, três adminers.</li><li>mcp-nano-banana parado desde junho.</li><li>Fora do Docker: simulador de medidor do CurtoLab (systemd), adbd, rpcbind.</li></ul></div>
</div>
</section>

<section>
<h2>Portas publicadas no host</h2>
<div class="wrap"><table>
<tr><th>Porta</th><th>Quem</th><th>Para quê</th></tr>
<tr><td class="port">80 443 8443 9443</td><td>global-nginx</td><td>edge LAN</td></tr>
<tr><td class="port">3000</td><td>sirbcc-app</td><td>app SIRBCC (também em /sirbcc)</td></tr>
<tr><td class="port">5432</td><td>ml_curto-db-1</td><td>Postgres ML_Curto</td></tr>
<tr><td class="port">5433 5434 5435 5436</td><td>kdl · cdl · ccradar · bdl postgres</td><td>bancos das stacks</td></tr>
<tr><td class="port">5437 5442 5443</td><td>ciport · garantia-dev · ccradar-dev postgres</td><td>bancos avulsos de dev</td></tr>
<tr><td class="port">6379</td><td>ml_curto-redis-1</td><td>Redis ML_Curto</td></tr>
<tr><td class="port">8001</td><td>calculadora-api</td><td>API interna</td></tr>
<tr><td class="port">8090 8091 8096</td><td>adminer mlcurto · ccradar · kdl</td><td>UI de banco</td></tr>
<tr><td class="port">8092</td><td>bau-evolution</td><td>Evolution API</td></tr>
<tr><td class="port">27017 · 5555 · 111 · 22</td><td>mongod · adbd · rpcbind · sshd</td><td>processos do host, fora do Docker</td></tr>
</table></div>
<p class="lead" style="margin-top:8px">Livres pra serviço novo: 8093-8095, 8097-8099; Postgres 5438-5441 e 5444+; Redis 6380+. Preferir não publicar porta e entrar na proxy-network.</p>
</section>

<section>
<h2>O que está quebrado ou pede atenção</h2>
<ol class="find">
<li><span class="sev bad">502</span><code>dedoduro.curto.local</code> e <code>:9443</code> apontam pra <code>mlcurto-nginx</code>, container hoje se chama <code>mlcurto-frontend</code>. Dois <code>set $upstream_mlcurto</code> em <code>mlcurto.conf</code>.</li>
<li><span class="sev bad">CPU</span>pm2 <code>sirbcc</code> em crash loop (984 mil restarts) porque a porta 3000 já é do container. É o que segura o load em ~2,8 num host ocioso.</li>
<li><span class="sev bad">cron</span>bot de orçamentos do cc-radar roda a cada 30 min e falha com <code>no such service: ccradar-bot</code>; log já tem 65 mil linhas.</li>
<li><span class="sev warn">disco</span>222 imagens (24 em uso) e 13 GB de build cache: cerca de 70 GB recuperáveis com prune.</li>
<li><span class="sev warn">rede</span>adbd escutando na 5555 pra toda a LAN.</li>
<li><span class="sev warn">dados</span><code>ccradar-dev-pg</code> sem volume e com <code>restart=no</code>: some no próximo reboot.</li>
<li><span class="sev warn">segurança</span><code>panel-api</code> monta o <code>docker.sock</code> e está exposto no nginx: equivale a root no host.</li>
<li><span class="sev info">legado</span><code>kdl-ngrok</code> ainda roda apesar do túnel Cloudflare já cobrir o mesmo gateway.</li>
<li><span class="sev info">imagem</span><code>nextcloud-db</code> e <code>bau-postgres</code> rodam uma imagem sem tag; um pull do compose troca a versão sem avisar.</li>
<li><span class="sev info">padrão</span>o ads-agent usa o <code>~/.claude</code> do usuário; o triage-agent tem home própria. Vale unificar.</li>
<li><span class="sev info">docs</span>o compose do host do cc-radar ainda declara watchtower, bling-pdf-agent e proposal-agents; host e repo divergem.</li>
</ol>
</section>
</main>
"""
import os; open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa.html"), "w").write(HTML)
print("ok", len(HTML))
