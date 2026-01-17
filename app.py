# app.py
import random
import math
import time
import base64
import pandas as pd
import streamlit as st


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")


# =========================
# STATE INIT
# =========================
def ss_init():
    defaults = {
        "started": False,
        "nomes": ["Ana", "Bruno", "Carlos", "Você"],
        "humano_idx": 3,

        "pontos": {},
        "vazas_rodada": {},
        "maos": {},
        "rodada": 1,

        "cartas_inicio": 0,
        "cartas_alvo": 0,
        "sobras_monte": 0,

        "mao_da_rodada": 0,
        "mao_primeira_sorteada": False,

        "fase": "setup",          # setup | prognostico | jogo | fim
        "show_final": False,

        "prognosticos": {},
        "progn_pre": {},
        "progn_pos": {},

        "ordem": [],
        "turn_idx": 0,
        "naipe_base": None,
        "mesa": [],
        "primeira_vaza": True,
        "copas_quebrada": False,

        "pontuou_rodada": False,
        "pending_play": None,

        "table_pop_until": 0.0,
        "winner_flash_name": None,
        "winner_flash_until": 0.0,

        # Trick animation
        "trick_pending": False,
        "trick_phase": None,          # show -> fly
        "trick_resolve_at": 0.0,
        "trick_fly_until": 0.0,
        "trick_winner": None,
        "trick_snapshot": [],

        "pile_counts": {},

        # autoplay
        "autoplay_last": 0.0,

        # UI
        "theme": "neon",              # neon | classic
        "menu_open": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


ss_init()


# =========================
# THEME + CSS
# =========================
def inject_css():
    theme = st.session_state.get("theme", "neon")

    if theme == "neon":
        bg1, bg2 = "#070A12", "#061A14"
        topbar_bg = "rgba(255,255,255,.08)"
        topbar_stroke = "rgba(255,255,255,.14)"
        text_main = "rgba(255,255,255,.92)"
        text_muted = "rgba(255,255,255,.72)"
        pill_bg = "rgba(255,255,255,.08)"
        pill_stroke = "rgba(255,255,255,.16)"

        # face da carta (IMPORTANTE pro neon)
        card_face1 = "#FFFFFF"
        card_face2 = "#F3F4F6"
        card_stroke = "rgba(0,0,0,.16)"
        card_shadow = "0 12px 26px rgba(0,0,0,.30)"
        seat_bg = "rgba(255,255,255,.86)"

    else:  # classic
        bg1, bg2 = "#F3F4F6", "#E5E7EB"
        topbar_bg = "rgba(255,255,255,.78)"
        topbar_stroke = "rgba(0,0,0,.10)"
        text_main = "rgba(17,24,39,.95)"
        text_muted = "rgba(17,24,39,.70)"
        pill_bg = "rgba(0,0,0,.04)"
        pill_stroke = "rgba(0,0,0,.10)"

        card_face1 = "#FFFFFF"
        card_face2 = "#F8F8F8"
        card_stroke = "rgba(0,0,0,.14)"
        card_shadow = "0 10px 22px rgba(0,0,0,.16)"
        seat_bg = "rgba(255,255,255,.92)"

    APP_CSS = f"""
<style>
:root{{
  --app-max: 1200px;
  --pad: .85rem;

  --bg1: {bg1};
  --bg2: {bg2};

  --topbar-bg: {topbar_bg};
  --topbar-stroke: {topbar_stroke};
  --text: {text_main};
  --muted: {text_muted};

  --pill-bg: {pill_bg};
  --pill-stroke: {pill_stroke};

  /* carta sempre visível (fix do neon) */
  --card-face1: {card_face1};
  --card-face2: {card_face2};
  --card-stroke: {card_stroke};
  --card-shadow: {card_shadow};

  --seat-bg: {seat_bg};

  --shadow: 0 18px 44px rgba(0,0,0,.28);
  --shadow2: 0 14px 34px rgba(0,0,0,.22);

  --radius: 18px;
  --radius2: 22px;

  --hand-card-w: 86px;
  --hand-card-h: 118px;
}}

header[data-testid="stHeader"]{
  height: 0rem;               /* tira a faixa extra */
}

.block-container{
  padding-top: calc(var(--pad) + 34px) !important; /* desce mais tudo */
}

.topbar{
  top: 1.05rem;               /* desce a barra sticky */
}


[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1200px 700px at 15% 10%, rgba(56,189,248,.10), transparent 55%),
    radial-gradient(900px 600px at 80% 35%, rgba(34,197,94,.10), transparent 55%),
    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
}}

[data-testid="stVerticalBlock"]{{ gap:.55rem; }}

html, body, [class*="css"] {{
  letter-spacing: .1px;
}}

/* ===== Title ===== */
.titleRow {{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
  margin-top: 10px; /* garante visível */
  margin-bottom: 6px;
}}
.titleRow h1 {{
  margin:0;
  font-size: 28px;
  color: var(--text);
}}
.badges {{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  justify-content:flex-end;
}}
.badge {{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.14);
  font-size:12px;
  font-weight:800;
  color: var(--text);
}}

/* ===== Topbar (sticky) ===== */
.topbar {{
  position: sticky;
  top: .45rem;
  z-index: 60;

  border-radius: 22px;
  border: 1px solid var(--topbar-stroke);
  background: var(--topbar-bg);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow2);
  padding: 12px 14px;

  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}}
.topbar:before {{
  content:"";
  position:absolute; inset:0;
  border-radius: 22px;
  background: radial-gradient(circle at 20% 10%, rgba(255,255,255,.18), transparent 40%);
  pointer-events:none;
}}
.topLeft {{ display:flex; flex-direction:column; gap:3px; }}
.topTitle {{ font-weight: 950; font-size: 14px; color: var(--text); }}
.topSub {{ font-weight: 800; font-size: 12px; color: var(--muted); }}
.topRight {{ display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }}

.pill {{
  display:inline-flex; align-items:center; gap:7px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid var(--pill-stroke);
  background: var(--pill-bg);
  color: var(--text);
  font-weight: 900;
  font-size: 12px;
}}
.pillGood{{ background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.26); }}
.pillWarn{{ background: rgba(245,158,11,.12); border-color: rgba(245,158,11,.26); }}
.pillInfo{{ background: rgba(56,189,248,.10); border-color: rgba(56,189,248,.22); }}

/* ===== Icon buttons ===== */
.iconBar {{
  display:flex;
  gap:8px;
  justify-content:flex-end;
  align-items:center;
}}
div[data-testid="stHorizontalBlock"] .stButton > button.iconBtn {{
  width: 44px !important;
  height: 40px !important;
  min-height: 40px !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  background: rgba(255,255,255,.10) !important;
  color: var(--text) !important;
  font-weight: 900 !important;
  padding: 0 !important;
}}
div[data-testid="stHorizontalBlock"] .stButton > button.iconBtn:hover {{
  transform: translateY(-2px);
  filter: drop-shadow(0 10px 16px rgba(0,0,0,.25));
}}

/* ===== Mesa ===== */
.mesaWrap{{ margin-top: 6px; }}
.mesa{
  border-radius: 999px; /* deixa oval automaticamente */
  border: 1px solid rgba(255,255,255,.18);

  background:
    radial-gradient(900px 420px at 50% 45%, rgba(255,255,255,.10), transparent 60%),
    radial-gradient(circle at 22% 18%, rgba(255,255,255,.12), transparent 42%),
    radial-gradient(circle at 80% 70%, rgba(0,0,0,.30), transparent 55%),
    linear-gradient(180deg, rgba(16,110,70,1) 0%, rgba(10,78,50,1) 55%, rgba(8,60,40,1) 100%);

  height: 470px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 22px 60px rgba(0,0,0,.34);
}

/* textura */
.mesa:before{
  content:"";
  position:absolute; inset:0;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.016) 0 1px, rgba(255,255,255,0) 1px 3px),
    repeating-linear-gradient(90deg, rgba(0,0,0,.014) 0 1px, rgba(0,0,0,0) 1px 4px);
  opacity:.55;
  pointer-events:none;
}

/* aro interno oval + brilho */
.mesa:after{
  content:"";
  position:absolute;
  inset: 14px;
  border-radius: 999px;  /* acompanha o oval */
  border: 1px solid rgba(255,255,255,.14);
  box-shadow:
    inset 0 0 0 1px rgba(0,0,0,.16),
    inset 0 0 40px rgba(0,0,0,.16);
  pointer-events:none;
}

.mesaCenter{{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-weight:900; opacity:.58;
  pointer-events:none;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(255,255,255,.90);
}}

@keyframes shimmer {{
  0%   {{ transform: translateX(-40%) rotate(10deg); opacity: 0; }}
  15%  {{ opacity: .10; }}
  55%  {{ opacity: .06; }}
  100% {{ transform: translateX(140%) rotate(10deg); opacity: 0; }}
}}

.mesa .shimmer{
  position:absolute;
  top: -35%;
  left: -30%;
  width: 60%;
  height: 170%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.18), transparent);
  filter: blur(6px);
  opacity: 0;
  pointer-events:none;
  animation: shimmer 6.2s ease-in-out infinite;
}

/* Assentos */
.seat{{
  position:absolute;
  padding:6px 10px;
  border-radius:999px;
  background: var(--seat-bg);
  border:1px solid rgba(0,0,0,.10);
  font-size:12px;
  white-space:nowrap;
  z-index: 25;
  display:flex;
  align-items:center;
  gap:8px;
}}
.seat.you{{ outline:2px solid rgba(34,197,94,.55); font-weight:900; }}
.seat.dealer{{ border-color: rgba(34,197,94,.35); background: rgba(255,255,255,.95); }}
.avatarImg{{
  width:26px; height:26px;
  border-radius:50%;
  border: 1px solid rgba(0,0,0,.12);
  background: rgba(0,0,0,.04);
  box-shadow: 0 6px 12px rgba(0,0,0,.10);
  flex: 0 0 auto;
}}

@keyframes winnerGlow {{
  0% {{ box-shadow: 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }}
  35% {{ box-shadow: 0 0 0 6px rgba(34,197,94,.22), 0 14px 28px rgba(0,0,0,.14); transform: translate(-50%,-50%) scale(1.03); }}
  100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }}
}}
.seat.winnerFlash{{
  animation: winnerGlow 1.2s ease-out;
  outline: 2px solid rgba(34,197,94,.55);
  background: rgba(255,255,255,.97);
}}

/* Carta (mesa) */
.playCard{{ position:absolute; transform: translate(-50%,-50%); pointer-events:none; z-index: 18; }}
@keyframes popIn {{
  0% {{ transform: translate(-50%,-50%) scale(.92); opacity: 0; }}
  100% {{ transform: translate(-50%,-50%) scale(1); opacity: 1; }}
}}
.playCard.pop{{ animation: popIn .16s ease-out; }}

/* Carta (visual) */
.card{{
  width:70px;
  height:102px;
  border-radius:14px;
  border:1px solid var(--card-stroke);
  background: linear-gradient(180deg, var(--card-face1) 0%, var(--card-face2) 100%);
  box-shadow: var(--card-shadow);
  position:relative;
  user-select:none;
}}
.card .tl{{ position:absolute; top:7px; left:7px; font-weight:900; font-size:13px; line-height:13px; }}
.card .br{{ position:absolute; bottom:7px; right:7px; font-weight:900; font-size:13px; line-height:13px; transform:rotate(180deg); }}
.card .mid{{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:900; opacity:.92; }}

/* Chips */
.chipWrap{{ position:absolute; transform: translate(-50%,-50%); z-index: 16; }}
.chipRow{{ display:flex; gap:6px; flex-wrap:wrap; justify-content:center; max-width: 140px; }}
.chipMini{{
  width:22px; height:22px;
  border-radius:50%;
  position:relative;
  box-shadow: 0 8px 14px rgba(0,0,0,.14);
  border: 2px solid rgba(0,0,0,.14);
  background:
    radial-gradient(circle at 30% 25%, rgba(255,255,255,.35), rgba(255,255,255,0) 45%),
    conic-gradient(from 0deg,
      rgba(255,255,255,0) 0 18deg,
      rgba(255,255,255,.70) 18deg 28deg,
      rgba(255,255,255,0) 28deg 54deg,
      rgba(255,255,255,.70) 54deg 64deg,
      rgba(255,255,255,0) 64deg 90deg,
      rgba(255,255,255,.70) 90deg 100deg,
      rgba(255,255,255,0) 100deg 126deg,
      rgba(255,255,255,.70) 126deg 136deg,
      rgba(255,255,255,0) 136deg 162deg,
      rgba(255,255,255,.70) 162deg 172deg,
      rgba(255,255,255,0) 172deg 198deg,
      rgba(255,255,255,.70) 198deg 208deg,
      rgba(255,255,255,0) 208deg 234deg,
      rgba(255,255,255,.70) 234deg 244deg,
      rgba(255,255,255,0) 244deg 270deg,
      rgba(255,255,255,.70) 270deg 280deg,
      rgba(255,255,255,0) 280deg 306deg,
      rgba(255,255,255,.70) 306deg 316deg,
      rgba(255,255,255,0) 316deg 342deg,
      rgba(255,255,255,.70) 342deg 352deg,
      rgba(255,255,255,0) 352deg 360deg
    );
  background-color: var(--chip-base, rgba(16,185,129,.88));
}}
.chipMini:after{{
  content:"";
  position:absolute;
  inset:5px;
  border-radius:50%;
  background: rgba(255,255,255,.78);
  border: 1px solid rgba(0,0,0,.10);
}}
.chipNote{{
  margin-top: 6px;
  font-size: 10px;
  font-weight: 900;
  opacity: .72;
  background: rgba(255,255,255,.76);
  border: 1px solid rgba(0,0,0,.08);
  padding: 3px 8px;
  border-radius: 999px;
  display:inline-block;
}}

/* Pile */
.pileWrap{{ position:absolute; transform: translate(-50%,-50%); z-index: 15; }}
.pileStack{{ position:relative; width:26px; height:40px; }}
.cardBackLayer{{
  position:absolute;
  width:26px; height:40px;
  border-radius:8px;
  border:1px solid rgba(0,0,0,.18);
  background: linear-gradient(180deg, rgba(12,110,80,.95) 0%, rgba(7,86,64,.95) 100%);
  box-shadow: 0 6px 10px rgba(0,0,0,.12);
  overflow:hidden;
}}
.cardBackLayer:before{{
  content:"";
  position:absolute; inset:-28%;
  background: repeating-linear-gradient(45deg, rgba(255,255,255,.12) 0 8px, rgba(255,255,255,0) 8px 16px);
  transform: rotate(14deg);
}}
.pileLabel{{
  margin-top:4px;
  text-align:center;
  font-weight:900;
  font-size:10px;
  opacity:.74;
  color: rgba(255,255,255,.92);
  text-shadow: 0 2px 6px rgba(0,0,0,.25);
}}

/* Dock da mão */
.handDock{{
  margin-top: 10px;
  border-radius: 18px;
  border:1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.10);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow2);
  padding: 12px;
}}
.handTitle{{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 6px; }}
.handTitle h3{{ margin:0; font-size:16px; color: var(--text); }}
.hint{{ font-size:12px; color: var(--muted); font-weight:800; }}

/* ===== Clique correto: botão invisível + carta por cima ===== */
div[data-testid="column"] .stButton > button {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;

  min-height: var(--hand-card-h) !important;
  height: var(--hand-card-h) !important;
  width: var(--hand-card-w) !important;
  min-width: var(--hand-card-w) !important;
  max-width: var(--hand-card-w) !important;

  padding: 0 !important;
  border-radius: 14px !important;
  margin: 0 auto !important;
  display:block !important;

  transition: transform .10s ease, filter .10s ease;
}}
div[data-testid="column"] .stButton > button:hover {{
  transform: translateY(-4px);
  filter: drop-shadow(0 12px 20px rgba(0,0,0,.22));
}}
div[data-testid="column"] .stButton > button:disabled {{
  opacity: .25 !important;
  transform:none !important;
  filter:none !important;
}}

/* overlay (a carta desenhada) */
.cardOverlay {{
  width: var(--hand-card-w) !important;
  height: var(--hand-card-h) !important;
  margin: 0 auto !important;
  margin-top: calc(-1 * var(--hand-card-h)) !important;
  pointer-events: none !important;
}}

/* ===== Face da carta da mão (FIX NEON: sempre sólida!) ===== */
.cardBtnInner {{
  width: var(--hand-card-w) !important;
  height: var(--hand-card-h) !important;
  border-radius: 14px;
  overflow:hidden;

  background: linear-gradient(180deg, var(--card-face1) 0%, var(--card-face2) 100%) !important;
  border: 1px solid var(--card-stroke) !important;
  box-shadow: var(--card-shadow) !important;
  position: relative;
}}
.cardBtnTL{{ position:absolute; top:10px; left:10px; font-weight:900; font-size:14px; line-height:14px; }}
.cardBtnBR{{ position:absolute; bottom:10px; right:10px; font-weight:900; font-size:14px; line-height:14px; transform: rotate(180deg); }}
.cardBtnMid{{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:34px; font-weight:900; opacity:.92; }}

@keyframes flyAway {{
  0%   {{ transform: translateY(0px) scale(1); opacity: 1; }}
  55%  {{ transform: translateY(-26px) scale(1.03); opacity: .85; }}
  100% {{ transform: translateY(-70px) scale(.96); opacity: 0; }}
}}
.flyAway{{ animation: flyAway .25s ease-in forwards; }}

/* Mobile */
@media (max-width: 900px){{
  :root{{ --pad: .55rem; --hand-card-w: 80px; --hand-card-h: 112px; }}

  .block-container{{ padding-left:.55rem !important; padding-right:.55rem !important; }}

  .titleRow h1{{ font-size: 22px; }}

  .mesa{{
    height: calc(100vh - 62px - 210px - 24px);
    min-height: 340px;
  }}
  .handDock{{
    position: fixed;
    left: .55rem;
    right: .55rem;
    bottom: .55rem;
    margin-top: 0 !important;
    z-index: 80;
  }}
  .mesaWrap{{ margin-bottom: 220px; }}
  .topbar{{ flex-direction:column; align-items:flex-start; }}
  .topRight{{ justify-content:flex-start; }}
}}
</style>
"""
    st.markdown(APP_CSS, unsafe_allow_html=True)


inject_css()


# =========================
# BARALHO / REGRAS
# =========================
VALORES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
PESO_VALOR = {v: i for i, v in enumerate(VALORES)}
COR_NAIPE = {"♦": "#C1121F", "♥": "#C1121F", "♠": "#111827", "♣": "#111827"}
ORDEM_NAIPE = {"♦": 0, "♠": 1, "♣": 2, "♥": 3}
TRUNFO = "♥"
HIGH_POINTS = {"A": 1.40, "K": 1.05, "Q": 0.80, "J": 0.55, 10: 0.35, 9: 0.20}


def criar_baralho():
    naipes = ["♠", "♦", "♣", "♥"]
    return [(n, v) for n in naipes for v in VALORES]


def peso_carta(c):
    naipe, valor = c
    return (ORDEM_NAIPE[naipe], PESO_VALOR[valor])


def valor_str(v):
    return str(v)


def carta_html(c):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = valor_str(valor)
    return (
        f'<div class="card">'
        f'<div class="tl" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'<div class="mid" style="color:{cor};">{naipe}</div>'
        f'<div class="br" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f"</div>"
    )


def card_btn_html(c, extra_class=""):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = valor_str(valor)
    cls = f"cardBtnInner {extra_class}".strip()
    return f"""
<div class="{cls}">
  <div class="cardBtnTL" style="color:{cor};">{vv}<br/>{naipe}</div>
  <div class="cardBtnMid" style="color:{cor};">{naipe}</div>
  <div class="cardBtnBR" style="color:{cor};">{vv}<br/>{naipe}</div>
</div>
"""


# =========================
# UTIL
# =========================
def ordem_da_mesa(nomes, mao_idx):
    return [nomes[(mao_idx + i) % len(nomes)] for i in range(len(nomes))]


def somente_trunfo(mao):
    return all(n == TRUNFO for (n, _) in mao) if mao else False


def tem_naipe(mao, naipe):
    return any(n == naipe for (n, _) in mao)


# =========================
# AVATAR CARTOON (SVG inline)
# =========================
def avatar_svg_data_uri(idx: int) -> str:
    skins = ["#F6D3B3", "#E9BE9D", "#D9A074", "#C6865F"]
    hairs = ["#2F2F2F", "#5B3A29", "#C8A14A", "#7A4B2B", "#1F2937"]
    shirts = ["#60A5FA", "#F59E0B", "#34D399", "#F472B6", "#A78BFA", "#FB7185", "#22C55E"]
    bg = ["#E0F2FE", "#ECFDF5", "#FFF7ED", "#FDF2F8", "#EEF2FF", "#F1F5F9"]

    skin = skins[idx % len(skins)]
    hair = hairs[idx % len(hairs)]
    shirt = shirts[idx % len(shirts)]
    b = bg[idx % len(bg)]

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <filter id="s" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity=".18"/>
    </filter>
  </defs>

  <circle cx="32" cy="32" r="30" fill="{b}" filter="url(#s)"/>

  <path d="M14 58c3-13 14-16 18-16s15 3 18 16" fill="{shirt}"/>
  <path d="M23 44c3 3 6 4 9 4s6-1 9-4" fill="none" stroke="rgba(0,0,0,.12)" stroke-width="2" stroke-linecap="round"/>

  <rect x="28" y="36" width="8" height="10" rx="4" fill="{skin}"/>
  <circle cx="32" cy="28" r="16" fill="{skin}"/>

  <path d="M16 28c2-12 10-18 16-18s14 6 16 18c-4-7-10-9-16-9s-12 2-16 9z" fill="{hair}"/>

  <circle cx="26" cy="28" r="2.2" fill="#111827"/>
  <circle cx="38" cy="28" r="2.2" fill="#111827"/>
  <circle cx="25.3" cy="27.4" r="0.7" fill="#fff"/>
  <circle cx="37.3" cy="27.4" r="0.7" fill="#fff"/>

  <path d="M26 34c2.2 2 4.4 3 6 3s3.8-1 6-3" fill="none" stroke="#111827" stroke-width="2" stroke-linecap="round"/>

  <circle cx="22" cy="33" r="2.1" fill="rgba(244,114,182,.35)"/>
  <circle cx="42" cy="33" r="2.1" fill="rgba(244,114,182,.35)"/>
</svg>
""".strip()

    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{svg_b64}"


# =========================
# IA: PROGNÓSTICO
# =========================
def ai_prognostico(mao, cartas_por_jogador: int) -> int:
    if not mao:
        return 0

    suit_counts = {"♠": 0, "♦": 0, "♣": 0, "♥": 0}
    for n, v in mao:
        suit_counts[n] += 1

    trumps = suit_counts["♥"]
    strength = 0.0
    strength += trumps * 0.95

    for n, v in mao:
        base = HIGH_POINTS.get(v, 0.0)
        strength += base * (1.35 if n == "♥" else 1.00)

    for s in ["♠", "♦", "♣"]:
        c = suit_counts[s]
        if c == 0:
            strength += 0.55 + (0.25 if trumps >= 2 else 0.0)
        elif c == 1:
            strength += 0.30 + (0.18 if trumps >= 2 else 0.0)
        elif c == 2:
            strength += 0.12

    distinct_nontrump_suits = sum(1 for s in ["♠", "♦", "♣"] if suit_counts[s] > 0)
    if trumps == 0 and distinct_nontrump_suits >= 3:
        strength -= 0.25

    expected = strength / 2.4
    expected += random.uniform(-0.25, 0.25)

    guess = int(round(expected))
    guess = max(0, min(cartas_por_jogador, guess))
    return guess


# =========================
# GAME CORE
# =========================
def distribuir(cartas_alvo: int):
    nomes = st.session_state.nomes
    n = len(nomes)
    baralho = criar_baralho()
    random.shuffle(baralho)

    usadas = cartas_alvo * n
    st.session_state.sobras_monte = len(baralho) - usadas
    st.session_state.cartas_alvo = cartas_alvo

    st.session_state.maos = {nome: [] for nome in nomes}
    for _ in range(cartas_alvo):
        for nome in nomes:
            st.session_state.maos[nome].append(baralho.pop())

    for nome in nomes:
        st.session_state.maos[nome] = sorted(st.session_state.maos[nome], key=peso_carta)

    if not st.session_state.mao_primeira_sorteada:
        st.session_state.mao_da_rodada = random.randint(0, n - 1)
        st.session_state.mao_primeira_sorteada = True
    else:
        st.session_state.mao_da_rodada = (st.session_state.mao_da_rodada + 1) % n

    st.session_state.prognosticos = {}
    st.session_state.progn_pre = {}
    st.session_state.progn_pos = {}
    st.session_state.vazas_rodada = {nome: 0 for nome in nomes}
    st.session_state.pile_counts = {nome: 0 for nome in nomes}

    st.session_state.fase = "prognostico"
    st.session_state.pontuou_rodada = False
    st.session_state.pending_play = None

    st.session_state.trick_pending = False
    st.session_state.trick_phase = None
    st.session_state.trick_resolve_at = 0.0
    st.session_state.trick_fly_until = 0.0
    st.session_state.trick_winner = None
    st.session_state.trick_snapshot = []


def preparar_prognosticos_anteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)
    prev = ordem[:pos_h]
    st.session_state.progn_pre = {n: ai_prognostico(st.session_state.maos[n], st.session_state.cartas_alvo) for n in prev}


def preparar_prognosticos_posteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)
    post = ordem[pos_h + 1 :]
    st.session_state.progn_pos = {n: ai_prognostico(st.session_state.maos[n], st.session_state.cartas_alvo) for n in post}


def iniciar_fase_jogo():
    nomes = st.session_state.nomes
    st.session_state.ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    st.session_state.turn_idx = 0
    st.session_state.naipe_base = None
    st.session_state.mesa = []
    st.session_state.primeira_vaza = True
    st.session_state.copas_quebrada = False
    st.session_state.fase = "jogo"


def cartas_validas_para_jogar(nome):
    mao = st.session_state.maos[nome]
    naipe_base = st.session_state.naipe_base
    primeira_vaza = st.session_state.primeira_vaza
    copas_quebrada = st.session_state.copas_quebrada

    if not mao:
        return []

    if naipe_base and tem_naipe(mao, naipe_base):
        return [c for c in mao if c[0] == naipe_base]

    if naipe_base and not tem_naipe(mao, naipe_base):
        if primeira_vaza and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]
        return mao[:]

    if naipe_base is None:
        if primeira_vaza:
            if somente_trunfo(mao):
                return mao[:]
            return [c for c in mao if c[0] != TRUNFO]
        if not copas_quebrada and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]

    return mao[:]


def jogar_carta(nome, carta):
    st.session_state.maos[nome].remove(carta)
    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta[0]
    if carta[0] == TRUNFO and not st.session_state.primeira_vaza:
        st.session_state.copas_quebrada = True
    st.session_state.mesa.append((nome, carta))
    st.session_state.table_pop_until = time.time() + 0.22


def vencedor_da_vaza(mesa_snapshot, naipe_base_snapshot):
    copas = [(n, c) for (n, c) in mesa_snapshot if c[0] == TRUNFO]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1][1]])[0]
    base = [(n, c) for (n, c) in mesa_snapshot if c[0] == naipe_base_snapshot]
    return max(base, key=lambda x: PESO_VALOR[x[1][1]])[0]


def schedule_trick_resolution():
    if st.session_state.trick_pending:
        return
    now = time.time()
    st.session_state.trick_pending = True
    st.session_state.trick_phase = "show"
    st.session_state.trick_snapshot = st.session_state.mesa[:]
    st.session_state.trick_winner = vencedor_da_vaza(st.session_state.trick_snapshot, st.session_state.naipe_base)
    show_seconds = 1.10
    fly_seconds = 0.55
    st.session_state.trick_resolve_at = now + show_seconds
    st.session_state.trick_fly_until = now + show_seconds + fly_seconds


def resolve_trick_if_due():
    if not st.session_state.trick_pending:
        return False

    now = time.time()

    if st.session_state.trick_phase == "show":
        if now < st.session_state.trick_resolve_at:
            return False
        st.session_state.trick_phase = "fly"
        return True

    if st.session_state.trick_phase == "fly":
        if now < st.session_state.trick_fly_until:
            return False

        win = st.session_state.trick_winner
        st.session_state.vazas_rodada[win] += 1
        st.session_state.pile_counts[win] = st.session_state.pile_counts.get(win, 0) + 1

        st.session_state.winner_flash_name = win
        st.session_state.winner_flash_until = time.time() + 1.2

        ordem = st.session_state.ordem
        st.session_state.turn_idx = ordem.index(win)
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.primeira_vaza = False

        st.session_state.trick_pending = False
        st.session_state.trick_phase = None
        st.session_state.trick_resolve_at = 0.0
        st.session_state.trick_fly_until = 0.0
        st.session_state.trick_winner = None
        st.session_state.trick_snapshot = []
        return True

    return False


def rodada_terminou():
    return all(len(st.session_state.maos[n]) == 0 for n in st.session_state.nomes)


def fim_de_rodada_pronto():
    return (
        rodada_terminou()
        and (not st.session_state.trick_pending)
        and (len(st.session_state.mesa) == 0)
    )


def pontuar_rodada():
    if st.session_state.pontuou_rodada:
        return
    for n in st.session_state.nomes:
        v = st.session_state.vazas_rodada.get(n, 0)
        p = v + (5 if st.session_state.prognosticos.get(n) == v else 0)
        st.session_state.pontos[n] = st.session_state.pontos.get(n, 0) + p
    st.session_state.pontuou_rodada = True


def ai_escolhe_carta(nome):
    validas = cartas_validas_para_jogar(nome)
    return random.choice(validas) if validas else None


def avancar_ate_humano_ou_fim():
    humano = st.session_state.nomes[st.session_state.humano_idx]
    ordem = st.session_state.ordem

    if st.session_state.trick_pending:
        return

    limit = 2500
    steps = 0
    while steps < limit:
        steps += 1

        if resolve_trick_if_due():
            return
        if st.session_state.trick_pending:
            return

        # garante animação da última vaza
        if rodada_terminou() and (not st.session_state.trick_pending):
            if len(st.session_state.mesa) == len(ordem):
                schedule_trick_resolution()
                return

        if fim_de_rodada_pronto():
            pontuar_rodada()
            if st.session_state.cartas_alvo <= 1:
                st.session_state.fase = "fim"
                st.session_state.show_final = True
                st.rerun()
            return

        atual = ordem[st.session_state.turn_idx]

        if len(st.session_state.maos[atual]) == 0:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        if atual == humano and len(st.session_state.maos[humano]) > 0:
            return

        carta = ai_escolhe_carta(atual)
        if carta is None:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        jogar_carta(atual, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

        if len(st.session_state.mesa) == len(ordem):
            schedule_trick_resolution()
            return


def start_next_round():
    if st.session_state.cartas_alvo <= 1:
        return
    st.session_state.rodada += 1
    prox = st.session_state.cartas_alvo - 1
    distribuir(prox)
    preparar_prognosticos_anteriores()


# =========================
# UI helpers: chips + pile
# =========================
def chip_color_for_index(idx: int) -> str:
    palette = [
        "rgba(16,185,129,.88)",
        "rgba(59,130,246,.88)",
        "rgba(245,158,11,.88)",
        "rgba(239,68,68,.88)",
        "rgba(168,85,247,.88)",
        "rgba(20,184,166,.88)",
        "rgba(100,116,139,.88)",
        "rgba(236,72,153,.88)",
    ]
    return palette[idx % len(palette)]


def render_progn_chips_html(prog, color: str) -> str:
    if isinstance(prog, str) or prog is None:
        return '<span class="chipNote">—</span>'
    p = max(0, int(prog))
    show = min(p, 12)
    chips = "".join([f'<div class="chipMini" style="--chip-base:{color};"></div>' for _ in range(show)])
    extra = f'<span class="chipNote">+{p-12}</span>' if p > 12 else ''
    return f'<div class="chipRow">{chips}</div>{extra}'


def render_small_pile_html(won: int) -> str:
    layers = min(max(won, 0), 10)
    parts = []
    for i in range(layers):
        dx = i * 1.1
        dy = -i * 1.2
        rot = (i % 3 - 1) * 2
        parts.append(f'<div class="cardBackLayer" style="left:{dx}px; top:{dy}px; transform: rotate({rot}deg);"></div>')
    label = f"{won}" if won > 10 else ""
    label_html = f'<div class="pileLabel">{label}</div>' if label else ''
    return f'<div class="pileStack">{"".join(parts)}</div>{label_html}'


# =========================
# HEADER (Title)
# =========================
st.markdown(
    """
<div class="titleRow">
  <div>
    <h1>🃏 Jogo de Prognóstico</h1>
    <div style="opacity:.70;font-weight:800;font-size:12px;color:rgba(255,255,255,.75);">
      Premium UI • Avatares cartoon • Montinho animado • Mobile Dock
    </div>
  </div>
  <div class="badges">
    <span class="badge">Trunfo: ♥</span>
    <span class="badge">1ª vaza: ♥ proibida</span>
    <span class="badge">Abrir com ♥ só após quebrar</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# TOPBAR (menu recolhível em cima)
# =========================
def render_topbar():
    if not st.session_state.ordem and st.session_state.started:
        st.session_state.ordem = ordem_da_mesa(st.session_state.nomes, st.session_state.mao_da_rodada)

    vez = "—"
    if st.session_state.started and st.session_state.ordem:
        st.session_state.turn_idx = st.session_state.turn_idx % len(st.session_state.ordem)
        vez = st.session_state.ordem[st.session_state.turn_idx]

    naipe_txt = st.session_state.naipe_base or "—"
    quebrada = "Sim" if st.session_state.copas_quebrada else "Não"
    primeira = "Sim" if st.session_state.primeira_vaza else "Não"

    st.markdown(
        f"""
<div class="topbar">
  <div class="topLeft">
    <div class="topTitle">🎮 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas</div>
    <div class="topSub">Vez: <b>{vez}</b></div>
  </div>
  <div class="topRight">
    <span class="pill pillInfo">Naipe {naipe_txt}</span>
    <span class="pill {'pillWarn' if quebrada=='Não' else 'pillGood'}">♥ quebrada: {quebrada}</span>
    <span class="pill pillInfo">1ª vaza: {primeira}</span>
    <span class="pill">Sobras {st.session_state.sobras_monte}</span>
  </div>
</div>
""",
        unsafe_allow_html=True
    )

    # Menu recolhível (controles + placar rápido) — fica acima da mesa, não dentro dela
    with st.expander("☰ Menu (placar + controles)", expanded=st.session_state.menu_open):
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            # Botão ícone: alternar tema
            icon = "✨" if st.session_state.theme != "neon" else "🌙"
            if st.button(icon, key="btn_theme", help="Alternar tema", use_container_width=True):
                st.session_state.theme = "classic" if st.session_state.theme == "neon" else "neon"
                st.session_state.menu_open = True
                st.rerun()

        with c2:
            if st.button("🔁", key="btn_restart_top", help="Reiniciar jogo", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                ss_init()
                st.rerun()

        with c3:
            st.session_state.menu_open = st.checkbox("Manter menu aberto", value=st.session_state.menu_open)

        st.markdown("---")

        # Botão topo: Próxima rodada (mesma regra do sidebar)
        if st.session_state.fase == "jogo" and fim_de_rodada_pronto():
            if st.session_state.cartas_alvo > 1:
                if st.button("➡️ Próxima rodada", use_container_width=True, key="btn_next_round_top"):
                    start_next_round()
                    st.rerun()
            else:
                pontuar_rodada()
                vencedor, pts = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)[0]
                st.success(f"🏆 Fim do jogo! {vencedor} com {pts} pts")


        st.markdown("### 📊 Placar (ao vivo)")
        if st.session_state.started:
            for n in st.session_state.nomes:
                st.session_state.pontos.setdefault(n, 0)
            ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
            df = pd.DataFrame([{"Posição": i + 1, "Jogador": n, "Pontos": p} for i, (n, p) in enumerate(ranking)])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Inicie uma partida para ver o placar.")


render_topbar()


# =========================
# SIDEBAR (placar principal)
# =========================
with st.sidebar:
    st.markdown("## 📊 Placar")

    if st.session_state.started:
        for n in st.session_state.nomes:
            st.session_state.pontos.setdefault(n, 0)

        ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
        for nome, pts in ranking:
            st.markdown(
                f"""
<div style="display:flex; justify-content:space-between; padding:8px 10px; border-radius:12px;
            border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.10); color:rgba(255,255,255,.90);
            margin-bottom:8px;">
  <div style="font-weight:900;">{nome}</div>
  <div style="font-weight:900;">{pts}</div>
</div>
""",
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div style="opacity:.75; font-size:12px; color:rgba(255,255,255,.80);">Rodada: {st.session_state.rodada} • Cartas/jogador: {st.session_state.cartas_alvo} • Sobras: {st.session_state.sobras_monte}</div>',
            unsafe_allow_html=True
        )

        if st.session_state.fase == "jogo" and fim_de_rodada_pronto():
            st.markdown("---")
            if st.session_state.cartas_alvo > 1:
                if st.button("➡️ Próxima rodada (-1 carta)", use_container_width=True, key="btn_next_round"):
                    start_next_round()
                    st.rerun()
            else:
                pontuar_rodada()
                vencedor, pts = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)[0]
                st.success(f"🏆 Fim do jogo! {vencedor} com {pts} pts")

        st.markdown("---")
        if st.button("🔁 Reiniciar", use_container_width=True, key="btn_restart_sidebar"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            ss_init()
            st.rerun()

    else:
        st.info("Inicie uma partida.")


# =========================
# SETUP
# =========================
if not st.session_state.started:
    st.markdown("### Configuração")
    nomes_txt = st.text_input(
        "Jogadores (separados por vírgula). O último será Você",
        value=", ".join(st.session_state.nomes),
        key="txt_players",
    )
    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True, key="btn_start")
    with colB:
        st.info("As cartas serão distribuídas igualmente. A cada rodada diminui 1 carta por jogador.")

    if start:
        nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
        if len(nomes) < 2:
            st.error("Informe pelo menos 2 jogadores.")
        else:
            st.session_state.nomes = nomes
            st.session_state.humano_idx = len(nomes) - 1
            st.session_state.pontos = {n: 0 for n in nomes}
            st.session_state.started = True

            n = len(nomes)
            cartas_inicio = 52 // n
            st.session_state.cartas_inicio = cartas_inicio
            st.session_state.cartas_alvo = cartas_inicio
            st.session_state.rodada = 1

            distribuir(cartas_inicio)
            preparar_prognosticos_anteriores()
            st.rerun()

    st.stop()


