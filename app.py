import streamlit as st
import random

# ==========================
# CONSTANTES
# ==========================

NAIPES = ["♦", "♠", "♣", "♥"]
VALORES = list(range(2, 11)) + ["J", "Q", "K", "A"]

PESO_VALOR = {v: i for i, v in enumerate(VALORES)}
PESO_NAIPE = {"♦": 0, "♠": 1, "♣": 2, "♥": 3}

COR_NAIPE = {
    "♦": "red",
    "♥": "red",
    "♠": "black",
    "♣": "black"
}

# ==========================
# MODELOS
# ==========================

class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def peso(self):
        return PESO_NAIPE[self.naipe], PESO_VALOR[self.valor]

    def render(self):
        return f"<span style='color:{COR_NAIPE[self.naipe]}; font-size:22px'>{self.valor}{self.naipe}</span>"

class Jogador:
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = 0
        self.vazas = 0
        self.pontos = 0

# ==========================
# FUNÇÕES
# ==========================

def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def distribuir(jogadores, qtd):
    baralho = criar_baralho()
    random.shuffle(baralho)

    for j in jogadores:
        j.mao = []
        j.vazas = 0

    for _ in range(qtd):
        for j in jogadores:
            j.mao.append(baralho.pop())

def ordenar_mao(mao):
    return sorted(
        mao,
        key=lambda c: (PESO_NAIPE[c.naipe], PESO_VALOR[c.valor])
    )


def vencedor_vaza(mesa, naipe_base):
    copas = [x for x in mesa if x[1].naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1].valor])[0]

    base = [x for x in mesa if x[1].naipe == naipe_base]
    return max(base, key=lambda x: PESO_VALOR[x[1].valor])[0]

# ==========================
# CONFIG
# ==========================

st.set_page_config("Jogo de Prognóstico", layout="centered")
st.title("🃏 Jogo de Prognóstico")

# ==========================
# ESTADO INICIAL
# ==========================

if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
    st.session_state.rodada = 10
    st.session_state.mao_inicial = 0

# ==========================
# INÍCIO
# ==========================

if st.session_state.fase == "inicio":
    nomes = st.text_input(
        "Jogadores (primeiro é você)",
        "Você, Ana, Bruno, Carlos"
    )

    if st.button("▶ Iniciar Jogo"):
        lista = [n.strip() for n in nomes.split(",")]
        st.session_state.jogadores = [
            Jogador(n, humano=(i == 0)) for i, n in enumerate(lista)
        ]
        st.session_state.fase = "distribuir"
        st.rerun()

# ==========================
# DISTRIBUIÇÃO
# ==========================

elif st.session_state.fase == "distribuir":
    distribuir(st.session_state.jogadores, st.session_state.rodada)
    st.session_state.fase = "prognostico"
    st.rerun()

# ==========================
# PROGNÓSTICO
# ==========================

elif st.session_state.fase == "prognostico":
    st.subheader(f"📊 Rodada com {st.session_state.rodada} cartas")

    humano = st.session_state.jogadores[0]
    humano.mao = ordenar_mao(humano.mao)

    st.markdown("🂡 **Suas cartas:**", unsafe_allow_html=True)
    st.markdown(" ".join(c.render() for c in humano.mao), unsafe_allow_html=True)

    humano.prognostico = st.number_input(
        "Seu prognóstico",
        0,
        st.session_state.rodada,
        0
    )

    if st.button("Confirmar Prognóstico"):
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, st.session_state.rodada)

        st.session_state.ordem = (
            st.session_state.jogadores[st.session_state.mao_inicial:] +
            st.session_state.jogadores[:st.session_state.mao_inicial]
        )
        st.session_state.mesa = []
        st.session_state.fase = "jogada"
        st.rerun()

# ==========================
# JOGADA
# ==========================

elif st.session_state.fase == "jogada":
    jogador = st.session_state.ordem[0]

    st.subheader(f"🎴 Vez de {jogador.nome}")

    if jogador.humano:
        jogador.mao = ordenar_mao(jogador.mao)
        cols = st.columns(len(jogador.mao))

        for i, carta in enumerate(jogador.mao):
            if cols[i].button(f"{carta.valor}{carta.naipe}"):
                jogador.mao.remove(carta)
                st.session_state.mesa.append((jogador, carta))
                st.session_state.naipe_base = carta.naipe
                st.session_state.ordem = st.session_state.ordem[1:]
                st.session_state.fase = "ia"
                st.rerun()
    else:
        carta = random.choice(jogador.mao)
        jogador.mao.remove(carta)
        st.session_state.mesa.append((jogador, carta))
        st.session_state.naipe_base = carta.naipe
        st.session_state.ordem = st.session_state.ordem[1:]
        st.session_state.fase = "ia"
        st.rerun()

# ==========================
# IA CONTINUA
# ==========================

elif st.session_state.fase == "ia":
    while st.session_state.ordem:
        j = st.session_state.ordem[0]
        if j.humano:
            st.session_state.fase = "jogada"
            st.rerun()

        carta = random.choice(j.mao)
        j.mao.remove(carta)
        st.session_state.mesa.append((j, carta))
        st.session_state.ordem = st.session_state.ordem[1:]

    vencedor = vencedor_vaza(
        st.session_state.mesa,
        st.session_state.naipe_base
    )
    vencedor.vazas += 1
    st.session_state.vencedor_vaza = vencedor
    st.session_state.fase = "resultado"
    st.rerun()

# ==========================
# RESULTADO DA VAZA
# ==========================

elif st.session_state.fase == "resultado":
    st.subheader("🏆 Resultado da Vaza")

    for j, c in st.session_state.mesa:
        st.markdown(f"{j.nome}: {c.render()}", unsafe_allow_html=True)

    st.success(f"Vencedor da vaza: **{st.session_state.vencedor_vaza.nome}**")

    st.session_state.mao_inicial = st.session_state.jogadores.index(
        st.session_state.vencedor_vaza
    )

    if st.button("Próxima vaza"):
        st.session_state.mesa = []
        if st.session_state.jogadores[0].mao:
            st.session_state.fase = "prognostico_jogada"
        else:
            st.session_state.fase = "pontuacao"
        st.rerun()

# ==========================
# PONTUAÇÃO
# ==========================

elif st.session_state.fase == "pontuacao":
    st.subheader("📊 Placar da Rodada")

    for j in st.session_state.jogadores:
        pontos = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos
        st.write(f"{j.nome}: {j.pontos} pontos")

    st.write(f"🂡 Próximo mão: **{st.session_state.jogadores[st.session_state.mao_inicial].nome}**")

    st.session_state.rodada -= 1
    st.session_state.fase = "distribuir" if st.session_state.rodada > 0 else "fim"
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
