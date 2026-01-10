# app.py
import random
import streamlit as st

# =========================
# CONFIG / ESTILO (APP)
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

APP_CSS = """
<style>
/* evita topo “cortado” e dá cara de app */
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: 0.5rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* cards estilo baralho */
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
.card .tl{
  position:absolute;
  top:8px; left:8px;
  font-weight:800;
  font-size:14px;
  line-height:14px;
}
.card .br{
  position:absolute;
  bottom:8px; right:8px;
  font-weight:800;
  font-size:14px;
  line-height:14px;
  transform:rotate(180deg);
}
.card .mid{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:30px;
  font-weight:800;
  opacity:.95;
}
.badge{
  display:inline-block;
  padding:4px 10px;
  border-radius:999px;
  background:rgba(0,0,0,.06);
  font-size:12px;
}
.topbar{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin: 2px 0 10px 0;
}
.titleRow{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom: 4px;
}
.titleRow h1{
  margin:0;
}
.panel{
  border:1px solid rgba(0,0,0,.08);
  border-radius:14px;
  padding:14px;
  background:#ffffff;
}
.mesa{
  border-radius:18px;
  border:1px solid rgba(0,0,0,.10);
  background: radial-gradient(circle at 30% 20%, rgba(0,150,110,.25) 0%, rgba(0,120,90,.15) 30%, rgba(0,0,0,.03) 65%, rgba(0,0,0,.02) 100%);
  min-height: 260px;
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
  opacity:.75;
}
.mesaSeat{
  position:absolute;
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.7);
  border:1px solid rgba(0,0,0,.06);
}
.seatTop{ top:14px; left:50%; transform:translateX(-50%); }
.seatBottom{ bottom:14px; left:50%; transform:translateX(-50%); }
.seatLeft{ left:14px; top:50%; transform:translateY(-50%); }
.seatRight{ right:14px; top:50%; transform:translateY(-50%); }

/* placar lateral simples */
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
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# REGRAS / MODELOS
# =========================
NAIPES = ["♦", "♠", "♣", "♥"]  # ordem pedida na visualização: ouro, espada, paus, copas
VALORES = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
PESO_VALOR = {v:i for i,v in enumerate(VALORES)}  # 2 menor, A maior
COR_NAIPE = {"♦":"red", "♥":"red", "♠":"black", "♣":"black"}

def criar_baralho():
    return [(n, v) for n in ["♠","♦","♣","♥"] for v in VALORES]  # baralho normal (naipes padrão)

def peso_carta(c):
    naipe, valor = c
    # ordenação por naipe: ♦, ♠, ♣, ♥
    ordem_naipe = {"♦":0,"♠":1,"♣":2,"♥":3}
    return (ordem_naipe[naipe], PESO_VALOR[valor])

def format_valor(v):
    return str(v)

def carta_html(c):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = format_valor(valor)
    return f"""
    <div class="card">
      <div class="tl" style="color:{cor};">{vv}<br/>{naipe}</div>
      <div class="mid" style="color:{cor};">{naipe}</div>
      <div class="br" style="color:{cor};">{vv}<br/>{naipe}</div>
    </div>
    """

def render_hand(mao, titulo="Suas cartas (visualização)"):
    mao_ordenada = sorted(mao, key=peso_carta)
    cards = "".join(carta_html(c) for c in mao_ordenada)
    st.markdown(f"### 🃏 {titulo}", unsafe_allow_html=True)
    st.markdown(f'<div class="handRow">{cards}</div>', unsafe_allow_html=True)

# =========================
# ESTADO
# =========================
def ss_init():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "nomes" not in st.session_state:
        st.session_state.nomes = ["Ana", "Bruno", "Carlos", "Você"]
    if "humano_idx" not in st.session_state:
        st.session_state.humano_idx = 3
    if "maos" not in st.session_state:
        st.session_state.maos = {}
    if "pontos" not in st.session_state:
        st.session_state.pontos = {}
    if "rodada" not in st.session_state:
        st.session_state.rodada = 1
    if "cartas_por_jog" not in st.session_state:
        st.session_state.cartas_por_jog = 13
    if "copas_quebrada" not in st.session_state:
        st.session_state.copas_quebrada = False
    if "mao_da_rodada" not in st.session_state:
        st.session_state.mao_da_rodada = 0
    if "prognosticos" not in st.session_state:
        st.session_state.prognosticos = {}
    if "fase" not in st.session_state:
        st.session_state.fase = "setup"  # setup | prognostico | jogo

ss_init()

# =========================
# SIDEBAR (PLACAR SIMPLES)
# =========================
with st.sidebar:
    st.markdown("## 📊 Placar")
    if st.session_state.started:
        # inicializa pontos se necessário
        for n in st.session_state.nomes:
            st.session_state.pontos.setdefault(n, 0)

        # ordena por pontos desc
        ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
        for nome, pts in ranking:
            st.markdown(
                f"""
                <div class="scoreItem">
                  <div class="scoreName">{nome}</div>
                  <div class="scorePts">{pts}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
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
# FUNÇÕES DE JOGO (básico para não quebrar)
# =========================
def distribuir():
    nomes = st.session_state.nomes
    n = len(nomes)
    baralho = criar_baralho()
    random.shuffle(baralho)

    # distribui igualmente até onde dá
    cartas_por = len(baralho) // n
    st.session_state.cartas_por_jog = cartas_por

    st.session_state.maos = {nome: [] for nome in nomes}
    for i in range(cartas_por):
        for nome in nomes:
            st.session_state.maos[nome].append(baralho.pop())

    for nome in nomes:
        st.session_state.maos[nome] = sorted(st.session_state.maos[nome], key=peso_carta)

    # mão aleatório por rodada (você depois pode trocar pela regra de “girar o mão”)
    st.session_state.mao_da_rodada = random.randint(0, n - 1)
    st.session_state.copas_quebrada = False
    st.session_state.prognosticos = {}
    st.session_state.rodada = 1
    st.session_state.fase = "prognostico"

