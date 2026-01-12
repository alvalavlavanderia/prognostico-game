# app.py
import random
import math
import time
import base64
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

# =========================
# CSS PREMIUM (felt verde + mini-monte + avatar imagem + animação do montinho)
# + HUD compacto (modo app)
# =========================
APP_CSS = """
<style>
.block-container { padding-top: .8rem !important; padding-bottom: .8rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: .4rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 20% 10%, rgba(0,150,110,.10), transparent 40%); }

/* Header */
.titleRow{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom: 6px; }
.titleRow h1{ margin:0; font-size: 28px; }
.badges{ display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.badge{ display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; background:rgba(0,0,0,.06); font-size:12px; font-weight:800; }

/* HUD compacto (modo app) */
.hudBar{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  align-items:center;
  justify-content:space-between;
  margin: 10px 0 10px 0;
}
.hudLeft, .hudRight{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  align-items:center;
}
.hudChip{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:8px 10px;
  border-radius:999px;
  border:1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 24px rgba(0,0,0,.08);
  font-weight:900;
  font-size:12px;
}
.hudChip .k{ opacity:.65; font-weight:900; }
.hudChip .v{ font-weight:900; }
.hudDot{
  width:10px; height:10px; border-radius:50%;
  background: rgba(16,185,129,.88);
  box-shadow: 0 6px 14px rgba(0,0,0,.12);
}
.hudDot.red{ background: rgba(239,68,68,.88); }
.hudDot.gray{ background: rgba(100,116,139,.88); }
.hudDot.blue{ background: rgba(59,130,246,.88); }
.hudDot.gold{ background: rgba(245,158,11,.92); }

.hudSpacer{ height: 2px; }

/* Mesa (felt verde profissional) */
.mesaWrap{ margin-top: 6px; }
.mesa{
  border-radius:22px;
  border:1px solid rgba(0,0,0,.14);

  background:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,.12) 0%, rgba(255,255,255,0) 42%),
    radial-gradient(circle at 70% 80%, rgba(0,0,0,.10) 0%, rgba(0,0,0,0) 48%),
    linear-gradient(180deg, rgba(18,90,55,1) 0%, rgba(13,72,45,1) 55%, rgba(10,58,36,1) 100%);

  height: 470px;
  position:relative;
  overflow:hidden;
  box-shadow: 0 18px 42px rgba(0,0,0,.18);
}
.mesa:before{
  content:"";
  position:absolute; inset:0;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.018) 0 1px, rgba(255,255,255,0) 1px 3px),
    repeating-linear-gradient(90deg, rgba(0,0,0,.016) 0 1px, rgba(0,0,0,0) 1px 4px);
  opacity:.55;
  pointer-events:none;
}
.mesa:after{
  content:"";
  position:absolute; inset:14px;
  border-radius:18px;
  border:1px solid rgba(255,255,255,.10);
  pointer-events:none;
}
.mesaCenter{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-weight:900; opacity:.58;
  pointer-events:none;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(255,255,255,.90);
}

/* Assentos (nome + avatar sempre visíveis) */
.seat{
  position:absolute;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.88);
  border:1px solid rgba(0,0,0,.10);
  font-size:12px;
  white-space:nowrap;
  z-index: 25;
  display:flex;
  align-items:center;
  gap:8px;
}
.seat.you{ outline:2px solid rgba(34,197,94,.55); font-weight:900; }
.seat.dealer{ border-color: rgba(34,197,94,.35); background: rgba(255,255,255,.95); }

/* Avatar imagem cartoon */
.avatarImg{
  width:26px; height:26px;
  border-radius:50%;
  border: 1px solid rgba(0,0,0,.12);
  background: rgba(0,0,0,.04);
  box-shadow: 0 6px 12px rgba(0,0,0,.10);
  flex: 0 0 auto;
}

/* Winner glow */
@keyframes winnerGlow {
  0% { box-shadow: 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }
  35% { box-shadow: 0 0 0 6px rgba(34,197,94,.22), 0 14px 28px rgba(0,0,0,.14); transform: translate(-50%,-50%) scale(1.03); }
  100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }
}
.seat.winnerFlash{
  animation: winnerGlow 1.2s ease-out;
  outline: 2px solid rgba(34,197,94,.55);
  background: rgba(255,255,255,.97);
}

/* Cartas na mesa */
.playCard{
  position:absolute;
  transform: translate(-50%,-50%);
  pointer-events:none;
  z-index: 18;
}
@keyframes popIn {
  0% { transform: translate(-50%,-50%) scale(.92); opacity: .0; }
  100% { transform: translate(-50%,-50%) scale(1.0); opacity: 1; }
}
.playCard.pop{ animation: popIn .16s ease-out; }

/* Carta (frente) */
.card{
  width:70px;
  height:102px;
  border-radius:14px;
  border:1px solid rgba(0,0,0,.16);
  background: linear-gradient(180deg, #ffffff 0%, #f8f8f8 100%);
  box-shadow: 0 10px 22px rgba(0,0,0,.12);
  position:relative;
  user-select:none;
}
.card .tl{ position:absolute; top:7px; left:7px; font-weight:900; font-size:13px; line-height:13px; }
.card .br{ position:absolute; bottom:7px; right:7px; font-weight:900; font-size:13px; line-height:13px; transform:rotate(180deg); }
.card .mid{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:900; opacity:.92; }

/* Chips pequenos */
.chipWrap{ position:absolute; transform: translate(-50%,-50%); z-index: 16; }
.chipRow{ display:flex; gap:6px; flex-wrap:wrap; justify-content:center; max-width: 140px; }
.chipMini{
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
}
.chipMini:after{
  content:"";
  position:absolute;
  inset:5px;
  border-radius:50%;
  background: rgba(255,255,255,.78);
  border: 1px solid rgba(0,0,0,.10);
}
.chipNote{
  margin-top: 6px;
  font-size: 10px;
  font-weight: 900;
  opacity: .72;
  background: rgba(255,255,255,.76);
  border: 1px solid rgba(0,0,0,.08);
  padding: 3px 8px;
  border-radius: 999px;
  display:inline-block;
}

/* Montinho mini-cartas (bem pequeno) */
.pileWrap{ position:absolute; transform: translate(-50%,-50%); z-index: 15; }
.pileStack{ position:relative; width:26px; height:40px; }
.cardBackLayer{
  position:absolute;
  width:26px; height:40px;
  border-radius:8px;
  border:1px solid rgba(0,0,0,.18);
  background: linear-gradient(180deg, rgba(12,110,80,.95) 0%, rgba(7,86,64,.95) 100%);
  box-shadow: 0 6px 10px rgba(0,0,0,.12);
  overflow:hidden;
}
.cardBackLayer:before{
  content:"";
  position:absolute; inset:-28%;
  background: repeating-linear-gradient(45deg, rgba(255,255,255,.12) 0 8px, rgba(255,255,255,0) 8px 16px);
  transform: rotate(14deg);
}
.pileLabel{
  margin-top:4px;
  text-align:center;
  font-weight:900;
  font-size:10px;
  opacity:.74;
  color: rgba(255,255,255,.92);
  text-shadow: 0 2px 6px rgba(0,0,0,.25);
}

/* Dock da mão */
.handDock{
  margin-top: 12px;
  border-radius: 18px;
  border:1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.75);
  backdrop-filter: blur(8px);
  box-shadow: 0 14px 34px rgba(0,0,0,.08);
  padding: 12px;
}
.handTitle{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 6px; }
.handTitle h3{ margin:0; font-size:16px; }
.hint{ font-size:12px; opacity:.70; font-weight:800; }

/* Botão-carta */
div[data-testid="column"] .stButton > button{
  border-radius: 14px !important;
  border: 1px solid rgba(0,0,0,.18) !important;
  background: linear-gradient(180deg, #ffffff 0%, #f9f9f9 100%) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.12) !important;
  min-height: 118px !important;
  width: 100% !important;
  padding: 0 !important;
  transition: transform .10s ease, box-shadow .10s ease, opacity .10s ease;
}
div[data-testid="column"] .stButton > button:hover{
  transform: translateY(-4px);
  box-shadow: 0 14px 26px rgba(0,0,0,.16) !important;
}
div[data-testid="column"] .stButton > button:disabled{
  opacity: .28 !important;
  transform:none !important;
  box-shadow: 0 6px 14px rgba(0,0,0,.08) !important;
}

/* Face da carta dentro do botão */
.cardBtnInner{
  width:100%;
  height:118px;
  position:relative;
  border-radius:14px;
  overflow:hidden;
}
.cardBtnTL{
  position:absolute; top:10px; left:10px;
  font-weight:900; font-size:14px; line-height:14px;
}
.cardBtnBR{
  position:absolute; bottom:10px; right:10px;
  font-weight:900; font-size:14px; line-height:14px;
  transform: rotate(180deg);
}
.cardBtnMid{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-size:34px; font-weight:900; opacity:.92;
}

/* Animação: carta sumindo */
@keyframes flyAway {
  0%   { transform: translateY(0px) scale(1); opacity: 1; }
  55%  { transform: translateY(-26px) scale(1.03); opacity: .85; }
  100% { transform: translateY(-70px) scale(.96); opacity: 0; }
}
.flyAway{ animation: flyAway .25s ease-in forwards; }

/* Overlay */
.playingOverlay{
  display:flex; align-items:center; gap:10px;
  padding:10px 12px; border-radius:14px;
  border:1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.85);
  font-weight:900;
  margin-top: 10px;
}

/* Sidebar */
.scoreItem{
  display:flex; justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.06);
  background:rgba(255,255,255,.70);
  margin-bottom:8px;
}
.scoreName{ font-weight:900; }
.scorePts{ font-weight:900; }
.smallMuted{ opacity:.70; font-size:12px; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# BARALHO / REGRAS
# =========================
VALORES = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
PESO_VALOR = {v:i for i,v in enumerate(VALORES)}
COR_NAIPE = {"♦":"#C1121F", "♥":"#C1121F", "♠":"#111827", "♣":"#111827"}
ORDEM_NAIPE = {"♦":0, "♠":1, "♣":2, "♥":3}
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
        f'</div>'
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
# IA: PROGNÓSTICO MAIS AVANÇADO
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
        strength += (base * 1.35) if n == "♥" else (base * 1.00)

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
# STATE
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

        "fase": "setup",

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

        # Animação da vaza indo pro vencedor
        "trick_pending": False,
        "trick_phase": None,          # "show" -> "fly"
        "trick_resolve_at": 0.0,      # quando sai do show e entra no fly
        "trick_fly_until": 0.0,       # quando termina o fly e contabiliza
        "trick_winner": None,
        "trick_snapshot": [],

        "pile_counts": {},

        # autoplay
        "autoplay_last": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

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
    st.session_state.progn_pre = {
        n: ai_prognostico(st.session_state.maos[n], st.session_state.cartas_alvo)
        for n in prev
    }

def preparar_prognosticos_posteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)
    post = ordem[pos_h+1:]
    st.session_state.progn_pos = {
        n: ai_prognostico(st.session_state.maos[n], st.session_state.cartas_alvo)
        for n in post
    }

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

    # Seguir naipe se tiver
    if naipe_base and tem_naipe(mao, naipe_base):
        return [c for c in mao if c[0] == naipe_base]

    # Não tem naipe base
    if naipe_base and not tem_naipe(mao, naipe_base):
        # 1ª vaza: não pode jogar trunfo se tiver outras (exceto só trunfo)
        if primeira_vaza and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]
        return mao[:]

    # Mão abrindo
    if naipe_base is None:
        if primeira_vaza:
            if somente_trunfo(mao):
                return mao[:]
            return [c for c in mao if c[0] != TRUNFO]
        # após 1ª vaza: só pode abrir com trunfo se já quebrou ou só trunfo
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

        if rodada_terminou():
            pontuar_rodada()
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
        "rgba(16,185,129,.88)",   # verde
        "rgba(59,130,246,.88)",   # azul
        "rgba(245,158,11,.88)",   # âmbar
        "rgba(239,68,68,.88)",    # vermelho
        "rgba(168,85,247,.88)",   # roxo
        "rgba(20,184,166,.88)",   # teal
        "rgba(100,116,139,.88)",  # slate
        "rgba(236,72,153,.88)",   # pink
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
        parts.append(
            f'<div class="cardBackLayer" style="left:{dx}px; top:{dy}px; transform: rotate({rot}deg);"></div>'
        )
    label = f"{won}" if won > 10 else ""
    label_html = f'<div class="pileLabel">{label}</div>' if label else ''
    return f'<div class="pileStack">{"".join(parts)}</div>{label_html}'

# =========================
# HUD (modo app)
# =========================
def render_hud():
    ordem = st.session_state.ordem
    humano = st.session_state.nomes[st.session_state.humano_idx]
    atual = ordem[st.session_state.turn_idx]
    naipe = st.session_state.naipe_base or "—"

    dot_turn = "gold" if atual == humano else "blue"
    dot_heart = "red" if st.session_state.copas_quebrada else "gray"
    dot_first = "gold" if st.session_state.primeira_vaza else "gray"

    mao_len = len(st.session_state.maos.get(humano, []))
    mesa_len = len(st.session_state.mesa)
    sobras = st.session_state.sobras_monte
    cartas_rodada = st.session_state.cartas_alvo

    st.markdown(
        f"""
