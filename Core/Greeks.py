from Core.Tree import Tree
from Core.Market import Market
from Core.Option import Option


class CalculateDerivatives:
    
    def __init__(self, function_to_derivate):
        """
        Initialise avec la fonction dont on veut calculer les dérivées.
        
        Args:
            function_to_derivate (callable): La fonction dont on veut calculer les dériv
        """
        self.func = function_to_derivate
        
    

    def calculate_first_derivative(self, point, h=1e-5):
        """
        Calcule la première dérivée de la fonction au point donné en utilisant la différence centrale.

        Args:
            point (float): Le point où calculer la dérivée.
            h (float): La petite perturbation utilisée pour la différence centrale.
        
        Returns:
            float: La valeur de la première dérivée au point donné.
        """
        return (self.func(point + h) - self.func(point - h)) / (2 * h)


    
    def calculate_second_derivative(self, point, h=1e-5):
        """
        Calcule la deuxième dérivée de la fonction au point donné en utilisant la différence centrale.
        
        Args:
            point (float): Le point où calculer la dérivée.
            h (float): La petite perturbation utilisée pour la différence centrale.
        
        Returns:
            float: La valeur de la deuxième dérivée au point donné.
        """
        return (self.func(point + h) - 2 * self.func(point) + self.func(point - h)) / (h ** 2)




class Greeks:

    def __init__(self, market: Market, option: Option, N: int):
        """
        Initialise la classe Greeks avec le marché, l'option et le nombre de pas N.
        
        Args:
            market (Market): Le marché contenant les paramètres financiers.
            option (Option): L'option pour laquelle calculer les Greeks.
            N (int): Le nombre de pas dans l'arbre binaire.
        """
        self.market = market
        self.option = option
        self.N = N



    def compute_option_price_from_asset_price(self, S):
        """
        Calcule le prix de l'option pour un prix d'actif sous-jacent donné S.

        Args:
            S (float): Le prix de l'actif sous-jacent.
        
        Returns:
            float: Le prix de l'option pour le prix d'actif donné.
        """
        # Créer un nouveau marché avec le prix modifié
        temp_market = Market(S0=S, sigma=self.market.sigma, rate=self.market.rate)
        model_tree = Tree(temp_market, self.option, self.N)
        return model_tree.get_option_price()



    def compute_option_price_from_volatility(self, sigma):
        """
        Calcule le prix de l'option pour une volatilité donnée sigma.

        Args:
            sigma (float): La volatilité.
        
        Returns:
            float: Le prix de l'option pour la volatilité donnée.
        """
        # Créer un nouveau marché avec la volatilité modifiée
        temp_market = Market(S0=self.market.S0, sigma=sigma, rate=self.market.rate)
        model_tree = Tree(temp_market, self.option, self.N)
        return model_tree.get_option_price()



    def compute_option_price_from_rate(self, rate):
        """
        Calcule le prix de l'option pour un taux d'intérêt donné rate.
        
        Args:
            rate (float): Le taux d'intérêt.
        
        Returns:
            float: Le prix de l'option pour le taux d'intérêt donné.
        """

        temp_market = Market(S0=self.market.S0, sigma=self.market.sigma, rate=rate)
        model_tree = Tree(temp_market, self.option, self.N)
        return model_tree.get_option_price()



    def compute_option_price_from_time(self, T):
        """
        Calcule le prix de l'option pour un temps à maturité donné T.
        
        Args:
            T (float): Le temps à maturité.
        
        Returns:
            float: Le prix de l'option pour le temps à maturité donné.
        """

        temp_option = Option(K=self.option.K, T=T, opt_type=self.option.type)
        model_tree = Tree(self.market, temp_option, self.N)
        return model_tree.get_option_price()
    


    def compute_delta(self):
        """
        Calcule Delta en utilisant la différence centrale.

        Returns:
            float: La valeur de Delta.
        """

        calc_deriv = CalculateDerivatives(self.compute_option_price_from_asset_price)
        # Perturbation de 0.001€ sur le spot
        delta = calc_deriv.calculate_first_derivative(self.market.S0, h=0.001)
        return delta



    def compute_gamma(self):
        """
        Calcule Gamma en utilisant la différence centrale avec perturbation optimisée.

        Returns:
            float: La valeur de Gamma.
        """
        
        h = 3.1 # Perturbation optimisée pour un bon compromis précision/instabilité numérique
        
        price_up = self.compute_option_price_from_asset_price(self.market.S0 + h)
        price_down = self.compute_option_price_from_asset_price(self.market.S0 - h)
        price_base = self.compute_option_price_from_asset_price(self.market.S0)
        
        # Formule de dérivée seconde centrale: f''(x) ≈ [f(x+h) - 2f(x) + f(x-h)] / h²
        gamma = (price_up - 2 * price_base + price_down) / (h ** 2)

        return gamma



    def compute_theta(self):
        """
        Calcule Theta en utilisant la différence centrale.

        Returns:
            float: La valeur de Theta par jour.
        """
        calc_deriv = CalculateDerivatives(self.compute_option_price_from_time)
        # Perturbation d'un jour et theta par jour
        theta_per_year = -calc_deriv.calculate_first_derivative(self.option.T, h=1/365)
        # Convertir en theta par jour
        theta_per_day = theta_per_year / 365
        return theta_per_day



    def compute_vega(self):
        """
        Calcule Vega en utilisant la différence centrale.
        
        Returns:
            float: La valeur de Vega pour 1% de volatilité.
        """
        calc_deriv = CalculateDerivatives(self.compute_option_price_from_volatility)
        # Perturbation de 1% de volatilité (0.01) et vega pour 1% de vol
        vega = calc_deriv.calculate_first_derivative(self.market.sigma, h=0.01) / 100
        return vega



    def compute_rho(self):
        """
        Calcule Rho en utilisant la différence centrale.

        Returns:
            float: La valeur de Rho pour 1% de taux d'intérêt.
        """
        calc_deriv = CalculateDerivatives(self.compute_option_price_from_rate)
        # Perturbation de 1% de taux (0.01) et rho pour 1% de taux
        rho = calc_deriv.calculate_first_derivative(self.market.rate, h=0.01) / 100
        return rho



    def calculate_all_greeks(self):
        """
        Calcule tous les Greeks et retourne un dictionnaire.

        Returns:
            dict: Un dictionnaire contenant Delta, Gamma, Theta, Vega, Rho et le prix de l'option de base.
        """
        base_tree = Tree(self.market, self.option, self.N)
        base_price = base_tree.get_option_price()
        
        greeks = {
            'delta': self.compute_delta(),
            'gamma': self.compute_gamma(),
            'theta': self.compute_theta(),
            'vega': self.compute_vega(),
            'rho': self.compute_rho(),
            'base_price': base_price
        }
        return greeks