def mesa_ui():
    nomes = st.session_state.nomes
    n = len(nomes)
    idx_mao = st.session_state.mao_da_rodada
    mao_nome = nomes[idx_mao]

    # posições simples (até 4 “bonitinho”; mais que isso fica só como referência)
    top = nomes[0] if n > 0 else ""
    right = nomes[1] if n > 1 else ""
    left = nomes[2] if n > 2 else ""
    bottom = nomes[st.session_state.humano_idx] if n > st.session_state.humano_idx else "Você"

    st.markdown("#### 🪑 Mesa")
    st.markdown(
        f"""
        <div class="mesa">
          <div class="mesaSeat seatTop">{top}</div>
          <div class="mesaSeat seatRight">{right}</div>
          <div class="mesaSeat seatLeft">{left}</div>
          <div class="mesaSeat seatBottom">{bottom}</div>
          <div class="mesaCenter">Mesa vazia — o mão abre a vaza</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.info(f"🟦 Mão da rodada: **{mao_nome}**")

# =========================
# TELA SETUP
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
            distribuir()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================
# TELA PROGNÓSTICO
# =========================
st.markdown(f"### 📌 Rodada {st.session_state.rodada} — {st.session_state.cartas_por_jog} cartas")

# Mesa ao centro
mesa_ui()

st.markdown("<hr/>", unsafe_allow_html=True)

# Mostrar cartas do humano lado a lado (corrigido)
humano_nome = st.session_state.nomes[st.session_state.humano_idx]
mao_humano = st.session_state.maos.get(humano_nome, [])
render_hand(mao_humano, "Suas cartas (visualização)")

st.markdown("<hr/>", unsafe_allow_html=True)

# Prognóstico (simples)
st.markdown("### ✅ Prognósticos")
max_palpite = len(mao_humano)
palpite = st.number_input("Seu prognóstico", min_value=0, max_value=max_palpite, value=0, step=1)

if st.button("Confirmar meu prognóstico", use_container_width=True):
    st.session_state.prognosticos[humano_nome] = int(palpite)
    st.success("Prognóstico registrado! (Próximo passo: fase de jogo)")
    # aqui você continuaria o fluxo da sua lógica (jogar vaza etc.)
