# app.py
import random
import math
import time
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

# =========================
# CSS PREMIUM
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

/* Mesa */
.mesaWrap{ margin-top: 6px; }
.mesa{
  border-radius:20px;
  border:1px solid rgba(0,0,0,.10);
  background: radial-gradient(circle at 30% 20%, rgba(0,150,110,.30) 0%, rgba(0,120,90,.18) 28%, rgba(0,0,0,.03) 60%, rgba(0,0,0,.02) 100%);
  height: 470px;
  position:relative;
  overflow:hidden;
  box-shadow: 0 18px 40px rgba(0,0,0,.10);
}
.mesaCenter{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-weight:900; opacity:.62;
  pointer-events:none;
  text-transform: uppercase;
  letter-spacing: .08em;
}

/* Assentos (nomes sempre visíveis) */
.seat{
  position:absolute;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.84);
  border:1px solid rgba(0,0,0,.08);
  font-size:12px;
  white-space:nowrap;
  z-index: 8; /* acima de fichas/monte */
}
.seat.you{ outline:2px solid rgba(0,120,90,.55); font-weight:900; }
.seat.dealer{ border-color: rgba(0,120,90,.30); background: rgba(255,255,255,.94); }

/* Winner glow */
@keyframes winnerGlow {
  0% { box-shadow: 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }
  35% { box-shadow: 0 0 0 6px rgba(0,150,110,.20), 0 14px 28px rgba(0,0,0,.10); transform: translate(-50%,-50%) scale(1.03); }
  100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); transform: translate(-50%,-50%) scale(1); }
}
.seat.winnerFlash{
  animation: winnerGlow 1.2s ease-out;
  outline: 2px solid rgba(0,150,110,.55);
  background: rgba(255,255,255,.96);
}

/* Cartas na mesa (um pouco menores) */
.playCard{
  position:absolute;
  transform: translate(-50%,-50%);
  pointer-events:none;
  z-index: 6;
}
@keyframes popIn {
  0% { transform: translate(-50%,-50%) scale(.92); opacity: .0; }
  100% { transform: translate(-50%,-50%) scale(1.0); opacity: 1; }
}
.playCard.pop{ animation: popIn .16s ease-out; }

/* Carta (frente) menor */
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

/* =========================
   MONTINHO EM CAMADAS
   ========================= */
.pileWrap{ position:absolute; transform: translate(-50%,-50%); z-index: 5; }
.pileStack{ position:relative; width:46px; height:68px; }
.cardBackLayer{
  position:absolute;
  width:46px; height:68px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.14);
  background: linear-gradient(180deg, rgba(0,120,90,.95) 0%, rgba(0,90,70,.95) 100%);
  box-shadow: 0 10px 16px rgba(0,0,0,.12);
  overflow:hidden;
}
.cardBackLayer:before{
  content:"";
  position:absolute; inset:-22%;
  background: repeating-linear-gradient(45deg, rgba(255,255,255,.16) 0 8px, rgba(255,255,255,0) 8px 16px);
  transform: rotate(12deg);
}
.pileLabel{
  margin-top:6px;
  text-align:center;
  font-weight:900;
  font-size:11px;
  opacity:.72;
}

/* Ficha do prognóstico (menor e mais “pra dentro”) */
.tokenWrap{ position:absolute; transform: translate(-50%,-50%); z-index: 4; }
.token{
  min-width: 104px;
  padding:7px 9px;
  border-radius: 16px;
  border:1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.84);
  box-shadow: 0 12px 24px rgba(0,0,0,.10);
  text-align:center;
}
.tokenTitle{ font-size:10px; font-weight:900; opacity:.70; letter-spacing:.06em; text-transform:uppercase; }
.tokenValue{ font-size:16px; font-weight:900; margin-top:2px; }
.tokenSub{ font-size:10px; font-weight:900; opacity:.70; margin-top:3px; }

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

/* Botão-carta (Streamlit) */
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