<div class="hudBar">
  <div class="hudLeft">
    <div class="hudChip"><span class="hudDot {dot_turn}"></span><span class="k">Vez</span><span class="v">{atual}</span></div>
    <div class="hudChip"><span class="hudDot gray"></span><span class="k">Naipe</span><span class="v">{naipe}</span></div>
    <div class="hudChip"><span class="hudDot {dot_heart}"></span><span class="k">♥ quebrada</span><span class="v">{"Sim" if st.session_state.copas_quebrada else "Não"}</span></div>
    <div class="hudChip"><span class="hudDot {dot_first}"></span><span class="k">1ª vaza</span><span class="v">{"Sim" if st.session_state.primeira_vaza else "Não"}</span></div>
  </div>

  <div class="hudRight">
    <div class="hudChip"><span class="hudDot gray"></span><span class="k">Sua mão</span><span class="v">{mao_len}</span></div>
    <div class="hudChip"><span class="hudDot gray"></span><span class="k">Na vaza</span><span class="v">{mesa_len}/{len(ordem)}</span></div>
    <div class="hudChip"><span class="hudDot gray"></span><span class="k">Cartas/rodada</span><span class="v">{cartas_rodada}</span></div>
    <div class="hudChip"><span class="hudDot gray"></span><span class="k">Sobras</span><span class="v">{sobras}</span></div>
  </div>
