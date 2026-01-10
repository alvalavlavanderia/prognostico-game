import random
from dataclasses import dataclass
import streamlit as st

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="Jogo de Prognóstico", layout="wide")

# ============================================================
# MODELOS
# ============================================================
NAIPES = ["♦", "♠", "♣", "♥"]  # ordem pedida p/ ordenar a mão: ouro, espada, paus, copas
NAIPE_NOME = {"♦": "Ouro", "♠": "Espadas", "♣": "Paus", "♥": "Copas"}
NAIPE_COR = {"♦": "red", "♥": "red", "♠": "black", "♣": "black"}

VALORES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALOR_PESO = {v: i for i, v in enumerate(VALORES)}  # 2 menor ... A maior


@dataclass(frozen=True)
class Carta:
    naipe: str
    valor: str

    def peso(self) -> int:
        return VALOR_PESO[self.valor]

    def __str__(self) -> str:
        return f"{self.valor}{self.naipe}"


@dataclass
class Jogador:
    nome: str
    mao: list
    prognostico: int = None
    vazas: int = 0
    pontos: int = 0

    def tem_naipe(self, naipe: str) -> bool:
        return any(c.naipe == naipe for c in self.mao)

    def somente_copas(self) -> bool:
        return len(self.mao) > 0 and all(c.naipe == "♥" for c in self.mao)


