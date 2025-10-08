import math

class Node:

    def __init__(self, value, step, tree):
       
        self.value = value
        self.tree = tree
        self.step = step

        self.option_price = 0
        self.cum_prob = 0
        
        
        self.up_neighbor = None
        self.down_neighbor = None
        self.backward_neighbor = None
        
        self.forward_up_neighbor = None
        self.forward_mid_neighbor = None
        self.forward_down_neighbor = None
        
        self.prob_forward_up_neighbor = 0
        self.prob_forward_mid_neighbor = 0
        self.prob_forward_down_neighbor = 0



    
    
    def create_forward_neighbors(self):
        """
        Crée les nœuds voisins en avant (up, mid, down) à partir de ce nœud.
        """
        # Récupération de la valeur de deltaT et alpha pour ce step

        alpha = self.get_alpha()


        # Création du Forward Mid
        self.forward_mid_neighbor = Node(
            self.value * math.exp(self.tree.market.rate * self.tree.deltaT) - self.tree.dividend_value(self.step + 1),
            self.step + 1, self.tree
        )
        self.forward_mid_neighbor.backward_neighbor = self

       
       # Création du Forward Up
        self.forward_up_neighbor = Node(
            self.forward_mid_neighbor.value * alpha,
            self.step + 1, self.tree
        )
        self.forward_mid_neighbor.up_neighbor = self.forward_up_neighbor
        self.forward_up_neighbor.down_neighbor = self.forward_mid_neighbor
        
        
        # Création du Forward Down
        self.forward_down_neighbor = Node(
            self.forward_mid_neighbor.value / alpha,
            self.step + 1, self.tree
        )
        self.forward_mid_neighbor.down_neighbor = self.forward_down_neighbor
        self.forward_down_neighbor.up_neighbor = self.forward_mid_neighbor

        # Calcul des probabilités
        self.compute_probabilities()

        


    
    def build_upper_neighbors(self):
        """
        Construit les voisins supérieurs du nœud courant en suivant la logique du trinomial.
        """
        alpha = self.get_alpha()

        # On garde une référence au nœud de départ pour revenir à la fin
        trunc = self

        # On commence par le voisin forward up
        current_forward_up = self.forward_up_neighbor

        while self.up_neighbor is not None:
            # Création du nouveau voisin supérieur
            new_up_node = Node(current_forward_up.value * alpha, self.step + 1, self.tree)
            new_up_node.down_neighbor = current_forward_up

            # Calcul du mid supposé pour ce nouveau nœud
            expected_mid_value = self.up_neighbor.value * math.exp(self.tree.market.rate * self.tree.deltaT) - self.tree.dividend_value(self.step + 1)

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
        self = trunc




    def build_lower_neighbors(self):
        """
        Construit les voisins inférieurs du nœud courant en suivant la logique du trinomial.
        """
        alpha = self.get_alpha()

        # On garde une référence au nœud de départ pour revenir à la fin
        start_node = self

        # On commence par le voisin forward down
        current_forward_down = self.forward_down_neighbor

        while self.down_neighbor is not None:
            # Création du nouveau voisin inférieur
            new_down_node = Node(current_forward_down.value / alpha, self.step + 1, self.tree)
            new_down_node.up_neighbor = current_forward_down

            # Calcul du mid supposé pour ce nouveau nœud
            expected_mid_value = self.down_neighbor.value * math.exp(self.tree.market.rate * self.tree.deltaT) - self.tree.dividend_value(self.step + 1)

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
        alpha = self.get_alpha()

        esperance = math.exp(self.tree.market.rate * self.tree.deltaT)
        variance = (math.exp(self.tree.market.sigma ** 2 * self.tree.deltaT) - 1) * math.exp(2 * self.tree.market.rate * self.tree.deltaT)

        p_down = (self.forward_mid_neighbor.value ** (-2) * (variance + esperance ** 2) - 1 - (alpha + 1) * (esperance / self.forward_mid_neighbor.value - 1)) / ((1 - alpha) * (alpha ** (-2) - 1))
        p_up = (esperance / self.forward_mid_neighbor.value - 1 - (1 / alpha - 1) * p_down) / (alpha - 1)
        p_mid = 1 - p_up - p_down

        self.prob_forward_up_neighbor = p_up
        self.prob_forward_mid_neighbor = p_mid
        self.prob_forward_down_neighbor = p_down

        print(f"Probabilities at step {self.step}: Up={p_up}, Mid={p_mid}, Down={p_down}")

        if self.forward_up_neighbor is not None :
            self.forward_up_neighbor.cum_prob += self.cum_prob * self.prob_forward_up_neighbor
        
        if self.forward_mid_neighbor is not None :
            self.forward_mid_neighbor.cum_prob += self.cum_prob * self.prob_forward_mid_neighbor
        
        if self.forward_down_neighbor is not None :
            self.forward_down_neighbor.cum_prob += self.cum_prob * self.prob_forward_down_neighbor



    def compute_price(self):

        discount_factor = math.exp(-self.tree.market.rate * self.tree.deltaT)

        price = (self.prob_forward_up_neighbor * self.forward_up_neighbor.option_price +
                 self.prob_forward_mid_neighbor * self.forward_mid_neighbor.option_price +
                 self.prob_forward_down_neighbor * self.forward_down_neighbor.option_price) * discount_factor
        
        print (f"Price at node with value {self.value} and step {self.step} is {price}")

        return price
    


    def price_option_at_node(self, r: float, deltaT: float):
        """
        Calcule le prix de l'option à ce nœud en fonction des prix des nœuds voisins en avant.
        """
        if self.forward_up_neighbor is None or self.forward_mid_neighbor is None or self.forward_down_neighbor is None:
            raise ValueError("Les nœuds voisins en avant doivent être définis pour calculer le prix de l'option.")

        discount_factor = math.exp(-r * deltaT)

        price = (self.prob_forward_up_neighbor * self.forward_up_neighbor.option_price +
                 self.prob_forward_mid_neighbor * self.forward_mid_neighbor.option_price +
                 self.prob_forward_down_neighbor * self.forward_down_neighbor.option_price) * discount_factor

        # Pour les options américaines, on compare avec le payoff immédiat
        if self.tree.option.style == "american":
            immediate_exercise_value = self.tree.option.payoff(self.value)
            price = max(price, immediate_exercise_value)

        self.option_price = price

        print(f"Option price at node with value {self.value} and step {self.step} is {self.option_price}")



    
    def compute_cum_prob(self):
        if self.backward_neighbor is None:
            self.cum_prob = 1.0
        else:
            if self is self.backward_neighbor.forward_up_neighbor:
                self.cum_prob = self.backward_neighbor.cum_prob * self.backward_neighbor.prob_forward_up_neighbor
            elif self is self.backward_neighbor.forward_mid_neighbor:
                self.cum_prob = self.backward_neighbor.cum_prob * self.backward_neighbor.prob_forward_mid_neighbor
            elif self is self.backward_neighbor.forward_down_neighbor:
                self.cum_prob = self.backward_neighbor.cum_prob * self.backward_neighbor.prob_forward_down_neighbor
            else:
                raise ValueError("Le nœud courant n'est pas un voisin valide du nœud arrière.")

        # Propagation
        if self.up_neighbor is not None:
            self.up_neighbor.compute_cum_prob()
        if self.down_neighbor is not None:
            self.down_neighbor.compute_cum_prob()

        print(f"Cumulative probability at node with value {self.value} and step {self.step} is {self.cum_prob}")

    
    def get_alpha(self):
        """
        Retourne les valeurs de deltaT et alpha pour ce nœud.
        """
        if self.tree.deltaT is None:
            raise ValueError("deltaT n'est pas défini dans l'arbre.")

        alpha = math.exp(self.tree.market.sigma * math.sqrt(3 * self.tree.deltaT))
        print(f"deltaT = {self.tree.deltaT}, alpha = {alpha}")
        return alpha
