import streamlit as st
import random

# =========================
# CONFIG & CONSTANTES
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

    def render_html(self):
        cor = NAIPE_COR[self.naipe]
        return f"<span style='color:{cor}; font-size:20px; font-weight:800'>{self.valor}{self.naipe}</span>"

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

def somente_copas(mao):
    return all(c.naipe == "♥" for c in mao) if mao else False

def cartas_legais(jogador, naipe_base, hearts_broken):
    """
    REGRAS:
    1) Se naipe_base existe (não é mão): deve seguir naipe se tiver.
    2) Se é mão (naipe_base None):
       - NÃO pode começar com ♥ enquanto hearts_broken == False
         EXCETO se só tiver ♥ na mão.
    """
    mao = jogador.mao
    if not mao:
        return []

    # Seguir naipe se naipe_base existe
    if naipe_base is not None:
        seguindo = [c for c in mao if c.naipe == naipe_base]
        return seguindo if seguindo else mao

    # É mão: copas travada de verdade
    if not hearts_broken and not somente_copas(mao):
        nao_copas = [c for c in mao if c.naipe != "♥"]
        if nao_copas:
            return nao_copas

    return mao

def definir_vencedor(mesa, naipe_base):
    """
    - ♥ é trunfo
    - Se tiver ♥ na mesa, maior ♥ vence
    - Senão, maior carta do naipe_base vence
    """
    copas = [x for x in mesa if x["carta"].naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

    seguindo = [x for x in mesa if x["carta"].naipe == naipe_base]
    return max(seguindo, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

def resetar_partida():
    st.session_state.clear()
    st.rerun()

def jogar_carta(jogador, carta_escolhida):
    # remove da mão real
    jogador.mao.remove(carta_escolhida)

    # coloca na mesa
    st.session_state.mesa.append({"jogador": jogador, "carta": carta_escolhida})

    # define naipe base se for a primeira da vaza
    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta_escolhida.naipe

    # copas quebra ao ser jogada por qualquer um
    if carta_escolhida.naipe == "♥":
        st.session_state.hearts_broken = True

    # próximo jogador da vaza
    st.session_state.indice_jogador += 1
    st.rerun()

def pontuar_rodada_uma_vez():
    """
    Evita o bug de pontuação duplicada por rerun.
    Só pontua se 'rodada_pontuada' for False.
    """
    if st.session_state.get("rodada_pontuada", False):
        return

    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos_rodada

    st.session_state.rodada_pontuada = True

# =========================
# ESTADO (INICIALIZAÇÃO)
# =========================
defaults = {
    "fase": "inicio",
    "jogadores": [],
    "ordem": [],
    "mesa": [],
    "naipe_base": None,
    "indice_jogador": 0,
    "vencedor": None,
    "hearts_broken": False,
    "historico_vazas": [],
    "rodada_inicial": 10,
    "rodada_atual": 10,
    "numero_vaza": 1,
    "numero_rodada": 1,
    "rodada_pontuada": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# UI
# =========================
st.title("🎴 Jogo de Prognóstico")

# Sidebar (placar e infos)
if st.session_state.jogadores:
    with st.sidebar:
        st.markdown("## 📊 Placar (Total)")
        for j in st.session_state.jogadores:
            st.write(f"**{j.nome}** — **{j.pontos}** pts")

        st.markdown("---")
        st.markdown("## 🎯 Rodada atual")
        for j in st.session_state.jogadores:
            st.write(f"{j.nome}: vazas **{j.vazas}** / prog. **{j.prognostico}**")

        st.markdown("---")
        st.markdown("## 🂡 Mão da vaza")
        if st.session_state.ordem:
            st.success(st.session_state.ordem[0].nome)

        st.markdown("---")
        st.markdown("## ♥ Copas")
        if st.session_state.hearts_broken:
            st.success("Copas quebrada ✅ (pode abrir com ♥)")
        else:
            st.warning("Copas travada ⛔ (não pode abrir com ♥)")

        st.markdown("---")
        st.markdown("## 🧾 Histórico (rodada)")
        if st.session_state.historico_vazas:
            for i, h in enumerate(st.session_state.historico_vazas, start=1):
                st.write(f"Vaza {i}: 🏆 {h['vencedor']}")
        else:
            st.caption("Nenhuma vaza ainda.")

        st.markdown("---")
        if st.button("🔄 Resetar partida"):
            resetar_partida()

# =========================
# FASE: INÍCIO
# =========================
if st.session_state.fase == "inicio":
    nomes = st.text_input("Jogadores (primeiro é você) — separados por vírgula", "Você, Ana, Bruno, Carlos")

    lista_tmp = [n.strip() for n in nomes.split(",") if n.strip()]
    n_jog = max(2, len(lista_tmp))
    max_cartas = 52 // n_jog

    cartas_por_jogador = st.number_input(
        f"Cartas por jogador (máx p/ {n_jog} jogadores = {max_cartas})",
        min_value=1,
        max_value=max_cartas,
        value=min(10, max_cartas),
        step=1
    )

    st.caption("Dica: para 4 jogadores, use 10 cartas (sobram 2 no baralho).")

    if st.button("▶ Iniciar"):
        lista = [n.strip() for n in nomes.split(",") if n.strip()]
        if len(lista) < 2:
            st.error("Informe pelo menos 2 jogadores.")
            st.stop()

        jogadores = [Jogador(nome, humano=(i == 0)) for i, nome in enumerate(lista)]
        st.session_state.jogadores = jogadores

        st.session_state.rodada_inicial = int(cartas_por_jogador)
        st.session_state.rodada_atual = int(cartas_por_jogador)
        st.session_state.numero_rodada = 1
        st.session_state.ordem = jogadores[:]  # ordem inicial

        st.session_state.fase = "distribuir"
        st.rerun()

# =========================
# FASE: DISTRIBUIR
# =========================
elif st.session_state.fase == "distribuir":
    # reset rodada
    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.indice_jogador = 0
    st.session_state.vencedor = None
    st.session_state.hearts_broken = False
    st.session_state.historico_vazas = []
    st.session_state.numero_vaza = 1
    st.session_state.rodada_pontuada = False  # <<< importante

    # reset stats rodada
    for j in st.session_state.jogadores:
        j.vazas = 0
        j.prognostico = 0

    # distribui cartas
    baralho = criar_baralho()
    random.shuffle(baralho)
    qtd = st.session_state.rodada_atual

    for j in st.session_state.jogadores:
        j.mao = ordenar_mao([baralho.pop() for _ in range(qtd)])

    st.session_state.fase = "prognostico"
    st.rerun()

# =========================
# FASE: PROGNÓSTICO
# =========================
elif st.session_state.fase == "prognostico":
    st.subheader(f"📌 Rodada {st.session_state.numero_rodada} — {st.session_state.rodada_atual} cartas")

    humano = st.session_state.jogadores[0]
    humano.mao = ordenar_mao(humano.mao)

    st.markdown("### 🂡 Suas cartas (ordenadas por naipe e valor)")
    st.markdown(" ".join([c.render_html() for c in humano.mao]), unsafe_allow_html=True)

    prog = st.number_input("Seu prognóstico (quantas vazas você fará)", 0, len(humano.mao), 0, step=1)

    if st.button("Confirmar Prognóstico"):
        humano.prognostico = int(prog)
        for j in st.session_state.jogadores[1:]:
            j.prognostico = random.randint(0, len(j.mao))

        st.session_state.fase = "jogada"
        st.rerun()

# =========================
# FASE: JOGADA
# =========================
elif st.session_state.fase == "jogada":
    st.subheader(f"🧩 Vaza {st.session_state.numero_vaza} — Mão: {st.session_state.ordem[0].nome}")

    # Se terminou a vaza, resolve antes
    if st.session_state.indice_jogador >= len(st.session_state.ordem):
        vencedor = definir_vencedor(st.session_state.mesa, st.session_state.naipe_base)
        vencedor.vazas += 1

        hist = {
            "mesa": [(x["jogador"].nome, x["carta"].texto()) for x in st.session_state.mesa],
            "vencedor": vencedor.nome
        }
        st.session_state.historico_vazas.append(hist)

        # vencedor começa a próxima vaza
        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]

        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado_vaza"
        st.rerun()

    # Mesa até agora
    if st.session_state.mesa:
        st.markdown("### 🪑 Mesa (até agora)")
        for item in st.session_state.mesa:
            st.markdown(f"- **{item['jogador'].nome}**: {item['carta'].render_html()}", unsafe_allow_html=True)
        st.caption(f"Naipe da vaza: {st.session_state.naipe_base}")

    jogador = st.session_state.ordem[st.session_state.indice_jogador]
    st.markdown(f"## 🎴 Vez de: **{jogador.nome}**")

    legais = ordenar_mao(cartas_legais(jogador, st.session_state.naipe_base, st.session_state.hearts_broken))

    # HUMANO: cartas como BOTÕES
    if jogador.humano:
        st.markdown("### ✅ Suas jogadas válidas (clique na carta)")

        # Mostra também sua mão completa (só visual)
        mao_visual = ordenar_mao(jogador.mao)
        st.markdown("**Sua mão:** " + " ".join([c.render_html() for c in mao_visual]), unsafe_allow_html=True)

        # grid de botões
        cols = st.columns(6)
        for i, carta in enumerate(legais):
            col = cols[i % 6]
            label = carta.texto()
            # para diferenciar e evitar “botão repetir”
            key = f"play_{st.session_state.numero_rodada}_{st.session_state.numero_vaza}_{st.session_state.indice_jogador}_{jogador.nome}_{label}_{i}"
            if col.button(label, key=key, use_container_width=True):
                jogar_carta(jogador, carta)

        st.caption("Obs: se você tiver o naipe da vaza, só aparecem cartas daquele naipe (regra de seguir naipe).")

    # IA
    else:
        carta = random.choice(legais)
        jogador.mao.remove(carta)
        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe

        if carta.naipe == "♥":
            st.session_state.hearts_broken = True

        st.session_state.indice_jogador += 1
        st.rerun()

# =========================
# FASE: RESULTADO DA VAZA
# =========================
elif st.session_state.fase == "resultado_vaza":
    st.subheader("🏆 Resultado da Vaza")

    for item in st.session_state.mesa:
        st.markdown(f"- **{item['jogador'].nome}**: {item['carta'].render_html()}", unsafe_allow_html=True)

    st.success(f"Vencedor da vaza: **{st.session_state.vencedor.nome}**")

    st.markdown("### 📊 Placar (parcial da rodada)")
    for j in st.session_state.jogadores:
        st.write(f"{j.nome}: vazas {j.vazas} / prognóstico {j.prognostico}")

    if st.button("➡ Continuar"):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0
        st.session_state.numero_vaza += 1

        if len(st.session_state.jogadores[0].mao) == 0:
            st.session_state.fase = "fim_rodada"
        else:
            st.session_state.fase = "jogada"

        st.rerun()

# =========================
# FASE: FIM DA RODADA
# =========================
elif st.session_state.fase == "fim_rodada":
    # ✅ pontua apenas uma vez (corrige “pontos dobrados”)
    pontuar_rodada_uma_vez()

    st.subheader(f"✅ Fim da Rodada {st.session_state.numero_rodada} ({st.session_state.rodada_atual} cartas)")

    st.markdown("## 📌 Resultado da rodada")
    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        acertou = "✅" if j.vazas == j.prognostico else "❌"
        st.write(
            f"**{j.nome}** — Vaz as: {j.vazas} | Prognóstico: {j.prognostico} {acertou} | "
            f"Pontos na rodada: **{pontos_rodada}** | Total: **{j.pontos}**"
        )

    st.markdown("---")
    st.markdown("## 🧾 Histórico completo das vazas (rodada)")
    for i, h in enumerate(st.session_state.historico_vazas, start=1):
        jogadas_txt = ", ".join([f"{nome}:{carta}" for nome, carta in h["mesa"]])
        st.write(f"Vaza {i} → [{jogadas_txt}] — 🏆 {h['vencedor']}")

    st.markdown("---")
    proxima_cartas = st.session_state.rodada_atual - 1

    if proxima_cartas >= 1:
        st.info(f"Próxima rodada será com **{proxima_cartas}** cartas por jogador.")
        if st.button("▶ Iniciar próxima rodada"):
            st.session_state.rodada_atual = proxima_cartas
            st.session_state.numero_rodada += 1
            st.session_state.fase = "distribuir"
            st.rerun()
    else:
        st.success("🏁 Jogo finalizado! (Rodadas concluídas até 1 carta)")
        ranking = sorted(st.session_state.jogadores, key=lambda x: x.pontos, reverse=True)
        st.markdown("## 🏆 Ranking Final")
        for i, j in enumerate(ranking, start=1):
            st.write(f"{i}º — **{j.nome}**: {j.pontos} pts")

        if st.button("🔄 Jogar novamente"):
            resetar_partida()






