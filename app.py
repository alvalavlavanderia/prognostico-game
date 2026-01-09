import random

NAIPES = ["♠", "♦", "♣", "♥"]
VALORES = list(range(2, 11)) + ["J", "Q", "K", "A"]
VALOR_PESO = {v: i for i, v in enumerate(VALORES)}

class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def __repr__(self):
        return f"{self.valor}{self.naipe}"

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.prognostico = 0
        self.vazas = 0
        self.pontos = 0

    def somente_copas(self):
        return all(c.naipe == "♥" for c in self.mao)

def criar_baralho():
    return [Carta(n, v) for n in NAIPES for v in VALORES]

class PrognosticoGame:
    def __init__(self, nomes_jogadores):
        self.jogadores = [Jogador(n) for n in nomes_jogadores]
        self.mao_inicial = random.randint(0, len(self.jogadores) - 1)

    def distribuir_cartas(self, cartas_por_jogador):
        baralho = criar_baralho()
        random.shuffle(baralho)

        for j in self.jogadores:
            j.mao = []
            j.vazas = 0

        for _ in range(cartas_por_jogador):
            for j in self.jogadores:
                j.mao.append(baralho.pop())

    def coletar_prognosticos(self):
        for j in self.jogadores:
            j.prognostico = random.randint(0, len(j.mao))

    def escolher_carta(self, jogador, naipe_base, primeira_vaza):
        validas = []
        for c in jogador.mao:
            if primeira_vaza and c.naipe == "♥" and not jogador.somente_copas():
                continue
            validas.append(c)

        if naipe_base:
            seguindo = [c for c in validas if c.naipe == naipe_base]
            if seguindo:
                return random.choice(seguindo)

        return random.choice(validas)

    def definir_vencedor(self, mesa, naipe_base, primeira_vaza):
        copas = [
            (j, c) for j, c in mesa
            if c.naipe == "♥" and (not primeira_vaza or j.somente_copas())
        ]

        if copas:
            return max(copas, key=lambda x: VALOR_PESO[x[1].valor])[0]

        mesmo_naipe = [(j, c) for j, c in mesa if c.naipe == naipe_base]
        return max(mesmo_naipe, key=lambda x: VALOR_PESO[x[1].valor])[0]

    def jogar_rodada(self, cartas_por_jogador):
        self.distribuir_cartas(cartas_por_jogador)
        self.coletar_prognosticos()

        ordem = self.jogadores[self.mao_inicial:] + self.jogadores[:self.mao_inicial]
        primeira_vaza = True

        while ordem[0].mao:
            mesa = []
            naipe_base = None

            for j in ordem:
                carta = self.escolher_carta(j, naipe_base, primeira_vaza)
                j.mao.remove(carta)

                if not naipe_base:
                    naipe_base = carta.naipe

                mesa.append((j, carta))

            vencedor = self.definir_vencedor(mesa, naipe_base, primeira_vaza)
            vencedor.vazas += 1

            idx = ordem.index(vencedor)
            ordem = ordem[idx:] + ordem[:idx]
            primeira_vaza = False

    def pontuar(self):
        for j in self.jogadores:
            pontos = j.vazas
            if j.vazas == j.prognostico:
                pontos += 5
            j.pontos += pontos

    def jogar(self):
        cartas_max = 52 // len(self.jogadores)

        for c in range(cartas_max, 0, -1):
            self.jogar_rodada(c)
            self.pontuar()

        self.jogadores.sort(key=lambda j: j.pontos, reverse=True)
