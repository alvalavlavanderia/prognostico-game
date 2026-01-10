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
.block-container { padding-top: 1.0rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: 0.5rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* ---------- visual cards (html) ---------- */
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
.card .tl{ position:absolute; top:8px; left:8px; font-weight:900; font-size:14px; line-height:14px; }
.card .br{ position:absolute; bottom:8px; right:8px; font-weight:900; font-size:14px; line-height:14px; transform:rotate(180deg); }
.card .mid{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:900; opacity:.95; }

/* ---------- app header ---------- */
.badge{ display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(0,0,0,.06); font-size:12px; }
.topbar{ display:flex; gap:10px; flex-wrap:wrap; margin: 2px 0 10px 0; }
.titleRow{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 4px; }
.titleRow h1{ margin:0; }

/* ---------- mesa ---------- */
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
  font-weight:800;
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
.seatIsYou{ outline: 2px solid rgba(0,120,90,.55); font-weight:900; }
.seatIsDealer{ background: rgba(255,255,255,.92); border-color: rgba(0,120,90,.30); }
.playCard{
  position:absolute;
  transform:translate(-50%,-50%);
  pointer-events:none;
}

/* ---------- sidebar score ---------- */
.scoreItem{
  display:flex;
  justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.06);
  background:rgba(255,255,255,.7);
  margin-bottom:8px;
}
.scoreName{ font-weight:800; }
.scorePts{ font-weight:900; }
.smallMuted{ opacity:.70; font-size:12px; }
hr{ margin: 0.8rem 0 !important; }

/* =========================
   MODO 2 (Streamlit + CSS)
   cartas clicáveis com cara de carta
   ========================= */
