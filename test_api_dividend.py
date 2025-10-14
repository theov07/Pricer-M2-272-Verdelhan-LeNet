#!/usr/bin/env python3
"""
Test rapide de l'API avec dividendes
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_with_dividend():
    """Test de l'API avec dividende"""
    print("🧪 Test de l'API avec dividende...")
    
    # Paramètres de test
    today = datetime.now()
    ex_div_date = today + timedelta(days=30)  # Dans 30 jours
    
    params = {
        'S0': 100,
        'K': 100,
        'T': 1.0,
        'r': 0.05,
        'sigma': 0.2,
        'N': 5,
        'option_type': 'call',
        'option_style': 'european',
        'dividend': 1.0,
        'ex_div_date': ex_div_date.strftime('%Y-%m-%d')
    }
    
    print(f"📊 Paramètres: {params}")
    
    try:
        response = requests.post('http://localhost:5001/api/calculate', json=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Prix trinomial: {data['trinomial_price']:.6f}€")
                print(f"✅ Prix Black-Scholes: {data['black_scholes_price']:.6f}€")
                print(f"✅ Différence: {data['difference']:.6f}€")
                return True
            else:
                print(f"❌ Erreur API: {data['error']}")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous qu'il est démarré.")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_api_with_dividend()