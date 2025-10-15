from flask import Blueprint, request, jsonify
import sys
import os
from API.visualization.tree_visualizer import TreeVisualizer
from Core.BlackScholes import BlackScholes
from Core.Option import Option
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
api_bp = Blueprint('api', __name__)


@api_bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    """Calculer l'option avec les paramètres fournis"""
    try:
        params = request.json
        
        # Validation des paramètres requis
        required_params = ['S0', 'K', 'start_date', 'maturity_date', 'r', 'sigma', 'N']
        optional_params = ['option_type', 'option_style', 'dividend', 'ex_div_date']
        
        # Vérifier les paramètres requis
        for param in required_params:
            if param not in params:
                return jsonify({
                    'success': False,
                    'error': f'Paramètre manquant: {param}'
                }), 400
        
        # Paramètres optionnels avec valeurs par défaut
        option_type = params.get('option_type', 'call')
        option_style = params.get('option_style', 'european')
        dividend = params.get('dividend', 0.0)
        ex_div_date = params.get('ex_div_date', None)
        
        # Validation des valeurs optionnelles
        if option_type not in ['call', 'put']:
            option_type = 'call'
        if option_style not in ['european', 'american']:
            option_style = 'european'
        
        # Conversion de la date ex-dividende
        ex_div_date_obj = None
        if ex_div_date:
            try:
                ex_div_date_obj = datetime.strptime(ex_div_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'error': 'Format de date ex-dividende invalide. Utilisez YYYY-MM-DD'}), 400
        
        # Création de l'option avec dates (T sera calculé automatiquement)
        try:
            option_obj = Option(
                K=params['K'],
                opt_type=option_type,
                style=option_style,
                start_date=params['start_date'],
                maturity_date=params['maturity_date']
            )
            T_calculated = option_obj.T
            
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        # Validation des autres valeurs
        if params['r'] < 0:
            return jsonify({'success': False, 'error': 'Le taux r doit être positif ou nul'}), 400
        if params['sigma'] <= 0:
            return jsonify({'success': False, 'error': 'La volatilité sigma doit être positive'}), 400
        if params['N'] <= 0:
            return jsonify({'success': False, 'error': 'Le nombre d\'étapes N doit être positif'}), 400
        if params['S0'] <= 0:
            return jsonify({'success': False, 'error': 'Le prix spot S0 doit être positif'}), 400
        if params['K'] <= 0:
            return jsonify({'success': False, 'error': 'Le strike K doit être positif'}), 400
        
        # Créer le visualiseur et calculer
        visualizer = TreeVisualizer()
        data = visualizer.create_tree_data(
            S0=params['S0'],
            K=params['K'],
            T=T_calculated,  # Utiliser le T calculé à partir des dates
            r=params['r'],
            sigma=params['sigma'],
            N=params['N'],
            option_type=option_type,
            option_style=option_style,
            dividend=dividend,
            ex_div_date=ex_div_date_obj
        )
        
        # Calcul Black-Scholes pour comparaison
        try:
            bs_model = BlackScholes(
                S=params['S0'],
                K=params['K'],
                T=T_calculated,  # Utiliser le T calculé
                r=params['r'],
                sigma=params['sigma']
            )
            bs_price = bs_model.price(option_type)
            data['black_scholes_price'] = bs_price
            
            # Ajouter les grecques si demandées
            if params.get('include_greeks', False):
                data['greeks'] = bs_model.get_greeks(option_type)
                
        except Exception as e:
            # En cas d'erreur Black-Scholes, continuer sans
            data['black_scholes_price'] = None
            data['bs_error'] = str(e)
        
        # Ajouter les informations de dates
        data['date_info'] = {
            'calculated_from_dates': True,
            'start_date': params['start_date'],
            'maturity_date': params['maturity_date'],
            'T_years': T_calculated,
            'T_days': round(T_calculated * 365)
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/tree', methods=['POST'])
def api_tree():
    """Obtenir uniquement les données de l'arbre pour visualisation"""
    try:
        params = request.json
        
        # Validation des paramètres requis
        required_params = ['S0', 'K', 'start_date', 'maturity_date', 'r', 'sigma', 'N']
        
        for param in required_params:
            if param not in params:
                return jsonify({
                    'success': False,
                    'error': f'Paramètre manquant: {param}'
                }), 400
        
        # Création de l'option pour obtenir T
        try:
            option_obj = Option(
                K=params['K'],
                start_date=params['start_date'],
                maturity_date=params['maturity_date']
            )
            T_calculated = option_obj.T
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
                
        except Exception as e:
            print(f"Erreur Black-Scholes: {e}")
            data['black_scholes_price'] = None
        
        trinomial_price = data["tree_params"]["final_price"]
        
        # Informations sur l'option
        data['option_info'] = {
            'type': option_type,
            'style': option_style
        }
        
        # Informations sur l'arbre
        data['tree_info'] = {
            'node_count': len(data['nodes']),
            'edge_count': len(data['edges']),
            'steps': params['N']
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'trinomial_price': trinomial_price,
            'black_scholes_price': data.get('black_scholes_price'),
            'difference': trinomial_price - data.get('black_scholes_price', 0) if data.get('black_scholes_price') else None
        })
        
    except Exception as e:
        print(f"Erreur dans api_calculate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erreur de calcul: {str(e)}'
        }), 500
