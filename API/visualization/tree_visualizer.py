import sys
import os
from Core.Market import Market
from Core.Option import Option
from Core.Tree import Tree


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TreeVisualizer:
    def __init__(self):
        pass
    
    def create_tree_data(self, S0, K, T, r, sigma, N, option_type='call', option_style='european', dividend=0.0, ex_div_date=None):
        print(f"Creation arbre: S0={S0}, K={K}, T={T}, r={r}, sigma={sigma}, N={N}, dividend={dividend}, ex_div_date={ex_div_date}")
        
        market = Market(S0=S0, rate=r, sigma=sigma, dividend=dividend, ex_div_date=ex_div_date)
        
        if option_type.lower() == 'call':
            option = Option(T=T, K=K, opt_type='call', style=option_style)
        else:
            option = Option(T=T, K=K, opt_type='put', style=option_style)
        
        tree = Tree(market=market, option=option, N=N)
        option_price = tree.get_option_price()
        
        nodes_data = []
        edges_data = []
        
        for step in range(N + 1):
            if step < len(tree.nodes_by_step):
                step_nodes = tree.nodes_by_step[step]
                
                for node in step_nodes:
                    node_data = {
                        'id': node.get_id(),
                        'step': step,
                        'value': node.value,
                        'option_value': node.option_price,
                        'payoff': getattr(node, 'payoff', 0)
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
        
        print(f"Donnees extraites: {len(nodes_data)} noeuds, {len(edges_data)} liens")
        
        return {
            'nodes': nodes_data,
            'edges': edges_data,
            'tree_params': tree_params
        }
