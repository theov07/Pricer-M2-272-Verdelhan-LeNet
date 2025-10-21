import math
from Core.Node import Node
from Core.Option import Option
import numpy as np
from datetime import datetime

class Tree:

    def __init__(self, market, option, N, threshold=0.0):
        self.N = N                                  # Nombre d'étapes dans l'arbre
        self.market = market
        self.option = option
        self.threshold = threshold                  # Seuil de pruning par défaut
        self.nodes_by_step = []                     # Liste des nœuds par étape pour recombinaison
    


    def build_tree(self, threshold=0):
        
        trunc = self.root = Node(self.market.S0, 0, self)

        self.deltaT = float(self.option.T) / float(self.N)
        
        # Initialiser le registre des nœuds par étape
        self.nodes_by_step = [[] for _ in range(self.N + 1)]
        self.nodes_by_step[0] = [self.root]  # Étape 0 = racine
        
        self.root.cum_prob = 1.0
        self.threshold = threshold
        
        if self.market.ex_div_date is not None:
            normalization_div_date = (self.market.ex_div_date - datetime.today()).days / 365
            self.dividend_step = math.ceil((normalization_div_date / self.option.T) * self.N)
        
        else:
            self.dividend_step = None               # No dividend step if ex_div_date is not set
        
        # Construction étape par étape avec vraie recombinaison
        for step in range(self.N):
            self.build_next_step(step)
            
        self.last_trunc = self.nodes_by_step[-1][0] if self.nodes_by_step[-1] else None
    
    
    
    def find_node_by_value(self, target_value: float, step: int, tolerance: float = 1e-8):
        """
        Recherche un nœud existant avec une valeur donnée à une étape donnée.
        Utilise le registre nodes_by_step pour éviter les cycles.
        """
        if step >= len(self.nodes_by_step):
            return None
            
        for node in self.nodes_by_step[step]:
            if abs(node.value - target_value) < tolerance:
                return node
        return None



    def add_node_to_step(self, node, step):
        """
        Ajoute un nœud au registre de l'étape correspondante.
        """
        if step < len(self.nodes_by_step):
            if node not in self.nodes_by_step[step]:
                self.nodes_by_step[step].append(node)


    
    def build_next_step(self, current_step):
        """
        Construit tous les nœuds de l'étape suivante avec recombinaison et pruning.
        """
        next_step = current_step + 1
        next_nodes = []
        
        for node in self.nodes_by_step[current_step]:
            # Appliquer le pruning : ignorer les nœuds dont la probabilité cumulée est trop faible
            if hasattr(node, 'cum_prob') and node.cum_prob < self.threshold:
                continue  # Skip ce nœud (pruning)
                
            # Calculer les valeurs des 3 nœuds suivants
            alpha = node.get_alpha()
            
            mid_value = node.value * math.exp(self.market.rate * self.deltaT)
            up_value = mid_value * alpha
            down_value = mid_value / alpha
            
            # Créer ou réutiliser les nœuds
            up_node = self.find_or_create_node(up_value, next_step, next_nodes)
            mid_node = self.find_or_create_node(mid_value, next_step, next_nodes)
            down_node = self.find_or_create_node(down_value, next_step, next_nodes)
            
            # Connecter les nœuds
            node.forward_up_neighbor = up_node
            node.forward_mid_neighbor = mid_node
            node.forward_down_neighbor = down_node
            
            # Connexions backward
            if mid_node.backward_neighbor is None:
                mid_node.backward_neighbor = node
                
            # Connexions up/down
            mid_node.up_neighbor = up_node
            mid_node.down_neighbor = down_node
            up_node.down_neighbor = mid_node
            down_node.up_neighbor = mid_node
            
            # Calcul des probabilités AVANT d'appliquer le pruning final
            node.compute_probabilities()
        
        # Trier les nœuds par valeur décroissante
        next_nodes.sort(key=lambda n: n.value, reverse=True)
        self.nodes_by_step[next_step] = next_nodes

    

    def find_or_create_node(self, target_value, step, nodes_list, tolerance=1e-8):
        """
        Trouve un nœud existant avec la valeur donnée ou en crée un nouveau.
        """
        # Chercher dans les nœuds déjà créés pour cette étape
        for node in nodes_list:
            if abs(node.value - target_value) < tolerance:
                return node
                
        # Créer un nouveau nœud
        new_node = Node(target_value, step, self)
        nodes_list.append(new_node)
        return new_node

    

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
        # Backward induction depuis la dernière étape
        for step in range(self.N - 1, -1, -1):
            for node in self.nodes_by_step[step]:
                node.calculate_option_price(self.market.rate, self.deltaT)


    
    def calculate_option_price(self):
        """
        Calcule le prix de l'option en utilisant l'arbre construit.
        """
        self.compute_payoff()
        self.backpropagation()
        return self.root.option_price
    


    def apply_dividend_to_step(self, step):
        """
        Applique le dividende à tous les nœuds d'un step donné.
        Cette méthode est appelée APRÈS la recombinaison pour éviter de casser les connexions.
        """
        if step < len(self.nodes_by_step) and self.market.dividend is not None:
            for node in self.nodes_by_step[step]:
                node.value -= self.market.dividend

    

    def get_option_price(self, threshold=None):
        """
        Retourne le prix de l'option à ce nœud.
        """
        if threshold is None:
            threshold = self.threshold
        self.build_tree(threshold=threshold)
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