# ============================================================
# ESTILO (CSS)
# ============================================================
CSS = """
<style>
/* tira espaços exagerados e ajuda reduzir scroll */
.block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
div[data-testid="stVerticalBlock"] > div { gap: 0.65rem; }

/* "App bar" */
.appbar{
  display:flex; align-items:center; justify-content:space-between;
  padding: 10px 14px; border-radius: 14px;
  background: linear-gradient(90deg, #0c7a6b, #0b5f54);
  color: white; margin-bottom: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,.08);
}
.appbar .title{ font-size: 24px; font-weight: 800; letter-spacing:.3px; display:flex; gap:10px; align-items:center; }
.badges{ display:flex; gap:8px; flex-wrap:wrap; }
.badge{
  background: rgba(255,255,255,.16);
  padding: 6px 10px; border-radius: 999px;
  font-size: 12px; font-weight: 600;
}

/* "Mesa" central */
.tableWrap{
  border-radius: 18px;
  background: #f2f2f2;
  border: 1px solid rgba(0,0,0,.06);
  padding: 14px;
  height: 260px;
  position: relative;
  overflow: hidden;
}
.tableTitle{
  display:flex; justify-content:space-between; align-items:center;
  margin-bottom: 10px;
}
.tableTitle .left{ font-weight: 800; }
.tableTitle .right{ font-size: 12px; opacity:.75; }

.seat{
  position:absolute; font-size: 12px; font-weight: 700;
  color: rgba(0,0,0,.65);
  background: rgba(255,255,255,.65);
  border: 1px solid rgba(0,0,0,.08);
  padding: 4px 8px;
  border-radius: 999px;
}
.seat.top{ top: 16px; left: 50%; transform: translateX(-50%); }
.seat.left{ left: 16px; top: 50%; transform: translateY(-50%); }
.seat.right{ right: 16px; top: 50%; transform: translateY(-50%); }
.seat.bottom{ bottom: 16px; left: 50%; transform: translateX(-50%); }

/* cartas na mesa */
.tableCards{
  position:absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display:flex; gap:14px; flex-wrap:wrap;
  justify-content:center; align-items:center;
  width: 90%;
}

/* carta (visual) */
.cardBtn button{
  width: 64px !important;
  height: 92px !important;
  padding: 0 !important;
  border-radius: 14px !important;
  border: 1px solid rgba(0,0,0,.20) !important;
  background: white !important;
  box-shadow: 0 10px 20px rgba(0,0,0,.10) !important;
  transition: transform .12s ease, box-shadow .12s ease;
}
.cardBtn button:hover{
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(0,0,0,.14) !important;
}
.cardBtn button:disabled{
  opacity: 0.35 !important;
  transform: none !important;
  box-shadow: none !important;
}
.cardLabel{
  display:flex; flex-direction:column; align-items:flex-start; justify-content:space-between;
  width: 64px; height: 92px; padding: 8px 9px;
  box-sizing:border-box;
  font-weight: 800;
}
.cardMid{ align-self:center; font-size: 22px; }
.cardCorner{ font-size: 14px; line-height: 1; }

/* mão do jogador */
.handRow{
  display:flex; gap:10px; flex-wrap:wrap; align-items:center;
}

/* tabela prognósticos */
.smallTable{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 14px;
  overflow:hidden;
}
.smallTable table{ width:100%; border-collapse:collapse; }
.smallTable th, .smallTable td{ padding: 8px 10px; border-bottom: 1px solid rgba(0,0,0,.06); font-size: 13px; }
.smallTable th{ background: rgba(0,0,0,.03); text-align:left; }

/* sidebar */
.sidebarBox{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 14px;
  padding: 10px;
  background: rgba(0,0,0,.02);
  margin-bottom: 10px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# FUNÇÕES DO JOGO
# ============================================================
def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]


def ordenar_mao(mao):
    # ordem: ♦, ♠, ♣, ♥ e dentro do naipe 2..A
    naipe_ord = {n: i for i, n in enumerate(NAIPES)}
    return sorted(mao, key=lambda c: (naipe_ord[c.naipe], c.peso()))


def distribuir_cartas(jogadores, cartas_por_jogador):
    baralho = criar_baralho()
    random.shuffle(baralho)
    for j in jogadores:
        j.mao = []
        j.vazas = 0
        j.prognostico = None
    for _ in range(cartas_por_jogador):
        for j in jogadores:
            j.mao.append(baralho.pop())
    for j in jogadores:
        j.mao = ordenar_mao(j.mao)


def proximo_indice(idx, n):
    return (idx + 1) % n


def idx_do_nome(jogadores, nome):
    for i, j in enumerate(jogadores):
        if j.nome == nome:
            return i
    return 0


def cartas_validas_para_jogada(jogador: Jogador, naipe_base: str, primeira_vaza_da_rodada: bool, copas_quebradas: bool):
    """
    Regras:
    - Deve seguir o naipe se tiver.
    - Copas não pode ser "aberta" na 1ª vaza (salvo se o jogador só tiver copas).
    - Copas trava até quebrar. Só quebra:
        * em vaza != 1, quando alguém joga copas (por não ter o naipe, ou abrindo se já quebrado)
        * na 1ª vaza NÃO quebra (salvo jogador só tem copas).
    """
    mao = jogador.mao

    # se tem naipe_base, é obrigado seguir
    if naipe_base and jogador.tem_naipe(naipe_base):
        return [c for c in mao if c.naipe == naipe_base]

    # caso seja mão (naipe_base None) ou não tem naipe_base
    validas = []
    for c in mao:
        if primeira_vaza_da_rodada:
            # primeira vaza: não pode jogar copas, exceto se só tiver copas
            if c.naipe == "♥" and not jogador.somente_copas():
                continue
        else:
            # depois: se copas ainda não quebrou, não pode "abrir" copas como mão,
            # mas pode jogar copas se não tiver o naipe base (slough), o que quebra copas.
            # Aqui a função apenas define se pode ou não selecionar; a quebra é aplicada no jogo.
            pass
        validas.append(c)

    # se nada sobrou (ex: só tinha copas na 1ª vaza), libera tudo
    if not validas:
        validas = mao[:]
    return validas


def vencedor_da_vaza(mesa, naipe_base):
    """
    mesa: lista de tuplas (idx_jogador, Carta)
    - Copas é trunfo, exceto:
      - na 1ª vaza, copas só vale se jogador só tinha copas (essa validação já aconteceu antes)
    Aqui assumimos que se uma copas entrou, ela vale como trunfo.
    """
    # se tem copas na mesa, maior copas ganha
    copas = [(idx, c) for idx, c in mesa if c.naipe == "♥"]
    if copas:
        return max(copas, key=lambda x: x[1].peso())[0]

    # senão maior do naipe base
    mesmo = [(idx, c) for idx, c in mesa if c.naipe == naipe_base]
    return max(mesmo, key=lambda x: x[1].peso())[0]


def pontuar_rodada(jogadores):
    for j in jogadores:
        pontos = j.vazas
        if j.prognostico is not None and j.vazas == j.prognostico:
            pontos += 5
        j.pontos += pontos


def resetar_jogo():
    for k in list(st.session_state.keys()):
        if k.startswith("game_") or k in ["jogadores", "humano_idx"]:
            del st.session_state[k]


# ============================================================
# UI: Cartas visualmente (dentro do botão)
# ============================================================
def card_inner_html(carta: Carta):
    cor = NAIPE_COR[carta.naipe]
    v = carta.valor
    n = carta.naipe
    # cantos + centro
    return f"""
    <div class="cardLabel" style="color:{cor};">
      <div class="cardCorner">{v}<br>{n}</div>
      <div class="cardMid">{n}</div>
      <div class="cardCorner" style="align-self:flex-end; transform: rotate(180deg);">{v}<br>{n}</div>
    </div>
    """


def render_small_table(rows, headers):
    # rows: list of list
    th = "".join([f"<th>{h}</th>" for h in headers])
    tr = ""
    for r in rows:
        tds = "".join([f"<td>{x}</td>" for x in r])
        tr += f"<tr>{tds}</tr>"
    return f"""
    <div class="smallTable">
      <table>
        <thead><tr>{th}</tr></thead>
        <tbody>{tr}</tbody>
      </table>
    </div>
    """


# ============================================================
# ESTADO / INICIALIZAÇÃO
# ============================================================
def garantir_estado_inicial():
    if "jogadores" not in st.session_state:
        st.session_state.jogadores = []
    if "humano_idx" not in st.session_state:
        st.session_state.humano_idx = None

    # estado do jogo
    defaults = {
        "game_started": False,
        "game_round": 1,
        "game_cards_per_player": None,
        "game_order": [],             # ordem de jogo (indices)
        "game_mao_idx": None,         # quem é o mão da rodada (indice jogador)
        "game_vaza_starter_idx": None,# quem abre a vaza atual
        "game_primeira_vaza": True,
        "game_copas_quebradas": False,
        "game_mesa": [],              # lista de (idx_jogador, Carta)
        "game_naipe_base": None,
        "game_log": [],               # mensagens da rodada
        "game_fase": "setup",         # setup -> prognostico -> jogando -> fim_rodada -> fim_jogo
        "game_prognostico_idx": 0,    # ponteiro para ordem de prognóstico
        "game_prognosticos_ordem": [],# lista de indices para palpite
        "game_vazas_total": 0,
        "game_vaza_num": 1,
        "game_max_cartas_inicial": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def iniciar_novo_jogo(nomes):
    jogadores = [Jogador(nome=n.strip(), mao=[]) for n in nomes if n.strip()]
    if len(jogadores) < 3:
        st.error("Use pelo menos 3 jogadores.")
        return

    # humano será o último nome (você)
    humano_idx = len(jogadores) - 1
    st.session_state.jogadores = jogadores
    st.session_state.humano_idx = humano_idx

    # cartas iniciais: regra pedida p/ 4 jogadores => 10 (sobra 2)
    n = len(jogadores)
    cartas_inicial = min(10, 52 // n)
    st.session_state.game_max_cartas_inicial = cartas_inicial

    # mão inicial aleatório (regra pedida)
    mao_idx = random.randint(0, n - 1)

    st.session_state.game_round = 1
    st.session_state.game_cards_per_player = cartas_inicial
    st.session_state.game_mao_idx = mao_idx

    preparar_rodada()
    st.session_state.game_started = True
    st.session_state.game_fase = "prognostico"
    st.session_state.game_log = []


def preparar_rodada():
    jogadores = st.session_state.jogadores
    n = len(jogadores)

    cartas_por_jogador = st.session_state.game_cards_per_player
    distribuir_cartas(jogadores, cartas_por_jogador)

    # ordem de jogo começa no mão da rodada
    mao_idx = st.session_state.game_mao_idx
    ordem = list(range(mao_idx, n)) + list(range(0, mao_idx))
    st.session_state.game_order = ordem

    # prognóstico segue a mesma ordem (mão -> ... -> pé)
    st.session_state.game_prognosticos_ordem = ordem[:]
    st.session_state.game_prognostico_idx = 0

    # vaza inicia pelo mão (na primeira vaza)
    st.session_state.game_vaza_starter_idx = mao_idx
    st.session_state.game_primeira_vaza = True
    st.session_state.game_copas_quebradas = False
    st.session_state.game_mesa = []
    st.session_state.game_naipe_base = None
    st.session_state.game_vazas_total = cartas_por_jogador
    st.session_state.game_vaza_num = 1

    # reset palpites e vazas
    for j in jogadores:
        j.vazas = 0
        j.prognostico = None


def avancar_prognostico(selecionado: int):
    jogadores = st.session_state.jogadores
    idx_lista = st.session_state.game_prognosticos_ordem
    ponteiro = st.session_state.game_prognostico_idx

    j_idx = idx_lista[ponteiro]
    jogadores[j_idx].prognostico = int(selecionado)

    st.session_state.game_prognostico_idx += 1
    if st.session_state.game_prognostico_idx >= len(idx_lista):
        st.session_state.game_fase = "jogando"
        st.session_state.game_log.append("✅ Prognósticos finalizados. Vamos iniciar as vazas!")


def ordem_da_vaza_atual():
    # a ordem da vaza começa pelo starter atual (quem abre a vaza)
    jogadores = st.session_state.jogadores
    n = len(jogadores)
    starter = st.session_state.game_vaza_starter_idx
    return list(range(starter, n)) + list(range(0, starter))


def jogar_carta(j_idx, carta: Carta):
    jogadores = st.session_state.jogadores

    # remove carta
    jogadores[j_idx].mao.remove(carta)
    jogadores[j_idx].mao = ordenar_mao(jogadores[j_idx].mao)

    # mesa + naipe base
    if st.session_state.game_naipe_base is None:
        st.session_state.game_naipe_base = carta.naipe

    st.session_state.game_mesa.append((j_idx, carta))

    # copas quebradas (mas NÃO quebra na 1ª vaza, salvo "só copas")
    if carta.naipe == "♥":
        if not st.session_state.game_primeira_vaza:
            st.session_state.game_copas_quebradas = True


def finalizar_vaza_se_completa():
    jogadores = st.session_state.jogadores
    n = len(jogadores)

    if len(st.session_state.game_mesa) < n:
        return  # ainda não acabou

    naipe_base = st.session_state.game_naipe_base
    vencedor_idx = vencedor_da_vaza(st.session_state.game_mesa, naipe_base)
    jogadores[vencedor_idx].vazas += 1

    # log
    mesa_str = ", ".join([f"{jogadores[i].nome}: {c}" for i, c in st.session_state.game_mesa])
    st.session_state.game_log.append(f"🟦 Vaza {st.session_state.game_vaza_num}: {mesa_str}")
    st.session_state.game_log.append(f"🏅 Vencedor da vaza: **{jogadores[vencedor_idx].nome}**")

    # próxima vaza começa pelo vencedor
    st.session_state.game_vaza_starter_idx = vencedor_idx
    st.session_state.game_mesa = []
    st.session_state.game_naipe_base = None
    st.session_state.game_primeira_vaza = False
    st.session_state.game_vaza_num += 1

    # terminou a rodada?
    if all(len(j.mao) == 0 for j in jogadores):
        pontuar_rodada(jogadores)
        st.session_state.game_fase = "fim_rodada"


def proxima_rodada_ou_fim():
    jogadores = st.session_state.jogadores
    n = len(jogadores)

    # próxima rodada tem -1 carta
    st.session_state.game_cards_per_player -= 1
    st.session_state.game_round += 1

    if st.session_state.game_cards_per_player <= 0:
        st.session_state.game_fase = "fim_jogo"
        return

    # REGRA pedida: mão da rodada vai para o jogador ao lado (sentido horário)
    st.session_state.game_mao_idx = proximo_indice(st.session_state.game_mao_idx, n)

    preparar_rodada()
    st.session_state.game_fase = "prognostico"


# ============================================================
# SIDEBAR (placar e status)
# ============================================================
def sidebar():
    jogadores = st.session_state.jogadores
    if not jogadores:
        return

    st.sidebar.markdown("### 📊 Placar")
    placar_rows = [[j.nome, j.pontos, j.vazas, (j.prognostico if j.prognostico is not None else "-")] for j in jogadores]
    st.sidebar.markdown(render_small_table(placar_rows, ["Jogador", "Pontos", "Vazas", "Progn."]), unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Status")
    st.sidebar.markdown('<div class="sidebarBox">', unsafe_allow_html=True)
    st.sidebar.write(f"Rodada: {st.session_state.game_round}")
    st.sidebar.write(f"Cartas na rodada: {st.session_state.game_cards_per_player}")
    st.sidebar.write(f"Vaza: {st.session_state.game_vaza_num}/{st.session_state.game_vazas_total}")
    st.sidebar.write(f"Copas: {'✅ quebrada' if st.session_state.game_copas_quebradas else '🔒 travada'}")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Resetar jogo (zera tudo)"):
        resetar_jogo()
        st.rerun()


# ============================================================
# TELAS
# ============================================================
def appbar():
    jogadores = st.session_state.jogadores
    humano = jogadores[st.session_state.humano_idx].nome if jogadores and st.session_state.humano_idx is not None else "Você"

    badge1 = f"Trunfo: ♥"
    badge2 = "1ª vaza: ♥ proibida (exceto só ♥)"
    badge3 = "Copas trava até quebrar"
    st.markdown(
        f"""
        <div class="appbar">
          <div class="title">🃏 Jogo de Prognóstico</div>
          <div class="badges">
            <div class="badge">{badge1}</div>
            <div class="badge">{badge2}</div>
            <div class="badge">{badge3}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def tela_setup():
    st.subheader("Configuração rápida")
    nomes_txt = st.text_input("Jogadores (separados por vírgula). **O último será Você**",
                             value="Ana, Bruno, Carlos, Você")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("▶️ Iniciar jogo", use_container_width=True):
            nomes = [n.strip() for n in nomes_txt.split(",") if n.strip()]
            iniciar_novo_jogo(nomes)
            if st.session_state.game_started:
                st.rerun()
    with col2:
        st.info("O jogo começa com 10 cartas por jogador (se possível). Para 4 jogadores sobram 2 cartas no baralho.")


