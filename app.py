# app.py
import random
import math
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

APP_CSS = """
<style>
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: 0.5rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* cards */
.handRow{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  align-items:flex-start;
}
.card{
  width:72px;
  height:104px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.15);
  box-shadow:0 8px 18px rgba(0,0,0,.10);
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfb 100%);
  position:relative;
  user-select:none;
}
.card .tl{ position:absolute; top:8px; left:8px; font-weight:800; font-size:14px; line-height:14px; }
.card .br{ position:absolute; bottom:8px; right:8px; font-weight:800; font-size:14px; line-height:14px; transform:rotate(180deg); }
.card .mid{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:800; opacity:.95; }

.badge{ display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(0,0,0,.06); font-size:12px; }
.topbar{ display:flex; gap:10px; flex-wrap:wrap; margin: 2px 0 10px 0; }
.titleRow{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 4px; }
.titleRow h1{ margin:0; }
.panel{ border:1px solid rgba(0,0,0,.08); border-radius:14px; padding:14px; background:#ffffff; }

.mesa{
  border-radius:18px;
  border:1px solid rgba(0,0,0,.10);
  background: radial-gradient(circle at 30% 20%, rgba(0,150,110,.25) 0%, rgba(0,120,90,.15) 30%, rgba(0,0,0,.03) 65%, rgba(0,0,0,.02) 100%);
  min-height: 320px;
  position:relative;
  overflow:hidden;
}
.mesaCenter{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:700;
  opacity:.70;
}
.mesaSeat{
  position:absolute;
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.78);
  border:1px solid rgba(0,0,0,.08);
  white-space:nowrap;
}
.seatIsYou{ outline: 2px solid rgba(0,120,90,.55); font-weight:800; }
.seatIsDealer{ background: rgba(255,255,255,.92); border-color: rgba(0,120,90,.30); }

.scoreItem{
  display:flex;
  justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.06);
  background:rgba(255,255,255,.7);
  margin-bottom:8px;
}
.scoreName{ font-weight:700; }
.scorePts{ font-weight:800; }
.smallMuted{ opacity:.70; font-size:12px; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# BARALHO / ORDENAÇÃO
# =========================
VALORES = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
PESO_VALOR = {v:i for i,v in enumerate(VALORES)}  # 2 menor, A maior
COR_NAIPE = {"♦":"red", "♥":"red", "♠":"black", "♣":"black"}
ORDEM_NAIPE = {"♦":0, "♠":1, "♣":2, "♥":3}  # ouro, espada, paus, copas

def criar_baralho():
    naipes = ["♠", "♦", "♣", "♥"]
    return [(n, v) for n in naipes for v in VALORES]

def peso_carta(c):
    naipe, valor = c
    return (ORDEM_NAIPE[naipe], PESO_VALOR[valor])

def format_valor(v):
    return str(v)

def carta_html(c):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = format_valor(valor)
    # sem identação para não virar "code block" no Markdown
    return (
        f'<div class="card">'
        f'<div class="tl" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'<div class="mid" style="color:{cor};">{naipe}</div>'
        f'<div class="br" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'</div>'
    )

def render_hand(mao, titulo="Suas cartas (visualização)"):
    mao_ordenada = sorted(mao, key=peso_carta)
    cards = "".join(carta_html(c) for c in mao_ordenada)
    st.markdown(f"### 🃏 {titulo}")
    st.markdown(f'<div class="handRow">{cards}</div>', unsafe_allow_html=True)

# =========================
# UTIL
# =========================
def ordem_da_mesa(nomes, mao_idx):
    """Retorna a ordem da rodada iniciando no mão."""
    return [nomes[(mao_idx + i) % len(nomes)] for i in range(len(nomes))]

def idx_na_ordem(ordem, nome):
    return ordem.index(nome)

# =========================
# STATE
# =========================
def ss_init():
    defaults = {
        "started": False,
        "nomes": ["Ana", "Bruno", "Carlos", "Você"],
        "humano_idx": 3,
        "pontos": {},
        "maos": {},
        "rodada": 1,
        "cartas_por_jog": 0,
        "sobras_monte": 0,
        "mao_da_rodada": 0,
        "fase": "setup",  # setup | prognostico | jogo
        "prognosticos": {},
        "progn_pre": {},  # prognósticos já visíveis (anteriores)
        "progn_pos": {},  # prognósticos escondidos (posteriores)
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# =========================
# SIDEBAR (PLACAR)
# =========================
with st.sidebar:
    st.markdown("## 📊 Placar")
    if st.session_state.started:
        # garante que TODOS aparecem (incluindo você)
        for n in st.session_state.nomes:
            st.session_state.pontos.setdefault(n, 0)

        ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
        for nome, pts in ranking:
            st.markdown(
                f'<div class="scoreItem"><div class="scoreName">{nome}</div><div class="scorePts">{pts}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown(f'<div class="smallMuted">Rodada: {st.session_state.rodada} • Cartas/jogador: {st.session_state.cartas_por_jog} • Sobras: {st.session_state.sobras_monte}</div>', unsafe_allow_html=True)

        if st.button("🔁 Reiniciar jogo", use_container_width=True):
            # reset total
            for key in [
                "started","pontos","maos","rodada","cartas_por_jog","sobras_monte",
                "mao_da_rodada","fase","prognosticos","progn_pre","progn_pos"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            ss_init()
            st.rerun()
    else:
        st.info("Inicie uma partida para ver o placar.")

# =========================
# HEADER
# =========================
st.markdown(
    """
