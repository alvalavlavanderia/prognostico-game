# app.py
import random
import math
import urllib.parse
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Prognóstico", page_icon="🃏", layout="wide")

# =========================
# CSS PREMIUM
# =========================
APP_CSS = """
<style>
.block-container { padding-top: .8rem !important; padding-bottom: .8rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { height: .4rem; }
div[data-testid="stSidebarContent"] { padding-top: 1rem; }
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 20% 10%, rgba(0,150,110,.10), transparent 40%); }

/* Header */
.titleRow{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom: 6px; }
.titleRow h1{ margin:0; font-size: 28px; }
.badges{ display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.badge{ display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; background:rgba(0,0,0,.06); font-size:12px; font-weight:800; }

/* Mesa */
.mesaWrap{ margin-top: 6px; }
.mesa{
  border-radius:20px;
  border:1px solid rgba(0,0,0,.10);
  background: radial-gradient(circle at 30% 20%, rgba(0,150,110,.30) 0%, rgba(0,120,90,.18) 28%, rgba(0,0,0,.03) 60%, rgba(0,0,0,.02) 100%);
  height: 420px;
  position:relative;
  overflow:hidden;
  box-shadow: 0 18px 40px rgba(0,0,0,.10);
}
.mesaCenter{
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-weight:900; opacity:.70;
  pointer-events:none;
  text-transform: uppercase;
  letter-spacing: .08em;
}
.seat{
  position:absolute;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.82);
  border:1px solid rgba(0,0,0,.08);
  font-size:12px;
  white-space:nowrap;
}
.seat.you{ outline:2px solid rgba(0,120,90,.55); font-weight:900; }
.seat.dealer{ border-color: rgba(0,120,90,.30); background: rgba(255,255,255,.92); }
.playCard{
  position:absolute;
  transform: translate(-50%,-50%);
  pointer-events:none;
}

/* Carta */
.card{
  width:76px;
  height:110px;
  border-radius:14px;
  border:1px solid rgba(0,0,0,.16);
  background: linear-gradient(180deg, #ffffff 0%, #f8f8f8 100%);
  box-shadow: 0 10px 22px rgba(0,0,0,.12);
  position:relative;
  user-select:none;
}
.card .tl{ position:absolute; top:8px; left:8px; font-weight:900; font-size:14px; line-height:14px; }
.card .br{ position:absolute; bottom:8px; right:8px; font-weight:900; font-size:14px; line-height:14px; transform:rotate(180deg); }
.card .mid{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:32px; font-weight:900; opacity:.92; }

/* Dock da mão */
.handDock{
  margin-top: 10px;
  border-radius: 18px;
  border:1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.75);
  backdrop-filter: blur(8px);
  box-shadow: 0 14px 34px rgba(0,0,0,.08);
  padding: 12px;
}
.handTitle{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 6px; }
.handTitle h3{ margin:0; font-size:16px; }
.hint{ font-size:12px; opacity:.70; font-weight:800; }
.handRow{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  align-items:flex-end;
}

/* Cartas clicáveis (Premium JS) */
.cardLink{
  display:inline-block;
  cursor:pointer;
  transition: transform .10s ease, filter .10s ease;
}
.cardLink:hover{
  transform: translateY(-4px);
  filter: saturate(1.05);
}
.cardLink.disabled{
  pointer-events:none;
  opacity:.28;
  transform:none;
  filter:none;
  cursor:default;
}
.cardLink.disabled .card{
  box-shadow: 0 6px 14px rgba(0,0,0,.08);
}

/* Pop */
@keyframes popIn {
  0% { transform: translate(-50%,-50%) scale(.92); opacity: .0; }
  100% { transform: translate(-50%,-50%) scale(1.0); opacity: 1; }
}
.playCard.pop { animation: popIn .14s ease-out; }

/* Sidebar */
.scoreItem{
  display:flex; justify-content:space-between;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,.06);
  background:rgba(255,255,255,.70);
  margin-bottom:8px;
}
.scoreName{ font-weight:900; }
.scorePts{ font-weight:900; }
.smallMuted{ opacity:.70; font-size:12px; }
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

def carta_html(c):
    naipe, valor = c
    cor = COR_NAIPE[naipe]
    vv = valor_str(valor)
    return (
        f'<div class="card">'
        f'<div class="tl" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'<div class="mid" style="color:{cor};">{naipe}</div>'
        f'<div class="br" style="color:{cor};">{vv}<br/>{naipe}</div>'
        f'</div>'
    )

def serialize_card(c):
    naipe, valor = c
    return f"{naipe}|{valor}"

def deserialize_card(s):
    naipe, valor = s.split("|", 1)
    if valor.isdigit():
        valor = int(valor)
    return (naipe, valor)

# =========================
# UTIL
# =========================
def ordem_da_mesa(nomes, mao_idx):
    return [nomes[(mao_idx + i) % len(nomes)] for i in range(len(nomes))]

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

        "fase": "setup",  # setup | prognostico | jogo

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

        "last_play": None,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# =========================
# GAME CORE
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

    st.session_state.fase = "prognostico"
    st.session_state.log = []
    st.session_state.pontuou_rodada = False
    st.session_state.last_play = None

def preparar_prognosticos_anteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)

    prev = ordem[:pos_h]
    st.session_state.progn_pre = {n: random.randint(0, len(st.session_state.maos[n])) for n in prev}

def preparar_prognosticos_posteriores():
    nomes = st.session_state.nomes
    ordem = ordem_da_mesa(nomes, st.session_state.mao_da_rodada)
    humano = nomes[st.session_state.humano_idx]
    pos_h = ordem.index(humano)

    post = ordem[pos_h+1:]
    st.session_state.progn_pos = {n: random.randint(0, len(st.session_state.maos[n])) for n in post}

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

    # seguir naipe
    if naipe_base and tem_naipe(mao, naipe_base):
        return [c for c in mao if c[0] == naipe_base]

    # descartar (não tem naipe da vaza)
    if naipe_base and not tem_naipe(mao, naipe_base):
        if primeira_vaza and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]
        return mao[:]

    # abrindo vaza
    if naipe_base is None:
        if primeira_vaza:
            if somente_trunfo(mao):
                return mao[:]
            return [c for c in mao if c[0] != TRUNFO]

        if not copas_quebrada and not somente_trunfo(mao):
            return [c for c in mao if c[0] != TRUNFO]

    return mao[:]

def jogar_carta(nome, carta):
    st.session_state.maos[nome].remove(carta)

    if st.session_state.naipe_base is None:
        st.session_state.naipe_base = carta[0]

    if carta[0] == TRUNFO and not st.session_state.primeira_vaza:
        st.session_state.copas_quebrada = True

    st.session_state.mesa.append((nome, carta))
    st.session_state.last_play = (nome, carta)
    st.session_state.log.append(f"🃏 {nome} jogou {valor_str(carta[1])}{carta[0]}.")

def vencedor_da_vaza():
    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base
    copas = [(n,c) for (n,c) in mesa if c[0] == TRUNFO]
    if copas:
        return max(copas, key=lambda x: PESO_VALOR[x[1][1]])[0]
    base = [(n,c) for (n,c) in mesa if c[0] == naipe_base]
    return max(base, key=lambda x: PESO_VALOR[x[1][1]])[0]

def fechar_vaza():
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

def avancar_ate_humano_ou_fim():
    humano = st.session_state.nomes[st.session_state.humano_idx]
    ordem = st.session_state.ordem

    limit = 2500
    steps = 0
    while steps < limit:
        steps += 1

        if len(st.session_state.mesa) == len(ordem):
            fechar_vaza()
            continue

        if rodada_terminou():
            pontuar_rodada()
            return

        atual = ordem[st.session_state.turn_idx]

        if len(st.session_state.maos[atual]) == 0:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        if atual == humano and len(st.session_state.maos[humano]) > 0:
            return

        carta = ai_escolhe_carta(atual)
        if carta is None:
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)
            continue

        jogar_carta(atual, carta)
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

def start_next_round():
    if st.session_state.cartas_alvo <= 1:
        return
    st.session_state.rodada += 1
    prox = st.session_state.cartas_alvo - 1
    distribuir(prox)
    preparar_prognosticos_anteriores()

# =========================
# QUERY PARAM HANDLER (Premium click)
# =========================
def consume_play_query():
    qp = st.experimental_get_query_params()
    if "play" not in qp:
        return False

    raw = qp.get("play", [""])[0]
    st.experimental_set_query_params()  # limpa

    if not raw or st.session_state.fase != "jogo":
        return False

    humano = st.session_state.nomes[st.session_state.humano_idx]
    ordem = st.session_state.ordem
    atual = ordem[st.session_state.turn_idx]
    if atual != humano:
        return False

    try:
        carta = deserialize_card(raw)
    except Exception:
        return False

    mao = st.session_state.maos[humano]
    if carta not in mao:
        return False

    if carta not in cartas_validas_para_jogar(humano):
        return False

    jogar_carta(humano, carta)
    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(ordem)

    if len(st.session_state.mesa) == len(ordem):
        fechar_vaza()

    avancar_ate_humano_ou_fim()
    if rodada_terminou():
        pontuar_rodada()

    return True

if consume_play_query():
    st.rerun()

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

        if st.session_state.fase == "jogo" and rodada_terminou():
            st.markdown("---")
            if st.session_state.cartas_alvo > 1:
                if st.button("➡️ Próxima rodada (-1 carta)", use_container_width=True):
                    start_next_round()
                    st.rerun()
            else:
                vencedor, pts = sorted(st.session_state.pontos.items(), key=lambda x: x[1], reverse=True)[0]
                st.success(f"🏆 Fim do jogo! {vencedor} com {pts} pts")

        st.markdown("---")
        if st.button("🔁 Reiniciar", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            ss_init()
            st.rerun()
    else:
        st.info("Inicie uma partida.")

# =========================
# HEADER
# =========================
st.markdown(
    """
