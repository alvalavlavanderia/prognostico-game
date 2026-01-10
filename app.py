import streamlit as st
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")

st.markdown(
    """
    <style>
      .block-container { padding-top: 0.8rem; padding-bottom: 0.6rem; max-width: 980px; }
      h1 { margin-bottom: 0.2rem; }
      h2, h3 { margin-top: 0.7rem; margin-bottom: 0.35rem; }
      .stButton>button { border-radius: 12px; padding: 0.52rem 0.55rem; font-weight: 800; }
      .stButton>button:disabled { opacity: 0.32; }
      .cardline { display:flex; flex-wrap:wrap; gap:8px; }
      .cardpill {
        border: 1px solid rgba(60,60,60,.20);
        border-radius: 12px;
        padding: 8px 10px;
        background: rgba(250,250,250,.95);
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
        font-weight: 900;
        font-size: 18px;
        min-width: 54px;
        text-align:center;
      }
      .small { font-size: 12px; opacity: 0.85; }
      footer { visibility: hidden; }
      .tight { margin-top: 0.2rem; margin-bottom: 0.2rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# CONSTANTES
# =========================
TRUNFO = "♥"

NAIPES = ["♦", "♠", "♣", "♥"]  # ordem visual: ouro, espada, paus, copas
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
        return f"<span style='color:{cor}; font-size:18px; font-weight:900'>{self.valor}{self.naipe}</span>"

class Jogador:
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = None
        self.vazas = 0
        self.pontos = 0

# =========================
# FUNÇÕES UTIL
# =========================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def ordenar_mao(mao):
    return sorted(mao, key=lambda c: c.peso())

def somente_copas(mao):
    return all(c.naipe == TRUNFO for c in mao) if mao else False

def render_cartinhas(mao):
    html = "<div class='cardline'>"
    for c in mao:
        cor = NAIPE_COR[c.naipe]
        html += f"<div class='cardpill' style='color:{cor}'>{c.valor}{c.naipe}</div>"
    html += "</div>"
    return html

# =========================
# REGRAS: CARTAS LEGAIS
# =========================
def cartas_legais(jogador, naipe_base, hearts_broken, primeira_vaza):
    """
    Regras:
    A) PRIMEIRA VAZA DA RODADA:
       - ♥ NÃO pode ser jogada por ninguém (nem descarte), exceto se o jogador só tiver ♥.
    B) Fora da primeira vaza:
       - Se não é mão (naipe_base existe): deve seguir naipe se tiver.
       - Se é mão: não pode abrir com ♥ enquanto hearts_broken == False, exceto se só tiver ♥.
    """
    mao = jogador.mao[:]
    if not mao:
        return []

    # A) Primeira vaza trava copas geral (exceto só-copas)
    if primeira_vaza and not somente_copas(mao):
        sem_copas = [c for c in mao if c.naipe != TRUNFO]
        if sem_copas:
            mao = sem_copas

    # Seguir naipe se já existe naipe base
    if naipe_base is not None:
        seguindo = [c for c in mao if c.naipe == naipe_base]
        return seguindo if seguindo else mao

    # É mão: copas travada até quebrar (exceto só-copas)
    if (not hearts_broken) and (not somente_copas(mao)):
        nao_copas = [c for c in mao if c.naipe != TRUNFO]
        if nao_copas:
            return nao_copas

    return mao

# =========================
# VENCEDOR (TRUNFO = COPAS)
# =========================
def definir_vencedor(mesa, naipe_base):
    copas = [x for x in mesa if x["carta"].naipe == TRUNFO]
    if copas:
        return max(copas, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

    seguindo = [x for x in mesa if x["carta"].naipe == naipe_base]
    return max(seguindo, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

def rank_carta_para_vaza(carta, naipe_base):
    """
    Rank alto = mais forte na vaza atual.
    Trunfo (♥) > naipe_base > outros.
    """
    if carta.naipe == TRUNFO:
        return 200 + VALOR_PESO[carta.valor]
    if naipe_base is not None and carta.naipe == naipe_base:
        return 100 + VALOR_PESO[carta.valor]
    return 0 + VALOR_PESO[carta.valor]

def melhor_rank_na_mesa(mesa, naipe_base):
    if not mesa:
        return -1
    return max(rank_carta_para_vaza(x["carta"], naipe_base) for x in mesa)

# =========================
# IA ESPERTA (Bater prognóstico)
# =========================
def escolher_carta_ia(jogador, legais, naipe_base, mesa):
    """
    IA heurística:
    - precisa ganhar? tenta ganhar com o MENOR gasto possível (menor carta que ainda vence).
    - precisa perder? tenta perder (menor carta, evita trunfo).
    """
    legais = ordenar_mao(legais)

    # quanto falta para bater o prognóstico
    alvo = jogador.prognostico if jogador.prognostico is not None else 0
    falta = alvo - jogador.vazas
    quer_ganhar = falta > 0

    # Se é mão (mesa vazia), não dá pra comparar contra alguém, então:
    if not mesa:
        if quer_ganhar:
            # tenta começar "forte" mas sem desperdiçar: pega uma carta média/alta do naipe mais forte disponível
            # prioriza trunfo se permitido, senão pega a mais alta do naipe que tiver mais cartas
            # simplificado: pega a mais alta entre as legais
            return max(legais, key=lambda c: rank_carta_para_vaza(c, c.naipe))
        else:
            # quer perder: joga a mais baixa (preferindo não-trunfo)
            nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
            pool = nao_trunfo if nao_trunfo else legais
            return min(pool, key=lambda c: rank_carta_para_vaza(c, c.naipe))

    # Não é mão: existe naipe_base (pelo menos a primeira carta já existe)
    melhor_atual = melhor_rank_na_mesa(mesa, naipe_base)

    if quer_ganhar:
        # pega a menor carta que ainda vence
        vencedoras = [c for c in legais if rank_carta_para_vaza(c, naipe_base) > melhor_atual]
        if vencedoras:
            return min(vencedoras, key=lambda c: rank_carta_para_vaza(c, naipe_base))
        # se não dá pra vencer, descarta a menor
        nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
        pool = nao_trunfo if nao_trunfo else legais
        return min(pool, key=lambda c: rank_carta_para_vaza(c, naipe_base))
    else:
        # quer perder: joga a menor possível, evitando trunfo
        nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
        pool = nao_trunfo if nao_trunfo else legais
        return min(pool, key=lambda c: rank_carta_para_vaza(c, naipe_base))

# =========================
# AÇÕES
# =========================
def resetar_partida():
    st.session_state.clear()
    st.rerun()

def jogar_carta(jogador, carta_escolhida):
    jogador.mao.remove(carta_escolhida)
    st.session_state.mesa.append({"jogador": jogador, "carta": carta_escolhida})

    # define naipe base
    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta_escolhida.naipe

    # quebra copas se alguém jogou copas (se na 1ª vaza foi permitido, é porque só tinha copas)
    if carta_escolhida.naipe == TRUNFO:
        st.session_state.hearts_broken = True

    st.session_state.indice_jogador += 1
    st.rerun()

def pontuar_rodada_uma_vez():
    if st.session_state.get("rodada_pontuada", False):
        return
    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        j.pontos += pontos_rodada
    st.session_state.rodada_pontuada = True

# =========================
# ESTADO
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
    "primeira_vaza": True,
    "mao_inicial_idx": 0,
    "bid_idx": 0,  # índice de prognóstico (ordem da mesa)
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# UI HEADER
# =========================
st.title("🎴 Jogo de Prognóstico")
st.markdown("<div class='small tight'>♥ Copas é trunfo. Copas travada até quebrar. Na 1ª vaza: ♥ proibida (exceto se o jogador só tiver ♥).</div>", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
if st.session_state.jogadores:
    with st.sidebar:
        st.markdown("## 📊 Placar (Total)")
        for j in st.session_state.jogadores:
            st.write(f"**{j.nome}** — **{j.pontos}** pts")

        st.markdown("---")
        st.markdown("## 🎯 Rodada atual")
        for j in st.session_state.jogadores:
            prog_txt = "-" if j.prognostico is None else str(j.prognostico)
            st.write(f"{j.nome}: vazas **{j.vazas}** | prog. **{prog_txt}**")

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

        st.session_state.jogadores = [Jogador(nome, humano=(i == 0)) for i, nome in enumerate(lista)]
        st.session_state.rodada_inicial = int(cartas_por_jogador)
        st.session_state.rodada_atual = int(cartas_por_jogador)
        st.session_state.numero_rodada = 1

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
    st.session_state.primeira_vaza = True
    st.session_state.rodada_pontuada = False
    st.session_state.bid_idx = 0

    # reset stats rodada
    for j in st.session_state.jogadores:
        j.vazas = 0
        j.prognostico = None

    # distribui cartas
    baralho = criar_baralho()
    random.shuffle(baralho)
    qtd = st.session_state.rodada_atual
    for j in st.session_state.jogadores:
        j.mao = ordenar_mao([baralho.pop() for _ in range(qtd)])

    # mão aleatório por rodada
    start_idx = random.randrange(len(st.session_state.jogadores))
    st.session_state.mao_inicial_idx = start_idx
    st.session_state.ordem = st.session_state.jogadores[start_idx:] + st.session_state.jogadores[:start_idx]

    st.session_state.fase = "prognostico"
    st.rerun()

# =========================
# FASE: PROGNÓSTICO (sequencial por ordem, revelando só anteriores)
# =========================
elif st.session_state.fase == "prognostico":
    st.subheader(f"📌 Rodada {st.session_state.numero_rodada} — {st.session_state.rodada_atual} cartas")
    st.info(f"🂡 Mão (quem inicia a rodada): **{st.session_state.ordem[0].nome}**")

    humano = next(j for j in st.session_state.jogadores if j.humano)

    # Avança bids automáticos dos bots ANTES do humano (na ordem)
    # até chegar no humano ou completar todos
    while st.session_state.bid_idx < len(st.session_state.ordem):
        atual = st.session_state.ordem[st.session_state.bid_idx]
        if atual.humano:
            break
        if atual.prognostico is None:
            atual.prognostico = random.randint(0, len(atual.mao))
        st.session_state.bid_idx += 1

    # Definição: quais prognósticos mostrar agora?
    # Mostrar apenas os anteriores ao humano na ordem, a menos que o humano seja o pé (último).
    idx_humano = st.session_state.ordem.index(humano)
    humano_e_pe = (idx_humano == len(st.session_state.ordem) - 1)

    st.markdown("### ✅ Prognósticos visíveis (antes de você)")
    linhas = []
    for i, j in enumerate(st.session_state.ordem):
        if j.humano:
            continue
        if humano_e_pe:
            # se humano é pé, vê todos
            prog = "-" if j.prognostico is None else str(j.prognostico)
            linhas.append((j.nome, prog))
        else:
            # vê só quem é anterior ao humano na ordem
            if i < idx_humano:
                prog = "-" if j.prognostico is None else str(j.prognostico)
                linhas.append((j.nome, prog))

    if linhas:
        st.table(linhas)
    else:
        st.caption("Nenhum prognóstico visível ainda (você é o primeiro a palpitar).")

    st.markdown("### 🂡 Suas cartas")
    st.markdown(render_cartinhas(ordenar_mao(humano.mao)), unsafe_allow_html=True)

    prog = st.number_input("Seu prognóstico (quantas vazas você fará)", 0, len(humano.mao), 0, step=1)

    if st.button("Confirmar meu prognóstico"):
        humano.prognostico = int(prog)
        st.session_state.bid_idx += 1  # passa do humano

        # Agora os bots restantes (depois do humano) palpitam, mas isso acontece após seu palpite
        while st.session_state.bid_idx < len(st.session_state.ordem):
            atual = st.session_state.ordem[st.session_state.bid_idx]
            if atual.prognostico is None:
                atual.prognostico = random.randint(0, len(atual.mao))
            st.session_state.bid_idx += 1

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

        # vencedor começa próxima vaza
        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]

        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado_vaza"
        st.rerun()

    # mesa atual
    if st.session_state.mesa:
        st.markdown("### 🪑 Mesa (até agora)")
        for item in st.session_state.mesa:
            st.markdown(f"- **{item['jogador'].nome}**: {item['carta'].render_html()}", unsafe_allow_html=True)
        st.caption(f"Naipe da vaza: {st.session_state.naipe_base}")

    jogador = st.session_state.ordem[st.session_state.indice_jogador]
    st.markdown(f"## 🎴 Vez de: **{jogador.nome}**")

    legais = cartas_legais(
        jogador=jogador,
        naipe_base=st.session_state.naipe_base,
        hearts_broken=st.session_state.hearts_broken,
        primeira_vaza=st.session_state.primeira_vaza
    )
    legais_set = set(c.texto() for c in legais)

    # HUMANO: mostra todas cartas, trava inválidas
    if jogador.humano:
        st.markdown("### 🂡 Sua mão (cartas inválidas travadas)")
        mao_ordenada = ordenar_mao(jogador.mao)

        cols = st.columns(6)
        for i, carta in enumerate(mao_ordenada):
            col = cols[i % 6]
            label = carta.texto()
            disabled = label not in legais_set
            key = f"btn_{st.session_state.numero_rodada}_{st.session_state.numero_vaza}_{st.session_state.indice_jogador}_{jogador.nome}_{label}_{i}"
            if col.button(label, key=key, use_container_width=True, disabled=disabled):
                jogar_carta(jogador, carta)

        if st.session_state.primeira_vaza and not somente_copas(jogador.mao):
            st.caption("Regra: na 1ª vaza, ♥ é proibida (exceto se você só tiver ♥).")
        if (not st.session_state.hearts_broken) and (st.session_state.naipe_base is None) and not somente_copas(jogador.mao):
            st.caption("Regra: enquanto copas não quebrou, não pode abrir uma vaza com ♥.")

    # IA: usa heurística inteligente
    else:
        carta = escolher_carta_ia(
            jogador=jogador,
            legais=legais,
            naipe_base=st.session_state.naipe_base,
            mesa=st.session_state.mesa
        )

        jogador.mao.remove(carta)
        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe

        if carta.naipe == TRUNFO:
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

    # ✅ removido o “parcial da rodada” daqui (já tem no sidebar)

    if st.button("➡ Continuar"):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0
        st.session_state.numero_vaza += 1

        # após terminar a vaza 1, não é mais primeira vaza
        if st.session_state.primeira_vaza:
            st.session_state.primeira_vaza = False

        # acabou a rodada?
        humano = next(j for j in st.session_state.jogadores if j.humano)
        if len(humano.mao) == 0:
            st.session_state.fase = "fim_rodada"
        else:
            st.session_state.fase = "jogada"

        st.rerun()

# =========================
# FASE: FIM DA RODADA
# =========================
elif st.session_state.fase == "fim_rodada":
    pontuar_rodada_uma_vez()

    st.subheader(f"✅ Fim da Rodada {st.session_state.numero_rodada} ({st.session_state.rodada_atual} cartas)")

    st.markdown("## 📌 Resultado da rodada")
    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        acertou = "✅" if j.vazas == j.prognostico else "❌"
        st.write(
            f"**{j.nome}** — Vaz as: {j.vazas} | Prog.: {j.prognostico} {acertou} | "
            f"Pontos na rodada: **{pontos_rodada}** | Total: **{j.pontos}**"
        )

    with st.expander("🧾 Ver histórico completo da rodada"):
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








