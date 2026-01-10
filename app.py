import streamlit as st
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 0.6rem; padding-bottom: 0.4rem; max-width: 1400px; }
      h1 { margin: 0.2rem 0 0.2rem 0; }
      h2, h3 { margin: 0.6rem 0 0.35rem 0; }
      .stButton>button { border-radius: 14px; padding: 0.52rem 0.55rem; font-weight: 900; }
      .stButton>button:disabled { opacity: 0.30; }
      .small { font-size: 12px; opacity: 0.85; }
      .chip { display:inline-block; padding: 6px 10px; border-radius: 999px; background: rgba(0,0,0,0.05); margin-right: 6px; font-weight: 700; }
      .panel { border: 1px solid rgba(60,60,60,.12); border-radius: 16px; padding: 14px; background: rgba(255,255,255,.75); box-shadow: 0 1px 6px rgba(0,0,0,.05); }
      .cardline { display:flex; flex-wrap:wrap; gap:8px; }
      .cardpill {
        border: 1px solid rgba(60,60,60,.18);
        border-radius: 14px;
        padding: 10px 12px;
        background: rgba(250,250,250,.96);
        box-shadow: 0 1px 5px rgba(0,0,0,.06);
        font-weight: 950;
        font-size: 18px;
        min-width: 58px;
        text-align:center;
      }
      .titleRow { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom: 6px; }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# CONSTANTES
# =========================
TRUNFO = "♥"

NAIPES = ["♦", "♠", "♣", "♥"]  # visual: ouro, espada, paus, copas
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
        return f"<span style='color:{cor}; font-size:18px; font-weight:950'>{self.valor}{self.naipe}</span>"

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
    mao = ordenar_mao(mao)
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
    A) 1ª VAZA DA RODADA:
       - ♥ proibida para todos, exceto se o jogador só tem ♥.
    B) Fora isso:
       - Se naipe_base existe: deve seguir naipe se tiver.
       - Se é mão: não pode abrir com ♥ enquanto hearts_broken == False (exceto só ♥).
    """
    mao = jogador.mao[:]
    if not mao:
        return []

    # A) Primeira vaza: trava copas geral (exceto só-copas)
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
# VENCEDOR / RANK
# =========================
def definir_vencedor(mesa, naipe_base):
    copas = [x for x in mesa if x["carta"].naipe == TRUNFO]
    if copas:
        return max(copas, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

    seguindo = [x for x in mesa if x["carta"].naipe == naipe_base]
    return max(seguindo, key=lambda x: VALOR_PESO[x["carta"].valor])["jogador"]

def rank_carta_para_vaza(carta, naipe_base):
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
# IA ESPERTA: tentar bater o próprio prognóstico
# =========================
def escolher_carta_ia(jogador, legais, naipe_base, mesa):
    legais = ordenar_mao(legais)
    alvo = jogador.prognostico if jogador.prognostico is not None else 0
    falta = alvo - jogador.vazas
    quer_ganhar = falta > 0

    # Se é mão (mesa vazia)
    if not mesa:
        if quer_ganhar:
            # abre com a mais forte dentre as legais (simplificado)
            return max(legais, key=lambda c: rank_carta_para_vaza(c, c.naipe))
        else:
            # tenta perder: menor carta, evitando trunfo
            nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
            pool = nao_trunfo if nao_trunfo else legais
            return min(pool, key=lambda c: rank_carta_para_vaza(c, c.naipe))

    # Não é mão: comparar com mesa
    melhor_atual = melhor_rank_na_mesa(mesa, naipe_base)

    if quer_ganhar:
        vencedoras = [c for c in legais if rank_carta_para_vaza(c, naipe_base) > melhor_atual]
        if vencedoras:
            return min(vencedoras, key=lambda c: rank_carta_para_vaza(c, naipe_base))
        # não dá pra vencer -> descarta baixo evitando trunfo
        nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
        pool = nao_trunfo if nao_trunfo else legais
        return min(pool, key=lambda c: rank_carta_para_vaza(c, naipe_base))
    else:
        # quer perder -> menor possível, evitando trunfo
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

    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta_escolhida.naipe

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
    "rodada_atual": 10,
    "numero_vaza": 1,
    "numero_rodada": 1,
    "rodada_pontuada": False,
    "primeira_vaza": True,
    "start_idx": None,  # <<< MÃO DA RODADA: 1ª aleatório, depois gira +1 por rodada
    "bid_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# HEADER
# =========================
st.markdown(
    """
    <div class='titleRow'>
      <h1 style='margin:0;'>🎴 Jogo de Prognóstico</h1>
      <span class='chip'>Trunfo: ♥</span>
      <span class='chip'>Copas trava até quebrar</span>
      <span class='chip'>1ª vaza: ♥ proibida (exceto só ♥)</span>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================
