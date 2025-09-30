
class Option:
    def __init__(self, T: float, K: float, opt_type: str = "call", style: str = "european"):
        self.T = T              # maturité
        self.K = K              # strike
        self.type = opt_type    # "call" ou "put"
        self.style = style      # "european" ou "american"

    def payoff(self, S: float) -> float:
        """Calcule le payoff au noeud final"""
        if self.type == "call":
            return max(S - self.K, 0)
        elif self.type == "put":
            return max(self.K - S, 0)
        else:
            raise ValueError("Type d'option invalide : doit être 'call' ou 'put'")