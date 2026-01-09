import streamlit as st
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")

NAIPES = ["♦", "♠", "♣", "♥"]
NAIPE_ORDEM = {"♦": 0, "♠": 1, "♣": 2, "♥": 3}
NAIPE_COR = {"♦": "red", "♥": "red", "♠": "black", "♣": "black"}

VALORES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
VALOR_PESO = {v: i for i, v in enumerate(VALORES)}

# =========================
# MODELOS
# =========================
class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def peso(self):
        return (NAIPE_ORDEM[self.naipe], VALOR_PESO[self.valor])

    def render(self):
        cor = NAIPE_COR[self.naipe]
        return f"<span style='color:{cor}; font-size:20px'>{self.valor}{self.naipe}</span>"

class Jogador:
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = 0
        self.vazas = 0
        self.pontos = 0

# =========================
# FUNÇÕES
# =========================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def ordenar_mao(mao):
    return sorted(mao, key=lambda c: c.peso())

def definir_vencedor(mesa, naipe_base):
    trunfos = [j for j in mesa if j["carta"].naipe == "♥"]
    if trunfos:
        return max(trunfos, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

    seguindo = [j for j in mesa if j["carta"].naipe == naipe_base]
    return max(seguindo, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

# =========================
# ESTADO INICIAL
# =========================
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "jogadores" not in st.session_state:
    st.session_state.jogadores = []

if "ordem" not in st.session_state:
    st.session_state.ordem = []

if "mesa" not in st.session_state:
    st.session_state.mesa = []

if "naipe_base" not in st.session_state:
    st.session_state.naipe_base = None

if "indice_jogador" not in st.session_state:
    st.session_state.indice_jogador = 0

# =========================
# INTERFACE
# =========================
st.title("🎴 Jogo de Prognóstico")

# =========================
# INÍCIO
# =========================
if st.session_state.fase == "inicio":
    nomes = st.text_input("Jogadores (separados por vírgula)", "Você, Ana, Bruno, Carlos")

    if st.button("Iniciar Jogo"):
        lista = [n.strip() for n in nomes.split(",")]

        jogadores = []
        for i, nome in enumerate(lista):
            jogadores.append(Jogador(nome, humano=(i == 0)))

        baralho = criar_baralho()
        random.shuffle(baralho)

        cartas_por_jogador = 10

        for j in jogadores:
            j.mao = ordenar_mao([baralho.pop() for _ in range(cartas_por_jogador)])

        st.session_state.jogadores = jogadores
        st.session_state.ordem = jogadores[:]
        st.session_state.fase = "prognostico"
        st.rerun()

# =========================
# PROGNÓSTICO
# =========================
if st.session_state.fase == "prognostico":
    humano = st.session_state.jogadores[0]

    st.subheader("Suas cartas")
    st.markdown(" ".join([c.render() for c in humano.mao]), unsafe_allow_html=True)

    prog = st.number_input("Quantas vazas você acredita que fará?", 0, len(humano.mao), 0)

    if st.button("Confirmar Prognóstico"):
        humano.prognostico = prog
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, len(j.mao))

        st.session_state.fase = "jogada"
        st.rerun()

# =========================
# JOGADA
# =========================
if st.session_state.fase == "jogada":
    jogador = st.session_state.ordem[st.session_state.indice_jogador]

    st.subheader(f"Vez de {jogador.nome}")

    if jogador.humano:
        carta_escolhida = st.selectbox(
            "Escolha uma carta",
            jogador.mao,
            format_func=lambda c: f"{c.valor}{c.naipe}"
        )

        if st.button("Jogar carta"):
            jogador.mao.remove(carta_escolhida)
            st.session_state.mesa.append({"jogador": jogador, "carta": carta_escolhida})

            if st.session_state.naipe_base is None:
                st.session_state.naipe_base = carta_escolhida.naipe

            st.session_state.indice_jogador += 1
            st.rerun()

    else:
        carta = random.choice(jogador.mao)
        jogador.mao.remove(carta)

        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe

        st.session_state.indice_jogador += 1
        st.rerun()

    if st.session_state.indice_jogador >= len(st.session_state.ordem):
        vencedor = definir_vencedor(st.session_state.mesa, st.session_state.naipe_base)
        vencedor.vazas += 1

        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]

        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado"
        st.rerun()

# =========================
# RESULTADO DA VAZA
# =========================
if st.session_state.fase == "resultado":
    st.success(f"🏆 {st.session_state.vencedor.nome} venceu a vaza!")

    if st.button("Próxima Vaza"):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0

        if len(st.session_state.jogadores[0].mao) == 0:
            st.session_state.fase = "fim"
        else:
            st.session_state.fase = "jogada"

        st.rerun()

# =========================
# FIM DA RODADA
# =========================
if st.session_state.fase == "fim":
    st.subheader("📊 Placar da Rodada")

    for j in st.session_state.jogadores:
        pontos = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos
        st.write(f"{j.nome} — Vaz as: {j.vazas} | Prognóstico: {j.prognostico} | Pontos: {j.pontos}")

    st.success("Rodada encerrada com sucesso!")