# =========================
# PROGNÓSTICO
# =========================
nomes = st.session_state.nomes
humano_nome = nomes[st.session_state.humano_idx]

if st.session_state.fase == "prognostico":
    ordem_preview = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    st.markdown(f"### 📌 Prognóstico — Rodada {st.session_state.rodada} ({st.session_state.cartas_alvo} cartas/jogador)")

    mao_humano = st.session_state.maos.get(humano_nome, [])
    st.markdown('<div class="handDock">', unsafe_allow_html=True)
    st.markdown(
        '<div class="handTitle"><h3>🃏 Suas cartas (prognóstico)</h3><div class="hint">Ordenadas por naipe e valor</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="display:flex; flex-wrap:wrap; gap:10px;">' + "".join(carta_html(c) for c in sorted(mao_humano, key=peso_carta)) + "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### ✅ Prognósticos visíveis (anteriores na mesa)")
    if not st.session_state.progn_pre:
        preparar_prognosticos_anteriores()

    vis = st.session_state.progn_pre
    if not vis:
        st.info("Você é o mão — ninguém fez prognóstico antes de você.")
    else:
        rows = [(n, vis[n]) for n in ordem_preview if n in vis]
        st.table({"Jogador": [r[0] for r in rows], "Prognóstico": [r[1] for r in rows]})

    palpite = st.number_input("Seu prognóstico", min_value=0, max_value=len(mao_humano), value=0, step=1, key="num_palpite")

    if st.button("Confirmar meu prognóstico", use_container_width=True, key="btn_confirm_progn"):
        st.session_state.prognosticos = {}
        st.session_state.prognosticos.update(st.session_state.progn_pre)
        st.session_state.prognosticos[humano_nome] = int(palpite)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        iniciar_fase_jogo()
        avancar_ate_humano_ou_fim()
        st.rerun()

    st.stop()


