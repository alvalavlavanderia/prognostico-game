import streamlit as st
import random

# ==========================
# CONSTANTES
# ==========================

NAIPES = ["♠", "♦", "♣", "♥"]
VALORES = list(range(2, 11)) + ["J", "Q", "K", "A"]
PESO = {v: i for i, v in enumerate(VALORES)}

# ==========================
# MODELOS
# ==========================

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
        self.pontos = 0

# ==========================
# FUNÇÕES DO JOGO
# ==========================

def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def distribuir_cartas(jogadores, qtd):
    baralho = criar_baralho()
    random.shuffle(baralho)

    for j in jogadores:
        j.mao = []
        j.vazas = 0

    for _ in range(qtd):
        for j in jogadores:
            j.mao.append(baralho.pop())

def vencedor_vaza(mesa, naipe_base):
    copas = [x for x in mesa if x[1].naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: PESO[x[1].valor])[0]

    mesmo_naipe = [x for x in mesa if x[1].naipe == naipe_base]
    return max(mesmo_naipe, key=lambda x: PESO[x[1].valor])[0]

# ==========================
# INTERFACE
# ==========================

st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")
st.title("🃏 Jogo de Prognóstico")

# ==========================
# ESTADO INICIAL
# ==========================

if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
    st.session_state.rodada = 10
    st.session_state.inicio_ordem = 0

# ==========================
# INÍCIO
# ==========================

if st.session_state.fase == "inicio":
    nomes = st.text_input(
        "Jogadores (separados por vírgula)",
        "Você, Ana, Bruno, Carlos"
    )

    if st.button("▶ Iniciar Jogo"):
        lista = [n.strip() for n in nomes.split(",")]
        jogadores = []

        for i, n in enumerate(lista):
            jogadores.append(Jogador(n, humano=(i == 0)))

        st.session_state.jogadores = jogadores
        st.session_state.fase = "distribuir"
        st.rerun()

# ==========================
# DISTRIBUIÇÃO
# ==========================

elif st.session_state.fase == "distribuir":
    distribuir_cartas(
        st.session_state.jogadores,
        st.session_state.rodada
    )

    st.session_state.fase = "prognostico"
    st.rerun()

# ==========================
# PROGNÓSTICO
# ==========================

elif st.session_state.fase == "prognostico":
    st.subheader(f"📊 Rodada com {st.session_state.rodada} cartas")

    humano = st.session_state.jogadores[0]

    st.write("🂡 **Suas cartas:**")
    st.write(" ".join(str(c) for c in humano.mao))

    humano.prognostico = st.number_input(
        "Quantas vazas você acha que vai fazer?",
        min_value=0,
        max_value=st.session_state.rodada,
        step=1
    )

    if st.button("Confirmar Prognóstico"):
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, st.session_state.rodada)

        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.fase = "jogada"
        st.rerun()

# ==========================
# JOGADA
# ==========================

elif st.session_state.fase == "jogada":
    jogadores = st.session_state.jogadores
    ordem = jogadores[st.session_state.inicio_ordem:] + jogadores[:st.session_state.inicio_ordem]

    atual = ordem[0]

    st.subheader(f"🎴 Vez de {atual.nome}")

    if atual.humano:
        cols = st.columns(len(atual.mao))
        for i, carta in enumerate(atual.mao):
            if cols[i].button(str(carta)):
                atual.mao.remove(carta)
                st.session_state.mesa.append((atual, carta))
                st.session_state.naipe_base = carta.naipe
                st.session_state.ordem_temp = ordem[1:]
                st.session_state.fase = "ia"
                st.rerun()
    else:
        carta = random.choice(atual.mao)
        atual.mao.remove(carta)
        st.session_state.mesa.append((atual, carta))
        st.session_state.naipe_base = carta.naipe
        st.session_state.ordem_temp = ordem[1:]
        st.session_state.fase = "ia"
        st.rerun()

# ==========================
# IA JOGA
# ==========================

elif st.session_state.fase == "ia":
    for j in st.session_state.ordem_temp:
        carta = random.choice(j.mao)
        j.mao.remove(carta)
        st.session_state.mesa.append((j, carta))

    vencedor = vencedor_vaza(
        st.session_state.mesa,
        st.session_state.naipe_base
    )
    vencedor.vazas += 1

    st.session_state.inicio_ordem = st.session_state.jogadores.index(vencedor)
    st.session_state.ultima_mesa = st.session_state.mesa.copy()
    st.session_state.mesa = []
    st.session_state.fase = "resultado"
    st.rerun()

# ==========================
# RESULTADO DA VAZA
# ==========================

elif st.session_state.fase == "resultado":
    st.subheader("🏆 Resultado da Vaza")

    for j, c in st.session_state.ultima_mesa:
        st.write(f"{j.nome}: {c}")

    if st.button("Próxima vaza"):
        if st.session_state.jogadores[0].mao:
            st.session_state.fase = "jogada"
        else:
            st.session_state.fase = "pontuacao"
        st.rerun()

# ==========================
# PONTUAÇÃO
# ==========================

elif st.session_state.fase == "pontuacao":
    st.subheader("📊 Pontuação da Rodada")

    for j in st.session_state.jogadores:
        pontos = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos
        st.write(f"{j.nome}: {pontos} pontos")

    st.session_state.rodada -= 1

    if st.session_state.rodada > 0:
        st.session_state.fase = "distribuir"
    else:
        st.session_state.fase = "fim"

    st.rerun()

# ==========================
# FIM
# ==========================

elif st.session_state.fase == "fim":
    st.subheader("🏆 Resultado Final")

    for j in sorted(
        st.session_state.jogadores,
        key=lambda x: x.pontos,
        reverse=True
    ):
        st.write(f"{j.nome}: {j.pontos} pontos")

    if st.button("🔄 Jogar Novamente"):
        st.session_state.clear()
        st.rerun()



