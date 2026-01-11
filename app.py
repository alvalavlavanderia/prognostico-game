import streamlit as st
import random
import time

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(
    page_title="Jogo de Prognóstico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CSS GLOBAL
# =========================
APP_CSS = """
<style>
.block-container { padding-top: .6rem; padding-bottom: .6rem; max-width: 1200px; }
header[data-testid="stHeader"] { height: .3rem; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 20% 10%, rgba(0,150,110,.12), transparent 40%);
}

/* ===== CARTAS ===== */
.handRow{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  align-items:flex-start;
  justify-content:flex-start;
}

.card{
  width:72px;
  height:108px;
  border-radius:14px;
  background:#fff;
  border:1px solid rgba(0,0,0,.2);
  box-shadow:0 10px 22px rgba(0,0,0,.14);
  position:relative;
  user-select:none;
}

.card .tl{
  position:absolute;
  top:7px;
  left:7px;
  font-weight:900;
  font-size:13px;
}

.card .br{
  position:absolute;
  bottom:7px;
  right:7px;
  font-weight:900;
  font-size:13px;
  transform:rotate(180deg);
}

.card .mid{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:30px;
  font-weight:900;
}

/* ===== SIDEBAR ===== */
.scoreItem{
  display:flex;
  justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.08);
  background:rgba(255,255,255,.7);
  margin-bottom:6px;
  font-weight:900;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# MODELOS
# =========================
NAIPES = ["♦", "♠", "♣", "♥"]
VALORES = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
VALOR_PESO = {v: i for i, v in enumerate(VALORES)}
COR = {"♦": "red", "♥": "red", "♠": "black", "♣": "black"}

class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def peso(self):
        return VALOR_PESO[self.valor]

    def to_dict(self):
        return {"naipe": self.naipe, "valor": self.valor}

    @staticmethod
    def from_dict(d):
        return Carta(d["naipe"], d["valor"])

# =========================
# FUNÇÕES
# =========================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def distribuir_cartas(jogadores, qtd):
    baralho = criar_baralho()
    random.shuffle(baralho)

    for j in jogadores:
        j["mao"] = []
        j["vazas"] = 0

    for _ in range(qtd):
        for j in jogadores:
            j["mao"].append(baralho.pop())

def pontuar_rodada(jogadores):
    for j in jogadores:
        j["pontos"] += j["vazas"]
        if j["vazas"] == j["prognostico"]:
            j["pontos"] += 5

def get_humano(jogadores):
    # 1) tenta achar explicitamente humano=True
    for j in jogadores:
        if j.get("humano", False):
            return j
    # 2) fallback: último jogador
    if jogadores:
        jogadores[-1]["humano"] = True
        return jogadores[-1]
    return None

def render_mao_html(cartas):
    # Renderiza TODAS as cartas em um único bloco HTML (não quebra o flex)
    cards_html = []
    for c in cartas:
        cards_html.append(
            f"""
            <div class="card">
              <div class="tl" style="color:{COR[c.naipe]}">{c.valor}{c.naipe}</div>
              <div class="mid" style="color:{COR[c.naipe]}">{c.naipe}</div>
              <div class="br" style="color:{COR[c.naipe]}">{c.valor}{c.naipe}</div>
            </div>
            """
        )
    return f"""<div class="handRow">{''.join(cards_html)}</div>"""

def rerun():
    st.rerun()

# =========================
# ESTADO INICIAL
# =========================
if "fase" not in st.session_state:
    st.session_state.fase = "setup"

# mão fixa da rodada (pra não mudar no +)
# st.session_state.rodada_deal_id identifica se já distribuímos praquela rodada
if "rodada_deal_id" not in st.session_state:
    st.session_state.rodada_deal_id = None

# =========================
# SIDEBAR (PLACAR)
# =========================
st.sidebar.title("🏆 Placar")
if "jogadores" in st.session_state:
    for j in st.session_state.jogadores:
        st.sidebar.markdown(
            f"<div class='scoreItem'><span>{j['nome']}</span><span>{j['pontos']}</span></div>",
            unsafe_allow_html=True
        )

# =========================
# SETUP
# =========================
if st.session_state.fase == "setup":
    st.title("🃏 Jogo de Prognóstico")
    st.write("As cartas serão distribuídas igualmente até acabar o baralho.")

    nomes = st.text_input(
        "Jogadores (separados por vírgula — o último será Você)",
        "Ana, Bruno, Carlos, Mauro"
    )

    if st.button("▶ Iniciar jogo"):
        lista = [n.strip() for n in nomes.split(",") if n.strip()]
        if len(lista) < 3:
            st.error("Informe pelo menos 3 jogadores.")
            st.stop()

        jogadores = []
        for idx, n in enumerate(lista):
            is_humano = (idx == len(lista) - 1) or (n.lower() in ["voce", "você", "vc"])
            jogadores.append({
                "nome": n,
                "mao": [],
                "vazas": 0,
                "prognostico": None,
                "pontos": 0,
                "humano": is_humano
            })

        if not any(j["humano"] for j in jogadores):
            jogadores[-1]["humano"] = True

        st.session_state.jogadores = jogadores

        # começa com N cartas (igual ao número de jogadores) — só pra demo
        st.session_state.rodada = len(jogadores)

        # força redistribuição ao entrar no prognóstico
        st.session_state.rodada_deal_id = None

        st.session_state.fase = "prognostico"
        rerun()

# =========================
# PROGNÓSTICO
# =========================
elif st.session_state.fase == "prognostico":
    st.subheader(f"🎯 Rodada — {st.session_state.rodada} cartas")

    jogadores = st.session_state.jogadores
    humano = get_humano(jogadores)
    if humano is None:
        st.error("Não foi possível identificar o jogador humano.")
        st.stop()

    # ✅ Distribui cartas UMA ÚNICA VEZ por rodada (não muda ao clicar no +)
    current_deal_id = f"rodada_{st.session_state.rodada}"
    if st.session_state.rodada_deal_id != current_deal_id:
        distribuir_cartas(jogadores, st.session_state.rodada)
        # zera prognósticos pra rodada
        for j in jogadores:
            j["prognostico"] = None
        st.session_state.rodada_deal_id = current_deal_id

    # ✅ Render em linha (um único HTML)
    st.markdown("### Suas cartas")
    st.markdown(render_mao_html(humano["mao"]), unsafe_allow_html=True)

    prog = st.number_input(
        "Seu prognóstico",
        min_value=0,
        max_value=st.session_state.rodada,
        step=1,
        key=f"prog_{st.session_state.rodada}"  # key por rodada
    )

    if st.button("Confirmar prognóstico"):
        humano["prognostico"] = int(prog)
        for j in jogadores:
            if not j["humano"]:
                j["prognostico"] = random.randint(0, st.session_state.rodada)

        st.session_state.fase = "fim_rodada"
        rerun()

# =========================
# FIM DA RODADA (SIMULAÇÃO)
# =========================
elif st.session_state.fase == "fim_rodada":
    st.subheader("🧮 Final da rodada")

    jogadores = st.session_state.jogadores

    # simula vazas
    for j in jogadores:
        j["vazas"] = random.randint(0, st.session_state.rodada)

    pontuar_rodada(jogadores)

    st.success("Rodada pontuada! Indo para a próxima...")
    time.sleep(1)

    if st.session_state.rodada > 1:
        st.session_state.rodada -= 1
        st.session_state.rodada_deal_id = None  # libera novo deal
        st.session_state.fase = "prognostico"
    else:
        st.session_state.fase = "fim_jogo"

    rerun()

# =========================
# FIM DO JOGO
# =========================
elif st.session_state.fase == "fim_jogo":
    st.title("🏆 Resultado Final")
    ordem = sorted(st.session_state.jogadores, key=lambda x: x["pontos"], reverse=True)
    for i, j in enumerate(ordem, 1):
        st.markdown(f"**{i}º — {j['nome']}**: {j['pontos']} pontos")

    if st.button("🔄 Jogar novamente"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.fase = "setup"
        rerun()

