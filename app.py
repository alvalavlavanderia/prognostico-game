def carta_ganha_contra(minha, outra, naipe_base):
    """Retorna True se minha vence outra, considerando trunfo e naipe base."""
    n1, v1 = minha
    n2, v2 = outra

    # trunfo vence não-trunfo
    if n1 == TRUNFO and n2 != TRUNFO:
        return True
    if n1 != TRUNFO and n2 == TRUNFO:
        return False

    # ambos trunfo
    if n1 == TRUNFO and n2 == TRUNFO:
        return PESO_VALOR[v1] > PESO_VALOR[v2]

    # nenhum trunfo: ganha quem segue naipe base e for mais alto
    if n1 == naipe_base and n2 != naipe_base:
        return True
    if n1 != naipe_base and n2 == naipe_base:
        return False
    if n1 == naipe_base and n2 == naipe_base:
        return PESO_VALOR[v1] > PESO_VALOR[v2]

    # se nenhum é naipe base (situação rara em comparação direta), compara peso simples
    return PESO_VALOR[v1] > PESO_VALOR[v2]

def melhor_para_ganhar(validas, mesa, naipe_base):
    """Escolhe a menor carta que 'provavelmente' ganha agora; se não dá, joga a maior."""
    if not mesa:
        # abrindo: joga a mais forte de forma moderada (não sempre a maior)
        # pega top 3 e escolhe a menor delas pra não desperdiçar
        top = sorted(validas, key=lambda c: PESO_VALOR[c[1]], reverse=True)[:3]
        return sorted(top, key=lambda c: PESO_VALOR[c[1]])[0]

    # existe carta liderando
    # define carta "atual vencedora" na mesa
    naipe = naipe_base
    melhor_nome, melhor_c = mesa[0]
    for nm, c in mesa[1:]:
        if carta_ganha_contra(c, melhor_c, naipe):
            melhor_c = c

    # tenta ganhar com a menor que bate a atual vencedora
    ganhadoras = [c for c in validas if carta_ganha_contra(c, melhor_c, naipe)]
    if ganhadoras:
        return sorted(ganhadoras, key=lambda c: (c[0] != TRUNFO, PESO_VALOR[c[1]]))[0]

    # não consegue ganhar: joga a menor
    return sorted(validas, key=lambda c: (c[0] == TRUNFO, PESO_VALOR[c[1]]))[0]

def melhor_para_perder(validas, mesa, naipe_base):
    """Escolhe a carta que minimiza chance de ganhar."""
    # se tem naipe base, joga a menor dele
    return sorted(validas, key=lambda c: (c[0] == TRUNFO, PESO_VALOR[c[1]]))[0]

def ai_escolhe_carta(nome):
    """
    IA premium:
    - tenta bater seu prognóstico (nem mais, nem menos)
    - se precisa ganhar, joga para ganhar
    - se já bateu, joga para perder
    """
    validas = cartas_validas_para_jogar(nome)
    if not validas:
        return None

    alvo = st.session_state.prognosticos.get(nome, 0)
    feitas = st.session_state.vazas_rodada.get(nome, 0)

    mesa = st.session_state.mesa
    naipe_base = st.session_state.naipe_base if st.session_state.naipe_base else (mesa[0][1][0] if mesa else None)

    # quantas vazas ainda restam (aprox)
    # (número de cartas do jogador atual)
    restam = len(st.session_state.maos[nome])

    # se ainda falta para atingir, joga agressivo
    if feitas < alvo:
        # se falta pouco e restam poucas, fica mais agressivo
        return melhor_para_ganhar(validas, mesa, naipe_base)

    # se já atingiu ou passou, joga para não ganhar
    return melhor_para_perder(validas, mesa, naipe_base)
