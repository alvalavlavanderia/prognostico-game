import streamlit as st
import random

# -------------------------
# MODELOS BÁSICOS
# -------------------------

NAIPES = ["♠", "♦", "♣", "♥"]
VALORES = list(range(2, 11)) + ["J", "Q", "K", "A"]
VALOR_PESO = {v: i for i, v in enumerate(VALORES)}

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

    def somente_copas(self):
        return all(c.naipe == "♥" for c in self.mao)

# -------------------------
# BARALHO
# -------------------------

def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

# -------------------------
# JOGO
# -------------------------

class PrognosticoGame:
    def __init__(self, nomes_jogadores, prognostico_humano):
        self.jogadores = []
        for i, nome in enumerate(nomes_jogadores):
            self.jogadores.append(
                Jogador(nome, humano=(i == 0))
            )

        self.prognostico_humano = prognostico_humano
        self.mao_inicial = random.randint(0, len(self.jogadores) - 1)

    def distribuir_cartas(self, cartas):
        baralho = criar_baralho()
        random.shuffle(baralho)

        for j in self.jogadores:
            j.mao = []
            j.vazas = 0

        for _ in range(cartas):
            for j in self.jogadores:
                j.mao.append(baralho.pop())

    def coletar_prognosticos(self):
        for j in self.jogadores:
            if j.humano:
                j.prognostico = self.prognostico_humano
            else:
                j.prognostico = random.randint(0, len(j.mao))

    def escolher_carta(self, jogador, naipe_base, primeira_vaza):
        cartas_validas = []

        for c in jogador.mao:
            if primeira_vaza and c.naipe == "♥" and not jogador.somente_copas():
                continue
            cartas_validas.append(c)

        if naipe_base:
            seguindo = [c for c in cartas_validas if c.naipe == naipe_base]
            if seguindo:
                return random.choice(seguindo)

        return random.choice(cartas_validas)

    def definir_vencedor(self, mesa, naipe_base):
        copas = [(j, c) for j, c in mesa if c.naipe == "♥"]
        if copas:
            return max(copas, key=lambda x: VALOR_PESO[x[1].valor])[0]

        mesmo_naipe = [(j, c) for j, c in mesa if c.naipe == naipe_base]
        return max(mesmo_naipe, key=lambda x: VALOR_PESO[x[1].valor])[0]

    def pontuar(self):
        for j in self.jogadores:
            pontos = j.vazas
            if j.vazas == j.prognostico:
                pontos += 5
            j.pontos += pontos

    def jogar_rodada(self, cartas):
        self.distribuir_cartas(cartas)
        self.coletar_prognosticos()

        ordem = self.jogadores[self.mao_inicial:] + self.jogadores[:self.mao_inicial]
        primeira_vaza = True

        while ordem[0].mao:
            mesa = []
            naipe_base = None

            for j in ordem:
                carta = self.escolher_carta(j, naipe_base, primeira_vaza)
                j.mao.remove(carta)

                if not naipe_base:
                    naipe_base = carta.naipe

                mesa.append((j, carta))

            vencedor = self.definir_vencedor(mesa, naipe_base)
            vencedor.vazas += 1

            idx = ordem.index(vencedor)
            ordem = ordem[idx:] + ordem[:idx]

            primeira_vaza = False

        self.pontuar()

    def jogar(self):
        cartas_max = 52 // len(self.jogadores)
        for c in range(cartas_max, 0, -1):
            self.jogar_rodada(c)

        self.jogadores.sort(key=lambda j: j.pontos, reverse=True)

# -------------------------
# STREAMLIT
# -------------------------

st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")

st.title("🃏 Jogo de Prognóstico")
st.write("Jogador 1 é humano. Os demais são automáticos.")

nomes_input = st.text_input(
    "Jogadores (o primeiro será você)",
    "Você, Ana, Bruno, Carlos"
)

cartas = st.slider("Quantidade de cartas da rodada", 1, 10, 5)

prognostico = st.number_input(
    "Seu prognóstico (quantas vazas você acha que fará)",
    min_value=0,
    max_value=cartas,
    step=1
)

if st.button("▶ Iniciar Jogo"):
    nomes = [n.strip() for n in nomes_input.split(",") if n.strip()]

    if len(nomes) < 2:
        st.error("Informe pelo menos 2 jogadores.")
    else:
        jogo = PrognosticoGame(nomes, prognostico)
        jogo.jogar()

        st.success("🏆 Resultado Final")
        for j in jogo.jogadores:
            marcador = "👤" if j.humano else "🤖"
            st.write(
                f"{marcador} **{j.nome}** | Prognóstico: {j.prognostico} | "
                f"Vazas: {j.vazas} | Pontos: {j.pontos}"
            )