div[data-testid="column"] button{
  border-radius: 14px !important;
  border: 1px solid rgba(0,0,0,.18) !important;
  background: linear-gradient(180deg, #ffffff 0%, #f9f9f9 100%) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.12) !important;
  padding: 0 !important;
  min-height: 110px !important;
  width: 100% !important;
  transition: transform .10s ease, box-shadow .10s ease, opacity .10s ease;
}
div[data-testid="column"] button:hover{
  transform: translateY(-3px);
  box-shadow: 0 14px 26px rgba(0,0,0,.16) !important;
}
div[data-testid="column"] button:disabled{
  opacity: .30 !important;
  transform: none !important;
  box-shadow: 0 6px 14px rgba(0,0,0,.08) !important;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# BARALHO / ORDENAÇÃO
# =========================
VALORES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
PESO_VALOR = {v: i for i, v in enumerate(VALORES)}  # 2 menor, A maior

COR_NAIPE = {"♦": "red", "♥": "red", "♠": "black", "♣": "black"}
ORDEM_NAIPE = {"♦": 0, "♠": 1, "♣": 2, "♥": 3}  # ouro, espada, paus, copas
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

def render_hand_visual(mao, titulo="Suas cartas"):
    mao_ordenada = sorted(mao, key=peso_carta)
    cards = "".join(carta_html(c) for c in mao_ordenada)
    st.markdown(f"### 🃏 {titulo}")
    st.markdown(f'<div class="handRow">{cards}</div>', unsafe_allow_html=True)

def card_button_label(c):
    # label com quebras de linha (fica bem com o CSS)
    naipe, valor = c
    vv = valor_str(valor)
    return f"{vv}\n{naipe}\n{vv}"

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

        "cartas_inicio": 0,
        "cartas_alvo": 0,
        "sobras_monte": 0,

        "mao_da_rodada": 0,
        "mao_primeira_sorteada": False,

        "fase": "setup",  # setup | prognostico | jogo | fim

        "prognosticos": {},
        "progn_pre": {},
        "progn_pos": {},

        "ordem": [],
        "turn_idx": 0,
        "naipe_base": None,
        "mesa": [],
        "primeira_vaza": True,
        "copas_quebrada": False,
        "log": [],
        "pontuou_rodada": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# =========================
# CORE (rodadas)
# =========================
def distribuir(cartas_alvo: int):
    nomes = st.session_state.nomes
    n = len(nomes)

    baralho = criar_baralho()
    random.shuffle(baralho)

    usadas = cartas_alvo * n
    sobras = len(baralho) - usadas

    st.session_state.cartas_alvo = cartas_alvo
    st.session_state.sobras_monte = sobras

    st.session_state.maos = {nome: [] for nome in nomes}

    for _ in range(cartas_alvo):
        for nome in nomes:
            st.session_state.maos[nome].append(baralho.pop())

    for nome in nomes:
        st.session_state.maos[nome] = sorted(st.session_state.maos[nome], key=peso_carta)

    # mão da rodada
    if not st.session_state.mao_primeira_sorteada:
        st.session_state.mao_da_rodada = random.randint(0, n - 1)
        st.session_state.mao_primeira_sorteada = True
    else:
        st.session_state.mao_da_rodada = (st.session_state.mao_da_rodada + 1) % n

    st.session_state.prognosticos = {}
    st.session_state.progn_pre = {}
    st.session_state.progn_pos = {}
    st.session_state.vazas_rodada = {nome: 0 for nome in nomes}
    st.session_state.log = []
    st.session_state.fase = "prognostico"
    st.session_state.pontuou_rodada = False

def start_game_from_setup(nomes):
    st.session_state.nomes = nomes
    st.session_state.humano_idx = len(nomes) - 1
    st.session_state.pontos = {n: 0 for n in nomes}
    st.session_state.started = True

    n = len(nomes)
    cartas_inicio = 52 // n
    st.session_state.cartas_inicio = cartas_inicio
    st.session_state.cartas_alvo = cartas_inicio
    st.session_state.rodada = 1

    distribuir(cartas_inicio)
    preparar_prognosticos_anteriores()

def start_next_round():
    # baixa 1 carta por jogador até 1
    if st.session_state.cartas_alvo <= 1:
        return
    st.session_state.rodada += 1
    prox = st.session_state.cartas_alvo - 1
    distribuir(prox)
    preparar_prognosticos_anteriores()

# =========================
# PROGNÓSTICOS
# =========================
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

    post = ordem[pos_humano + 1:]
    pos = {}
    for nome in post:
        mao = st.session_state.maos[nome]
        pos[nome] = random.randint(0, len(mao))
    st.session_state.progn_pos = pos

# =========================
# JOGO (vazas)
# =========================
def iniciar_fase_jogo():
    nomes = st.session_state.nomes
    st.session_state.ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    st.session_state.turn_idx = 0
    st.session_state.naipe_base = None
    st.session_state.mesa = []
    st.session_state.primeira_vaza = True
    st.session_state.copas_quebrada = False
    st.session_state.fase = "jogo"
    st.session_state.log.append(f"🎬 Início da rodada — mão: {st.session_state.ordem[0]}.")

def cartas_validas_para_jogar(nome):
    mao = st.session_state.maos[nome]
    naipe_base = st.session_state.naipe_base
    primeira_vaza = st.session_state.primeira_vaza
    copas_quebrada = st.session_state.copas_quebrada

    if not mao:
        return []

    # 1) seguindo naipe é obrigatório
    if naipe_base and tem_naipe(mao, naipe_base):
        return [c for c in mao if c[0] == naipe_base]

    # 2) se NÃO tem o naipe_base (vai descartar) => regras especiais na 1ª vaza:
    if naipe_base and not tem_naipe(mao, naipe_base):
        # na 1ª vaza: NÃO pode jogar copas, exceto se só tiver copas
        if primeira_vaza and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]
        # fora da 1ª vaza, pode descartar copas (quebra)
        return mao[:]

    # 3) abrindo a vaza (naipe_base None): regra de copas
    if naipe_base is None:
        # 1ª vaza: não pode abrir com copas, exceto só copas
        if primeira_vaza:
            if somente_trunfo(mao):
                return mao[:]
            return [c for c in mao if c[0] != TRUNFO]

        # demais vazas: não abre com copas se não quebrou, exceto só copas
        if not copas_quebrada and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]

    return mao[:]

def jogar_carta(nome, carta):
    st.session_state.maos[nome].remove(carta)

    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta[0]

    # copas só "quebra" se foi jogada após a 1ª vaza
    if carta[0] == TRUNFO and not st.session_state.primeira_vaza:
        st.session_state.copas_quebrada = True

    st.session_state.mesa.append((nome, carta))
    st.session_state.log.append(f"🃏 {nome} jogou {valor_str(carta[1])}{carta[0]}.")

def vencedor_da_vaza():
    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base

    copas = [(n, c) for (n, c) in mesa if c[0] == TRUNFO]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1][1]])[0]

    base = [(n, c) for (n, c) in mesa if c[0] == naipe_base]
    return max(base, key=lambda x: PESO_VALOR[x[1][1]])[0]

