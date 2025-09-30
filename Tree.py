import math
import Node


class Tree:
    def __init__(self, market, option, N):
       
        self.N = N  # Nombre d'étapes dans l'arbre
        self.deltaT = option.T / N  # Durée de chaque étape
        self.delta = math.sqrt(3 * self.deltaT)  # Pas de l'arbre
        self.market = market
        self.option = option

    
    def build_tree(self):
        """
        Construit l'arbre trinomial en partant de la racine.
        """
        self.root = Node(self.market.S0, 0, self)

        trunc = self.root

        for _ in range(self.N, 1):
            trunc.create_forward_neighbors() 
            trunc.generate_upper_neighbors()
            trunc.generate_lower_neighbors()
            trunc = trunc.forward_mid_neighbor  

        self.last_trunc = trunc
        

    def compute_payoff(self):
        """
        Calcule le payoff pour chaque nœud de l'arbre.
        """
        trunc = self.last_trunc

        trunc.option_price = trunc.option.payoff(trunc.value)

        while trunc.backward_neighbor is not None:
            trunc = trunc.backward_neighbor
            trunc.option_price = trunc.option.payoff(trunc.value)
            lower = trunc.down_neighbor
            while lower is not None:
                lower.option_price = lower.option.payoff(lower.value)
                lower = lower.down_neighbor

            upper = trunc.up_neighbor
            while upper is not None:
                upper.option_price = upper.option.payoff(upper.value)
                upper = upper.up_neighbor

        return trunc
        

    def backpropagation(self):
        """
        Effectue la rétropropagation des prix des options à travers l'arbre.
        """
        last_trunc = self.last_trunc

        while last_trunc.backward_neighbor is not None:
            last_trunc = last_trunc.backward_neighbor
            last_trunc.price_option_at_node(self.market.r, self.delta)

            lower = last_trunc.down_neighbor
            while lower is not None:
                lower.price_option_at_node(self.market.r, self.delta)
                lower = lower.down_neighbor

            upper = last_trunc.up_neighbor
            while upper is not None:
                upper.price_option_at_node(self.market.r, self.delta)
                upper = upper.up_neighbor


    
    def calculate_option_price(self):
        """
        Calcule le prix de l'option en utilisant l'arbre construit.
        """
        self.compute_payoff()
        self.backpropagation()
        return self.root.option_price