if st.session_state.jogadores:
    with st.sidebar:
        st.markdown("## 📊 Placar")
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
            st.success("Copas quebrada ✅")
        else:
            st.warning("Copas travada ⛔")

        st.markdown("---")
        if st.button("🔄 Resetar partida"):
            resetar_partida()

# =========================
# FASE: INÍCIO
# =========================
if st.session_state.fase == "inicio":
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
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

    if st.button("▶ Iniciar", use_container_width=True):
        lista = [n.strip() for n in nomes.split(",") if n.strip()]
        if len(lista) < 2:
            st.error("Informe pelo menos 2 jogadores.")
            st.stop()

        st.session_state.jogadores = [Jogador(nome, humano=(i == 0)) for i, nome in enumerate(lista)]
        st.session_state.rodada_atual = int(cartas_por_jogador)
        st.session_state.numero_rodada = 1
        st.session_state.start_idx = None  # força 1ª rodada aleatória

        st.session_state.fase = "distribuir"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FASE: DISTRIBUIR (NOVA RODADA)
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

    # MÃO DA RODADA:
    # - 1ª rodada: aleatório
    # - depois: gira +1 por rodada (jogador ao lado)
    n = len(st.session_state.jogadores)
    if st.session_state.start_idx is None:
        st.session_state.start_idx = random.randrange(n)
    # ordem da rodada começa no start_idx
    idx = st.session_state.start_idx
    st.session_state.ordem = st.session_state.jogadores[idx:] + st.session_state.jogadores[:idx]

    st.session_state.fase = "prognostico"
    st.rerun()

