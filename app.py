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

    def texto(self):
        return f"{self.valor}{self.naipe}"

    def render(self):
        cor = NAIPE_COR[self.naipe]
        return f"<span style='color:{cor}; font-size:20px; font-weight:600'>{self.valor}{self.naipe}</span>"

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
    # regra simples: copas é trunfo
    copas = [x for x in mesa if x["carta"].naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

    seguindo = [x for x in mesa if x["carta"].naipe == naipe_base]
    return max(seguindo, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

# =========================
# ESTADO (SEMPRE INICIALIZAR)
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

if "vencedor" not in st.session_state:
    st.session_state.vencedor = None

# =========================
# UI
# =========================
st.title("🎴 Jogo de Prognóstico")

# =========================
# INÍCIO
# =========================
if st.session_state.fase == "inicio":
    nomes = st.text_input("Jogadores (separados por vírgula)", "Você, Ana, Bruno, Carlos")
    cartas_por_jogador = st.number_input("Cartas por jogador (ex: 10 para 4 jogadores)", min_value=1, max_value=13, value=10, step=1)

    if st.button("Iniciar Jogo"):
        lista = [n.strip() for n in nomes.split(",") if n.strip()]
        if len(lista) < 2:
            st.error("Informe pelo menos 2 jogadores.")
            st.stop()

        jogadores = []
        for i, nome in enumerate(lista):
            jogadores.append(Jogador(nome, humano=(i == 0)))

        baralho = criar_baralho()
        random.shuffle(baralho)

        # distribuição
        for j in jogadores:
            j.mao = ordenar_mao([baralho.pop() for _ in range(cartas_por_jogador)])

        st.session_state.jogadores = jogadores
        st.session_state.ordem = jogadores[:]
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0
        st.session_state.vencedor = None

        st.session_state.fase = "prognostico"
        st.rerun()

# =========================
# PROGNÓSTICO
# =========================
elif st.session_state.fase == "prognostico":
    humano = st.session_state.jogadores[0]
    humano.mao = ordenar_mao(humano.mao)

    st.subheader("🂡 Suas cartas (ordenadas)")
    st.markdown(" ".join([c.render() for c in humano.mao]), unsafe_allow_html=True)

    prog = st.number_input("Quantas vazas você acredita que fará?", 0, len(humano.mao), 0, step=1)

    if st.button("Confirmar Prognóstico"):
        humano.prognostico = int(prog)
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, len(j.mao))

        st.session_state.fase = "jogada"
        st.rerun()

# =========================
# JOGADA (UMA CARTA POR VEZ)
# =========================
elif st.session_state.fase == "jogada":
    jogador = st.session_state.ordem[st.session_state.indice_jogador]

    st.subheader(f"🎴 Vez de: {jogador.nome}")

    # Mostra mesa atual
    if st.session_state.mesa:
        st.markdown("### 🪑 Mesa")
        for item in st.session_state.mesa:
            st.markdown(f"- {item['jogador'].nome}: {item['carta'].render()}", unsafe_allow_html=True)

    # HUMANO escolhe (corrigido: selectbox com STRINGS)
    if jogador.humano:
        jogador.mao = ordenar_mao(jogador.mao)

        # cria uma lista de chaves únicas, estáveis
        opcoes = [f"{i}|{c.texto()}" for i, c in enumerate(jogador.mao)]
        escolha = st.selectbox(
            "Escolha uma carta para jogar",
            opcoes,
            format_func=lambda x: x.split("|", 1)[1],
            key=f"pick_{len(jogador.mao)}_{st.session_state.indice_jogador}_{len(st.session_state.mesa)}"
        )

        if st.button("Jogar carta"):
            idx = int(escolha.split("|", 1)[0])
            carta_escolhida = jogador.mao.pop(idx)

            st.session_state.mesa.append({"jogador": jogador, "carta": carta_escolhida})

            if st.session_state.naipe_base is None:
                st.session_state.naipe_base = carta_escolhida.naipe

            st.session_state.indice_jogador += 1
            st.rerun()

    # IA joga
    else:
        carta = random.choice(jogador.mao)
        jogador.mao.remove(carta)

        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe

        st.session_state.indice_jogador += 1
        st.rerun()

    # Quando todos jogaram a vaza, resolve vencedor
    if st.session_state.indice_jogador >= len(st.session_state.ordem):
        vencedor = definir_vencedor(st.session_state.mesa, st.session_state.naipe_base)
        vencedor.vazas += 1

        # vencedor vira o próximo mão (roda a ordem)
        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]

        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado"
        st.rerun()

# =========================
# RESULTADO DA VAZA
# =========================
elif st.session_state.fase == "resultado":
    st.subheader("🏆 Resultado da Vaza")

    for item in st.session_state.mesa:
        st.markdown(f"- {item['jogador'].nome}: {item['carta'].render()}", unsafe_allow_html=True)

    st.success(f"Vencedor da vaza: **{st.session_state.vencedor.nome}**")

    if st.button("Próxima vaza"):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0

        # acabou a mão do humano? então acabou a rodada
        if len(st.session_state.jogadores[0].mao) == 0:
            st.session_state.fase = "fim"
        else:
            st.session_state.fase = "jogada"

        st.rerun()

# =========================
# FIM DA RODADA
# =========================
elif st.session_state.fase == "fim":
    st.subheader("📊 Placar da Rodada")

    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos_rodada
        st.write(
            f"{j.nome} — Vaz as: {j.vazas} | Prognóstico: {j.prognostico} | "
            f"Pontos na rodada: {pontos_rodada} | Total: {j.pontos}"
        )

    st.info(f"🂡 Próximo mão será: **{st.session_state.ordem[0].nome}** (vencedor da última vaza)")

    if st.button("🔄 Reiniciar"):
        st.session_state.clear()
        st.rerun()


