import random
import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", layout="wide")

NAIPES = ["♦", "♠", "♣", "♥"]  # ♦ Ouro (vermelho), ♠ Espadas (preto), ♣ Paus (preto), ♥ Copas (vermelho)
TRUNFO = "♥"
ORDEM_NAIPE = {"♦": 0, "♠": 1, "♣": 2, "♥": 3}
VALORES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
PESO_VALOR = {v: i for i, v in enumerate(VALORES)}  # 2 menor, A maior

APP_CSS = """
<style>
/* ---- fundo + top bar ---- */
.block-container{padding-top:1.0rem; padding-bottom:1.0rem;}
.headerBar{
  background: linear-gradient(90deg, #0a5, #0a7);
  border-radius: 18px;
  padding: 14px 16px;
  color: #fff;
  box-shadow: 0 10px 25px rgba(0,0,0,.10);
  margin-bottom: 14px;
}
.headerBar .title{font-size: 28px; font-weight: 800; display:flex; gap:10px; align-items:center;}
.badges{display:flex; gap:8px; flex-wrap:wrap; margin-top:6px;}
.badge{
  background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.18);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

/* ---- mesa ---- */
.tableWrap{
  background: radial-gradient(ellipse at center, #2f8f55 0%, #1b6b3c 55%, #0f4a28 100%);
  border-radius: 22px;
  padding: 16px;
  box-shadow: inset 0 0 0 2px rgba(255,255,255,.06), 0 18px 40px rgba(0,0,0,.18);
}
.tableTitle{
  color: rgba(255,255,255,.92);
  font-weight: 800;
  letter-spacing: .4px;
  margin-bottom: 10px;
  display:flex;
  justify-content:space-between;
  align-items:center;
}
.seats{
  display:grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 10px;
  align-items:center;
  justify-items:center;
  min-height: 260px;
}
.seat{
  color: rgba(255,255,255,.95);
  font-weight: 700;
  font-size: 13px;
  background: rgba(0,0,0,.18);
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 14px;
  padding: 8px 10px;
  min-width: 120px;
  text-align:center;
}
.seat.me{background: rgba(255,255,255,.14);}
.centerMsg{
  grid-column: 2;
  grid-row: 2;
  color: rgba(255,255,255,.92);
  font-weight: 800;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(0,0,0,.22);
  border: 1px solid rgba(255,255,255,.10);
  text-align:center;
  min-width: 260px;
}
.centerCards{
  grid-column: 2;
  grid-row: 2;
  margin-top: 54px;
  display:flex;
  gap: 10px;
  justify-content:center;
  align-items:center;
  flex-wrap:wrap;
}
.chipRow{
  display:flex; gap:6px; justify-content:center; flex-wrap:wrap; margin-top:6px;
}
.chip{
  width: 12px; height: 12px;
  border-radius: 999px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 1px 3px rgba(0,0,0,.25);
  border: 1px solid rgba(0,0,0,.20);
}
.stack{
  width: 18px; height: 14px;
  border-radius: 6px;
  background: rgba(0,0,0,.22);
  border: 1px solid rgba(255,255,255,.10);
  margin: 6px auto 0;
}

/* ---- mão (cartas clicáveis) ---- */
.handDock{
  background: rgba(255,255,255,.65);
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 12px;
  box-shadow: 0 10px 20px rgba(0,0,0,.07);
}
.handTitle{
  display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom:8px;
}
.handTitle h3{margin:0;}
.handTitle .hint{opacity:.75; font-weight:600; font-size:12px;}
.handLinksRow{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  align-items:flex-start;
}
.handCardLink{
  display:block;
  text-decoration:none !important;
  color:inherit !important;
}
.handCardLink .card{
  cursor:pointer;
  transition: transform .12s ease, box-shadow .12s ease, opacity .12s ease;
}
.handCardLink:hover .card{
  transform: translateY(-4px);
  box-shadow: 0 14px 26px rgba(0,0,0,.16);
}
.handCardLink.disabled{
  pointer-events:none;
  opacity:.28;
  filter: grayscale(.15);
}

/* ---- carta ---- */
.card{
  width: 74px;
  height: 102px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.14);
  box-shadow: 0 10px 18px rgba(0,0,0,.12);
  position: relative;
  user-select:none;
}
.tl{
  position:absolute; top:6px; left:8px;
  font-weight:800; font-size:14px; line-height:14px;
  text-align:left;
}
.br{
  position:absolute; bottom:6px; right:8px;
  font-weight:800; font-size:14px; line-height:14px;
  text-align:right;
  transform: rotate(180deg);
}
.mid{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-size: 28px; font-weight:900;
}
.red{color:#d11;}
.black{color:#111;}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def peso_carta(c):
    naipe, valor = c
    return (ORDEM_NAIPE[naipe], PESO_VALOR[valor])

def only_trunfo(mao):
    return all(c[0] == TRUNFO for c in mao) and len(mao) > 0

def criar_baralho():
    baralho = [(n, v) for n in NAIPES for v in VALORES]
    random.shuffle(baralho)
    return baralho

def carta_color_class(naipe):
    return "red" if naipe in ("♦", "♥") else "black"

def carta_html(c):
    naipe, valor = c
    cor = carta_color_class(naipe)
    return f"""
    <div class="card">
      <div class="tl {cor}">{valor}<br>{naipe}</div>
      <div class="mid {cor}">{naipe}</div>
      <div class="br {cor}">{valor}<br>{naipe}</div>
    </div>
    """

def get_query_params():
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()

def clear_play_param():
    try:
        qp = dict(st.query_params)
        if "play" in qp:
            del qp["play"]
            st.query_params.clear()
            for k, v in qp.items():
                st.query_params[k] = v
    except Exception:
        qp = st.experimental_get_query_params()
        if "play" in qp:
            qp.pop("play", None)
            st.experimental_set_query_params(**qp)

# =========================
# REGRAS / VALIDAÇÃO
# =========================
def cartas_validas_para_jogar(nome):
    """Regras:
    - deve seguir naipe se tiver
    - na 1ª vaza: não pode jogar copas (trunfo) a menos que só tenha copas na mão
    - iniciar vaza com copas só se copas quebrada (ou só copas na mão)
    """
    mao = st.session_state.maos[nome]
    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base
    primeira_vaza = st.session_state.primeira_vaza
    copas_quebrada = st.session_state.copas_quebrada

    # 1) se não tem mesa ainda (vai abrir)
    if not mesa:
        validas = []
        for c in mao:
            if c[0] == TRUNFO:
                # não pode abrir de copas se não quebrou, exceto se só copas
                if (not copas_quebrada) and (not only_trunfo(mao)):
                    continue
                # na 1ª vaza não pode copas exceto só copas
                if primeira_vaza and (not only_trunfo(mao)):
                    continue
            validas.append(c)
        return validas if validas else mao[:]  # fallback de segurança

    # 2) se já tem naipe base
    if naipe_base:
        seguindo = [c for c in mao if c[0] == naipe_base]
        if seguindo:
            validas = seguindo
        else:
            validas = mao[:]
    else:
        validas = mao[:]

    # 3) regra da 1ª vaza: copas proibida, exceto só copas
    if primeira_vaza and (not only_trunfo(mao)):
        validas = [c for c in validas if c[0] != TRUNFO]

    return validas if validas else mao[:]

def definir_vencedor_vaza(mesa, naipe_base):
    """mesa = [(nome, (naipe, valor)), ...]"""
    # se tem trunfo na mesa, maior trunfo ganha
    trunfos = [(nm, c) for nm, c in mesa if c[0] == TRUNFO]
    if trunfos:
        return max(trunfos, key=lambda x: PESO_VALOR[x[1][1]])[0]
    # senão, maior do naipe base
    seguindo = [(nm, c) for nm, c in mesa if c[0] == naipe_base]
    return max(seguindo, key=lambda x: PESO_VALOR[x[1][1]])[0]

# =========================
# IA DIFÍCIL
# =========================
def ai_prognostico_dificil(mao, qtd_cartas):
    """Heurística forte:
    - trunfos contam mais
    - cartas altas contam mais
    - penaliza se poucas cartas de naipe (tende a ser forçado)
    """
    trunfos = [c for c in mao if c[0] == TRUNFO]
    altas = [c for c in mao if c[1] in ("A", "K", "Q", "J", 10)]
    score = 0.0
    score += len(trunfos) * 0.75
    score += sum(0.55 if c[1] in ("A", "K") else 0.35 for c in altas)

    # distribuição por naipe
    by = {n: 0 for n in NAIPES}
    for n, v in mao:
        by[n] += 1
    curto = sum(1 for n in NAIPES if by[n] <= 1)
    score -= curto * 0.10

    # limita
    palpite = int(round(min(max(score, 0), qtd_cartas)))
    return palpite

def carta_ganha_contra(minha, outra, naipe_base):
    n1, v1 = minha
    n2, v2 = outra
    if n1 == TRUNFO and n2 != TRUNFO:
        return True
    if n1 != TRUNFO and n2 == TRUNFO:
        return False
    if n1 == TRUNFO and n2 == TRUNFO:
        return PESO_VALOR[v1] > PESO_VALOR[v2]
    # nenhum trunfo
    if n1 == naipe_base and n2 != naipe_base:
        return True
    if n1 != naipe_base and n2 == naipe_base:
        return False
    if n1 == naipe_base and n2 == naipe_base:
        return PESO_VALOR[v1] > PESO_VALOR[v2]
    return PESO_VALOR[v1] > PESO_VALOR[v2]

def ai_escolhe_carta_dificil(nome):
    """IA difícil: tenta bater o prognóstico com precisão."""
    validas = cartas_validas_para_jogar(nome)
    if not validas:
        return None

    alvo = int(st.session_state.prognosticos.get(nome, 0))
    feitas = int(st.session_state.vazas_rodada.get(nome, 0))
    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base if st.session_state.naipe_base else (mesa[0][1][0] if mesa else None)

    # define carta líder atual
    if mesa:
        melhor_c = mesa[0][1]
        for _, c in mesa[1:]:
            if carta_ganha_contra(c, melhor_c, naipe_base):
                melhor_c = c
    else:
        melhor_c = None

    # se precisa ganhar ainda, tenta ganhar com a menor ganhadora
    if feitas < alvo:
        if not mesa:
            # abrindo: tenta abrir forte mas sem desperdiçar: top 3 -> menor delas
            top = sorted(validas, key=lambda c: PESO_VALOR[c[1]], reverse=True)[:3]
            return sorted(top, key=lambda c: PESO_VALOR[c[1]])[0]

        ganhadoras = [c for c in validas if carta_ganha_contra(c, melhor_c, naipe_base)]
        if ganhadoras:
            # menor que ganha
            return sorted(ganhadoras, key=lambda c: (c[0] != TRUNFO, PESO_VALOR[c[1]]))[0]

        # não consegue ganhar -> joga a menor
        return sorted(validas, key=lambda c: (c[0] == TRUNFO, PESO_VALOR[c[1]]))[0]

    # se já bateu (ou passou), joga para perder: menor possível (evita trunfo)
    return sorted(validas, key=lambda c: (c[0] == TRUNFO, PESO_VALOR[c[1]]))[0]

# =========================
# ESTADO / SETUP
# =========================
def reset_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def init_state(nomes):
    st.session_state.nomes = nomes
    st.session_state.n = len(nomes)
    st.session_state.humano_idx = len(nomes) - 1
    st.session_state.humano = nomes[st.session_state.humano_idx]

    # pontuação total
    st.session_state.pontos = {nm: 0 for nm in nomes}

    # mão inicial aleatória (cada rodada a mão base roda +1)
    st.session_state.base_mao_idx = random.randrange(st.session_state.n)

    # controle de rodada
    st.session_state.rodada = 1
    st.session_state.cartas_iniciais = min(10, 52 // st.session_state.n)
    st.session_state.cartas_por_jogador = st.session_state.cartas_iniciais

    # runtime
    iniciar_rodada()

def iniciar_rodada():
    n = st.session_state.n
    c = st.session_state.cartas_por_jogador

    baralho = criar_baralho()

    # distribui exatamente c para cada jogador (sobras ficam no baralho)
    st.session_state.maos = {nm: [] for nm in st.session_state.nomes}
    for _ in range(c):
        for nm in st.session_state.nomes:
            st.session_state.maos[nm].append(baralho.pop())

    # ordena mãos
    for nm in st.session_state.nomes:
        st.session_state.maos[nm] = sorted(st.session_state.maos[nm], key=peso_carta)

    # ordem da rodada: começa no base_mao_idx
    idx = st.session_state.base_mao_idx % n
    st.session_state.ordem = st.session_state.nomes[idx:] + st.session_state.nomes[:idx]
    st.session_state.turn_idx = 0  # quem joga agora dentro da ordem da rodada
    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.copas_quebrada = False
    st.session_state.primeira_vaza = True
    st.session_state.vazas_rodada = {nm: 0 for nm in st.session_state.nomes}
    st.session_state.prognosticos = {nm: None for nm in st.session_state.nomes}
    st.session_state.prog_idx = 0  # índice dentro da ordem fazendo prognóstico
    st.session_state.phase = "prognostico"  # ou "jogo"
    st.session_state.rodada_ja_pontuada = False

def aplicar_pontuacao_da_rodada():
    """APLICA UMA ÚNICA VEZ; garante bônus da última vaza."""
    if st.session_state.rodada_ja_pontuada:
        return

    for nm in st.session_state.nomes:
        vazas = int(st.session_state.vazas_rodada.get(nm, 0))
        prog = st.session_state.prognosticos.get(nm)
        prog = int(prog) if prog is not None else 0

        pontos_rodada = vazas
        if vazas == prog:
            pontos_rodada += 5

        st.session_state.pontos[nm] = int(st.session_state.pontos.get(nm, 0)) + pontos_rodada

    st.session_state.rodada_ja_pontuada = True

def avancar_para_proxima_rodada_ou_fim():
    # desce 1 carta por rodada até 1
    if st.session_state.cartas_por_jogador > 1:
        st.session_state.rodada += 1
        st.session_state.cartas_por_jogador -= 1
        st.session_state.base_mao_idx = (st.session_state.base_mao_idx + 1) % st.session_state.n
        iniciar_rodada()
        return

    st.session_state.phase = "fim"
    st.session_state.fim_msg = "🏁 Jogo encerrado! Veja o placar final no sidebar."

# =========================
# UI COMPONENTS
# =========================
def sidebar_placar():
    st.sidebar.markdown("### 📊 Placar")
    # apenas nome + pontos (como você pediu)
    rows = [{"Jogador": nm, "Pontos": st.session_state.pontos.get(nm, 0)} for nm in st.session_state.nomes]
    df = pd.DataFrame(rows).sort_values("Pontos", ascending=False)
    st.sidebar.dataframe(df, use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Rodada (parcial)")
    rows2 = []
    for nm in st.session_state.nomes:
        rows2.append({
            "Jogador": nm,
            "Prog": st.session_state.prognosticos.get(nm),
            "Vazas": st.session_state.vazas_rodada.get(nm, 0)
        })
    st.sidebar.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)

def render_header():
    rod = st.session_state.rodada
    c = st.session_state.cartas_por_jogador
    mao_base = st.session_state.ordem[0] if "ordem" in st.session_state else "-"
    st.markdown(
        f"""
        <div class="headerBar">
          <div class="title">🃏 Jogo de Prognóstico</div>
          <div class="badges">
            <div class="badge">Rodada {rod} — {c} carta(s) por jogador</div>
            <div class="badge">Trunfo: {TRUNFO}</div>
            <div class="badge">Mão da rodada: {mao_base}</div>
            <div class="badge">IA: Difícil</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_table():
    nomes = st.session_state.nomes
    humano = st.session_state.humano

    # mapeia posições na mesa (grid 3x3) para N jogadores (até 8 fica legal)
    ordem = st.session_state.ordem
    # posições fixas (top, left, right, bottom) e extras
    pos_slots = [
        ("top", 0, 1),
        ("left", 1, 0),
        ("right", 1, 2),
        ("bottom", 2, 1),
        ("top-left", 0, 0),
        ("top-right", 0, 2),
        ("bottom-left", 2, 0),
        ("bottom-right", 2, 2),
    ]

    # atribui jogadores aos slots pela ordem da rodada, garantindo você em "bottom"
    # coloca humano sempre em bottom
    others = [nm for nm in ordem if nm != humano]
    layout_players = [None]*len(pos_slots)
    # bottom slot index = 3
    layout_players[3] = humano
    i = 0
    for sidx in range(len(pos_slots)):
        if sidx == 3:
            continue
        if i < len(others):
            layout_players[sidx] = others[i]
            i += 1

    # chips (prognóstico) + stacks (vazas) no seat
    seat_html = []
    for sidx, nm in enumerate(layout_players):
        if nm is None:
            continue
        is_me = (nm == humano)
        prog = st.session_state.prognosticos.get(nm)
        vazas = int(st.session_state.vazas_rodada.get(nm, 0))
        chips = ""
        if isinstance(prog, int):
            chips = "<div class='chipRow'>" + ("".join(["<div class='chip'></div>" for _ in range(prog)])) + "</div>"
        stack = ""
        if vazas > 0:
            stack = "<div class='stack'></div>"

        seat_html.append((sidx, f"<div class='seat {'me' if is_me else ''}'>{nm}{chips}{stack}</div>"))

    # mesa (cartas jogadas)
    mesa = st.session_state.mesa
    center_cards = ""
    if mesa:
        center_cards = "<div class='centerCards'>" + "".join([carta_html(c) for _, c in mesa]) + "</div>"

    if st.session_state.phase == "prognostico":
        msg = "Aguardando prognósticos..."
    elif st.session_state.phase == "jogo":
        atual = st.session_state.ordem[st.session_state.turn_idx]
        msg = f"Vez de: {atual}"
    else:
        msg = st.session_state.get("fim_msg", "Fim de jogo.")

    # monta grid
    grid = [["" for _ in range(3)] for _ in range(3)]
    for sidx, html in seat_html:
        _, r, c = pos_slots[sidx]
        grid[r][c] = html

    center = f"<div class='centerMsg'>{msg}</div>{center_cards}"
    grid[1][1] = center

    table_html = """
    <div class="tableWrap">
      <div class="tableTitle">
        <div>🎴 Mesa</div>
        <div style="opacity:.88;font-size:12px;">Copas quebrada: {copas}</div>
      </div>
      <div class="seats">
        {cells}
      </div>
    </div>
    """.format(
        copas="✅" if st.session_state.copas_quebrada else "❌",
        cells="".join([f"<div>{grid[r][c]}</div>" for r in range(3) for c in range(3)])
    )
    st.markdown(table_html, unsafe_allow_html=True)

