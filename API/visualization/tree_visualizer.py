import sys
import os
from Core.Market import Market
from Core.Option import Option
from Core.Tree import Tree


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TreeVisualizer:
    def __init__(self):
        pass
    
    def create_tree_data(self, S0, K, T, r, sigma, N, option_type='call', option_style='european', dividend=0.0, threshold=0.0, ex_div_date=None):
        print(f"Creation arbre: S0={S0}, K={K}, T={T}, r={r}, sigma={sigma}, N={N}, dividend={dividend}, threshold={threshold}, ex_div_date={ex_div_date}")
        
        market = Market(S0=S0, rate=r, sigma=sigma, dividend=dividend, ex_div_date=ex_div_date)
        
        if option_type.lower() == 'call':
            option = Option(T=T, K=K, opt_type='call', style=option_style)
        else:
            option = Option(T=T, K=K, opt_type='put', style=option_style)
        
        tree = Tree(market=market, option=option, N=N, threshold=threshold)
        original_threshold = threshold  # Garder le threshold original pour les statistiques
        fallback_used = False
        warning_message = None
        
        try:
            option_price = tree.get_option_price()
            
            if option_price is None:
                print(f"⚠️ AVERTISSEMENT: Pruning trop agressif avec threshold={threshold}, tentative de fallback avec threshold réduit")
                # Fallback: réduire le threshold automatiquement
                fallback_threshold = max(0.0, threshold * 0.5)
                tree_fallback = Tree(market=market, option=option, N=N, threshold=fallback_threshold)
                option_price = tree_fallback.get_option_price()
                tree = tree_fallback  # Utiliser l'arbre de fallback
                fallback_used = True
                warning_message = f"Pruning avec threshold={original_threshold:.1%} trop agressif, utilisé threshold={fallback_threshold:.1%}"
                print(f"✅ Fallback réussi avec threshold={fallback_threshold}")
            
        except AttributeError as e:
            if "'NoneType' object has no attribute 'tree'" in str(e):
                print(f"⚠️ AVERTISSEMENT: Pruning avec threshold={threshold} a échoué, utilisation du fallback sans pruning")
                # Fallback: arbre sans pruning
                tree_fallback = Tree(market=market, option=option, N=N, threshold=0.0)
                option_price = tree_fallback.get_option_price()
                tree = tree_fallback  # Utiliser l'arbre de fallback
                fallback_used = True
                warning_message = f"Pruning avec threshold={original_threshold:.1%} a échoué, utilisé threshold=0.0%"
                print(f"✅ Fallback réussi sans pruning (threshold=0.0)")
            else:
                raise e
        except Exception as e:
            print(f"⚠️ ERREUR: {str(e)}, tentative de fallback sans pruning")
            # Fallback: arbre sans pruning
            tree_fallback = Tree(market=market, option=option, N=N, threshold=0.0)
            option_price = tree_fallback.get_option_price()
            tree = tree_fallback  # Utiliser l'arbre de fallback
            fallback_used = True
            warning_message = f"Erreur avec threshold={original_threshold:.1%}, utilisé threshold=0.0%"
            print(f"✅ Fallback réussi sans pruning (threshold=0.0)")
        
        nodes_data = []
        edges_data = []
        
        for step in range(N + 1):
            if step < len(tree.nodes_by_step):
                step_nodes = tree.nodes_by_step[step]
                
                for node in step_nodes:
                    # Pour les nœuds finaux, option_price = payoff
                    # Pour les nœuds intermédiaires, option_price = prix calculé par rétropropagation
                    is_final_node = (step == N)
                    payoff_value = node.option_price if is_final_node else option.payoff(node.value)
                    
                    node_data = {
                        'id': node.get_id(),
                        'step': step,
                        'value': node.value,
                        'option_value': node.option_price,
                        'payoff': payoff_value
                    }
                    
                    # Ajouter les probabilités si disponibles
                    node_data['prob_up'] = getattr(node, 'prob_forward_up_neighbor', 0)
                    node_data['prob_mid'] = getattr(node, 'prob_forward_mid_neighbor', 0)
                    node_data['prob_down'] = getattr(node, 'prob_forward_down_neighbor', 0)
                    
                    nodes_data.append(node_data)
                    
                    # Créer les liens vers les noeuds suivants
                    if step < N:
                        if node.forward_up_neighbor:
                            edges_data.append({
                                'source': node.get_id(),
                                'target': node.forward_up_neighbor.get_id(),
                                'direction': 'up',
                                'probability': node.prob_forward_up_neighbor
                            })
                        
                        if node.forward_mid_neighbor:
                            edges_data.append({
                                'source': node.get_id(),
                                'target': node.forward_mid_neighbor.get_id(),
                                'direction': 'middle',
                                'probability': node.prob_forward_mid_neighbor
                            })
                        
                        if node.forward_down_neighbor:
                            edges_data.append({
                                'source': node.get_id(),
                                'target': node.forward_down_neighbor.get_id(),
                                'direction': 'down',
                                'probability': node.prob_forward_down_neighbor
                            })
        
        tree_params = {
            'S0': S0,
            'K': K,
            'T': T,
            'r': r,
            'sigma': sigma,
            'N': N,
            'final_price': option_price,
            'option_type': option_type,
            'option_style': option_style
        }
        
        # Calculer les statistiques de pruning avec le threshold original
        actual_nodes = len(nodes_data)
        theoretical_nodes = sum(2 * i + 1 for i in range(N + 1))
        
        # Si un fallback a été utilisé, calculer combien de nœuds auraient été ignorés avec le threshold original
        nodes_ignored_by_original_threshold = 0
        if fallback_used and original_threshold > 0:
            # Compter les nœuds qui auraient été ignorés avec le threshold original
            for step in range(N + 1):
                if step < len(tree.nodes_by_step):
                    for node in tree.nodes_by_step[step]:
                        if hasattr(node, 'cum_prob') and node.cum_prob < original_threshold:
                            nodes_ignored_by_original_threshold += 1
        
        print(f"Donnees extraites: {len(nodes_data)} noeuds, {len(edges_data)} liens")
        
        result = {
            'nodes': nodes_data,
            'edges': edges_data,
            'tree_params': tree_params
        }
        
        # Ajouter les informations de pruning et de fallback
        if fallback_used:
            result['fallback_used'] = True
            result['original_threshold'] = original_threshold
            result['warning_message'] = warning_message
            result['nodes_ignored_by_original_threshold'] = nodes_ignored_by_original_threshold
        
        return result
