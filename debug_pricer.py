#!/usr/bin/env python3
"""
Debug Pricer - Outil de test et validation pour le pricer trinomial
Permet de tester différents cas et de comparer avec Black-Scholes
"""

from contextlib import redirect_stdout
from io import StringIO
from Market import Market
from Option import Option  
from Tree import Tree
import math
from datetime import datetime

def calculate_black_scholes(S, K, r, sigma, T):
    """Prix Black-Scholes pour une option call européenne"""
    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    
    from scipy.stats import norm
    call_price = S*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
    return call_price

def test_convergence():
    """Test de convergence avec différentes valeurs de N"""
    print("🧪 Test de convergence du trinomial vers Black-Scholes")
    print("=" * 60)
    
    S0 = 100.0    
    K = 102.0     
    r = 0.05      
    sigma = 0.2   
    T = 0.25      
    
    bs_price = calculate_black_scholes(S0, K, r, sigma, T)
    print(f"Prix Black-Scholes : {bs_price:.6f}")
    print()
    print("Convergence du trinomial vers Black-Scholes :")
    print("-" * 50)
    
    # Test pour différentes valeurs de N
    for N in [3, 5, 10, 20, 30, 50, 100]:
        try:
            market = Market(S0=S0, rate=r, sigma=sigma, dividend=0)
            option = Option(T=T, K=K)
            tree = Tree(market=market, option=option, N=N)
            
            # Suppression des éventuels prints de debug
            with redirect_stdout(StringIO()):
                tree.build_tree()
                trinomial_price = tree.calculate_option_price()
            
            error = abs(trinomial_price - bs_price) / bs_price * 100
            print(f"N={N:3d} : Prix={trinomial_price:.6f}, Erreur={error:5.2f}%")
            
        except Exception as e:
            print(f"N={N:3d} : ERREUR - {str(e)[:50]}")
    
    print()

def test_original_parameters():
    """Test avec les paramètres originaux du test.py"""
    print("🧪 Test avec les paramètres originaux")
    print("=" * 50)
    
    # Paramètres du test.py original
    today = datetime(2025, 9, 1)
    maturity_date = datetime(2026, 9, 1)
    T = (maturity_date - today).days / 365.0
    
    S0 = 100                # Prix initial 
    K = 102                 # Strike
    N = 400                 # Nombre d'étapes original
    r = 0.05                # Taux sans risque
    sigma = 0.3             # Volatilité
    
    print(f"Paramètres : S0={S0}, K={K}, r={r}, σ={sigma}, T={T:.4f}, N={N}")
    
    # Prix théorique Black-Scholes
    bs_price = calculate_black_scholes(S0, K, r, sigma, T)
    print(f"Prix Black-Scholes : {bs_price:.6f}")
    
    # Construction du modèle trinomial
    market = Market(S0=S0, rate=r, sigma=sigma, dividend=0)
    option = Option(T=T, K=K)
    tree = Tree(market=market, option=option, N=N)
    
    print("Calcul en cours... (peut prendre quelques secondes avec N=400)")
    
    try:
        # Suppression des éventuels prints de debug
        with redirect_stdout(StringIO()):
            tree.build_tree()
            trinomial_price = tree.calculate_option_price()
        
        error = abs(trinomial_price - bs_price) / bs_price * 100
        print(f"\nRésultats :")
        print(f"Prix trinomial N={N} : {trinomial_price:.6f}")
        print(f"Erreur relative : {error:.2f}%")
        
        if error < 1.0:
            print("✅ Excellente précision (<1%)")
        elif error < 5.0:
            print("✅ Bonne précision (<5%)")  
        else:
            print("⚠️ Précision à améliorer")
            
    except Exception as e:
        print(f"❌ Erreur avec N={N} : {e}")
        print("Cela peut être dû à des problèmes de précision numérique avec un N très élevé")
    
    print()



def test_simple_case():
    """Test simple avec N=10"""
    print("🧪 Test simple (N=10)")
    print("=" * 30)
    
    S0 = 100.0    
    K = 102.0     
    r = 0.05      
    sigma = 0.2   
    T = 0.25      
    N = 10
    
    bs_price = calculate_black_scholes(S0, K, r, sigma, T)
    print(f"Prix Black-Scholes : {bs_price:.6f}")
    
    market = Market(S0=S0, rate=r, sigma=sigma, dividend=0)
    option = Option(T=T, K=K)
    tree = Tree(market=market, option=option, N=N)
    
    # Suppression des éventuels prints de debug
    with redirect_stdout(StringIO()):
        tree.build_tree()
        trinomial_price = tree.calculate_option_price()
    
    error = abs(trinomial_price - bs_price) / bs_price * 100
    print(f"Prix trinomial N={N} : {trinomial_price:.6f}")
    print(f"Erreur relative : {error:.2f}%")
    print()

def main():
    """Menu principal"""
    print("🚀 DEBUG PRICER TRINOMIAL")
    print("=" * 60)
    print("1. Test simple (N=10)")
    print("2. Test de convergence (N=3 à 100)")
    print("3. Test paramètres originaux (N=400)")
    print("4. Tous les tests")
    print("=" * 60)
    
    choice = input("Choisissez un test (1-4) ou appuyez sur Entrée pour tous : ").strip()
    
    if choice == "1":
        test_simple_case()
    elif choice == "2":
        test_convergence()
    elif choice == "3":
        test_original_parameters()
    else:
        # Tous les tests par défaut
        test_simple_case()
        test_convergence()
        test_original_parameters()
        
    print("✅ Tests terminés !")

if __name__ == "__main__":
    main()