# =========================
# FASE: PROGNÓSTICO (revela só anteriores, se você for pé mostra todos)
# =========================
elif st.session_state.fase == "prognostico":
    humano = next(j for j in st.session_state.jogadores if j.humano)

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader(f"📌 Rodada {st.session_state.numero_rodada} — {st.session_state.rodada_atual} cartas")
        st.info(f"🂡 Mão da rodada: **{st.session_state.ordem[0].nome}**")

        # bots antes do humano palpita (na ordem)
        while st.session_state.bid_idx < len(st.session_state.ordem):
            atual = st.session_state.ordem[st.session_state.bid_idx]
            if atual.humano:
                break
            if atual.prognostico is None:
                atual.prognostico = random.randint(0, len(atual.mao))
            st.session_state.bid_idx += 1

        idx_humano = st.session_state.ordem.index(humano)
        humano_e_pe = (idx_humano == len(st.session_state.ordem) - 1)

        st.markdown("### ✅ Prognósticos visíveis")
        linhas = []
        for i, j in enumerate(st.session_state.ordem):
            if j.humano:
                continue
            if humano_e_pe:
                prog = "-" if j.prognostico is None else str(j.prognostico)
                linhas.append((j.nome, prog))
            else:
                if i < idx_humano:
                    prog = "-" if j.prognostico is None else str(j.prognostico)
                    linhas.append((j.nome, prog))
        if linhas:
            st.table(linhas)
        else:
            st.caption("Você é o primeiro a palpitar (ninguém antes de você).")

        prog = st.number_input("Seu prognóstico", 0, len(humano.mao), 0, step=1)
        if st.button("Confirmar meu prognóstico", use_container_width=True):
            humano.prognostico = int(prog)
            st.session_state.bid_idx += 1

            # bots depois do humano palpita (sem mostrar antes)
            while st.session_state.bid_idx < len(st.session_state.ordem):
                atual = st.session_state.ordem[st.session_state.bid_idx]
                if atual.prognostico is None:
                    atual.prognostico = random.randint(0, len(atual.mao))
                st.session_state.bid_idx += 1

            st.session_state.fase = "jogada"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("🂡 Suas cartas")
        st.markdown(render_cartinhas(humano.mao), unsafe_allow_html=True)
        st.markdown("<div class='small'>Você só vê os prognósticos anteriores (a menos que seja o pé).</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FASE: JOGADA (APP layout 2 colunas)
# =========================
elif st.session_state.fase == "jogada":
    # resolve vaza se todos jogaram
    if st.session_state.indice_jogador >= len(st.session_state.ordem):
        vencedor = definir_vencedor(st.session_state.mesa, st.session_state.naipe_base)
        vencedor.vazas += 1

        st.session_state.historico_vazas.append({
            "mesa": [(x["jogador"].nome, x["carta"].texto()) for x in st.session_state.mesa],
            "vencedor": vencedor.nome
        })

        # vencedor começa próxima vaza
        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]

        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado_vaza"
        st.rerun()

    humano = next(j for j in st.session_state.jogadores if j.humano)
    jogador = st.session_state.ordem[st.session_state.indice_jogador]

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader(f"🧩 Vaza {st.session_state.numero_vaza}")
        st.markdown(f"<span class='chip'>Mão: {st.session_state.ordem[0].nome}</span>"
                    f"<span class='chip'>Vez: {jogador.nome}</span>", unsafe_allow_html=True)

        if st.session_state.mesa:
            st.markdown("### 🪑 Mesa")
            for item in st.session_state.mesa:
                st.markdown(f"- **{item['jogador'].nome}**: {item['carta'].render_html()}", unsafe_allow_html=True)
            st.markdown(f"<div class='small'>Naipe da vaza: <b>{st.session_state.naipe_base}</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='small'>Mesa vazia — o mão abre a vaza.</div>", unsafe_allow_html=True)

        # histórico compactado
        with st.expander("🧾 Histórico da rodada", expanded=False):
            if st.session_state.historico_vazas:
                for i, h in enumerate(st.session_state.historico_vazas, start=1):
                    jogadas_txt = ", ".join([f"{nome}:{carta}" for nome, carta in h["mesa"]])
                    st.write(f"Vaza {i} → [{jogadas_txt}] — 🏆 {h['vencedor']}")
            else:
                st.caption("Nenhuma vaza finalizada ainda.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("🂡 Sua mão")

        # cartas legais do jogador atual
        legais = cartas_legais(
            jogador=jogador,
            naipe_base=st.session_state.naipe_base,
            hearts_broken=st.session_state.hearts_broken,
            primeira_vaza=st.session_state.primeira_vaza
        )
        legais_set = set(c.texto() for c in legais)

        # HUMANO joga com botões travando inválidas
        if jogador.humano:
            mao_ordenada = ordenar_mao(jogador.mao)

            st.markdown(render_cartinhas(mao_ordenada), unsafe_allow_html=True)
            st.markdown("<div class='small'>Clique em uma carta. As inválidas ficam travadas.</div>", unsafe_allow_html=True)

            cols = st.columns(8)
            for i, carta in enumerate(mao_ordenada):
                col = cols[i % 8]
                label = carta.texto()
                disabled = label not in legais_set
                key = f"btn_{st.session_state.numero_rodada}_{st.session_state.numero_vaza}_{st.session_state.indice_jogador}_{jogador.nome}_{label}_{i}"
                if col.button(label, key=key, use_container_width=True, disabled=disabled):
                    jogar_carta(jogador, carta)

            if st.session_state.primeira_vaza and not somente_copas(jogador.mao):
                st.caption("Regra: na 1ª vaza, ♥ é proibida (exceto se você só tiver ♥).")
            if (not st.session_state.hearts_broken) and (st.session_state.naipe_base is None) and not somente_copas(jogador.mao):
                st.caption("Regra: enquanto copas não quebrou, não pode abrir uma vaza com ♥.")
        else:
            # Se não é humano, mostre mão humana só visual (pra ficar “APP”)
            st.markdown(render_cartinhas(ordenar_mao(humano.mao)), unsafe_allow_html=True)
            st.markdown("<div class='small'>Aguarde: jogada automática dos bots.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # IA joga automaticamente quando é a vez dela
    if (not jogador.humano):
        carta = escolher_carta_ia(jogador, legais, st.session_state.naipe_base, st.session_state.mesa)
        jogador.mao.remove(carta)
        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe
        if carta.naipe == TRUNFO:
            st.session_state.hearts_broken = True

        st.session_state.indice_jogador += 1
        st.rerun()

# =========================
# RESULTADO DA VAZA
# =========================
elif st.session_state.fase == "resultado_vaza":
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("🏆 Resultado da Vaza")

    for item in st.session_state.mesa:
        st.markdown(f"- **{item['jogador'].nome}**: {item['carta'].render_html()}", unsafe_allow_html=True)

    st.success(f"Vencedor: **{st.session_state.vencedor.nome}**")

    if st.button("➡ Próxima vaza", use_container_width=True):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0
        st.session_state.numero_vaza += 1

        # após terminar a vaza 1, não é mais primeira vaza
        if st.session_state.primeira_vaza:
            st.session_state.primeira_vaza = False

        humano = next(j for j in st.session_state.jogadores if j.humano)
        if len(humano.mao) == 0:
            st.session_state.fase = "fim_rodada"
        else:
            st.session_state.fase = "jogada"

        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FIM DA RODADA
# =========================
elif st.session_state.fase == "fim_rodada":
    pontuar_rodada_uma_vez()

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader(f"✅ Fim da Rodada {st.session_state.numero_rodada} ({st.session_state.rodada_atual} cartas)")

    for j in st.session_state.jogadores:
        pontos_rodada = j.vazas + (5 if j.vazas == j.prognostico else 0)
        acertou = "✅" if j.vazas == j.prognostico else "❌"
        st.write(
            f"**{j.nome}** — Vaz as: {j.vazas} | Prog.: {j.prognostico} {acertou} | "
            f"Pontos na rodada: **{pontos_rodada}** | Total: **{j.pontos}**"
        )

    with st.expander("🧾 Ver histórico completo da rodada", expanded=False):
        for i, h in enumerate(st.session_state.historico_vazas, start=1):
            jogadas_txt = ", ".join([f"{nome}:{carta}" for nome, carta in h["mesa"]])
            st.write(f"Vaza {i} → [{jogadas_txt}] — 🏆 {h['vencedor']}")

    st.markdown("---")

    proxima_cartas = st.session_state.rodada_atual - 1
    if proxima_cartas >= 1:
        if st.button("▶ Próxima rodada", use_container_width=True):
            # ✅ ROTACIONAR MÃO DA RODADA: próximo jogador (ao lado)
            n = len(st.session_state.jogadores)
            st.session_state.start_idx = (st.session_state.start_idx + 1) % n

            st.session_state.rodada_atual = proxima_cartas
            st.session_state.numero_rodada += 1
            st.session_state.fase = "distribuir"
            st.rerun()
    else:
        st.success("🏁 Jogo finalizado! (Rodadas até 1 carta)")
        ranking = sorted(st.session_state.jogadores, key=lambda x: x.pontos, reverse=True)
        st.markdown("## 🏆 Ranking Final")
        for i, j in enumerate(ranking, start=1):
            st.write(f"{i}º — **{j.nome}**: {j.pontos} pts")

        if st.button("🔄 Jogar novamente", use_container_width=True):
            resetar_partida()

    st.markdown("</div>", unsafe_allow_html=True)
