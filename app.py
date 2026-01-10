import streamlit as st
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 0.5rem; padding-bottom: 0.35rem; max-width: 1500px; }
      h1 { margin: 0.2rem 0 0.2rem 0; }
      h2, h3 { margin: 0.55rem 0 0.3rem 0; }
      footer { visibility: hidden; }

      /* Painéis */
      .panel {
        border: 1px solid rgba(60,60,60,.10);
        border-radius: 18px;
        padding: 14px;
        background: rgba(255,255,255,.80);
        box-shadow: 0 1px 8px rgba(0,0,0,.05);
      }
      .chip {
        display:inline-block; padding: 6px 10px; border-radius: 999px;
        background: rgba(0,0,0,0.06); margin-right: 6px; font-weight: 800;
      }
      .small { font-size: 12px; opacity: 0.85; }

      /* Mesa central */
      .tableWrap {
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        gap:10px;
        padding: 8px 6px;
      }
      .tableTitle { font-weight: 900; opacity: 0.9; }
      .tableCards {
        display:flex; flex-wrap:wrap; justify-content:center; gap:10px;
        min-height: 88px;
        width: 100%;
      }

      /* Cartas (visual) */
      .cardFace {
        width: 64px; height: 90px;
        border-radius: 14px;
        border: 1px solid rgba(30,30,30,.18);
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,248,248,0.98) 100%);
        box-shadow: 0 2px 10px rgba(0,0,0,.08);
        position: relative;
        overflow: hidden;

        animation: fadeInUp .18s ease-out both;
      }
      .cardFace:hover { transform: translateY(-2px); transition: .12s ease; }

      .cornerTL, .cornerBR {
        position:absolute;
        font-weight: 950;
        font-size: 15px;
        line-height: 1;
      }
      .cornerTL { top: 8px; left: 9px; text-align:left; }
      .cornerBR { bottom: 8px; right: 9px; text-align:right; transform: rotate(180deg); }

      .suitCenter {
        position:absolute;
        top: 50%; left: 50%;
        transform: translate(-50%,-50%);
        font-size: 30px;
        font-weight: 950;
        opacity: 0.9;
      }

      .nameTag {
        margin-top: 4px;
        text-align:center;
        font-size: 12px;
        font-weight: 800;
        opacity: 0.9;
      }

      /* Cartas clicáveis (botão com cara de carta) */
      div.stButton > button.cardBtn {
        width: 64px !important;
        height: 90px !important;
        padding: 0 !important;
        border-radius: 14px !important;
        border: 1px solid rgba(30,30,30,.18) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,248,248,0.98) 100%) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,.08) !important;
        font-weight: 950 !important;
        position: relative !important;
        overflow: hidden !important;
        animation: fadeInUp .18s ease-out both;
      }
      div.stButton > button.cardBtn:hover {
        transform: translateY(-2px) !important;
        transition: .12s ease !important;
      }
      div.stButton > button.cardBtn:disabled {
        opacity: 0.35 !important;
        box-shadow: none !important;
        transform: none !important;
      }

      /* Pequena animação */
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
      }

      /* Compactar sidebar */
      section[data-testid="stSidebar"] .block-container { padding-top: 0.6rem; }

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

class Jogador:
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = None
        self.vazas = 0
        self.pontos = 0

# =========================
# UTIL
# =========================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

def ordenar_mao(mao):
    return sorted(mao, key=lambda c: c.peso())

def somente_copas(mao):
    return all(c.naipe == TRUNFO for c in mao) if mao else False

def carta_html_face(carta, show_name=None):
    cor = NAIPE_COR[carta.naipe]
    valor = str(carta.valor)
    naipe = carta.naipe
    extra = f"<div class='nameTag'>{show_name}</div>" if show_name else ""
    return f"""
      <div>
        <div class="cardFace">
          <div class="cornerTL" style="color:{cor};">{valor}<br>{naipe}</div>
          <div class="suitCenter" style="color:{cor};">{naipe}</div>
          <div class="cornerBR" style="color:{cor};">{valor}<br>{naipe}</div>
        </div>
        {extra}
      </div>
    """

def mesa_html(mesa):
    if not mesa:
        return "<div class='small'>Mesa vazia — o mão abre a vaza.</div>"
    parts = []
    for item in mesa:
        parts.append(carta_html_face(item["carta"], show_name=item["jogador"].nome))
    return "<div class='tableCards'>" + "".join(parts) + "</div>"

