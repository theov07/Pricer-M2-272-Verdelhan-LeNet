from datetime import datetime

class Option:

    def __init__(self, K: float, opt_type: str = "call", style: str = "european", 
                 T: float = None, start_date: str = None, maturity_date: str = None):
        """
        Initialise une option avec soit T directement, soit des dates pour calculer T
        
        Args:
            K: Strike price
            opt_type: "call" ou "put"
            style: "european" ou "american"
            T: Maturité en années (optionnel si dates fournies)
            start_date: Date de début au format YYYY-MM-DD
            maturity_date: Date de maturité au format YYYY-MM-DD
        """
        self.K = K
        self.type = opt_type
        self.style = style
        
        if T is not None:
            self.T = T
            self.start_date = None
            self.end_date = None
        
        elif start_date is not None and maturity_date is not None:
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            self.end_date = datetime.strptime(maturity_date, '%Y-%m-%d')
            self.T = (self.end_date - self.start_date).days / 365.0
        
        else:
            raise ValueError("Soit T, soit start_date et maturity_date doivent être fournis")


    
    def payoff(self, S: float) -> float:
        """
        Calcule le payoff au noeud final
        
        Args:
            S: Prix du sous-jacent au noeud final
        
        Returns:
            float: Payoff de l'option
        """
        if self.type == "call":
            return max(S - self.K, 0)
        elif self.type == "put":
            return max(self.K - S, 0)
        else:
            raise ValueError("Type d'option invalide : doit être 'call' ou 'put'")