/* Animação: carta sumindo da mão */
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

        "trick_pending": False,
        "trick_resolve_at": 0.0,
        "trick_winner": None,
        "trick_snapshot": [],

        "pile_counts": {},
    }
    for k,v in defaults.items():
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
    st.session_state.trick_resolve_at = 0.0
    st.session_state.trick_winner = None
    st.session_state.trick_snapshot = []

def preparar_prognosticos_anteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)
    prev = ordem[:pos_h]
    st.session_state.progn_pre = {n: random.randint(0, len(st.session_state.maos[n])) for n in prev}

def preparar_prognosticos_posteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)
    post = ordem[pos_h+1:]
    st.session_state.progn_pos = {n: random.randint(0, len(st.session_state.maos[n])) for n in post}

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
    copas = [(n,c) for (n,c) in mesa_snapshot if c[0] == TRUNFO]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1][1]])[0]
    base = [(n,c) for (n,c) in mesa_snapshot if c[0] == naipe_base_snapshot]
    return max(base, key=lambda x: PESO_VALOR[x[1][1]])[0]

def schedule_trick_resolution(delay_seconds=1.4):
    if st.session_state.trick_pending:
        return
    st.session_state.trick_pending = True
    st.session_state.trick_resolve_at = time.time() + float(delay_seconds)
    st.session_state.trick_snapshot = st.session_state.mesa[:]
    st.session_state.trick_winner = vencedor_da_vaza(st.session_state.trick_snapshot, st.session_state.naipe_base)

def resolve_trick_if_due():
    if not st.session_state.trick_pending:
        return False
    if time.time() < st.session_state.trick_resolve_at:
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
    st.session_state.trick_resolve_at = 0.0
    st.session_state.trick_winner = None
    st.session_state.trick_snapshot = []
    return True

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
            pass
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
            schedule_trick_resolution(delay_seconds=1.4)
            return

def start_next_round():
    if st.session_state.cartas_alvo <= 1:
        return
    st.session_state.rodada += 1
    prox = st.session_state.cartas_alvo - 1
    distribuir(prox)
    preparar_prognosticos_anteriores()

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
    <div style="opacity:.70;font-weight:800;font-size:12px;">Montinhos em camadas • Cartas menores • Nomes sempre visíveis</div>
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
# UI: Mesa + fichas + montes em camadas
# =========================
def render_pile_layers_html(won: int):
    """
    Renderiza montinho em camadas (até 6 camadas visuais).
    Ex.: won=1 => 1 camada, won=8 => 6 camadas.
    """
    layers = min(max(won, 0), 6)
    parts = []
    for i in range(layers):
        # deslocamento em "escadinha" (para parecer pilha)
        dx = i * 2
        dy = -i * 2
        rot = (i % 3 - 1) * 2  # -2,0,2 graus
        parts.append(
            f'<div class="cardBackLayer" style="left:{dx}px; top:{dy}px; transform: rotate({rot}deg);"></div>'
        )
    label = f"{won}" if won > 6 else ""  # se passar de 6, mostra número; senão deixa só visual
    label_html = f'<div class="pileLabel">{label}</div>' if label else '<div class="pileLabel"></div>'
    return f'<div class="pileStack">{"".join(parts)}</div>{label_html}'

