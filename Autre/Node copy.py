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
        # Récupération de la valeur de alpha
        alpha = self.get_alpha()

        # Création du Forward Mid
        mid_value = self.value * math.exp(self.tree.market.rate * self.tree.deltaT) - self.tree.dividend_value(self.step + 1)
        self.forward_mid_neighbor = Node(mid_value, self.step + 1, self.tree)
        self.forward_mid_neighbor.backward_neighbor = self

        # Création du Forward Up
        up_value = self.forward_mid_neighbor.value * alpha
        self.forward_up_neighbor = Node(up_value, self.step + 1, self.tree)
        self.forward_mid_neighbor.up_neighbor = self.forward_up_neighbor
        self.forward_up_neighbor.down_neighbor = self.forward_mid_neighbor

        # Création du Forward Down
        down_value = self.forward_mid_neighbor.value / alpha
        self.forward_down_neighbor = Node(down_value, self.step + 1, self.tree)
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



    def compute_probabilities(self):
        """
        Calcule les probabilités associées aux nœuds voisins en avant.
        """
        # Récupération de alpha
        alpha = self.get_alpha()

        # Calcul de l'espérance et de la variance
        esperance = self.value * math.exp(self.tree.market.rate * self.tree.deltaT) - self.tree.dividend_value(self.step + 1)
        variance = self.value ** 2 * math.exp(2 * self.tree.market.rate * self.tree.deltaT) * (math.exp(self.tree.market.sigma ** 2 * self.tree.deltaT) - 1)

        # Vérification de l'existence du nœud central
        if not hasattr(self, "forward_mid_neighbor") or self.forward_mid_neighbor is None:
            raise ValueError("forward_mid_neighbor est manquant avant calcul des probabilités")

        mid_value = self.forward_mid_neighbor.value

        # Calcul des probabilités pour les voisins
        p_down = ((mid_value ** -2 * (variance + esperance ** 2) - 1 - (alpha + 1) * (esperance / mid_value - 1))
                / ((1 - alpha) * (alpha ** (-2) - 1)))
        p_up = (esperance / mid_value - 1 - (1 / alpha - 1) * p_down) / (alpha - 1)
        p_mid = 1 - p_up - p_down

        # Assignation aux attributs
        self.prob_forward_up_neighbor = p_up
        self.prob_forward_mid_neighbor = p_mid
        self.prob_forward_down_neighbor = p_down

        # Mise à jour des probabilités cumulées
        if not hasattr(self, "cum_prob"):
            self.cum_prob = 1.0

        if getattr(self, "forward_up_neighbor", None) is not None:
            self.forward_up_neighbor.cum_prob += self.cum_prob * self.prob_forward_up_neighbor

        if getattr(self, "forward_mid_neighbor", None) is not None:
            self.forward_mid_neighbor.cum_prob += self.cum_prob * self.prob_forward_mid_neighbor

        if getattr(self, "forward_down_neighbor", None) is not None:
            self.forward_down_neighbor.cum_prob += self.cum_prob * self.prob_forward_down_neighbor



    def calculate_option_price(self, r: float, deltaT: float):
        """
        Calcule le prix de l'option à ce nœud en fonction des prix des nœuds voisins en avant.
        """
        # Si c'est un nœud terminal (pas de voisins en avant), le prix est déjà défini (payoff)
        if (
            self.forward_up_neighbor is None
            and self.forward_mid_neighbor is None
            and self.forward_down_neighbor is None
        ):
            # Pour les nœuds terminaux, le prix est déjà défini par le payoff
            return

        # Facteur d'actualisation
        discount_factor = math.exp(-r * deltaT)

        # Cas du nœud monomialisé (seulement forward_mid_neighbor existe)
        if self.forward_up_neighbor is None and self.forward_down_neighbor is None:
            price = self.prob_forward_mid_neighbor * self.forward_mid_neighbor.option_price * discount_factor
        else:
            # Cas trinomial normal
            price = (
                self.prob_forward_up_neighbor * self.forward_up_neighbor.option_price
                + self.prob_forward_mid_neighbor * self.forward_mid_neighbor.option_price
                + self.prob_forward_down_neighbor * self.forward_down_neighbor.option_price
            ) * discount_factor

        # Si option américaine, comparer avec la valeur d’exercice immédiat
        if self.tree.option.style == "american":
            immediate_exercise_value = self.tree.option.payoff(self.value)
            price = max(price, immediate_exercise_value)
        
        else :
            # Enregistrement du prix de l’option dans ce nœud
            self.option_price = price


    
    
    def get_alpha(self):
        """
        Calcule et retourne le coefficient alpha pour ce nœud, en fonction de la volatilité du marché et du pas de temps deltaT.
        """
        if self.tree.deltaT is None:
            raise ValueError("deltaT n'est pas défini dans l'arbre.")

        alpha = math.exp(self.tree.market.sigma * math.sqrt(3 * self.tree.deltaT))
        return alpha


    def monomial(self):
        """
        Applique la monomialisation en supprimant les voisins up et down.
        """
        self.forward_down_neighbor = None
        self.forward_up_neighbor = None
        self.prob_forward_mid_neighbor = 1.0