import math

class Node:

    
    def __init__(self, value, step, tree):
       

        self.value = value
        self.step = step
        self.tree = tree
        self.option_price = None
        self.cum_prob = 0.0
        
        self.up_neighbor = None
        self.down_neighbor = None
        self.backward_neighbor = None
        
        self.forward_up_neighbor = None
        self.forward_mid_neighbor = None
        self.forward_down_neighbor = None
        
        self.prob_forward_up_neighbor = 0.0
        self.prob_forward_mid_neighbor = 0.0
        self.prob_forward_down_neighbor = 0.0



    
    
    def create_forward_neighbors(self):
        """
        Crée les nœuds voisins en avant (up, mid, down) à partir de ce nœud.
        """
        # Récupération de la valeur de deltaT et alpha pour ce step
        
        deltaT = self.tree.deltaT
        k = self.tree.k
        alpha = math.exp(self.tree.market.sigma * k * math.sqrt(deltaT))


        # Création du Forward Mid
        self.forward_mid_neighbor = Node(
            self.value * math.exp(self.tree.market.rate * deltaT) - self.tree.dividend_value(self.step + 1),
            self.step + 1, self.tree
        )
        self.forward_mid_neighbor.backward_neighbor = self

        # Création du Forward Up
        self.forward_up_neighbor = Node(self.forward_mid_neighbor.value * alpha, self.step + 1, self.tree)
        self.forward_mid_neighbor.up_neighbor = self.forward_up_neighbor
        self.forward_up_neighbor.down_neighbor = self.forward_mid_neighbor
        
        # Création du Forward Down
        self.forward_down_neighbor = Node(self.forward_mid_neighbor.value / alpha, self.step + 1, self.tree)
        self.forward_mid_neighbor.down_neighbor = self.forward_down_neighbor
        self.forward_down_neighbor.up_neighbor = self.forward_mid_neighbor

        # Calcul des probabilités
        self.compute_probabilities()




    
    def build_upper_neighbors(self):
        """
        Construit les voisins supérieurs du nœud courant en suivant la logique du trinomial.
        """
        deltaT = self.tree.deltaT
        alpha = math.exp(self.tree.market.sigma * self.tree.k * math.sqrt(deltaT))

        # On garde une référence au nœud de départ pour revenir à la fin
        start_node = self

        # On commence par le voisin forward up
        current_forward_up = self.forward_up_neighbor

        while self.up_neighbor is not None:
            # Création du nouveau voisin supérieur
            new_up_node = Node(current_forward_up.value * alpha, self.step + 1, self.tree)
            new_up_node.down_neighbor = current_forward_up

            # Calcul du mid supposé pour ce nouveau nœud
            expected_mid_value = self.up_neighbor.value * math.exp(self.tree.market.rate * deltaT) - self.tree.dividend_value(self.step + 1)

            # Définition des bornes pour vérifier la cohérence
            upper_limit = current_forward_up.value * (1 + alpha) / 2
            lower_limit = current_forward_up.value * (1 + 1 / alpha) / 2

            # Si la valeur du mid est dans les bornes, on connecte les voisins
            if lower_limit < expected_mid_value < upper_limit:
                self.up_neighbor.forward_up_neighbor = new_up_node
                self.up_neighbor.forward_mid_neighbor = current_forward_up
                self.up_neighbor.forward_down_neighbor = current_forward_up.down_neighbor

                # Calcul des probabilités pour ce nœud
                self.up_neighbor.compute_probabilities()

                # Si la probabilité cumulée est faible et qu'il n'y a pas encore de voisin supérieur, on applique la monomialisation
                if self.up_neighbor.forward_up_neighbor.cum_prob < self.tree.threshold and self.up_neighbor.up_neighbor is None:
                    self.up_neighbor.monomial()
                    new_up_node = None  # On coupe la branche

                # On avance dans l'arbre
                self = self.up_neighbor

            # On continue à monter
            current_forward_up = new_up_node

        # On revient au nœud de départ
        self = start_node




    def build_lower_neighbors(self):
        """
        Construit les voisins inférieurs du nœud courant en suivant la logique du trinomial.
        """
        deltaT = self.tree.deltaT
        alpha = math.exp(self.tree.market.sigma * self.tree.k * math.sqrt(deltaT))

        # On garde une référence au nœud de départ pour revenir à la fin
        start_node = self

        # On commence par le voisin forward down
        current_forward_down = self.forward_down_neighbor

        while self.down_neighbor is not None:
            # Création du nouveau voisin inférieur
            new_down_node = Node(current_forward_down.value / alpha, self.step + 1, self.tree)
            new_down_node.up_neighbor = current_forward_down

            # Calcul du mid supposé pour ce nouveau nœud
            expected_mid_value = self.down_neighbor.value * math.exp(self.tree.market.rate * deltaT) - self.tree.dividend_value(self.step + 1)

            # Définition des bornes pour vérifier la cohérence
            upper_limit = current_forward_down.value * (1 + alpha) / 2
            lower_limit = current_forward_down.value * (1 + 1 / alpha) / 2

            # Si la valeur du mid est dans les bornes, on connecte les voisins
            if lower_limit < expected_mid_value < upper_limit:
                self.down_neighbor.forward_up_neighbor = current_forward_down.up_neighbor
                self.down_neighbor.forward_mid_neighbor = current_forward_down
                self.down_neighbor.forward_down_neighbor = new_down_node

                # Calcul des probabilités pour ce nœud
                self.down_neighbor.compute_probabilities()

                # Si la probabilité cumulée est faible et qu'il n'y a pas encore de voisin inférieur, on applique la monomialisation
                if self.down_neighbor.forward_down_neighbor.cum_prob < self.tree.threshold and self.down_neighbor.down_neighbor is None:
                    self.down_neighbor.monomial()
                    new_down_node = None  # On coupe la branche

                # On avance dans l'arbre
                self = self.down_neighbor

            # On continue à descendre
            current_forward_down = new_down_node

        # On revient au nœud de départ
        self = start_node



    def monomial(self):
        """
        Applique la monomialisation en supprimant les voisins up et down.
        """
        self.forward_down_neighbor = None
        self.forward_up_neighbor = None
        self.prob_forward_mid_neighbor = 1.0




    def compute_probabilities(self):
        """
        Calcule les probabilités associées aux nœuds voisins en avant.
        """
        deltaT = self.tree.deltaT
        alpha = math.exp(self.tree.market.sigma * self.tree.k * math.sqrt(deltaT))

        esperance = math.exp(self.tree.market.rate * deltaT)
        variance = (math.exp(self.tree.market.sigma ** 2 * deltaT) - 1) * math.exp(2 * self.tree.market.rate * deltaT)

        p_down = (self.forward_mid_neighbor.value ** (-2) * (variance + esperance ** 2) - 1 - (alpha + 1) * (esperance / self.forward_mid_neighbor.value - 1)) / ((1 - alpha) * (alpha ** (-2) - 1))
        p_up = (esperance / self.forward_mid_neighbor.value - 1 - (1 / alpha - 1) * p_down) / (alpha - 1)
        p_mid = 1 - p_up - p_down

        self.prob_forward_up_neighbor = p_up
        self.prob_forward_mid_neighbor = p_mid
        self.prob_forward_down_neighbor = p_down





    def compute_price(self):

        discount_factor = math.exp(-self.tree.market.rate * self.tree.deltaT)

        price = (self.prob_forward_up_neighbor * self.forward_up_neighbor.option_price +
                 self.prob_forward_mid_neighbor * self.forward_mid_neighbor.option_price +
                 self.prob_forward_down_neighbor * self.forward_down_neighbor.option_price) * discount_factor

        return price
    