<div class="titleRow">
  <div>
    <h1>🃏 Jogo de Prognóstico</h1>
    <div class="smallMuted">Premium UI • Mesa central • Cartas clicáveis • Animação leve</div>
  </div>
  <div class="badges">
    <span class="badge">Trunfo: ♥</span>
    <span class="badge">1ª vaza: ♥ proibida</span>
    <span class="badge">Abrir com ♥ só após quebrar</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# =========================
# SETUP
# =========================
if not st.session_state.started:
    st.markdown("### Configuração")
    nomes_txt = st.text_input("Jogadores (separados por vírgula). O último será Você", value=", ".join(st.session_state.nomes))
    colA, colB = st.columns([1, 2])
    with colA:
        start = st.button("▶️ Iniciar jogo", use_container_width=True)
    with colB:
        st.info("As cartas serão distribuídas igualmente até acabar o baralho (sobras no monte). A cada rodada diminui 1 carta por jogador.")

    if start:
        nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
        if len(nomes) < 2:
            st.error("Informe pelo menos 2 jogadores.")
        else:
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

    st.markdown('<div class="handDock">', unsafe_allow_html=True)
    st.markdown('<div class="handTitle"><h3>🃏 Suas cartas (prognóstico)</h3><div class="hint">Ordenadas por naipe e valor</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="handRow">' + "".join(carta_html(c) for c in sorted(mao_humano, key=peso_carta)) + "</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### ✅ Prognósticos visíveis (anteriores na mesa)")
    if not st.session_state.progn_pre:
        preparar_prognosticos_anteriores()

    vis = st.session_state.progn_pre
    if not vis:
        st.info("Você é o mão — ninguém fez prognóstico antes de você.")
    else:
        rows = [(n, vis[n]) for n in ordem_preview if n in vis]
        st.table({"Jogador": [r[0] for r in rows], "Prognóstico": [r[1] for r in rows]})

    palpite = st.number_input("Seu prognóstico", min_value=0, max_value=len(mao_humano), value=0, step=1)

    if st.button("Confirmar meu prognóstico", use_container_width=True):
        st.session_state.prognosticos = {}
        st.session_state.prognosticos.update(st.session_state.progn_pre)
        st.session_state.prognosticos[humano_nome] = int(palpite)

        preparar_prognosticos_posteriores()
        st.session_state.prognosticos.update(st.session_state.progn_pos)

        iniciar_fase_jogo()
        avancar_ate_humano_ou_fim()
        st.rerun()