</div>
<div class="hudSpacer"></div>
""",
        unsafe_allow_html=True
    )

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 📊 Placar")
    if st.session_state.started:
        for n in st.session_state.nomes:
            st.session_state.pontos.setdefault(n, 0)

        ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
        for nome, pts in ranking:
            st.markdown(
                f'<div class="scoreItem"><div class="scoreName">{nome}</div><div class="scorePts">{pts}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="smallMuted">Rodada: {st.session_state.rodada} • Cartas/jogador: {st.session_state.cartas_alvo} • Sobras: {st.session_state.sobras_monte}</div>',
            unsafe_allow_html=True
        )

        if st.session_state.fase == "jogo" and rodada_terminou():
            st.markdown("---")
            if st.session_state.cartas_alvo > 1:
                if st.button("➡️ Próxima rodada (-1 carta)", use_container_width=True):
                    start_next_round()
                    st.rerun()
            else:
                vencedor, pts = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)[0]
                st.success(f"🏆 Fim do jogo! {vencedor} com {pts} pts")

        st.markdown("---")
        if st.button("🔁 Reiniciar", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            ss_init()
            st.rerun()
    else:
        st.info("Inicie uma partida.")

# =========================
# HEADER
# =========================
st.markdown(
    """
<div class="titleRow">
  <div>
    <h1>🃏 Jogo de Prognóstico</h1>
    <div style="opacity:.70;font-weight:800;font-size:12px;">Premium UI • Avatares cartoon • Montinho animado</div>
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
# SETUP
# =========================
if not st.session_state.started:
    st.markdown("### Configuração")
    nomes_txt = st.text_input("Jogadores (separados por vírgula). O último será Você", value=", ".join(st.session_state.nomes))
    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with colB:
        st.info("As cartas serão distribuídas igualmente até acabar o baralho (sobras no monte). A cada rodada diminui 1 carta por jogador.")

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
    st.markdown(f"### 📌 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas por jogador")

    mao_humano = st.session_state.maos.get(humano_nome, [])
    st.markdown('<div class="handDock">', unsafe_allow_html=True)
    st.markdown('<div class="handTitle"><h3>🃏 Suas cartas (prognóstico)</h3><div class="hint">Ordenadas por naipe e valor</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex; flex-wrap:wrap; gap:10px;">' + "".join(carta_html(c) for c in sorted(mao_humano, key=peso_carta)) + "</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### ✅ Prognósticos visíveis (anteriores na mesa)")
    if not st.session_state.progn_pre:
        preparar_prognosticos_anteriores()

    vis = st.session_state.progn_pre
    if not vis:
        st.info("Você é o mão — ninguém fez prognóstico antes de você.")
    else:
        rows = [(n, vis[n]) for n in ordem_preview if n in vis]
        st.table({"Jogador": [r[0] for r in rows], "Prognóstico": [r[1] for r in rows]})

    palpite = st.number_input("Seu prognóstico", min_value=0, max_value=len(mao_humano), value=0, step=1)

    if st.button("Confirmar meu prognóstico", use_container_width=True):
        st.session_state.prognosticos = {}
        st.session_state.prognosticos.update(st.session_state.progn_pre)
        st.session_state.prognosticos[humano_nome] = int(palpite)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        iniciar_fase_jogo()
        avancar_ate_humano_ou_fim()
        st.rerun()