<div class="titleRow">
  <h1>🃏 Jogo de Prognóstico</h1>
  <div class="topbar">
    <span class="badge">Trunfo: ♥</span>
    <span class="badge">1ª vaza: ♥ proibida (exceto só ♥)</span>
    <span class="badge">Copas trava até quebrar</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# =========================
# JOGO
# =========================
def distribuir():
    nomes = st.session_state.nomes
    n = len(nomes)
    baralho = criar_baralho()
    random.shuffle(baralho)

    cartas_por = len(baralho) // n
    sobras = len(baralho) - (cartas_por * n)

    st.session_state.cartas_por_jog = cartas_por
    st.session_state.sobras_monte = sobras

    st.session_state.maos = {nome: [] for nome in nomes}

    for _ in range(cartas_por):
        for nome in nomes:
            st.session_state.maos[nome].append(baralho.pop())

    for nome in nomes:
        st.session_state.maos[nome] = sorted(st.session_state.maos[nome], key=peso_carta)

    st.session_state.mao_da_rodada = random.randint(0, n - 1)
    st.session_state.prognosticos = {}
    st.session_state.progn_pre = {}
    st.session_state.progn_pos = {}
    st.session_state.fase = "prognostico"

def preparar_prognosticos_anteriores():
    """Gera apenas os prognósticos dos jogadores ANTES do humano na ordem (começando pelo mão)."""
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_humano = idx_na_ordem(ordem, humano)

    # jogadores anteriores (0 .. pos_humano-1)
    prev = ordem[:pos_humano]

    pre = {}
    for nome in prev:
        mao = st.session_state.maos[nome]
        pre[nome] = random.randint(0, len(mao))  # IA simples
    st.session_state.progn_pre = pre

def preparar_prognosticos_posteriores():
    """Após humano confirmar, gera os prognósticos dos jogadores DEPOIS do humano na ordem."""
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_humano = idx_na_ordem(ordem, humano)

    post = ordem[pos_humano+1:]
    pos = {}
    for nome in post:
        mao = st.session_state.maos[nome]
        pos[nome] = random.randint(0, len(mao))
    st.session_state.progn_pos = pos

def mesa_ui():
    nomes = st.session_state.nomes
    n = len(nomes)
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    dealer = ordem[0]

    st.markdown("#### 🪑 Mesa (todos os jogadores)")
    # posições em círculo
    # raio relativo ao container
    cx, cy = 50, 50
    rx, ry = 42, 36  # elipse para caber melhor
    seats_html = ""

    for i, nome in enumerate(ordem):
        ang = (2 * math.pi) * (i / n) - (math.pi/2)  # começa no topo
        x = cx + rx * math.cos(ang)
        y = cy + ry * math.sin(ang)

        cls = "mesaSeat"
        if nome == humano:
            cls += " seatIsYou"
        if nome == dealer:
            cls += " seatIsDealer"

        label = nome
        if nome == humano:
            label = f"{nome} (Você)"
        if nome == dealer:
            label = f"{label} • mão"

        seats_html += f'<div class="{cls}" style="left:{x}%; top:{y}%; transform:translate(-50%,-50%);">{label}</div>'

    st.markdown(
        f"""
<div class="mesa">
  {seats_html}
  <div class="mesaCenter">Mesa pronta — aguardando início da 1ª vaza</div>
</div>
""",
        unsafe_allow_html=True
    )
    st.info(f"🟦 Mão da rodada: **{dealer}** • Ordem: " + " → ".join(ordem))