def fechar_vaza_e_preparar_proxima():
    win = vencedor_da_vaza()
    st.session_state.vazas_rodada[win] += 1
    st.session_state.log.append(f"🏅 {win} venceu a vaza.")

    ordem = st.session_state.ordem
    st.session_state.turn_idx = ordem.index(win)

    st.session_state.mesa = []
    st.session_state.naipe_base = None
    st.session_state.primeira_vaza = False

def rodada_terminou():
    return all(len(st.session_state.maos[n]) == 0 for n in st.session_state.nomes)

def pontuar_rodada():
    if st.session_state.pontuou_rodada:
        return
    for n in st.session_state.nomes:
        v = st.session_state.vazas_rodada.get(n, 0)
        p = v + (5 if st.session_state.prognosticos.get(n) == v else 0)
        st.session_state.pontos[n] = st.session_state.pontos.get(n, 0) + p
    st.session_state.pontuou_rodada = True
    st.session_state.log.append("📌 Fim da rodada — pontuação aplicada.")

def ai_escolhe_carta(nome):
    validas = cartas_validas_para_jogar(nome)
    return random.choice(validas) if validas else None

def avancar_jogo_ate_vez_do_humano_ou_fim():
    nomes = st.session_state.nomes
    humano = nomes[st.session_state.humano_idx]
    ordem = st.session_state.ordem

    limit = 2000
    steps = 0
    while steps < limit:
        steps += 1

        # fecha vaza completa
        if len(st.session_state.mesa) == len(ordem):
            fechar_vaza_e_preparar_proxima()
            continue

        # fim de rodada
        if rodada_terminou():
            pontuar_rodada()
            return

        atual = ordem[st.session_state.turn_idx]

        # se atual não tem cartas, pula
        if len(st.session_state.maos[atual]) == 0:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        # sua vez
        if atual == humano and len(st.session_state.maos[humano]) > 0:
            return

        # IA joga
        carta = ai_escolhe_carta(atual)
        if carta is None:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        jogar_carta(atual, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

    st.session_state.log.append("⚠️ Proteção: limite de automação atingido.")

# =========================
# UI (mesa)
# =========================
def mesa_ui():
    nomes = st.session_state.nomes
    n = len(nomes)
    ordem = st.session_state.ordem
    humano = nomes[st.session_state.humano_idx]
    dealer = ordem[0] if ordem else nomes[st.session_state.mao_da_rodada]

    cx, cy = 50, 50
    rx, ry = 42, 36
    seats_html = ""

    for i, nome in enumerate(ordem):
        ang = (2 * math.pi) * (i / n) - (math.pi / 2)
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

    plays_html = ""
    pos_map = {nome: i for i, nome in enumerate(ordem)}
    for nome, carta in st.session_state.mesa:
        i = pos_map.get(nome, 0)
        ang = (2 * math.pi) * (i / n) - (math.pi / 2)
        x = cx + (rx * 0.55) * math.cos(ang)
        y = cy + (ry * 0.55) * math.sin(ang)
        plays_html += f'<div class="playCard" style="left:{x}%; top:{y}%;">{carta_html(carta)}</div>'

    centro_txt = "Mesa vazia" if not st.session_state.mesa else "Vaza em andamento"
    if st.session_state.fase == "jogo":
        if st.session_state.naipe_base is None and len(st.session_state.mesa) == 0:
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
            f'<div class="smallMuted">Rodada: {st.session_state.rodada} • Cartas/jogador: {st.session_state.cartas_alvo} • Sobras: {st.session_state.sobras_monte}</div>',
            unsafe_allow_html=True
        )

        # ✅ botão sempre acessível quando a rodada terminar
        if st.session_state.fase == "jogo" and rodada_terminou():
            st.markdown("---")
            if st.session_state.cartas_alvo > 1:
                if st.button("➡️ Próxima rodada (-1 carta)", use_container_width=True):
                    start_next_round()
                    st.rerun()
            else:
                st.markdown("---")
                vencedor, pts = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)[0]
                st.success(f"🏆 Fim do jogo! {vencedor} com {pts} pts")

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
    <span class="badge">Abrir com ♥ só após quebrar (ou só ♥)</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# =========================