# =========================
# RENDER MESA + animação do "montinho voando"
# =========================
def seat_positions(ordem):
    n = len(ordem)
    cx, cy = 50, 50
    rx, ry = 42, 36
    pos = {}
    for i, nome in enumerate(ordem):
        ang = (2*math.pi) * (i/n) - (math.pi/2)
        x = cx + rx*math.cos(ang)
        y = cy + ry*math.sin(ang)
        tx = cx + (rx*0.70)*math.cos(ang)
        ty = cy + (ry*0.70)*math.sin(ang)
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

    if st.session_state.trick_pending:
        mesa_to_render = st.session_state.trick_snapshot
    else:
        mesa_to_render = st.session_state.mesa

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
        ang = (2*math.pi) * (i/n) - (math.pi/2)
        cx, cy = 50, 50
        rx, ry = 42, 36
        x = cx + (rx*0.47)*math.cos(ang)
        y = cy + (ry*0.47)*math.sin(ang)

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
            cls = "playCard"

        plays_html += f'<div class="{cls}" style="{extra_style}">{carta_html(carta)}</div>'

    if st.session_state.trick_pending:
        if st.session_state.trick_phase == "show":
            centro_txt = "Vaza completa — mostrando..."
        else:
            centro_txt = "Vaza completa — indo ao vencedor..."
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
  {seats_html}
  {chips_html}
  {piles_html}
  {plays_html}
  <div class="mesaCenter">{centro_txt}</div>
