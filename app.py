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
# CSS GLOBAL (OK)
# =========================
APP_CSS = """
<style>
.block-container { padding-top: .6rem; padding-bottom: .6rem; max-width: 1200px; }
header[data-testid="stHeader"] { height: .3rem; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 20% 10%, rgba(0,150,110,.12), transparent 40%);
}

/* ===== MESA ===== */
.mesa{
  border-radius:22px;
  border:1px solid rgba(0,0,0,.14);
  height: 460px;
  position:relative;
  overflow:hidden;
  background:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,.12), rgba(255,255,255,0) 45%),
    linear-gradient(180deg, #125a37 0%, #0d482d 55%, #0a3a24 100%);
  box-shadow: 0 18px 42px rgba(0,0,0,.18);
}

.mesaCenter{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:900;
  color:rgba(255,255,255,.85);
  letter-spacing:.08em;
}

/* ===== CARTAS ===== */
.card{
  width:72px;
  height:108px;
  border-radius:14px;
  background:#fff;
  border:1px solid rgba(0,0,0,.2);
  box-shadow:0 10px 22px rgba(0,0,0,.14);
  position:relative;
  user-select:none;
  display:inline-block;
  margin-right:10px;
  margin-bottom:10px;
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

/* ===== MÃO ===== */
.handRow{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  align-items:flex-start;
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

# =========================
# FUNÇÕES DE JOGO
# =========================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def distribuir_cartas(jogadores, qtd):
    baralho = criar_baralho()
    random.shuffle(baralho)

    for j in jogadores:
        j["mao"] = []
        j["vazas"] = 0  # zera vazas da rodada

    # distribui igual para todos
    for _ in range(qtd):
        for j in jogadores:
            j["mao"].append(baralho.pop())

def pontuar_rodada(jogadores):
    # Pontuação: 1 ponto por vaza + 5 se acertar prognóstico
    for j in jogadores:
        j["pontos"] += j["vazas"]
        if j["vazas"] == j["prognostico"]:
            j["pontos"] += 5

def rerun_safe():
    # Compatível com versões novas do Streamlit
    st.rerun()

# =========================
# ESTADO INICIAL
# =========================
if "fase" not in st.session_state:
    st.session_state.fase = "setup"

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
        "Jogadores (separados por vírgula — você por último)",
        "Ana, Bruno, Carlos, Você"
    )

    if st.button("▶ Iniciar jogo"):
        lista = [n.strip() for n in nomes.split(",") if n.strip()]
        if len(lista) < 3:
            st.error("Informe pelo menos 3 jogadores (incluindo Você).")
            st.stop()

        jogadores = []
        for n in lista:
            jogadores.append({
                "nome": n,
                "mao": [],
                "vazas": 0,
                "prognostico": None,
                "pontos": 0,
                "humano": n.lower() in ["voce", "você"]
            })

        st.session_state.jogadores = jogadores
        st.session_state.rodada = len(jogadores)  # começando simples
        st.session_state.fase = "prognostico"
        rerun_safe()

# =========================
# PROGNÓSTICO
# =========================
elif st.session_state.fase == "prognostico":
    st.subheader(f"🎯 Rodada — {st.session_state.rodada} cartas")

    distribuir_cartas(st.session_state.jogadores, st.session_state.rodada)

    humano = next(j for j in st.session_state.jogadores if j["humano"])

    st.markdown("### Suas cartas")
    st.markdown("<div class='handRow'>", unsafe_allow_html=True)
    for c in humano["mao"]:
        st.markdown(
            f"""
            <div class='card'>
              <div class='tl' style='color:{COR[c.naipe]}'>{c.valor}{c.naipe}</div>
              <div class='mid' style='color:{COR[c.naipe]}'>{c.naipe}</div>
              <div class='br' style='color:{COR[c.naipe]}'>{c.valor}{c.naipe}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    prog = st.number_input(
        "Seu prognóstico",
        min_value=0,
        max_value=st.session_state.rodada,
        step=1
    )

    if st.button("Confirmar prognóstico"):
        humano["prognostico"] = int(prog)

        for j in st.session_state.jogadores:
            if not j["humano"]:
                j["prognostico"] = random.randint(0, st.session_state.rodada)

        st.session_state.fase = "fim_rodada"
        rerun_safe()

# =========================
# FIM DA RODADA (SIMULAÇÃO)
# =========================
elif st.session_state.fase == "fim_rodada":
    st.subheader("🧮 Final da rodada")

    # Simulação provisória: atribui vazas aleatórias
    # (a lógica real de jogo vai entrar depois)
    for j in st.session_state.jogadores:
        j["vazas"] = random.randint(0, st.session_state.rodada)

    # Pontua (inclui a última mão)
    pontuar_rodada(st.session_state.jogadores)

    st.success("Rodada pontuada! Indo para a próxima...")

    time.sleep(1)

    if st.session_state.rodada > 1:
        st.session_state.rodada -= 1
        st.session_state.fase = "prognostico"
    else:
        st.session_state.fase = "fim_jogo"

    rerun_safe()

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
        rerun_safe()
