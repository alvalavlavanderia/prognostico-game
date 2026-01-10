# app.py
import random
import math
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

APP_CSS = """
<style>
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: 0.5rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }

.handRow{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  align-items:flex-start;
}
.card{
  width:72px;
  height:104px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.15);
  box-shadow:0 8px 18px rgba(0,0,0,.10);
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfb 100%);
  position:relative;
  user-select:none;
}
.card .tl{ position:absolute; top:8px; left:8px; font-weight:800; font-size:14px; line-height:14px; }
.card .br{ position:absolute; bottom:8px; right:8px; font-weight:800; font-size:14px; line-height:14px; transform:rotate(180deg); }
.card .mid{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:800; opacity:.95; }

.badge{ display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(0,0,0,.06); font-size:12px; }
.topbar{ display:flex; gap:10px; flex-wrap:wrap; margin: 2px 0 10px 0; }
.titleRow{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 4px; }
.titleRow h1{ margin:0; }
.panel{ border:1px solid rgba(0,0,0,.08); border-radius:14px; padding:14px; background:#ffffff; }

.mesa{
  border-radius:18px;
  border:1px solid rgba(0,0,0,.10);
  background: radial-gradient(circle at 30% 20%, rgba(0,150,110,.25) 0%, rgba(0,120,90,.15) 30%, rgba(0,0,0,.03) 65%, rgba(0,0,0,.02) 100%);
  min-height: 360px;
  position:relative;
  overflow:hidden;
}
.mesaCenter{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:700;
  opacity:.70;
  pointer-events:none;
}
.mesaSeat{
  position:absolute;
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.78);
  border:1px solid rgba(0,0,0,.08);
  white-space:nowrap;
}
.seatIsYou{ outline: 2px solid rgba(0,120,90,.55); font-weight:800; }
.seatIsDealer{ background: rgba(255,255,255,.92); border-color: rgba(0,120,90,.30); }

.playCard{
  position:absolute;
  transform:translate(-50%,-50%);
  pointer-events:none;
}

.scoreItem{
  display:flex;
  justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.06);
  background:rgba(255,255,255,.7);
  margin-bottom:8px;
}
.scoreName{ font-weight:700; }
.scorePts{ font-weight:800; }
.smallMuted{ opacity:.70; font-size:12px; }
hr{ margin: 0.8rem 0 !important; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# BARALHO / ORDENAÇÃO
# =========================
VALORES = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
PESO_VALOR = {v:i for i,v in enumerate(VALORES)}  # 2 menor, A maior
COR_NAIPE = {"♦":"red", "♥":"red", "♠":"black", "♣":"black"}
ORDEM_NAIPE = {"♦":0, "♠":1, "♣":2, "♥":3}  # ouro, espada, paus, copas
TRUNFO = "♥"

def criar_baralho():
    naipes = ["♠", "♦", "♣", "♥"]
    return [(n, v) for n in naipes for v in VALORES]

def peso_carta(c):
    naipe, valor = c
    return (ORDEM_NAIPE[naipe], PESO_VALOR[valor])

def valor_str(v):
    return str(v)

def carta_html(c, cls="card"):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = valor_str(valor)
    return (
        f'<div class="{cls}">'
        f'<div class="tl" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'<div class="mid" style="color:{cor};">{naipe}</div>'
        f'<div class="br" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'</div>'
    )

def render_hand_visual(mao, titulo="Suas cartas (visualização)"):
    mao_ordenada = sorted(mao, key=peso_carta)
    cards = "".join(carta_html(c) for c in mao_ordenada)
    st.markdown(f"### 🃏 {titulo}")
    st.markdown(f'<div class="handRow">{cards}</div>', unsafe_allow_html=True)

# =========================
# UTIL
# =========================
def ordem_da_mesa(nomes, mao_idx):
    return [nomes[(mao_idx + i) % len(nomes)] for i in range(len(nomes))]

def idx_na_ordem(ordem, nome):
    return ordem.index(nome)

def somente_trunfo(mao):
    return all(n == TRUNFO for (n, _) in mao) if mao else False

def tem_naipe(mao, naipe):
    return any(n == naipe for (n, _) in mao)

# =========================
# STATE
# =========================
def ss_init():
    defaults = {
        "started": False,
        "nomes": ["Ana", "Bruno", "Carlos", "Você"],
        "humano_idx": 3,

        "pontos": {},
        "vazas_rodada": {},

        "maos": {},
        "rodada": 1,
        "cartas_por_jog": 0,
        "sobras_monte": 0,

        "mao_da_rodada": 0,
        "fase": "setup",  # setup | prognostico | jogo

        "prognosticos": {},
        "progn_pre": {},
        "progn_pos": {},

        # jogo de vazas
        "ordem": [],
        "turn_idx": 0,           # índice na ordem (quem joga agora)
        "naipe_base": None,      # naipe da vaza
        "mesa": [],              # lista de (nome, carta)
        "primeira_vaza": True,
        "copas_quebrada": False,
        "log": [],               # mensagens de rodada/vaza
        "lock_render": False,    # evita rerun no meio de automações
        "show_all_progn": False,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 📊 Placar")
    if st.session_state.started:
        for n in st.session_state.nomes:
            st.session_state.pontos.setdefault(n, 0)

        ranking = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)
        for nome, pts in ranking:
            st.markdown(
                f'<div class="scoreItem"><div class="scoreName">{nome}</div><div class="scorePts">{pts}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="smallMuted">Rodada: {st.session_state.rodada} • Cartas/jogador: {st.session_state.cartas_por_jog} • Sobras: {st.session_state.sobras_monte}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        if st.button("🔁 Reiniciar jogo", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            ss_init()
            st.rerun()
    else:
        st.info("Inicie uma partida para ver o placar.")

# =========================
# HEADER
# =========================
st.markdown(
    """
