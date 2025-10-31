from datetime import datetime

class Market:
    def __init__(self, S0: float, rate: float, sigma: float, dividend: float = 0.0, ex_div_date: datetime = None):
        """
        Initialise les paramètres du marché.
        
        args:
            S0 (float): Prix initial du sous-jacent.
            rate (float): Taux sans risque annuel.
            sigma (float): Volatilité annuelle du sous-jacent.
            dividend (float): Montant du dividende (par défaut 0.0).
            ex_div_date (datetime): Date d'ex-dividende (par défaut None).

        """
        self.S0 = S0           
        self.rate = rate         
        self.sigma = sigma        
        self.dividend = dividend
        self.ex_div_date = ex_div_date