def render_mesa():
    ordem = st.session_state.ordem
    n = len(ordem)
    humano = st.session_state.nomes[st.session_state.humano_idx]
    dealer = ordem[0]

    now = time.time()
    flash_name = st.session_state.winner_flash_name if now <= st.session_state.winner_flash_until else None
    pop_active = now <= st.session_state.table_pop_until

    mesa_to_render = st.session_state.trick_snapshot if st.session_state.trick_pending else st.session_state.mesa
    naipe_base_show = st.session_state.naipe_base

    cx, cy = 50, 50
    rx, ry = 42, 36

    seats_html = ""
    tokens_html = ""
    piles_html = ""
    plays_html = ""

    pos_map = {nome:i for i,nome in enumerate(ordem)}

    for i, nome in enumerate(ordem):
        ang = (2*math.pi) * (i/n) - (math.pi/2)

        # Nome fica mais pra fora
        x = cx + rx*math.cos(ang)
        y = cy + ry*math.sin(ang)

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

        seats_html += f'<div class="{cls}" style="left:{x}%; top:{y}%; transform:translate(-50%,-50%);">{label}</div>'

        # Ficha mais pra dentro (deixa nome livre)
        tx = cx + (rx*0.72)*math.cos(ang)
        ty = cy + (ry*0.72)*math.sin(ang)

        prog = st.session_state.prognosticos.get(nome, "-")
        won = st.session_state.pile_counts.get(nome, 0)

        tokens_html += f"""
<div class="tokenWrap" style="left:{tx}%; top:{ty}%;">
  <div class="token">
    <div class="tokenTitle">PROGNÓSTICO</div>
    <div class="tokenValue">{prog}</div>
    <div class="tokenSub">Vazas: {won}</div>
  </div>
</div>
"""

        # Montinho em camadas mais pra dentro ainda (abaixo da ficha)
        if won > 0:
            px = tx
            py = ty + 12
            piles_html += f"""
<div class="pileWrap" style="left:{px}%; top:{py}%;">
  {render_pile_layers_html(won)}
</div>
"""

    # Cartas na mesa, ainda mais perto do centro (para não conflitar)
    for idx, (nome, carta) in enumerate(mesa_to_render):
        i = pos_map.get(nome, 0)
        ang = (2*math.pi) * (i/n) - (math.pi/2)
        x = cx + (rx*0.47)*math.cos(ang)
        y = cy + (ry*0.47)*math.sin(ang)

        is_last = (idx == len(mesa_to_render) - 1)
        cls = "playCard"
        if pop_active and is_last and not st.session_state.trick_pending:
            cls += " pop"
        plays_html += f'<div class="{cls}" style="left:{x}%; top:{y}%;">{carta_html(carta)}</div>'

    if st.session_state.trick_pending:
        centro_txt = "Vaza completa — aguardando..."
    else:
        centro_txt = "Aguardando jogada" if not st.session_state.mesa else "Vaza em andamento"
    if naipe_base_show:
        centro_txt = f"{centro_txt} • Naipe: {naipe_base_show}"

    st.markdown('<div class="mesaWrap">', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="mesa">
  {seats_html}
  {tokens_html}
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
    hint = "Clique numa carta válida" if atual == humano else "Aguardando sua vez"
    if st.session_state.trick_pending:
        hint = "Vaza completa — aguardando 1–2s"
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

    if resolve_trick_if_due():
        st.rerun()

    render_mesa()

    ordem = st.session_state.ordem
    atual = ordem[st.session_state.turn_idx]

    st.info(
        f"🎯 Vez de: **{atual}** | Naipe: **{st.session_state.naipe_base or '-'}** | "
        f"♥ quebrada: **{'Sim' if st.session_state.copas_quebrada else 'Não'}** | "
        f"1ª vaza: **{'Sim' if st.session_state.primeira_vaza else 'Não'}**"
    )

    if rodada_terminou():
        pontuar_rodada()
        st.success("✅ Rodada finalizada. Vá ao sidebar para iniciar a próxima.")
        st.stop()

    humano = st.session_state.nomes[st.session_state.humano_idx]

    if st.session_state.trick_pending:
        time.sleep(0.15)
        st.rerun()

    if atual != humano and st.session_state.pending_play is None:
        if st.button("▶️ Continuar (IA)", use_container_width=True):
            avancar_ate_humano_ou_fim()
            st.rerun()

    clicked = render_hand_clickable_streamlit()

    if clicked is not None:
        st.session_state.pending_play = clicked
        st.rerun()

    if st.session_state.pending_play is not None and atual == humano:
        st.markdown('<div class="playingOverlay">✨ Jogando carta...</div>', unsafe_allow_html=True)
        time.sleep(0.25)

        carta = st.session_state.pending_play
        st.session_state.pending_play = None

        jogar_carta(humano, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

        if len(st.session_state.mesa) == len(ordem):
            schedule_trick_resolution(delay_seconds=1.4)

        avancar_ate_humano_ou_fim()
        st.rerun()

# =========================
# PROGNÓSTICO / SETUP (final)
# =========================
# (já tratado acima)
