import math
from scipy.stats import norm

class BlackScholes:
    """
    Classe pour le calcul du prix d'options européennes selon le modèle Black-Scholes
    """
    
    def __init__(self, S, K, T, r, sigma):
        """
        Initialise les paramètres du modèle Black-Scholes
        
        Args:
            S (float): Prix spot du sous-jacent
            K (float): Prix d'exercice (strike)
            T (float): Temps jusqu'à l'échéance (en années)
            r (float): Taux sans risque
            sigma (float): Volatilité du sous-jacent
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        
        # Calcul des paramètres d1 et d2
        self._calculate_d_parameters()
    
    def _calculate_d_parameters(self):
        """Calcule les paramètres d1 et d2 utilisés dans les formules Black-Scholes"""
        if self.T <= 0:
            self.d1 = float('inf') if self.S > self.K else float('-inf')
            self.d2 = self.d1
        else:
            self.d1 = (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * math.sqrt(self.T))
            self.d2 = self.d1 - self.sigma * math.sqrt(self.T)
    
    def call_price(self):
        """
        Calcule le prix d'un call européen
        
        Returns:
            float: Prix du call européen
        """
        if self.T <= 0:
            return max(self.S - self.K, 0)
        
        call_price = self.S * norm.cdf(self.d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(self.d2)
        return call_price
    
    def put_price(self):
        """
        Calcule le prix d'un put européen
        
        Returns:
            float: Prix du put européen
        """
        if self.T <= 0:
            return max(self.K - self.S, 0)
        
        put_price = self.K * math.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S * norm.cdf(-self.d1)
        return put_price
    
    def price(self, option_type='call'):
        """
        Calcule le prix de l'option selon son type
        
        Args:
            option_type (str): Type d'option ('call' ou 'put')
            
        Returns:
            float: Prix de l'option
        """
        if option_type.lower() == 'call':
            return self.call_price()
        elif option_type.lower() == 'put':
            return self.put_price()
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")
    
    def delta(self, option_type='call'):
        """
        Calcule le delta de l'option (sensibilité au prix du sous-jacent)
        
        Args:
            option_type (str): Type d'option ('call' ou 'put')
            
        Returns:
            float: Delta de l'option
        """
        if self.T <= 0:
            if option_type.lower() == 'call':
                return 1.0 if self.S > self.K else 0.0
            else:
                return -1.0 if self.S < self.K else 0.0
        
        if option_type.lower() == 'call':
            return norm.cdf(self.d1)
        elif option_type.lower() == 'put':
            return norm.cdf(self.d1) - 1
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")
    
    def gamma(self):
        """
        Calcule le gamma de l'option (sensibilité du delta)
        
        Returns:
            float: Gamma de l'option
        """
        if self.T <= 0:
            return 0.0
        
        return norm.pdf(self.d1) / (self.S * self.sigma * math.sqrt(self.T))
    
    def theta(self, option_type='call'):
        """
        Calcule le theta de l'option (sensibilité au temps)
        
        Args:
            option_type (str): Type d'option ('call' ou 'put')
            
        Returns:
            float: Theta de l'option
        """
        if self.T <= 0:
            return 0.0
        
        first_term = -self.S * norm.pdf(self.d1) * self.sigma / (2 * math.sqrt(self.T))
        
        if option_type.lower() == 'call':
            second_term = -self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(self.d2)
            return first_term + second_term
        elif option_type.lower() == 'put':
            second_term = self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-self.d2)
            return first_term + second_term
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")
    
    def vega(self):
        """
        Calcule le vega de l'option (sensibilité à la volatilité)
        
        Returns:
            float: Vega de l'option
        """
        if self.T <= 0:
            return 0.0
        
        return self.S * norm.pdf(self.d1) * math.sqrt(self.T)
    
    def rho(self, option_type='call'):
        """
        Calcule le rho de l'option (sensibilité au taux sans risque)
        
        Args:
            option_type (str): Type d'option ('call' ou 'put')
            
        Returns:
            float: Rho de l'option
        """
        if self.T <= 0:
            return 0.0
        
        if option_type.lower() == 'call':
            return self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(self.d2)
        elif option_type.lower() == 'put':
            return -self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(-self.d2)
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")
    
    def get_greeks(self, option_type='call'):
        """
        Retourne toutes les grecques de l'option
        
        Args:
            option_type (str): Type d'option ('call' ou 'put')
            
        Returns:
            dict: Dictionnaire contenant toutes les grecques
        """
        return {
            'delta': self.delta(option_type),
            'gamma': self.gamma(),
            'theta': self.theta(option_type),
            'vega': self.vega(),
            'rho': self.rho(option_type)
        }