def render_hand_clickable_html():
    humano = st.session_state.humano
    ordem = st.session_state.ordem
    atual = ordem[st.session_state.turn_idx]

    mao = st.session_state.maos[humano]
    validas = set(cartas_validas_para_jogar(humano))

    # clique via query param
    qp = get_query_params()
    clicked = None
    if "play" in qp and qp["play"]:
        raw = qp["play"]
        if isinstance(raw, list):
            raw = raw[0]
        try:
            naipe, valor = raw.split("|", 1)
            if valor.isdigit():
                valor = int(valor)
            clicked = (naipe, valor)
        except Exception:
            clicked = None
        clear_play_param()

    st.markdown('<div class="handDock">', unsafe_allow_html=True)

    hint = "Clique numa carta válida" if atual == humano else "Aguardando (IA jogando...)"
    st.markdown(
        f'<div class="handTitle"><h3>🂠 Sua mão</h3><div class="hint">{hint}</div></div>',
        unsafe_allow_html=True
    )

    mao_ord = sorted(mao, key=peso_carta)
    cards_html = ['<div class="handLinksRow">']
    for c in mao_ord:
        disabled = (atual != humano) or (c not in validas) or (st.session_state.phase != "jogo")
        key = f"{c[0]}|{c[1]}"
        cls = "handCardLink disabled" if disabled else "handCardLink"
        href = "#" if disabled else f"?play={key}"
        cards_html.append(f'<a class="{cls}" href="{href}">{carta_html(c)}</a>')
    cards_html.append("</div>")

    st.markdown("".join(cards_html), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked

# =========================
# FLUXO DO JOGO
# =========================
def resolver_vaza_se_completa():
    """Resolve a vaza imediatamente quando mesa tem N cartas.
    >>> ESTE É O PONTO QUE GARANTE QUE A ÚLTIMA VAZA CONTA <<<
    """
    n = st.session_state.n
    if len(st.session_state.mesa) != n:
        return

    # copas quebrada: se qualquer copas foi jogada (e não era primeira_vaza restrita)
    if any(c[0] == TRUNFO for _, c in st.session_state.mesa):
        st.session_state.copas_quebrada = True

    naipe_base = st.session_state.naipe_base
    vencedor = definir_vencedor_vaza(st.session_state.mesa, naipe_base)

    # soma vaza do vencedor (inclusive na ÚLTIMA vaza)
    st.session_state.vazas_rodada[vencedor] = int(st.session_state.vazas_rodada.get(vencedor, 0)) + 1

    # próxima vaza: vencedor vira mão (turn_idx ajusta)
    # limpa mesa e naipe_base
    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.primeira_vaza = False

    # rearranja ordem para começar pelo vencedor
    ordem = st.session_state.ordem
    idx = ordem.index(vencedor)
    st.session_state.ordem = ordem[idx:] + ordem[:idx]
    st.session_state.turn_idx = 0

    # se acabou a rodada (todos sem cartas), pontua e avança
    if all(len(st.session_state.maos[nm]) == 0 for nm in st.session_state.nomes):
        # >>> GARANTE pontuação após contabilizar a última vaza <<<
        aplicar_pontuacao_da_rodada()
        avancar_para_proxima_rodada_ou_fim()

def play_card(nome, carta):
    # remove da mão
    st.session_state.maos[nome].remove(carta)

    # define naipe base se é a 1ª carta da vaza
    if not st.session_state.mesa:
        st.session_state.naipe_base = carta[0]

    st.session_state.mesa.append((nome, carta))

    # avança turno
    st.session_state.turn_idx += 1

    # se vaza completa, resolve
    resolver_vaza_se_completa()

def step_ai_if_needed():
    """Executa jogadas de IA até ser vez do humano ou até mudar fase."""
    humano = st.session_state.humano
    while st.session_state.phase == "jogo":
        ordem = st.session_state.ordem
        if st.session_state.turn_idx >= len(ordem):
            break
        atual = ordem[st.session_state.turn_idx]
        if atual == humano:
            break
        carta = ai_escolhe_carta_dificil(atual)
        if carta is None:
            break
        play_card(atual, carta)

def render_prognostico():
    st.markdown("### ✅ Prognósticos")

    ordem = st.session_state.ordem
    humano = st.session_state.humano
    idx = st.session_state.prog_idx

    # mostra apenas anteriores ao humano, a menos que humano seja o último (pé)
    humano_pos = ordem.index(humano)
    mostrar_todos = (humano_pos == len(ordem) - 1)

    visiveis = []
    for i, nm in enumerate(ordem):
        p = st.session_state.prognosticos.get(nm)
        if p is None:
            continue
        if mostrar_todos or i <= humano_pos:
            visiveis.append({"Jogador": nm, "Prognóstico": p})

    if visiveis:
        st.dataframe(pd.DataFrame(visiveis), use_container_width=True, hide_index=True)

    atual = ordem[idx]
    st.info(f"Vez de prognóstico: **{atual}**")

    # IA faz automático
    if atual != humano:
        mao = st.session_state.maos[atual]
        palpite = ai_prognostico_dificil(mao, st.session_state.cartas_por_jogador)
        st.session_state.prognosticos[atual] = int(palpite)
        st.session_state.prog_idx += 1
        st.rerun()

    # Humano escolhe
    st.markdown("#### Seu prognóstico")
    maxv = st.session_state.cartas_por_jogador
    prog = st.number_input("Escolha quantas vazas você acredita que fará:", min_value=0, max_value=maxv, value=0, step=1)
    if st.button("Confirmar meu prognóstico", use_container_width=True):
        st.session_state.prognosticos[humano] = int(prog)
        st.session_state.prog_idx += 1

        # se todos fizeram, inicia jogo
        if st.session_state.prog_idx >= len(ordem):
            st.session_state.phase = "jogo"
            st.session_state.turn_idx = 0
            st.session_state.mesa = []
            st.session_state.naipe_base = None
            st.rerun()
        else:
            st.rerun()

def render_jogo():
    # primeiro deixa IA jogar até ser vez do humano
    step_ai_if_needed()

    # humano joga clicando carta
    clicked = render_hand_clickable_html()
    if clicked:
        humano = st.session_state.humano
        ordem = st.session_state.ordem
        atual = ordem[st.session_state.turn_idx]

        if atual == humano:
            validas = set(cartas_validas_para_jogar(humano))
            if clicked in validas and clicked in st.session_state.maos[humano]:
                play_card(humano, clicked)
                st.rerun()
            else:
                st.warning("Carta inválida para esta jogada.")

    # se após sua jogada virar IA, ela segue
    if st.session_state.phase == "jogo":
        step_ai_if_needed()

def render_start_screen():
    st.markdown("## Configuração rápida")
    st.caption("Jogadores (separados por vírgula). O último será Você")
    nomes_txt = st.text_input("Jogadores", "Ana, Bruno, Carlos, Você")
    col1, col2 = st.columns([1, 2], vertical_alignment="center")
    with col1:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with col2:
        st.info("As cartas serão distribuídas igualmente até acabar o baralho.", icon="ℹ️")

    if start:
        nomes = [x.strip() for x in nomes_txt.split(",") if x.strip()]
        if len(nomes) < 3:
            st.error("Use pelo menos 3 jogadores.")
            return
        # garante "Você" como último
        if nomes[-1].lower() not in ("você", "voce"):
            nomes.append("Você")
        else:
            nomes[-1] = "Você"

        init_state(nomes)
        st.rerun()

# =========================
# MAIN
# =========================
def main():
    if "nomes" not in st.session_state:
        render_start_screen()
        return

    sidebar_placar()
    render_header()

    # layout: mesa centro / mão embaixo
    colA, colB = st.columns([1.35, 1], gap="large")
    with colA:
        render_table()
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.session_state.phase == "prognostico":
            render_prognostico()
        elif st.session_state.phase == "jogo":
            render_jogo()
        else:
            st.success(st.session_state.get("fim_msg", "Fim!"))
            if st.button("🔄 Reiniciar", use_container_width=True):
                reset_all()
                st.rerun()

    with colB:
        st.markdown("### 🔧 Controles")
        st.write(f"Jogadores: **{len(st.session_state.nomes)}**")
        st.write(f"Rodada: **{st.session_state.rodada}**")
        st.write(f"Cartas por jogador: **{st.session_state.cartas_por_jogador}**")
        sobras = 52 - (st.session_state.cartas_por_jogador * len(st.session_state.nomes))
        st.write(f"Sobras no monte: **{sobras}**")
        st.write("---")
        if st.button("🧨 Resetar jogo (zera tudo)", use_container_width=True):
            reset_all()
            st.rerun()

main()