</div>
""",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

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
    cols = st.columns(10)
    clicked = None
    pending = st.session_state.pending_play

    for i, c in enumerate(mao_ord):
        disabled = (
            (c not in validas) or
            (atual != humano) or
            (pending is not None) or
            st.session_state.trick_pending
        )
        with cols[i % 10]:
            if st.button(" ", key=f"card_{st.session_state.rodada}_{c[0]}_{c[1]}_{i}", disabled=disabled, use_container_width=True):
                clicked = c
            extra = "flyAway" if (pending is not None and c == pending) else ""
            st.markdown(card_btn_html(c, extra_class=extra), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return clicked

# =========================
# JOGO
# =========================
if st.session_state.fase == "jogo":
    st.markdown(f"### 🎮 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas por jogador")

    # controla fases da animação (show->fly->contabiliza)
    if resolve_trick_if_due():
        st.rerun()

    # HUD compacto (SUBSTITUI o st.info grandão)
    render_hud()

    render_mesa()

    ordem = st.session_state.ordem
    atual = ordem[st.session_state.turn_idx]
    humano = st.session_state.nomes[st.session_state.humano_idx]

    if rodada_terminou():
        pontuar_rodada()
        st.success("✅ Rodada finalizada. Vá ao sidebar para iniciar a próxima.")
        st.stop()

    if st.session_state.trick_pending:
        time.sleep(0.06)
        st.rerun()

    # AUTOPLAY IA (sem botão)
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
        st.markdown('<div class="playingOverlay">✨ Jogando carta...</div>', unsafe_allow_html=True)
        time.sleep(0.18)

        carta = st.session_state.pending_play
        st.session_state.pending_play = None

        jogar_carta(humano, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

        if len(st.session_state.mesa) == len(ordem):
            schedule_trick_resolution()

        avancar_ate_humano_ou_fim()
        st.rerun()