def mostrar_mesa():
    jogadores = st.session_state.jogadores
    ordem = ordem_da_vaza_atual()
    humano_idx = st.session_state.humano_idx

    # lugares (top/left/right/bottom)
    # bottom = humano, top = o "oposto" se existir, left/right conforme sobra
    nomes = [jogadores[i].nome for i in ordem]
    # vamos montar os assentos em relação ao humano:
    # seat bottom = humano
    # os outros em sequência na ordem (depois do humano)
    if humano_idx in ordem:
        pos_h = ordem.index(humano_idx)
    else:
        pos_h = 0

    outros = ordem[pos_h+1:] + ordem[:pos_h]
    seat_bottom = jogadores[humano_idx].nome if humano_idx is not None else "Você"
    seat_top = jogadores[outros[1]].nome if len(outros) >= 2 else (jogadores[outros[0]].nome if outros else "")
    seat_left = jogadores[outros[2]].nome if len(outros) >= 3 else (jogadores[outros[0]].nome if outros else "")
    seat_right = jogadores[outros[0]].nome if len(outros) >= 1 else ""

    mesa = st.session_state.game_mesa

    # cartas na mesa
    cards_html = ""
    for j_idx, c in mesa:
        cards_html += f"""
        <div style="text-align:center;">
          <div style="font-size:12px; font-weight:800; margin-bottom:6px;">{jogadores[j_idx].nome}</div>
          <div style="display:inline-block;">
            <div style="width:64px;height:92px;border-radius:14px;border:1px solid rgba(0,0,0,.2);background:#fff;box-shadow:0 10px 20px rgba(0,0,0,.10);">
              {card_inner_html(c)}
            </div>
          </div>
        </div>
        """

    titulo_dir = "Aguardando início da 1ª vaza" if st.session_state.game_primeira_vaza and not mesa else f"Naipe da vaza: {st.session_state.game_naipe_base or '—'}"

    st.markdown(
        f"""
        <div class="tableWrap">
          <div class="tableTitle">
            <div class="left">🪑 MESA</div>
            <div class="right">{titulo_dir}</div>
          </div>

          <div class="seat top">{seat_top}</div>
          <div class="seat left">{seat_left}</div>
          <div class="seat right">{seat_right}</div>
          <div class="seat bottom">{seat_bottom}</div>

          <div class="tableCards">
            {cards_html if cards_html else '<div style="opacity:.6;font-weight:700;">Mesa vazia — o mão abre a vaza</div>'}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def tela_prognostico():
    jogadores = st.session_state.jogadores
    humano_idx = st.session_state.humano_idx
    humano = jogadores[humano_idx]

    st.markdown(f"#### 📌 Rodada {st.session_state.game_round} — {st.session_state.game_cards_per_player} cartas")

    mao_nome = jogadores[st.session_state.game_mao_idx].nome
    st.info(f"🟦 Mão da rodada: **{mao_nome}**")

    # Mostrar mão do humano (VISUALIZAÇÃO) — corrigido p/ não aparecer HTML como texto
    st.markdown("#### 🃏 Suas cartas (visualização)")
    st.markdown('<div class="handRow">', unsafe_allow_html=True)
    for c in humano.mao:
        # renderiza visual sem botão (apenas para ver o jogo antes do prognóstico)
        st.markdown(
            f"""
            <div style="width:64px;height:92px;border-radius:14px;border:1px solid rgba(0,0,0,.2);background:#fff;box-shadow:0 10px 20px rgba(0,0,0,.10);">
              {card_inner_html(c)}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Mostrar prognósticos visíveis:
    ordem = st.session_state.game_prognosticos_ordem
    ponteiro = st.session_state.game_prognostico_idx
    idx_atual = ordem[ponteiro]

    # regra pedida:
    # - se humano é o pé (último a palpitar), pode ver todos os anteriores (que são todos)
    # - caso contrário, humano só vê prognósticos de quem já palpitou antes dele na ordem (anteriores a ele)
    pos_h = ordem.index(humano_idx)
    if ponteiro > pos_h:
        # humano já palpitou, então pode ver todos os já feitos (até ponteiro)
        visiveis = ordem[:ponteiro]
    else:
        # humano ainda não palpitou
        if pos_h == len(ordem) - 1:
            visiveis = ordem[:ponteiro]  # se ele é pé, enxerga todos os já feitos
        else:
            # enxerga apenas quem vem antes dele, e que já palpitou
            visiveis = [i for i in ordem[:ponteiro] if ordem.index(i) < pos_h]

    rows = []
    for i in visiveis:
        p = jogadores[i].prognostico
        if p is not None:
            rows.append([jogadores[i].nome, p])

    if rows:
        st.markdown("#### ✅ Prognósticos visíveis")
        st.markdown(render_small_table(rows, ["Jogador", "Prognóstico"]), unsafe_allow_html=True)
    else:
        st.markdown("#### ✅ Prognósticos visíveis")
        st.caption("Ainda não há prognósticos visíveis para você neste momento.")

    st.markdown("---")

    # Quem está palpitando agora?
    st.markdown(f"#### 🎯 Agora é a vez de **{jogadores[idx_atual].nome}** dar o prognóstico")

    max_palpite = st.session_state.game_cards_per_player
    if idx_atual == humano_idx:
        col1, col2 = st.columns([1, 1])
        with col1:
            palpite = st.number_input("Seu prognóstico", min_value=0, max_value=max_palpite, value=0, step=1)
        with col2:
            st.write("")
            st.write("")
            if st.button("Confirmar meu prognóstico", use_container_width=True):
                avancar_prognostico(int(palpite))
                st.rerun()
    else:
        # IA simples pros outros (placeholder) — mantém andando
        palpite_bot = random.randint(0, max_palpite)
        avancar_prognostico(palpite_bot)
        st.rerun()

    # mesa (pré-jogo)
    mostrar_mesa()


def tela_jogando():
    jogadores = st.session_state.jogadores
    humano_idx = st.session_state.humano_idx
    humano = jogadores[humano_idx]

    st.markdown(f"#### 📌 Rodada {st.session_state.game_round} — {st.session_state.game_cards_per_player} cartas")

    # Mesa ao centro
    mostrar_mesa()

    st.markdown("---")

    # Ordem da vaza e vez de jogar
    ordem_vaza = ordem_da_vaza_atual()
    ja_jogaram = [idx for idx, _ in st.session_state.game_mesa]
    faltam = [i for i in ordem_vaza if i not in ja_jogaram]
    vez_idx = faltam[0] if faltam else None

    if vez_idx is None:
        finalizar_vaza_se_completa()
        st.rerun()
        return

    st.markdown(f"### 🎮 Sua mão (jogo) — vez de: **{jogadores[vez_idx].nome}**")
    st.caption("Cartas inválidas ficam travadas (desabilitadas).")

    # AI joga automaticamente quando não é humano
    if vez_idx != humano_idx:
        j = jogadores[vez_idx]
        validas = cartas_validas_para_jogada(
            j,
            st.session_state.game_naipe_base,
            st.session_state.game_primeira_vaza,
            st.session_state.game_copas_quebradas
        )
        # escolha simples: menor válida
        carta = sorted(validas, key=lambda c: c.peso())[0]
        jogar_carta(vez_idx, carta)
        finalizar_vaza_se_completa()
        st.rerun()
        return

    # Se é humano, mostra todas as cartas como "cartas-botão"
    validas = cartas_validas_para_jogada(
        humano,
        st.session_state.game_naipe_base,
        st.session_state.game_primeira_vaza,
        st.session_state.game_copas_quebradas
    )
    valid_set = set(validas)

    # mostra sua mão (ordenada)
    st.markdown('<div class="handRow">', unsafe_allow_html=True)
    cols = st.columns(min(10, max(1, len(humano.mao))))  # quebra se muitas
    for i, carta in enumerate(humano.mao):
        disabled = carta not in valid_set
        with cols[i % len(cols)]:
            # botão "vazio" mas estilizado como carta via CSS class .cardBtn
            st.markdown('<div class="cardBtn">', unsafe_allow_html=True)
            clicked = st.button(" ", key=f"play_{st.session_state.game_round}_{st.session_state.game_vaza_num}_{i}_{str(carta)}",
                                disabled=disabled, use_container_width=True)
            # desenha a carta em cima (visual)
            st.markdown(
                f"""
                <div style="margin-top:-92px; pointer-events:none;">
                  {card_inner_html(carta)}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if clicked and not disabled:
                jogar_carta(humano_idx, carta)
                finalizar_vaza_se_completa()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧾 Eventos recentes")
    # log compacto
    for msg in st.session_state.game_log[-6:]:
        st.write(msg)


def tela_fim_rodada():
    jogadores = st.session_state.jogadores

    st.success("✅ Rodada finalizada! Pontuação atualizada.")

    rows = [[j.nome, j.prognostico, j.vazas, j.pontos] for j in jogadores]
    st.markdown(render_small_table(rows, ["Jogador", "Prognóstico", "Vazas", "Total Pontos"]), unsafe_allow_html=True)

    st.markdown("---")
    if st.button("➡️ Próxima rodada", use_container_width=True):
        proxima_rodada_ou_fim()
        st.rerun()


def tela_fim_jogo():
    jogadores = sorted(st.session_state.jogadores, key=lambda j: j.pontos, reverse=True)

    st.balloons()
    st.success("🏆 Jogo finalizado!")

    rows = [[j.nome, j.pontos] for j in jogadores]
    st.markdown(render_small_table(rows, ["Jogador", "Pontos finais"]), unsafe_allow_html=True)

    if st.button("🔄 Novo jogo", use_container_width=True):
        resetar_jogo()
        st.rerun()


# ============================================================
# MAIN
# ============================================================
def main():
    garantir_estado_inicial()
    appbar()
    sidebar()

    if not st.session_state.game_started:
        tela_setup()
        return

    fase = st.session_state.game_fase
    if fase == "prognostico":
        tela_prognostico()
    elif fase == "jogando":
        tela_jogando()
    elif fase == "fim_rodada":
        tela_fim_rodada()
    elif fase == "fim_jogo":
        tela_fim_jogo()
    else:
        tela_setup()


if __name__ == "__main__":
    main()


