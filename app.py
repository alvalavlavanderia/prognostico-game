import streamlit as st
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="wide")

CSS = """
<style>
  .block-container { padding-top: 0.45rem; padding-bottom: 0.25rem; max-width: 1500px; }
  h1 { margin: 0.15rem 0 0.15rem 0; }
  h2, h3 { margin: 0.45rem 0 0.25rem 0; }
  footer { visibility: hidden; }
  div[data-testid="stToolbar"] { visibility: hidden; height: 0px; }

  /* Painéis */
  .panel {
    border: 1px solid rgba(60,60,60,.10);
    border-radius: 18px;
    padding: 12px 14px;
    background: rgba(255,255,255,.85);
    box-shadow: 0 1px 8px rgba(0,0,0,.05);
  }
  .chip {
    display:inline-block; padding: 6px 10px; border-radius: 999px;
    background: rgba(0,0,0,0.06); margin-right: 6px; font-weight: 800;
  }
  .small { font-size: 12px; opacity: 0.85; }

  /* Mesa central estilo feltro */
  .tablePanel {
    border-radius: 22px;
    padding: 14px;
    background: radial-gradient(circle at 30% 20%, rgba(255,255,255,.08) 0%, rgba(255,255,255,0) 35%),
                radial-gradient(circle at 70% 75%, rgba(255,255,255,.06) 0%, rgba(255,255,255,0) 40%),
                linear-gradient(180deg, rgba(5,120,90,0.96) 0%, rgba(4,90,68,0.98) 100%);
    box-shadow: 0 8px 24px rgba(0,0,0,.12);
    border: 1px solid rgba(0,0,0,.18);
  }
  .tableTop {
    display:flex;
    justify-content: space-between;
    align-items:center;
    gap: 10px;
    color: rgba(255,255,255,.92);
    margin-bottom: 10px;
    flex-wrap: wrap;
  }
  .tableTitle { font-weight: 950; letter-spacing: .2px; }
  .tableMeta { opacity: .9; font-weight: 800; }

  /* Layout "mesa real": nomes ao redor + cartas no centro */
  .tableArea {
    position: relative;
    min-height: 340px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(0,0,0,.08);
    overflow: hidden;
  }
  .seat {
    position: absolute;
    padding: 8px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,.10);
    color: rgba(255,255,255,.92);
    font-weight: 900;
    font-size: 13px;
    text-shadow: 0 1px 2px rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.18);
    backdrop-filter: blur(4px);
    white-space: nowrap;
  }
  .seat.you { background: rgba(255,255,255,.18); border-color: rgba(255,255,255,.28); }
  .seat.top { top: 12px; left: 50%; transform: translateX(-50%); }
  .seat.bottom { bottom: 12px; left: 50%; transform: translateX(-50%); }
  .seat.left { left: 12px; top: 50%; transform: translateY(-50%); }
  .seat.right { right: 12px; top: 50%; transform: translateY(-50%); }

  .tableCards {
    position: absolute;
    left: 50%; top: 50%;
    transform: translate(-50%,-50%);
    display:flex; flex-wrap:wrap; justify-content:center; gap:12px;
    min-width: 240px;
    padding: 10px 8px;
  }
  .emptyTable {
    position: absolute;
    left: 50%; top: 50%;
    transform: translate(-50%,-50%);
    text-align:center;
    color: rgba(255,255,255,.92);
    font-weight: 900;
    opacity: .95;
    padding: 16px 12px;
  }

  /* Cartas (visual) */
  .cardFace {
    width: 76px; height: 106px;
    border-radius: 16px;
    border: 1px solid rgba(30,30,30,.22);
    background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(245,245,245,0.98) 100%);
    box-shadow: 0 6px 16px rgba(0,0,0,.14);
    position: relative;
    overflow: hidden;
    animation: fadeInUp .18s ease-out both;
  }
  .cardFace:hover { transform: translateY(-2px); transition: .12s ease; }

  .cornerTL, .cornerBR {
    position:absolute;
    font-weight: 950;
    font-size: 16px;
    line-height: 1;
  }
  .cornerTL { top: 10px; left: 10px; text-align:left; }
  .cornerBR { bottom: 10px; right: 10px; text-align:right; transform: rotate(180deg); }

  .suitCenter {
    position:absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    font-size: 36px;
    font-weight: 950;
    opacity: 0.9;
  }

  /* Sua mão embaixo: botões virando cartas */
  .handZone { display:flex; justify-content:center; }
  .handZone div[data-testid="stButton"] > button {
    width: 76px !important;
    height: 106px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(30,30,30,.22) !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(245,245,245,0.98) 100%) !important;
    box-shadow: 0 6px 16px rgba(0,0,0,.14) !important;
    padding: 0 !important;
    margin: 0 !important;
    font-weight: 950 !important;
    font-size: 20px !important;
    line-height: 1 !important;
    transition: transform .12s ease, opacity .12s ease;
  }
  .handZone div[data-testid="stButton"] > button:hover { transform: translateY(-2px); }
  .handZone div[data-testid="stButton"] > button:disabled {
    opacity: 0.35 !important;
    transform: none !important;
    cursor: not-allowed !important;
  }

  /* Pequena animação */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Sidebar compacto */
  section[data-testid="stSidebar"] .block-container { padding-top: 0.55rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================
# CONSTANTES
# =========================
TRUNFO = "♥"
NAIPES = ["♦", "♠", "♣", "♥"]  # ouro, espada, paus, copas
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

def carta_html_face(carta):
    cor = NAIPE_COR[carta.naipe]
    valor = str(carta.valor)
    naipe = carta.naipe
    return f"""
      <div class="cardFace">
        <div class="cornerTL" style="color:{cor};">{valor}<br>{naipe}</div>
        <div class="suitCenter" style="color:{cor};">{naipe}</div>
        <div class="cornerBR" style="color:{cor};">{valor}<br>{naipe}</div>
      </div>
    """

def mesa_html_sem_nomes(mesa, jogadores, mao_nome, vez_nome):
    # Assentos: top, right, left, bottom (bottom = humano)
    # Para 4 jogadores fica perfeito. Para mais/menos, a gente simplifica.
    humano = next(j for j in jogadores if j.humano)

    # monta uma ordem de "assentos" baseada na ordem atual da rodada
    # bottom = humano; top = jogador oposto (se existir)
    others = [j for j in jogadores if j != humano]
    # fallback
    seat_top = others[0].nome if len(others) > 0 else "-"
    seat_right = others[1].nome if len(others) > 1 else "-"
    seat_left = others[2].nome if len(others) > 2 else "-"

    # destaca mão e vez no nome
    def nome_label(nome):
        extra = []
        if nome == mao_nome:
            extra.append("mão")
        if nome == vez_nome:
            extra.append("vez")
        tag = f" ({', '.join(extra)})" if extra else ""
        return f"{nome}{tag}"

    # cartas no centro
    if not mesa:
        cards_html = "<div class='emptyTable'>Mesa vazia — o mão abre a vaza</div>"
    else:
        cards_html = "<div class='tableCards'>" + "".join(carta_html_face(x["carta"]) for x in mesa) + "</div>"

    return f"""
      <div class="tableArea">
        <div class="seat top">{nome_label(seat_top)}</div>
        <div class="seat right">{nome_label(seat_right)}</div>
        <div class="seat left">{nome_label(seat_left)}</div>
        <div class="seat bottom you">{nome_label(humano.nome)}</div>
        {cards_html}
      </div>
    """

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
# REGRAS
# =========================
def cartas_legais(jogador, naipe_base, hearts_broken, primeira_vaza):
    mao = jogador.mao[:]
    if not mao:
        return []

    # 1ª vaza: trava ♥ (exceto só ♥)
    if primeira_vaza and not somente_copas(mao):
        sem_copas = [c for c in mao if c.naipe != TRUNFO]
        if sem_copas:
            mao = sem_copas

    # seguir naipe se possível
    if naipe_base is not None:
        seguindo = [c for c in mao if c.naipe == naipe_base]
        return seguindo if seguindo else mao

    # mão: não pode abrir ♥ enquanto não quebrou (exceto só ♥)
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

# =========================
# IA
# =========================
def escolher_carta_ia(jogador, legais, naipe_base, mesa):
    legais = ordenar_mao(legais)
    alvo = jogador.prognostico if jogador.prognostico is not None else 0
    falta = alvo - jogador.vazas
    quer_ganhar = falta > 0

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
    "start_idx": None,
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
      <span class="chip">1ª vaza: ♥ proibida (exceto só ♥)</span>
      <span class="chip">Copas trava até quebrar</span>
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
        st.markdown("## 🂡 Mão")
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
        st.session_state.start_idx = None
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
# FASE: PROGNÓSTICO
# =========================
elif st.session_state.fase == "prognostico":
    humano = next(j for j in st.session_state.jogadores if j.humano)

    top = st.container()
    bottom = st.container()

    with top:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader(f"📌 Rodada {st.session_state.numero_rodada} — {st.session_state.rodada_atual} cartas")
        st.info(f"🂡 Mão da rodada: **{st.session_state.ordem[0].nome}**")

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
                linhas.append({"Jogador": j.nome, "Prognóstico": prog})
        if linhas:
            st.dataframe(linhas, use_container_width=True, hide_index=True)
        else:
            st.caption("Você é o primeiro a palpitar (ninguém antes de você).")

        prog = st.number_input("Seu prognóstico", 0, len(humano.mao), 0, step=1)
        if st.button("Confirmar meu prognóstico", use_container_width=True):
            humano.prognostico = int(prog)
            st.session_state.bid_idx += 1
            while st.session_state.bid_idx < len(st.session_state.ordem):
                atual = st.session_state.ordem[st.session_state.bid_idx]
                if atual.prognostico is None:
                    atual.prognostico = random.randint(0, len(atual.mao))
                st.session_state.bid_idx += 1
            st.session_state.fase = "jogada"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom:
        st.markdown("<div class='tablePanel'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='tableTop'><div class='tableTitle'>🪑 MESA (pré-jogo)</div>"
            f"<div class='tableMeta'>Aguardando início da 1ª vaza</div></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            mesa_html_sem_nomes(
                mesa=[],
                jogadores=st.session_state.jogadores,
                mao_nome=st.session_state.ordem[0].nome if st.session_state.ordem else "-",
                vez_nome=st.session_state.ordem[0].nome if st.session_state.ordem else "-"
            ),
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FASE: JOGADA (MESA CENTRO + MÃO EMBAIXO)
# =========================
elif st.session_state.fase == "jogada":
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

    # ====== MESA (CENTRO)
    st.markdown("<div class='tablePanel'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='tableTop'>"
        f"<div class='tableTitle'>🪑 MESA — Vaza {st.session_state.numero_vaza}</div>"
        f"<div class='tableMeta'>Mão: <b>{st.session_state.ordem[0].nome}</b> | "
        f"Vez: <b>{jogador.nome}</b> | Naipe: <b>{st.session_state.naipe_base or '-'}</b></div>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        mesa_html_sem_nomes(
            mesa=st.session_state.mesa,
            jogadores=st.session_state.jogadores,
            mao_nome=st.session_state.ordem[0].nome,
            vez_nome=jogador.nome
        ),
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ====== Ações / sua mão (EMBAIXO)
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    if jogador.humano:
        st.subheader("🂡 Sua mão — clique na carta")
        legais = cartas_legais(
            jogador=jogador,
            naipe_base=st.session_state.naipe_base,
            hearts_broken=st.session_state.hearts_broken,
            primeira_vaza=st.session_state.primeira_vaza
        )
        legais_set = set(c.texto() for c in legais)
        mao = ordenar_mao(jogador.mao)

        st.markdown("<div class='handZone'>", unsafe_allow_html=True)
        cols = st.columns(10, gap="small")
        for i, carta in enumerate(mao):
            disabled = (carta.texto() not in legais_set)
            col = cols[i % 10]
            if col.button(
                carta.texto(),
                key=f"card_{st.session_state.numero_rodada}_{st.session_state.numero_vaza}_{i}_{carta.texto()}",
                disabled=disabled
            ):
                jogar_carta(jogador, carta)
        st.markdown("</div>", unsafe_allow_html=True)

        st.caption("Cartas inválidas ficam apagadas (travadas).")
    else:
        st.subheader("🤖 Jogada dos adversários…")
        st.caption("Aguarde: o jogo faz a jogada automática dos bots.")

        legais = cartas_legais(
            jogador=jogador,
            naipe_base=st.session_state.naipe_base,
            hearts_broken=st.session_state.hearts_broken,
            primeira_vaza=st.session_state.primeira_vaza
        )
        carta = escolher_carta_ia(jogador, legais, st.session_state.naipe_base, st.session_state.mesa)
        jogador.mao.remove(carta)
        st.session_state.mesa.append({"jogador": jogador, "carta": carta})

        if st.session_state.naipe_base is None:
            st.session_state.naipe_base = carta.naipe
        if carta.naipe == TRUNFO:
            st.session_state.hearts_broken = True

        st.session_state.indice_jogador += 1
        st.rerun()

    with st.expander("🧾 Histórico da rodada", expanded=False):
        if st.session_state.historico_vazas:
            for i, h in enumerate(st.session_state.historico_vazas, start=1):
                jogadas_txt = ", ".join([f"{nome}:{carta}" for nome, carta in h["mesa"]])
                st.write(f"Vaza {i} → [{jogadas_txt}] — 🏆 {h['vencedor']}")
        else:
            st.caption("Nenhuma vaza finalizada ainda.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# RESULTADO DA VAZA
# =========================
elif st.session_state.fase == "resultado_vaza":
    st.markdown("<div class='tablePanel'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='tableTop'><div class='tableTitle'>🏆 Resultado da Vaza</div>"
        f"<div class='tableMeta'>Vencedor: <b>{st.session_state.vencedor.nome}</b></div></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        mesa_html_sem_nomes(
            mesa=st.session_state.mesa,
            jogadores=st.session_state.jogadores,
            mao_nome=st.session_state.ordem[0].nome if st.session_state.ordem else "-",
            vez_nome=st.session_state.vencedor.nome if st.session_state.vencedor else "-"
        ),
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
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

    st.markdown("---")
    proxima_cartas = st.session_state.rodada_atual - 1

    if proxima_cartas >= 1:
        if st.button("▶ Próxima rodada", use_container_width=True):
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
