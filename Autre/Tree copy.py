import math
from Node import Node
from Option import Option
import numpy as np

class Tree:

    def __init__(self, market, option, N):
        self.N = N                                  # Nombre d'étapes dans l'arbre
        self.market = market
        self.option = option
    

    def build_tree(self, factor: float = 1e-10, threshold: float = 1e-10):
        
        self.root = Node(self.market.S0, 0, self)
        self.threshold = threshold                        # Default threshold value for probability checks

        self.deltaT = float(self.option.T) / float(self.N)
        self.root.cum_prob = 1.0
        trunc = self.root

        if self.market.ex_div_date is not None:
            self.dividend_step = math.ceil((self.market.ex_div_date / self.option.T) * self.N) 
        else:
            self.dividend_step = None               # No dividend step if ex_div_date is not set

        for _ in range(0, self.N, 1):
            trunc.create_forward_neighbors()
            trunc.build_upper_neighbors()
            trunc.build_lower_neighbors()
            trunc = trunc.forward_mid_neighbor  

        self.last_trunc = trunc
        


    def compute_payoff(self):
        
        last_node = trunc = self.last_trunc
        trunc.option_price = trunc.tree.option.payoff(last_node.value)

        while last_node.down_neighbor is not None:
            last_node = last_node.down_neighbor
            last_node.option_price = last_node.tree.option.payoff(last_node.value)

        last_node = trunc

        while last_node.up_neighbor is not None:
            last_node = last_node.up_neighbor
            last_node.option_price = last_node.tree.option.payoff(last_node.value)
        
        return trunc



    def backpropagation(self):
        """
        Effectue la rétropropagation des prix des options à travers l'arbre.
        """
        last_trunc = self.last_trunc

        while last_trunc.backward_neighbor is not None:
            last_trunc = last_trunc.backward_neighbor
            last_trunc.price_option_at_node(self.market.rate, self.deltaT)

            lower = last_trunc.down_neighbor
            while lower is not None:
                lower.price_option_at_node(self.market.rate, self.deltaT)
                lower = lower.down_neighbor

            upper = last_trunc.up_neighbor
            while upper is not None:
                upper.price_option_at_node(self.market.rate, self.deltaT)
                upper = upper.up_neighbor


    
    def calculate_option_price(self):
        """
        Calcule le prix de l'option en utilisant l'arbre construit.
        """
        self.compute_payoff()
        self.backpropagation()
        print(f"calculate_option_price : Option price at root node: {self.root.option_price}")
        return self.root.option_price
    

    def dividend_value(self, step):
        """
        Calcule la valeur du dividende à une étape donnée.
        """
        if self.dividend_step == step:
            print("Dividend step reached")
            return self.market.dividend
        return 0.0

        