# =========================
# SETUP
# =========================
if not st.session_state.started:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Configuração rápida")
    nomes_txt = st.text_input(
        "Jogadores (separados por vírgula). O último será Você",
        value=", ".join(st.session_state.nomes)
    )

    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with colB:
        st.markdown(
            '<div class="panel" style="padding:12px; background:rgba(0,120,90,.06); border-color:rgba(0,120,90,.20);">'
            'As cartas serão distribuídas igualmente até acabar o baralho.'
            "</div>",
            unsafe_allow_html=True
        )

    if start:
        nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
        if len(nomes) < 2:
            st.error("Informe pelo menos 2 jogadores.")
        else:
            st.session_state.nomes = nomes
            st.session_state.humano_idx = len(nomes) - 1
            st.session_state.pontos = {n: 0 for n in nomes}
            st.session_state.started = True
            st.session_state.rodada = 1
            distribuir()
            preparar_prognosticos_anteriores()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================
# PROGNÓSTICO
# =========================
nomes = st.session_state.nomes
humano_nome = nomes[st.session_state.humano_idx]

st.markdown(f"### 📌 Rodada {st.session_state.rodada} — {st.session_state.cartas_por_jog} cartas por jogador")
mesa_ui()
st.markdown("<hr/>", unsafe_allow_html=True)

# Mão do humano
mao_humano = st.session_state.maos.get(humano_nome, [])
render_hand(mao_humano, "Suas cartas (visualização)")

st.markdown("<hr/>", unsafe_allow_html=True)

# =========================
# VISUALIZAÇÃO DE PROGNÓSTICOS (regra que você pediu)
# - mostra anteriores na ordem do mão
# - se humano for o último (pé), mostra todos (anteriores já + posteriores depois que ele confirmar)
# =========================
ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
pos_humano = idx_na_ordem(ordem, humano_nome)
eh_pe = (pos_humano == len(ordem) - 1)

st.markdown("### ✅ Prognósticos visíveis (anteriores na mesa)")
# garante que pre existe
if st.session_state.fase == "prognostico" and not st.session_state.progn_pre:
    preparar_prognosticos_anteriores()

visiveis = dict(st.session_state.progn_pre)

# se você é o pé, você já pode ver todos os anteriores (ok)
# os posteriores só aparecem depois do seu confirm (quando gerarmos)
if eh_pe and st.session_state.progn_pos:
    # quando pé, após seu confirm, pode ver todos mesmo
    visiveis.update(st.session_state.progn_pos)

if not visiveis:
    st.info("Você é o mão — ninguém fez prognóstico antes de você.")
else:
    # mostra na ordem correta do mão
    linhas = []
    for nome in ordem:
        if nome in visiveis:
            linhas.append((nome, visiveis[nome]))
    st.table({"Jogador": [x[0] for x in linhas], "Prognóstico": [x[1] for x in linhas]})

st.markdown("<hr/>", unsafe_allow_html=True)

# Entrada do humano
max_palpite = len(mao_humano)
palpite = st.number_input("Seu prognóstico", min_value=0, max_value=max_palpite, value=0, step=1)

if st.session_state.fase == "prognostico":
    if st.button("Confirmar meu prognóstico", use_container_width=True):
        # grava prognóstico humano
        st.session_state.prognosticos[humano_nome] = int(palpite)

        # grava também os anteriores e calcula posteriores
        st.session_state.prognosticos.update(st.session_state.progn_pre)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        # se for pé, agora pode ver todos (na próxima renderização)
        st.success("✅ Prognóstico registrado! Indo para a fase de jogo...")
        st.session_state.fase = "jogo"
        st.rerun()

# =========================
# FASE DE JOGO (placeholder por enquanto)
# =========================
if st.session_state.fase == "jogo":
    st.markdown("## 🎮 Fase de Jogo")
    st.success("Prognósticos fechados! (Próximo passo: jogar vazas com cartas clicáveis na mesa.)")

    # Mostra todos os prognósticos na ordem do mão (agora pode)
    linhas = []
    for nome in ordem:
        linhas.append((nome, st.session_state.prognosticos.get(nome, "-")))
    st.markdown("### 📋 Prognósticos da rodada (ordem do mão)")
    st.table({"Jogador": [x[0] for x in linhas], "Prognóstico": [x[1] for x in linhas]})
