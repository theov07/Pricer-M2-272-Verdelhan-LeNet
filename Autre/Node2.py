import math


class Node:
    def __init__(self, S: float, t: int, p: float = None):
        self.S = S
        self.t = t
        self.p = p
        self.children = {}

    def add_child(self, direction: str, node: "Node", p: float):
        self.children[direction] = {"node": node, "p": p}

    def grow(self, N, market, delta, k=3):
        """
        Crée récursivement les enfants jusqu'à la profondeur N.
        """
        if self.t >= N:
            return  # Stop condition: feuille

        # Calcul des prix pour le prochain step
        r = market.r
        sigma = market.sigma

        Smid = self.S * math.exp(r * delta)
        stddev = Smid * (math.exp(sigma**2 * delta) - 1)
        alpha = 1 + k * stddev / Smid

        Sup = Smid * alpha
        Sdown = Smid / alpha

        # Probabilités risk-neutral
        mu = r - 0.5 * sigma ** 2
        p_up = 0.5 * (
            (sigma ** 2 * delta + mu ** 2 * delta ** 2) / (sigma ** 2 * delta)
            + mu * delta / (sigma * math.sqrt(2 * delta))
        )
        p_down = 0.5 * (
            (sigma ** 2 * delta + mu ** 2 * delta ** 2) / (sigma ** 2 * delta)
            - mu * delta / (sigma * math.sqrt(2 * delta))
        )
        p_mid = 1 - p_up - p_down

        # Création des enfants
        up_node = Node(S=Sup, t=self.t + 1)
        mid_node = Node(S=Smid, t=self.t + 1)
        down_node = Node(S=Sdown, t=self.t + 1)

        self.add_child("up", up_node, p_up)
        self.add_child("mid", mid_node, p_mid)
        self.add_child("down", down_node, p_down)

        # Appel récursif pour chaque enfant
        up_node.grow(N, market, delta, k)
        mid_node.grow(N, market, delta, k)
        down_node.grow(N, market, delta, k)


    def price(self, option, r=0, delta=0):
        """
        Calcule le prix de l'option à partir de ce noeud (backward induction).
        """
        if not self.children:  # Si feuille
            return option.payoff(self.S)
        else:
            value = 0
            for info in self.children.values():
                child = info["node"]
                p = info["p"]
                # Actualisation risk-neutral
                value += p * child.price(option, r, delta)
            # Actualisation à la date courante
            return math.exp(-r * delta) * value
        