# SETUP
# =========================
if not st.session_state.started:
    st.markdown("### Configuração rápida")
    nomes_txt = st.text_input(
        "Jogadores (separados por vírgula). O último será Você",
        value=", ".join(st.session_state.nomes),
    )
    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with colB:
        st.info("As cartas serão distribuídas igualmente até acabar o baralho. A cada rodada diminui 1 carta por jogador.")

    if start:
        nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
        if len(nomes) < 2:
            st.error("Informe pelo menos 2 jogadores.")
        else:
            start_game_from_setup(nomes)
            st.rerun()

    st.stop()

# =========================
# PROGNÓSTICO
# =========================
nomes = st.session_state.nomes
humano_nome = nomes[st.session_state.humano_idx]

if st.session_state.fase == "prognostico":
    ordem_preview = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)

    st.markdown(f"### 📌 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas por jogador")

    mao_humano = st.session_state.maos.get(humano_nome, [])
    render_hand_visual(mao_humano, "Suas cartas (visualização)")
    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown("### ✅ Prognósticos visíveis (anteriores na mesa)")
    if not st.session_state.progn_pre:
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

    if st.button("Confirmar meu prognóstico", use_container_width=True):
        st.session_state.prognosticos = {}
        st.session_state.prognosticos.update(st.session_state.progn_pre)
        st.session_state.prognosticos[humano_nome] = int(palpite)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        iniciar_fase_jogo()
        avancar_jogo_ate_vez_do_humano_ou_fim()
        st.rerun()

# =========================
# JOGO (VAZAS)
# =========================
if st.session_state.fase == "jogo":
    st.markdown(f"### 🎮 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas por jogador")
    col1, col2 = st.columns([1.25, 1])

    with col1:
        mesa_ui()
        ordem = st.session_state.ordem
        atual = ordem[st.session_state.turn_idx]

        st.info(
            f"🎯 Vez de: **{atual}** | "
            f"Naipe: **{st.session_state.naipe_base or '-'}** | "
            f"♥ quebrada: **{'Sim' if st.session_state.copas_quebrada else 'Não'}** | "
            f"1ª vaza: **{'Sim' if st.session_state.primeira_vaza else 'Não'}**"
        )

        with st.expander("📋 Ver prognósticos da rodada"):
            st.table({
                "Jogador": st.session_state.ordem,
                "Prognóstico": [st.session_state.prognosticos.get(n, "-") for n in st.session_state.ordem]
            })

        # Se rodada terminou, só informa (botão de próxima rodada está no sidebar)
        if rodada_terminou():
            pontuar_rodada()
            st.success("✅ Rodada finalizada (todos sem cartas). Use o botão no sidebar para ir à próxima.")
            st.stop()

        st.markdown("### 🂠 Sua mão")
        mao = st.session_state.maos[humano_nome]
        render_hand_visual(mao, "Suas cartas")

        if atual != humano_nome or len(mao) == 0:
            st.warning("Aguarde — a IA está jogando. Clique em continuar para avançar.")
            if st.button("▶️ Continuar", use_container_width=True):
                avancar_jogo_ate_vez_do_humano_ou_fim()
                st.rerun()
        else:
            validas = set(cartas_validas_para_jogar(humano_nome))
            st.caption("Clique em uma carta válida (as inválidas ficam travadas, mas visíveis).")

            mao_ord = sorted(mao, key=peso_carta)
            cols = st.columns(10)

            clicked = None
            for i, carta in enumerate(mao_ord):
                disabled = carta not in validas
                with cols[i % 10]:
                    if st.button(
                        card_button_label(carta),
                        key=f"play_{st.session_state.rodada}_{len(st.session_state.log)}_{i}",
                        use_container_width=True,
                        disabled=disabled
                    ):
                        clicked = carta

            if clicked is not None:
                jogar_carta(humano_nome, clicked)
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

                if len(st.session_state.mesa) == len(ordem):
                    fechar_vaza_e_preparar_proxima()

                avancar_jogo_ate_vez_do_humano_ou_fim()
                if rodada_terminou():
                    pontuar_rodada()

                st.rerun()

    with col2:
        st.markdown("### 🧾 Registro")
        for msg in reversed(st.session_state.log[-18:]):
            st.write(msg)

        st.markdown("---")
        st.markdown("### 🎯 Vazas na rodada")
        for n in st.session_state.nomes:
            st.write(f"• **{n}**: {st.session_state.vazas_rodada.get(n, 0)}")
