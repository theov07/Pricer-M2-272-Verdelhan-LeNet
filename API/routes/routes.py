from flask import Blueprint, request, jsonify
import sys
import os
import time
from API.visualization.tree_visualizer import TreeVisualizer
from Core.BlackScholes import BlackScholes
from Core.Greeks import Greeks
from Core.Option import Option
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
api_bp = Blueprint('api', __name__)


@api_bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    """Calculate option with provided parameters"""
    try:
        params = request.json
        
        # Validation des paramètres requis
        required_params = ['S0', 'K', 'start_date', 'maturity_date', 'r', 'sigma', 'N']
        optional_params = ['option_type', 'option_style', 'dividend', 'threshold', 'ex_div_date']
        
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
        threshold = params.get('threshold', 0.0)
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
        
        # Create option with dates (T will be calculated automatically)
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
            return jsonify({'success': False, 'error': 'Spot price S0 must be positive'}), 400
        if params['K'] <= 0:
            return jsonify({'success': False, 'error': 'Le strike K doit être positif'}), 400
        
        # Validation de la combinaison threshold/N pour avertir du pruning excessif
        warning_message = None
        if threshold > 0:
            if params['N'] > 100 and threshold > 0.05:
                warning_message = f'⚠️ Attention: N={params["N"]} avec threshold={threshold} peut être instable. Recommandé: threshold ≤ 0.05'
            elif params['N'] > 50 and threshold > 0.1:
                warning_message = f'⚠️ Attention: N={params["N"]} avec threshold={threshold} peut éliminer trop de nœuds. Recommandé: threshold ≤ 0.1'
            elif params['N'] > 20 and threshold > 0.2:
                warning_message = f'⚠️ Attention: N={params["N"]} avec threshold={threshold} peut être agressif. Recommandé: threshold ≤ 0.2'
        
        # Create visualizer and calculate with time measurement
        visualizer = TreeVisualizer()
        
        # Mesure du temps pour le modèle trinomial
        trinomial_start_time = time.time()
        data = visualizer.create_tree_data(
            S0=params['S0'],
            K=params['K'],
            T=T_calculated,  # Use T calculated from dates
            r=params['r'],
            sigma=params['sigma'],
            N=params['N'],
            option_type=option_type,
            option_style=option_style,
            dividend=dividend,
            threshold=threshold,
            ex_div_date=ex_div_date_obj
        )
        trinomial_end_time = time.time()
        trinomial_execution_time = trinomial_end_time - trinomial_start_time
        
        # Calculate Greeks using trinomial tree
        greeks_data = None
        try:
            from Core.Market import Market
            
            # Create market and option objects for Greeks calculation
            market = Market(
                S0=params['S0'],
                rate=params['r'],
                sigma=params['sigma'],
                dividend=dividend,
                ex_div_date=ex_div_date_obj
            )
            
            option = Option(
                K=params['K'],
                opt_type=option_type,
                style=option_style,
                T=T_calculated
            )
            
            # Calculate Greeks with smaller steps for faster computation
            greeks_calculator = Greeks(market, option, min(params['N'], 100))  # Limit N for Greeks
            greeks_data = greeks_calculator.calculate_all_greeks()
            print(f"Greeks calculated: {greeks_data}")
            
        except Exception as e:
            # In case of Greeks calculation error, continue without Greeks
            greeks_data = None
            print(f"Greeks calculation error: {e}")
            import traceback
            traceback.print_exc()
        
        # Black-Scholes calculation for comparison with time measurement
        try:
            # Mesure du temps pour Black-Scholes
            bs_start_time = time.time()
            bs_model = BlackScholes(
                S=params['S0'],
                K=params['K'],
                T=T_calculated,  # Use calculated T
                r=params['r'],
                sigma=params['sigma']
            )
            bs_price = bs_model.price(option_type)
            bs_end_time = time.time()
            bs_execution_time = bs_end_time - bs_start_time
            
            data['black_scholes_price'] = bs_price
            
            # Ajouter les temps d'exécution
            data['execution_times'] = {
                'trinomial_time': trinomial_execution_time,
                'blackscholes_time': bs_execution_time,
                'speed_ratio': trinomial_execution_time / bs_execution_time if bs_execution_time > 0 else 0
            }
            
            # Ajouter les grecques si demandées
            if params.get('include_greeks', False):
                data['greeks'] = bs_model.get_greeks(option_type)
                
        except Exception as e:
            # En cas d'erreur Black-Scholes, continuer sans
            data['black_scholes_price'] = None
            data['bs_error'] = str(e)
            data['execution_times'] = {
                'trinomial_time': trinomial_execution_time,
                'blackscholes_time': None,
                'speed_ratio': None
            }
        
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
            'data': data,
            'price': data["tree_params"]["final_price"],
            'greeks': greeks_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/tree', methods=['POST'])
def api_tree():
    """Get tree data only for visualization"""
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
        
        # Tree information
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
            'difference': trinomial_price - data.get('black_scholes_price', 0) if data.get('black_scholes_price') else None,
            'warning': warning_message
        })
        
    except Exception as e:
        print(f"Error in api_calculate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}'
        }), 500


@api_bp.route('/api/convergence', methods=['POST'])
def api_convergence():
    """Generate convergence analysis data"""
    try:
        params = request.json
        
        # Utiliser toujours la même progression jusqu'à 500
        steps = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500]
        
        print(f"📊 Analyse de convergence avec steps fixes: {steps}")
        
        # Import nécessaire
        from Core.Market import Market
        from Core.Tree import Tree
        from Core.Option import Option
        from Core.Greeks import Greeks
        import time
        
        results = []
        
        for N in steps:
            try:
                # Créer les objets avec N steps
                market = Market(
                    S0=params['S0'],
                    rate=params['r'],
                    sigma=params['sigma']
                )
                
                # Créer l'option avec les dates (comme dans l'API principale)
                option = Option(
                    K=params['K'],
                    opt_type=params.get('option_type', 'call'),
                    style=params.get('option_style', 'european'),
                    start_date=params['start_date'],
                    maturity_date=params['maturity_date']
                )
                
                tree = Tree(market, option, N)
                
                # Calculer le prix trinomial
                trinomial_price = tree.get_option_price()
                
                # Calculer Black-Scholes pour comparaison
                bs = BlackScholes(market.S0, option.K, option.T, market.rate, market.sigma)
                blackscholes_price = bs.call_price() if option.type == 'call' else bs.put_price()
                
                results.append({
                    'N': N,
                    'trinomial_price': trinomial_price,
                    'blackscholes_price': blackscholes_price
                })
                
            except Exception as e:
                print(f"Error for N={N}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        print(f"Error in api_convergence: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Convergence calculation error: {str(e)}'
        }), 500
