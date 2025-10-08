from datetime import datetime
class Market:
    def __init__(self, S0: float, rate: float, sigma: float, dividend: float = 0.0, ex_div_date: datetime = None):
        
        self.S0 = S0                        # prix initial du sous-jacent
        self.rate = rate                    # taux sans risque
        self.sigma = sigma                  # volatilité annuelle
        self.dividend = dividend            # dividende
        self.ex_div_date = ex_div_date      # date d'ex-dividende