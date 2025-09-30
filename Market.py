## trinomial tree class otion pricing
import math
from datetime import datetime


class Market:
    
    def __init__(self, S0: float, r: float, sigma: float):
        self.S0 = S0            # prix initial du sous-jacent
        self.r = r              # taux sans risque
        self.sigma = sigma      # volatilité annuelle