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
    def __init__(self, nome, humano=False):
        self.nome = nome
        self.humano = humano
        self.mao = []
        self.prognostico = None
        self.vazas = 0
        self.pontos = 0

    def tem_naipe(self, naipe):
        return any(c.naipe == naipe for c in self.mao)

    def somente_copas(self):
        return all(c.naipe == "♥" for c in self.mao)

class PrognosticoGame:
    def __init__(self):
        self.jogadores = [
            Jogador("Você", humano=True),
            Jogador("Bot 1"),
            Jogador("Bot 2"),
            Jogador("Bot 3"),
        ]
        self.ordem = []
        self.mesa = []
        self.naipe_base = None
        self.primeira_vaza = True

    def criar_baralho(self):
        return [Carta(n, v) for n in NAIPES for v in VALORES]

    def distribuir_cartas(self, qtd):
        baralho = self.criar_baralho()
        random.shuffle(baralho)
        for j in self.jogadores:
            j.mao = []
            j.vazas = 0
        for _ in range(qtd):
            for j in self.jogadores:
                j.mao.append(baralho.pop())

        self.ordem = self.jogadores.copy()
        random.shuffle(self.ordem)

    def cartas_validas(self, jogador):
        validas = []
        for c in jogador.mao:
            if self.primeira_vaza and c.naipe == "♥" and not jogador.somente_copas():
                continue
            validas.append(c)

        if self.naipe_base and jogador.tem_naipe(self.naipe_base):
            validas = [c for c in validas if c.naipe == self.naipe_base]

        return validas

    def jogar_bot(self, jogador):
        carta = random.choice(self.cartas_validas(jogador))
        self.jogar_carta(jogador, carta)

    def jogar_carta(self, jogador, carta):
        jogador.mao.remove(carta)
        if not self.naipe_base:
            self.naipe_base = carta.naipe
        self.mesa.append((jogador, carta))

    def fechar_vaza(self):
        copas = [(j, c) for j, c in self.mesa if c.naipe == "♥"]
        if copas and not self.primeira_vaza:
            vencedor = max(copas, key=lambda x: VALOR_PESO[x[1].valor])[0]
        else:
            mesmo_naipe = [(j, c) for j, c in self.mesa if c.naipe == self.naipe_base]
            vencedor = max(mesmo_naipe, key=lambda x: VALOR_PESO[x[1].valor])[0]

        vencedor.vazas += 1
        self.ordem = self.ordem[self.ordem.index(vencedor):] + \
                     self.ordem[:self.ordem.index(vencedor)]

        self.mesa = []
        self.naipe_base = None
        self.primeira_vaza = False
