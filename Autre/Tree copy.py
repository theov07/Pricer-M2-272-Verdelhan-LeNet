import math
from Node import Node
from Option import Option
import numpy as np
from datetime import datetime

class Tree:

    def __init__(self, market, option, N):
        self.N = N                                  # Nombre d'étapes dans l'arbre
        self.market = market
        self.option = option
    

    def build_tree(self, threshold=0):
        
        trunc = self.root = Node(self.market.S0, 0, self)

        self.deltaT = float(self.option.T) / float(self.N)
        
        self.root.cum_prob = 1.0
        self.threshold = threshold

        
        if self.market.ex_div_date is not None:
            normalization_div_date = (self.market.ex_div_date - datetime.today()).days / 365
            self.dividend_step = math.ceil((normalization_div_date / self.option.T) * self.N)
        
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
            last_trunc.calculate_option_price(self.market.rate, self.deltaT)

            lower = last_trunc.down_neighbor
            while lower is not None:
                lower.calculate_option_price(self.market.rate, self.deltaT)
                lower = lower.down_neighbor

            upper = last_trunc.up_neighbor
            while upper is not None:
                upper.calculate_option_price(self.market.rate, self.deltaT)
                upper = upper.up_neighbor


    
    def calculate_option_price(self):
        """
        Calcule le prix de l'option en utilisant l'arbre construit.
        """
        self.compute_payoff()
        self.backpropagation()
        return self.root.option_price
    

    def dividend_value(self, step):
        """
        Calcule la valeur du dividende à une étape donnée.
        """
        # print(f"dividend_value called for step {step}")
        if self.dividend_step == step:
            # print("Dividend step reached")
            return self.market.dividend
        return 0.0

    

    def get_option_price(self, threshold=0):
        """
        Retourne le prix de l'option à ce nœud.
        """
        self.build_tree(threshold=threshold)
        print(f"yo: {self.calculate_option_price}")
        return self.calculate_option_price()
    

    def get_node_count(self):
        """
        Retourne le nombre total de nœuds dans l'arbre.
        """
        count = 0
        node = self.root
        while node is not None:
            count += 1
            down_node = node.down_neighbor
            while down_node is not None:
                count += 1
                down_node = down_node.down_neighbor
            node = node.forward_mid_neighbor
        return count