<div class="titleRow">
  <h1>🃏 Jogo de Prognóstico</h1>
  <div class="topbar">
    <span class="badge">Trunfo: ♥</span>
    <span class="badge">1ª vaza: ♥ proibida (exceto só ♥)</span>
    <span class="badge">Copas trava até quebrar</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# =========================
# CORE
# =========================
def distribuir():
    nomes = st.session_state.nomes
    n = len(nomes)
    baralho = criar_baralho()
    random.shuffle(baralho)

    cartas_por = len(baralho) // n
    sobras = len(baralho) - (cartas_por * n)

    st.session_state.cartas_por_jog = cartas_por
    st.session_state.sobras_monte = sobras

    st.session_state.maos = {nome: [] for nome in nomes}
    for _ in range(cartas_por):
        for nome in nomes:
            st.session_state.maos[nome].append(baralho.pop())

    for nome in nomes:
        st.session_state.maos[nome] = sorted(st.session_state.maos[nome], key=peso_carta)

    st.session_state.mao_da_rodada = random.randint(0, n - 1)
    st.session_state.prognosticos = {}
    st.session_state.progn_pre = {}
    st.session_state.progn_pos = {}

    st.session_state.vazas_rodada = {nome: 0 for nome in nomes}
    st.session_state.log = []
    st.session_state.fase = "prognostico"

def preparar_prognosticos_anteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_humano = idx_na_ordem(ordem, humano)

    prev = ordem[:pos_humano]
    pre = {}
    for nome in prev:
        mao = st.session_state.maos[nome]
        pre[nome] = random.randint(0, len(mao))
    st.session_state.progn_pre = pre

def preparar_prognosticos_posteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_humano = idx_na_ordem(ordem, humano)

    post = ordem[pos_humano+1:]
    pos = {}
    for nome in post:
        mao = st.session_state.maos[nome]
        pos[nome] = random.randint(0, len(mao))
    st.session_state.progn_pos = pos

def iniciar_fase_jogo():
    nomes = st.session_state.nomes
    st.session_state.ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)

    # turno começa no "mão" (posição 0 da ordem)
    st.session_state.turn_idx = 0
    st.session_state.naipe_base = None
    st.session_state.mesa = []
    st.session_state.primeira_vaza = True
    st.session_state.copas_quebrada = False

    st.session_state.fase = "jogo"
    st.session_state.log.append(f"🎬 Início do jogo — mão da rodada: {st.session_state.ordem[0]}.")