# =========================
# UI: Mesa e mão premium
# =========================
def render_mesa():
    ordem = st.session_state.ordem
    nomes = st.session_state.nomes
    n = len(ordem)
    humano = nomes[st.session_state.humano_idx]
    dealer = ordem[0]

    cx, cy = 50, 50
    rx, ry = 42, 36

    seats_html = ""
    for i, nome in enumerate(ordem):
        ang = (2*math.pi) * (i/n) - (math.pi/2)
        x = cx + rx*math.cos(ang)
        y = cy + ry*math.sin(ang)

        cls = "seat"
        label = nome
        if nome == humano:
            cls += " you"
            label = f"{nome} (Você)"
        if nome == dealer:
            cls += " dealer"
            label = f"{label} • mão"

        seats_html += f'<div class="{cls}" style="left:{x}%; top:{y}%; transform:translate(-50%,-50%);">{label}</div>'

    plays_html = ""
    pos_map = {nome:i for i,nome in enumerate(ordem)}
    for nome, carta in st.session_state.mesa:
        i = pos_map.get(nome, 0)
        ang = (2*math.pi) * (i/n) - (math.pi/2)
        x = cx + (rx*0.55)*math.cos(ang)
        y = cy + (ry*0.55)*math.sin(ang)
        plays_html += f'<div class="playCard" style="left:{x}%; top:{y}%;">{carta_html(carta)}</div>'

    centro_txt = "Aguardando jogada" if not st.session_state.mesa else "Vaza em andamento"
    if st.session_state.naipe_base:
        centro_txt = f"Naipe da vaza: {st.session_state.naipe_base}"

    st.markdown('<div class="mesaWrap">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

def render_hand_clickable():
    ordem = st.session_state.ordem
    humano = st.session_state.nomes[st.session_state.humano_idx]
    atual = ordem[st.session_state.turn_idx]
    mao = st.session_state.maos[humano]
    validas = set(cartas_validas_para_jogar(humano))

    st.markdown('<div class="handDock">', unsafe_allow_html=True)
    hint = "Clique numa carta válida" if atual == humano else "Aguardando sua vez"
    st.markdown(f'<div class="handTitle"><h3>🂠 Sua mão</h3><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

    # JS: atualiza query param na URL atual, sem perder caminho do app e sem abrir aba
    # (isso corrige exatamente seu problema)
    parts = ['<div class="handRow">']
    for c in sorted(mao, key=peso_carta):
        cid = serialize_card(c)
        cid_enc = urllib.parse.quote(cid, safe="")  # segura para URL
        disabled = (c not in validas) or (atual != humano)

        if disabled:
            parts.append(f'<div class="cardLink disabled">{carta_html(c)}</div>')
        else:
            parts.append(
                f"""
<div class="cardLink" onclick="
  (function(){{
    const url = new URL(window.location.href);
    url.searchParams.set('play', '{cid_enc}');
    window.location.href = url.toString();
  }})()
">
  {carta_html(c)}
</div>
"""
            )
    parts.append("</div>")

    st.markdown("".join(parts), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# JOGO
# =========================
if st.session_state.fase == "jogo":
    st.markdown(f"### 🎮 Rodada {st.session_state.rodada} — {st.session_state.cartas_alvo} cartas por jogador")

    col1, col2 = st.columns([1.35, 1])

    with col1:
        render_mesa()

        ordem = st.session_state.ordem
        atual = ordem[st.session_state.turn_idx]
        st.info(
            f"🎯 Vez de: **{atual}** | Naipe: **{st.session_state.naipe_base or '-'}** | "
            f"♥ quebrada: **{'Sim' if st.session_state.copas_quebrada else 'Não'}** | "
            f"1ª vaza: **{'Sim' if st.session_state.primeira_vaza else 'Não'}**"
        )

        with st.expander("📋 Ver prognósticos da rodada"):
            st.table({
                "Jogador": st.session_state.ordem,
                "Prognóstico": [st.session_state.prognosticos.get(n, "-") for n in st.session_state.ordem]
            })

        if rodada_terminou():
            pontuar_rodada()
            st.success("✅ Rodada finalizada (todos sem cartas). Use o botão no sidebar para ir à próxima.")
        else:
            humano = st.session_state.nomes[st.session_state.humano_idx]
            if atual != humano:
                st.warning("A IA está jogando. Clique para avançar.")
                if st.button("▶️ Continuar", use_container_width=True):
                    avancar_ate_humano_ou_fim()
                    st.rerun()

            render_hand_clickable()

    with col2:
        st.markdown("### 🧾 Registro")
        for msg in reversed(st.session_state.log[-18:]):
            st.write(msg)

        st.markdown("---")
        st.markdown("### 🎯 Vazas na rodada")
        for n in st.session_state.nomes:
            st.write(f"• **{n}**: {st.session_state.vazas_rodada.get(n, 0)}")

