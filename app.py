import streamlit as st
import random

# ==========================
# MODELOS
# ==========================

NAIPES = ["♠", "♦", "♣", "♥"]
VALORES = list(range(2, 11)) + ["J", "Q", "K", "A"]
PESO = {v: i for i, v in enumerate(VALORES)}

class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def __repr__(self):
        return f"{self.valor}{self.naipe}"

class Jogador:
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = 0
        self.vazas = 0

# ==========================
# FUNÇÕES DO JOGO
# ==========================

def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def distribuir(jogadores, cartas_por_jogador):
    baralho = criar_baralho()
    random.shuffle(baralho)
    for j in jogadores:
        j.mao = []
        j.vazas = 0
        for _ in range(cartas_por_jogador):
            j.mao.append(baralho.pop())

def carta_vencedora(mesa, naipe_base):
    copas = [c for c in mesa if c[1].naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: PESO[x[1].valor])[0]
    mesmo_naipe = [c for c in mesa if c[1].naipe == naipe_base]
    return max(mesmo_naipe, key=lambda x: PESO[x[1].valor])[0]

# ==========================
# INTERFACE STREAMLIT
# ==========================

st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")

st.title("🃏 Jogo de Prognóstico – Etapa 2")

# Estado inicial
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

# ==========================
# TELA INICIAL
# ==========================

if st.session_state.fase == "inicio":
    nomes = st.text_input("Jogadores (separados por vírgula)", "Você, Ana, Bruno, Carlos")

    if st.button("▶ Iniciar Jogo"):
        lista = [n.strip() for n in nomes.split(",")]
        jogadores = []
        for i, n in enumerate(lista):
            jogadores.append(Jogador(n, humano=(i == 0)))

        distribuir(jogadores, 5)

        st.session_state.jogadores = jogadores
        st.session_state.ordem = jogadores.copy()
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.fase = "prognostico"
        st.experimental_rerun()

# ==========================
# PROGNÓSTICO
# ==========================

elif st.session_state.fase == "prognostico":
    st.subheader("📊 Faça seu prognóstico")
    humano = st.session_state.jogadores[0]

    humano.prognostico = st.number_input(
        "Quantas vazas você acha que vai fazer?",
        min_value=0,
        max_value=len(humano.mao),
        step=1
    )

    if st.button("Confirmar Prognóstico"):
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, len(j.mao))
        st.session_state.fase = "jogada"
        st.experimental_rerun()

# ==========================
# JOGADA
# ==========================

elif st.session_state.fase == "jogada":
    st.subheader("🂡 Sua vez de jogar")

    humano = st.session_state.jogadores[0]

    st.write("### Suas cartas:")
    cols = st.columns(len(humano.mao))

    for i, carta in enumerate(humano.mao):
        if cols[i].button(str(carta)):
            st.session_state.mesa.append((humano, carta))
            humano.mao.remove(carta)
            st.session_state.naipe_base = carta.naipe
            st.session_state.fase = "ia"
            st.experimental_rerun()

# ==========================
# IA JOGA
# ==========================

elif st.session_state.fase == "ia":
    for j in st.session_state.jogadores[1:]:
        carta = random.choice(j.mao)
        j.mao.remove(carta)
        st.session_state.mesa.append((j, carta))

    vencedor = carta_vencedora(
        st.session_state.mesa,
        st.session_state.naipe_base
    )
    vencedor.vazas += 1

    st.session_state.ultima_mesa = st.session_state.mesa.copy()
    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.fase = "resultado"
    st.experimental_rerun()

# ==========================
# RESULTADO DA VAZA
# ==========================

elif st.session_state.fase == "resultado":
    st.subheader("🏆 Resultado da vaza")

    for j, c in st.session_state.ultima_mesa:
        st.write(f"{j.nome}: {c}")

    vencedor = max(
        st.session_state.ultima_mesa,
        key=lambda x: PESO[x[1].valor]
    )[0]

    st.success(f"Vencedor da vaza: {vencedor.nome}")

    if st.button("Próxima vaza"):
        if st.session_state.jogadores[0].mao:
            st.session_state.fase = "jogada"
        else:
            st.session_state.fase = "fim"
        st.experimental_rerun()

# ==========================
# FIM DO JOGO
# ==========================

elif st.session_state.fase == "fim":
    st.subheader("📊 Resultado Final")

    for j in st.session_state.jogadores:
        bonus = 5 if j.vazas == j.prognostico else 0
        total = j.vazas + bonus
        st.write(f"{j.nome}: {total} pontos")

    st.button("🔄 Jogar Novamente", on_click=lambda: st.session_state.clear())