def cartas_validas_para_jogar(nome):
    mao = st.session_state.maos[nome]
    naipe_base = st.session_state.naipe_base
    primeira_vaza = st.session_state.primeira_vaza
    copas_quebrada = st.session_state.copas_quebrada

    if not mao:
        return []

    # se precisa seguir naipe
    if naipe_base and tem_naipe(mao, naipe_base):
        return [c for c in mao if c[0] == naipe_base]

    # se está abrindo a vaza (naipe_base None): aplicar regras de copas
    if naipe_base is None:
        # na 1ª vaza: não pode abrir com copas, exceto se só tiver copas
        if primeira_vaza:
            if somente_trunfo(mao):
                return mao[:]  # pode
            return [c for c in mao if c[0] != TRUNFO]

        # demais vazas: copas só pode abrir se já quebrou, exceto se só tiver copas
        if not copas_quebrada and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]

    # caso geral
    return mao[:]

def jogar_carta(nome, carta):
    # remove da mão
    st.session_state.maos[nome].remove(carta)

    # define naipe base se for primeira da vaza
    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta[0]

    # se alguém jogou copas (fora exceções), marca como quebrada
    if carta[0] == TRUNFO and not st.session_state.primeira_vaza:
        st.session_state.copas_quebrada = True

    # mesa
    st.session_state.mesa.append((nome, carta))
    st.session_state.log.append(f"🃏 {nome} jogou {valor_str(carta[1])}{carta[0]}.")

def vencedor_da_vaza():
    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base

    # se tiver copas, maior copas vence
    copas = [(n,c) for (n,c) in mesa if c[0] == TRUNFO]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1][1]])[0]

    # senão, maior do naipe base
    base = [(n,c) for (n,c) in mesa if c[0] == naipe_base]
    return max(base, key=lambda x: PESO_VALOR[x[1][1]])[0]

def fechar_vaza_e_preparar_proxima():
    win = vencedor_da_vaza()
    st.session_state.vazas_rodada[win] += 1
    st.session_state.log.append(f"🏅 {win} venceu a vaza.")

    # próximo turno: vencedor abre
    ordem = st.session_state.ordem
    st.session_state.turn_idx = ordem.index(win)

    # reset vaza
    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.primeira_vaza = False

def rodada_terminou():
    # terminou quando humano ficou sem cartas (todos ficam com mesmo tamanho)
    humano = st.session_state.nomes[st.session_state.humano_idx]
    return len(st.session_state.maos[humano]) == 0

def pontuar_rodada():
    # regra que você vinha usando: pontos = vazas + 5 se acertou prognóstico
    nomes = st.session_state.nomes
    for n in nomes:
        v = st.session_state.vazas_rodada.get(n, 0)
        p = v
        if st.session_state.prognosticos.get(n) == v:
            p += 5
        st.session_state.pontos[n] = st.session_state.pontos.get(n, 0) + p

    st.session_state.log.append("📌 Fim da rodada — pontuação aplicada.")

def ai_escolhe_carta(nome):
    validas = cartas_validas_para_jogar(nome)
    if not validas:
        return None
    # simples: escolhe aleatória entre válidas
    return random.choice(validas)

def avancar_ate_vez_do_humano():
    """Faz a IA jogar automaticamente até ser a vez do humano (ou a vaza fechar)."""
    nomes = st.session_state.nomes
    humano = nomes[st.session_state.humano_idx]
    ordem = st.session_state.ordem

    # segurança
    limit = 500
    steps = 0

    while steps < limit:
        steps += 1

        # se a rodada acabou
        if rodada_terminou():
            return

        # se a vaza está completa, fechar e continuar (IA pode abrir próxima)
        if len(st.session_state.mesa) == len(ordem):
            fechar_vaza_e_preparar_proxima()
            continue

        atual = ordem[st.session_state.turn_idx]

        # se chegou no humano e ele ainda não jogou nesta vaza, parar
        if atual == humano:
            return

        # IA joga
        carta = ai_escolhe_carta(atual)
        if carta is None:
            return

        # regra: copas quebra apenas após primeira vaza; mas se IA jogar copas na 1ª vaza, só se só tiver copas
        # (isso já é garantido por cartas_validas_para_jogar)
        jogar_carta(atual, carta)

        # próximo jogador na ordem
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

    # se cair aqui, evita loop infinito
    st.session_state.log.append("⚠️ Aviso: limite de automação atingido (proteção).")