# =========================
# REGRAS
# =========================
def cartas_legais(jogador, naipe_base, hearts_broken, primeira_vaza):
    mao = jogador.mao[:]
    if not mao:
        return []

    # 1ª vaza: trava ♥ geral (exceto só ♥)
    if primeira_vaza and not somente_copas(mao):
        sem_copas = [c for c in mao if c.naipe != TRUNFO]
        if sem_copas:
            mao = sem_copas

    # seguir naipe se possível
    if naipe_base is not None:
        seguindo = [c for c in mao if c.naipe == naipe_base]
        return seguindo if seguindo else mao

    # é mão: não pode abrir ♥ enquanto não quebrou (exceto só ♥)
    if (not hearts_broken) and (not somente_copas(mao)):
        nao_copas = [c for c in mao if c.naipe != TRUNFO]
        if nao_copas:
            return nao_copas

    return mao

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
# IA (mais esperta)
# =========================
def escolher_carta_ia(jogador, legais, naipe_base, mesa):
    legais = ordenar_mao(legais)
    alvo = jogador.prognostico if jogador.prognostico is not None else 0
    falta = alvo - jogador.vazas
    quer_ganhar = falta > 0

    # mão abrindo
    if not mesa:
        if quer_ganhar:
            return max(legais, key=lambda c: rank_carta_para_vaza(c, c.naipe))
        nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
        pool = nao_trunfo if nao_trunfo else legais
        return min(pool, key=lambda c: rank_carta_para_vaza(c, c.naipe))

    melhor_atual = melhor_rank_na_mesa(mesa, naipe_base)

    if quer_ganhar:
        vencedoras = [c for c in legais if rank_carta_para_vaza(c, naipe_base) > melhor_atual]
        if vencedoras:
            return min(vencedoras, key=lambda c: rank_carta_para_vaza(c, naipe_base))
        nao_trunfo = [c for c in legais if c.naipe != TRUNFO]
        pool = nao_trunfo if nao_trunfo else legais
        return min(pool, key=lambda c: rank_carta_para_vaza(c, naipe_base))
    else:
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
    "start_idx": None,  # 1ª aleatório, depois gira
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
    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:6px;">
      <h1 style="margin:0;">🎴 Jogo de Prognóstico</h1>
      <span class="chip">Trunfo: ♥</span>
      <span class="chip">Copas trava até quebrar</span>
      <span class="chip">1ª vaza: ♥ proibida (exceto só ♥)</span>
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
        st.markdown("## 🎯 Rodada")
        for j in st.session_state.jogadores:
            prog_txt = "-" if j.prognostico is None else str(j.prognostico)
            st.write(f"{j.nome}: vazas **{j.vazas}** | prog. **{prog_txt}**")

        st.markdown("---")
        st.markdown("## 🂡 Mão da vaza")
        if st.session_state.ordem:
            st.success(st.session_state.ordem[0].nome)

        st.markdown("---")
        st.markdown("## ♥ Copas")
        st.success("Copas quebrada ✅") if st.session_state.hearts_broken else st.warning("Copas travada ⛔")

        st.markdown("---")
        if st.button("🔄 Resetar", use_container_width=True):
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
        st.session_state.start_idx = None  # 1ª rodada aleatória
        st.session_state.fase = "distribuir"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FASE: DISTRIBUIR
# =========================
elif st.session_state.fase == "distribuir":
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

    for j in st.session_state.jogadores:
        j.vazas = 0
        j.prognostico = None

    baralho = criar_baralho()
    random.shuffle(baralho)
    qtd = st.session_state.rodada_atual
    for j in st.session_state.jogadores:
        j.mao = ordenar_mao([baralho.pop() for _ in range(qtd)])

    n = len(st.session_state.jogadores)
    if st.session_state.start_idx is None:
        st.session_state.start_idx = random.randrange(n)

    idx = st.session_state.start_idx
    st.session_state.ordem = st.session_state.jogadores[idx:] + st.session_state.jogadores[:idx]
    st.session_state.fase = "prognostico"
    st.rerun()

