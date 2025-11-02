import math

class Node:

    def __init__(self, value, step, tree):
        """
        Initialise un nœud dans l'arbre trinomial.

        Args:
            value: La valeur du nœud.
            step: L'étape à laquelle se trouve le nœud.
            tree: L'arbre auquel appartient le nœud.
        """

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
    


    def get_id(self):
        """
        Génère un ID unique pour ce nœud basé sur l'étape et la valeur.
        """
        return f"node_{self.step}_{hash(str(round(self.value, 8)))}"



    def compute_probabilities(self):
        """
        Calcule les probabilités associées aux nœuds voisins en avant.
        """
        # Récupération de alpha
        alpha = self.get_alpha()

        # Calcul de l'espérance - forward price avec gestion correcte du dividende
        forward_value = self.value * math.exp(self.tree.market.rate * self.tree.deltaT)
        if self.tree.dividend_step == (self.step + 1):
            esperance = forward_value - self.tree.market.dividend
        else:
            esperance = forward_value
            
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
        
        # Alias pour le visualiseur
        self.prob_up = p_up
        self.prob_mid = p_mid
        self.prob_down = p_down

        # Mise à jour des probabilités cumulées vers les nœuds suivants
        if not hasattr(self, "cum_prob"):
            self.cum_prob = 1.0  # Par défaut pour la racine

        if getattr(self, "forward_up_neighbor", None) is not None:
            if not hasattr(self.forward_up_neighbor, "cum_prob"):
                self.forward_up_neighbor.cum_prob = 0.0
            self.forward_up_neighbor.cum_prob += self.cum_prob * self.prob_forward_up_neighbor

        if getattr(self, "forward_mid_neighbor", None) is not None:
            if not hasattr(self.forward_mid_neighbor, "cum_prob"):
                self.forward_mid_neighbor.cum_prob = 0.0
            self.forward_mid_neighbor.cum_prob += self.cum_prob * self.prob_forward_mid_neighbor

        if getattr(self, "forward_down_neighbor", None) is not None:
            if not hasattr(self.forward_down_neighbor, "cum_prob"):
                self.forward_down_neighbor.cum_prob = 0.0
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
            american_option_price = max(price, immediate_exercise_value)
            self.option_price = american_option_price

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