def mesa_ui():
    nomes = st.session_state.nomes
    n = len(nomes)
    ordem = st.session_state.ordem
    humano = nomes[st.session_state.humano_idx]
    dealer = ordem[0] if ordem else nomes[st.session_state.mao_da_rodada]

    # posições em círculo
    cx, cy = 50, 50
    rx, ry = 42, 36
    seats_html = ""

    for i, nome in enumerate(ordem):
        ang = (2 * math.pi) * (i / n) - (math.pi/2)
        x = cx + rx * math.cos(ang)
        y = cy + ry * math.sin(ang)

        cls = "mesaSeat"
        if nome == humano:
            cls += " seatIsYou"
        if nome == dealer:
            cls += " seatIsDealer"

        label = nome
        if nome == humano:
            label = f"{nome} (Você)"
        if nome == dealer:
            label = f"{label} • mão"

        seats_html += f'<div class="{cls}" style="left:{x}%; top:{y}%; transform:translate(-50%,-50%);">{label}</div>'

    # cartas jogadas na mesa (perto de cada seat)
    plays_html = ""
    mesa = st.session_state.mesa
    pos_map = {nome: i for i, nome in enumerate(ordem)}
    for nome, carta in mesa:
        i = pos_map.get(nome, 0)
        ang = (2 * math.pi) * (i / n) - (math.pi/2)
        x = cx + (rx * 0.55) * math.cos(ang)
        y = cy + (ry * 0.55) * math.sin(ang)
        plays_html += f'<div class="playCard" style="left:{x}%; top:{y}%;">{carta_html(carta)}</div>'

    centro_txt = "Mesa vazia" if not mesa else "Vaza em andamento"
    if st.session_state.fase == "jogo":
        if st.session_state.naipe_base is None and len(mesa) == 0:
            centro_txt = "Aguardando o mão abrir a vaza"
        elif st.session_state.naipe_base is not None:
            centro_txt = f"Naipe da vaza: {st.session_state.naipe_base}"

    st.markdown("#### 🎴 Mesa")
    st.markdown(
        f"""
<div class="mesa">
  {seats_html}
  {plays_html}
  <div class="mesaCenter">{centro_txt}</div>
</div>
""",
        unsafe_allow_html=True
    )

# =========================
# SETUP
# =========================
if not st.session_state.started:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Configuração rápida")
    nomes_txt = st.text_input(
        "Jogadores (separados por vírgula). O último será Você",
        value=", ".join(st.session_state.nomes)
    )

    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with colB:
        st.markdown(
            '<div class="panel" style="padding:12px; background:rgba(0,120,90,.06); border-color:rgba(0,120,90,.20);">'
            'As cartas serão distribuídas igualmente até acabar o baralho.'
            "</div>",
            unsafe_allow_html=True
        )

    if start:
        nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
        if len(nomes) < 2:
            st.error("Informe pelo menos 2 jogadores.")
        else:
            st.session_state.nomes = nomes
            st.session_state.humano_idx = len(nomes) - 1
            st.session_state.pontos = {n: 0 for n in nomes}
            st.session_state.started = True
            st.session_state.rodada = 1
            distribuir()
            preparar_prognosticos_anteriores()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================
# PROGNÓSTICO
# =========================
nomes = st.session_state.nomes
humano_nome = nomes[st.session_state.humano_idx]

# Ordem por rodada (ainda não setada em jogo)
ordem_preview = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
pos_humano = idx_na_ordem(ordem_preview, humano_nome)
eh_pe = (pos_humano == len(ordem_preview) - 1)

st.markdown(f"### 📌 Rodada {st.session_state.rodada} — {st.session_state.cartas_por_jog} cartas por jogador")

# MÃO VISUAL
mao_humano = st.session_state.maos.get(humano_nome, [])
render_hand_visual(mao_humano, "Suas cartas (visualização)")
st.markdown("<hr/>", unsafe_allow_html=True)

# Prognósticos visíveis (apenas anteriores)
st.markdown("### ✅ Prognósticos visíveis (anteriores na mesa)")
if st.session_state.fase == "prognostico" and not st.session_state.progn_pre:
    preparar_prognosticos_anteriores()

visiveis = dict(st.session_state.progn_pre)
if not visiveis:
    st.info("Você é o mão — ninguém fez prognóstico antes de você.")
else:
    linhas = []
    for nome in ordem_preview:
        if nome in visiveis:
            linhas.append((nome, visiveis[nome]))
    st.table({"Jogador": [x[0] for x in linhas], "Prognóstico": [x[1] for x in linhas]})