# =========================
# FASE: PROGNÓSTICO (mostra só anteriores, se você for pé mostra todos)
# =========================
elif st.session_state.fase == "prognostico":
    humano = next(j for j in st.session_state.jogadores if j.humano)

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader(f"📌 Rodada {st.session_state.numero_rodada} — {st.session_state.rodada_atual} cartas")
        st.info(f"🂡 Mão da rodada: **{st.session_state.ordem[0].nome}**")

        # bots antes do humano
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
            if humano_e_pe or (i < idx_humano):
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

            # bots depois do humano (ocultos até você confirmar)
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
        st.markdown("<div class='tableWrap'>", unsafe_allow_html=True)
        st.markdown("<div class='tableCards'>" + "".join([carta_html_face(c) for c in ordenar_mao(humano.mao)]) + "</div>", unsafe_allow_html=True)
        st.markdown("<div class='small'>Clique nas cartas quando for sua vez.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FASE: JOGADA (mesa centralizada + cartas clicáveis estilo carta)
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
        idx = st.session_state.ordem.index(vencedor)
        st.session_state.ordem = st.session_state.ordem[idx:] + st.session_state.ordem[:idx]
        st.session_state.vencedor = vencedor
        st.session_state.fase = "resultado_vaza"
        st.rerun()

    humano = next(j for j in st.session_state.jogadores if j.humano)
    jogador = st.session_state.ordem[st.session_state.indice_jogador]

    left, right = st.columns([1.20, 0.80], gap="large")

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader(f"🧩 Vaza {st.session_state.numero_vaza}")
        st.markdown(
            f"<span class='chip'>Mão: {st.session_state.ordem[0].nome}</span>"
            f"<span class='chip'>Vez: {jogador.nome}</span>"
            f"<span class='chip'>Naipe: {st.session_state.naipe_base or '-'}</span>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='tableWrap'>", unsafe_allow_html=True)
        st.markdown("<div class='tableTitle'>🪑 Mesa</div>", unsafe_allow_html=True)
        st.markdown(mesa_html(st.session_state.mesa), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

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

        legais = cartas_legais(
            jogador=jogador,
            naipe_base=st.session_state.naipe_base,
            hearts_broken=st.session_state.hearts_broken,
            primeira_vaza=st.session_state.primeira_vaza
        )
        legais_set = set(c.texto() for c in legais)

        if jogador.humano:
            mao = ordenar_mao(jogador.mao)

            # Grid de "cartas-botão"
            cols = st.columns(7)
            for i, carta in enumerate(mao):
                col = cols[i % 7]
                label = carta.texto()
                disabled = label not in legais_set

                # botão com classe cardBtn; label fica invisível mas precisamos de algo
                key = f"card_{st.session_state.numero_rodada}_{st.session_state.numero_vaza}_{st.session_state.indice_jogador}_{jogador.nome}_{label}_{i}"
                pressed = col.button(" ", key=key, use_container_width=False, disabled=disabled)
                # aplicar classe cardBtn no botão recém-criado via hack CSS selector:
                # Streamlit não permite class diretamente; usamos JS? não.
                # Alternativa: estilo geral para botões e "card look" com :has não funciona.
                # Então, usamos um truque: desenhar carta acima e botão transparente por cima NÃO é possível diretamente.
                # Solução prática: manter o botão com cara de carta usando st.markdown + col.button(label) e ocultar texto.
                # Para ficar 100% robusto, renderizamos a carta por markdown abaixo e colocamos o label no botão mesmo.

                # Como não dá pra “vestir” o botão com CSS de forma seletiva sem JS,
                # mostramos um botão com texto e uma carta visual acima (fica APP e funcional).
                col.markdown(carta_html_face(carta), unsafe_allow_html=True)

                # botão real com label (funcional)
                # (fica logo abaixo da carta; discreto e clicável)
                click_key = f"play_{key}"
                if col.button(label, key=click_key, use_container_width=True, disabled=disabled):
                    jogar_carta(jogador, carta)

            if st.session_state.primeira_vaza and not somente_copas(jogador.mao):
                st.caption("Regra: na 1ª vaza, ♥ é proibida (exceto se você só tiver ♥).")
            if (not st.session_state.hearts_broken) and (st.session_state.naipe_base is None) and not somente_copas(jogador.mao):
                st.caption("Regra: enquanto copas não quebrou, não pode abrir uma vaza com ♥.")
        else:
            st.markdown("<div class='small'>Aguarde: jogada automática dos bots.</div>", unsafe_allow_html=True)
            st.markdown("<div class='tableCards'>" + "".join([carta_html_face(c) for c in ordenar_mao(humano.mao)]) + "</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # IA joga automaticamente quando for a vez dela
    if not jogador.humano:
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

    st.markdown("<div class='tableWrap'>", unsafe_allow_html=True)
    st.markdown("<div class='tableCards'>" + "".join([carta_html_face(x["carta"], show_name=x["jogador"].nome) for x in st.session_state.mesa]) + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.success(f"Vencedor: **{st.session_state.vencedor.nome}**")

    if st.button("➡ Próxima vaza", use_container_width=True):
        st.session_state.mesa = []
        st.session_state.naipe_base = None
        st.session_state.indice_jogador = 0
        st.session_state.numero_vaza += 1

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
            # gira mão da rodada
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