# =========================
# MESA + animação do montinho
# =========================
def seat_positions(ordem):
    n = len(ordem)
    cx, cy = 50, 50
    rx, ry = 42, 36
    pos = {}
    for i, nome in enumerate(ordem):
        ang = (2 * math.pi) * (i / n) - (math.pi / 2)
        x = cx + rx * math.cos(ang)
        y = cy + ry * math.sin(ang)
        tx = cx + (rx * 0.70) * math.cos(ang)
        ty = cy + (ry * 0.70) * math.sin(ang)
        pos[nome] = {"seat": (x, y), "target": (tx, ty)}
    return pos


def render_mesa():
    ordem = st.session_state.ordem
    n = len(ordem)
    humano = st.session_state.nomes[st.session_state.humano_idx]
    dealer = ordem[0]
    pos = seat_positions(ordem)

    now = time.time()
    flash_name = st.session_state.winner_flash_name if now <= st.session_state.winner_flash_until else None
    pop_active = now <= st.session_state.table_pop_until

    mesa_to_render = st.session_state.trick_snapshot if st.session_state.trick_pending else st.session_state.mesa
    naipe_base_show = st.session_state.naipe_base

    seats_html = ""
    chips_html = ""
    piles_html = ""
    plays_html = ""
    anim_css = ""

    for i, nome in enumerate(ordem):
        x, y = pos[nome]["seat"]
        tx, ty = pos[nome]["target"]

        cls = "seat"
        label = nome
        if nome == humano:
            cls += " you"
            label = f"{nome} (Você)"
        if nome == dealer:
            cls += " dealer"
            label = f"{label} • mão"
        if flash_name and nome == flash_name:
            cls += " winnerFlash"

        avatar_src = avatar_svg_data_uri(i)
        seats_html += f'''
<div class="{cls}" style="left:{x}%; top:{y}%; transform:translate(-50%,-50%);">
  <img class="avatarImg" src="{avatar_src}" alt="avatar"/>
  <span>{label}</span>
</div>
'''

        # chips (prognóstico) + pile (vazas ganhas)
        prog = st.session_state.prognosticos.get(nome, None)
        won = st.session_state.pile_counts.get(nome, 0)
        color = chip_color_for_index(i)

        chips_html += f"""
<div class="chipWrap" style="left:{tx}%; top:{ty}%;">
  {render_progn_chips_html(prog, color)}
</div>
"""

        if won > 0:
            px = tx
            py = ty + 12
            piles_html += f"""
<div class="pileWrap" style="left:{px}%; top:{py}%;">
  {render_small_pile_html(won)}
</div>
"""

    winner = st.session_state.trick_winner
    winner_target = None
    if winner:
        wx, wy = pos[winner]["target"]
        winner_target = (wx, wy + 12)

    for idx, (nome, carta) in enumerate(mesa_to_render):
        i = ordem.index(nome)
        ang = (2 * math.pi) * (i / n) - (math.pi / 2)
        cx, cy = 50, 50
        rx, ry = 42, 36
        x = cx + (rx * 0.47) * math.cos(ang)
        y = cy + (ry * 0.47) * math.sin(ang)

        is_last = (idx == len(mesa_to_render) - 1)
        cls = "playCard"
        extra_style = f"left:{x}%; top:{y}%;"

        if pop_active and is_last and not st.session_state.trick_pending:
            cls += " pop"

        if st.session_state.trick_pending and st.session_state.trick_phase == "fly" and winner_target:
            tx, ty = winner_target
            anim_name = f"flyToWinner_{idx}"
            anim_css += f"""
@keyframes {anim_name} {{
  0% {{ left:{x}%; top:{y}%; opacity:1; transform:translate(-50%,-50%) scale(1); }}
  70% {{ opacity:.85; }}
  100% {{ left:{tx}%; top:{ty}%; opacity:.22; transform:translate(-50%,-50%) scale(.70); }}
}}
"""
            extra_style = f"left:{x}%; top:{y}%; animation:{anim_name} .55s ease-in forwards;"

        plays_html += f'<div class="{cls}" style="{extra_style}">{carta_html(carta)}</div>'

    if st.session_state.trick_pending:
        centro_txt = "Vaza completa — mostrando..." if st.session_state.trick_phase == "show" else "Vaza completa — indo ao vencedor..."
    else:
        centro_txt = "Aguardando jogada" if not st.session_state.mesa else "Vaza em andamento"

    if naipe_base_show:
        centro_txt = f"{centro_txt} • Naipe: {naipe_base_show}"

    if anim_css.strip():
        st.markdown(f"<style>{anim_css}</style>", unsafe_allow_html=True)

    st.markdown('<div class="mesaWrap">', unsafe_allow_html=True)
    st.markdown(
    f"""
<div class="mesa">
  <div class="shimmer"></div>
  {seats_html}
  {chips_html}
  {piles_html}
  {plays_html}
  <div class="mesaCenter">{centro_txt}</div>
</div>
""",
    unsafe_allow_html=True
)
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# MÃO clicável
# =========================
def render_hand_clickable_streamlit():
    ordem = st.session_state.ordem
    humano = st.session_state.nomes[st.session_state.humano_idx]
    atual = ordem[st.session_state.turn_idx]
    mao = st.session_state.maos[humano]
    validas = set(cartas_validas_para_jogar(humano))

    st.markdown('<div class="handDock">', unsafe_allow_html=True)
    hint = "Clique numa carta válida" if atual == humano else "Aguardando sua vez (IA jogando...)"
    if st.session_state.trick_pending:
        hint = "Vaza completa — animação"
    st.markdown(f'<div class="handTitle"><h3>🂠 Sua mão</h3><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

    mao_ord = sorted(mao, key=peso_carta)
    if not mao_ord:
        st.markdown("</div>", unsafe_allow_html=True)
        return None

    clicked = None
    pending = st.session_state.pending_play

    # grade fixa (10 colunas) pra não esticar cartas
    cols = st.columns(10)

    for i, c in enumerate(mao_ord):
        disabled = (
            (c not in validas)
            or (atual != humano)
            or (pending is not None)
            or st.session_state.trick_pending
        )

        with cols[i % 10]:
            if st.button(" ", key=f"card_{st.session_state.rodada}_{c[0]}_{c[1]}_{i}", disabled=disabled):
                clicked = c

            extra = "flyAway" if (pending is not None and c == pending) else ""
            st.markdown(f'<div class="cardOverlay">{card_btn_html(c, extra_class=extra)}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


# =========================
# TELA FINAL
# =========================
def render_tela_final():
    st.markdown("## 🏁 Placar final")

    ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)

    linhas = []
    for i, (nome, pts) in enumerate(ranking, start=1):
        medalha = ""
        if i == 1:
            medalha = "🥇"
        elif i == 2:
            medalha = "🥈"
        elif i == 3:
            medalha = "🥉"

        linhas.append({"Posição": f"{medalha} {i}º".strip(), "Jogador": nome, "Pontos": pts})

    df = pd.DataFrame(linhas)
    st.dataframe(df, use_container_width=True, hide_index=True)

    vencedor, pts = ranking[0]
    st.success(f"🏆 Vencedor: {vencedor} com {pts} pontos!")

    # botão ícone com key fixa
    if st.button("🔁", use_container_width=True, key="btn_play_again", help="Jogar novamente"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        ss_init()
        st.rerun()


# =========================
# JOGO
# =========================
if st.session_state.fase == "jogo":

    # resolve animação se chegou a hora
    if resolve_trick_if_due():
        st.rerun()

    render_mesa()

    ordem = st.session_state.ordem
    atual = ordem[st.session_state.turn_idx]
    humano = st.session_state.nomes[st.session_state.humano_idx]

    # garante animação da última vaza antes de pontuar
    if rodada_terminou() and (not st.session_state.trick_pending) and (len(st.session_state.mesa) == len(ordem)):
        schedule_trick_resolution()
        st.rerun()

    if fim_de_rodada_pronto():
        pontuar_rodada()

        if st.session_state.cartas_alvo <= 1:
            st.session_state.fase = "fim"
            st.session_state.show_final = True
            st.rerun()

        st.success("✅ Rodada finalizada. Vá ao sidebar para continuar.")
        st.stop()

    if st.session_state.trick_pending:
        time.sleep(0.06)
        st.rerun()

    # autoplay IA
    if atual != humano and st.session_state.pending_play is None:
        now = time.time()
        if now - st.session_state.autoplay_last > 0.08:
            st.session_state.autoplay_last = now
            avancar_ate_humano_ou_fim()
            time.sleep(0.03)
            st.rerun()

    clicked = render_hand_clickable_streamlit()

    if clicked is not None:
        st.session_state.pending_play = clicked
        st.rerun()

    if st.session_state.pending_play is not None and atual == humano:
        st.markdown(
            '<div style="padding:10px 12px;border-radius:14px;border:1px solid rgba(255,255,255,.14);'
            'background:rgba(255,255,255,.10);color:rgba(255,255,255,.92);font-weight:900;margin-top:10px;">'
            '✨ Jogando carta...</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.18)

        carta = st.session_state.pending_play
        st.session_state.pending_play = None

        jogar_carta(humano, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

        if len(st.session_state.mesa) == len(ordem):
            schedule_trick_resolution()

        avancar_ate_humano_ou_fim()
        st.rerun()


# =========================
# FIM
# =========================
if st.session_state.fase == "fim" and st.session_state.show_final:
    render_tela_final()
    st.stop()