st.markdown("<hr/>", unsafe_allow_html=True)

max_palpite = len(mao_humano)
palpite = st.number_input("Seu prognóstico", min_value=0, max_value=max_palpite, value=0, step=1)

if st.session_state.fase == "prognostico":
    if st.button("Confirmar meu prognóstico", use_container_width=True):
        # salva prognóstico humano
        st.session_state.prognosticos = {}
        st.session_state.prognosticos.update(st.session_state.progn_pre)
        st.session_state.prognosticos[humano_nome] = int(palpite)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        # se humano é o pé, pode ver tudo, mas vamos deixar escondido por padrão (você pediu)
        st.session_state.show_all_progn = False

        iniciar_fase_jogo()
        # já avança o jogo até ser sua vez (se IA é mão)
        avancar_ate_vez_do_humano()
        st.rerun()

# =========================
# JOGO (VAZAS)
# =========================
if st.session_state.fase == "jogo":
    st.markdown("<hr/>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.25, 1])
    with col1:
        mesa_ui()

        # status topo
        ordem = st.session_state.ordem
        atual = ordem[st.session_state.turn_idx]
        st.info(
            f"🎯 Vez de: **{atual}**  |  "
            f"Naipe da vaza: **{st.session_state.naipe_base or '-'}**  |  "
            f"Copas quebrada: **{'Sim' if st.session_state.copas_quebrada else 'Não'}**  |  "
            f"1ª vaza: **{'Sim' if st.session_state.primeira_vaza else 'Não'}**"
        )

        # Mostra prognósticos mas escondidos (você pediu que não ficasse “poluindo”)
        with st.expander("📋 Ver prognósticos da rodada"):
            linhas = []
            for nome in ordem:
                linhas.append((nome, st.session_state.prognosticos.get(nome, "-")))
            st.table({"Jogador": [x[0] for x in linhas], "Prognóstico": [x[1] for x in linhas]})

        st.markdown("### 🂠 Sua mão (para jogar)")
        mao = st.session_state.maos[humano_nome]
        # visual
        render_hand_visual(mao, "Suas cartas")

        # seleção clicável (com trava das inválidas)
        validas = set(cartas_validas_para_jogar(humano_nome))

        # se não é sua vez, só informa e não mostra botões
        if atual != humano_nome:
            st.warning("Aguarde — a IA está jogando. Quando for sua vez, as cartas liberam.")
            # garante que IA avance (caso algo tenha parado)
            if st.button("▶️ Continuar", use_container_width=True):
                avancar_ate_vez_do_humano()
                st.rerun()
        else:
            st.markdown("#### Clique em uma carta válida para jogar (as inválidas ficam travadas)")
            # coloca botões em grid com colunas
            cols = st.columns(8)
            mao_ord = sorted(mao, key=peso_carta)

            clicked = None
            for i, carta in enumerate(mao_ord):
                naipe, valor = carta
                label = f"{valor_str(valor)}{naipe}"
                disabled = carta not in validas
                with cols[i % 8]:
                    if st.button(label, key=f"play_{st.session_state.rodada}_{len(st.session_state.log)}_{i}", use_container_width=True, disabled=disabled):
                        clicked = carta

            if clicked is not None:
                jogar_carta(humano_nome, clicked)
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

                # se vaza completa, fecha
                if len(st.session_state.mesa) == len(ordem):
                    fechar_vaza_e_preparar_proxima()

                # avança IA até voltar pra você (ou terminar)
                avancar_ate_vez_do_humano()

                # se acabou a rodada, pontua
                if rodada_terminou():
                    pontuar_rodada()
                    st.success("✅ Rodada finalizada e pontuação aplicada!")
                st.rerun()

    with col2:
        st.markdown("### 🧾 Registro")
        # log curto, mais recente em cima
        for msg in reversed(st.session_state.log[-14:]):
            st.write(msg)

        st.markdown("---")
        st.markdown("### 🎯 Vaz as na rodada")
        for n in st.session_state.nomes:
            st.write(f"• **{n}**: {st.session_state.vazas_rodada.get(n, 0)}")

        # se rodada terminou, botão para próxima
        if rodada_terminou():
            st.markdown("---")
            if st.button("➡️ Próxima rodada", use_container_width=True):
                st.session_state.rodada += 1
                distribuir()
                preparar_prognosticos_anteriores()
                st.rerun()

