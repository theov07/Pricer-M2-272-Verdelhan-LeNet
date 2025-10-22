from Core.Market import Market
from Core.Option import Option
from Core.Tree import Tree
from datetime import datetime



def test_pricer():
    """
    Script de test simple pour le pricer trinomial
    Paramètres modifiables directement dans le code
    """
    print("=" * 60)
    print("🌳 PRICER TRINOMIAL - SCRIPT DE TEST")
    print("=" * 60)
    
    # ===========================================
    # PARAMÈTRES À MODIFIER ICI
    # ===========================================
    
    # Paramètres du marché
    S0 = 100.0              # Prix initial du sous-jacent
    rate = 0.05             # Taux sans risque (5%)
    sigma = 0.30            # Volatilité (30%)
    dividend = 3.0          # Dividende en euros
    
    
    K = 102.0               # Strike
    option_type = "call"    # "call" ou "put"
    style = "european"      # "european" ou "american"
    
    #(format YYYY-MM-DD)
    start_date = "2025-09-01"
    maturity_date = "2026-09-01"
    ex_div_date = "2026-04-21"      # Date ex-dividende
    
    # Paramètres du pricer
    N = 400                     # Nombre d'étapes
    threshold = 0.001           # Seuil de pruning (0.1%)
    
    # ===========================================
    
    print(f"📊 PARAMÈTRES:")
    print(f"   • S0 = {S0}€, K = {K}€")
    print(f"   • Type: {option_type.upper()}, Style: {style}")
    print(f"   • Taux: {rate*100:.1f}%, Volatilité: {sigma*100:.1f}%")
    print(f"   • Dividende: {dividend}€")
    print(f"   • Dates: {start_date} → {maturity_date}")
    print(f"   • Ex-dividende: {ex_div_date}")
    #print(f"   • N = {N}, Seuil = {threshold*100:.3f}%")
    print()
    
    ex_div_datetime = datetime.strptime(ex_div_date, '%Y-%m-%d')
    
    market = Market(
        S0=S0,
        rate=rate,
        sigma=sigma,
        dividend=dividend,
        ex_div_date=ex_div_datetime
    )
    
    option = Option(
        K=K,
        opt_type=option_type,
        style=style,
        start_date=start_date,
        maturity_date=maturity_date
    )
    
    print(f"⏰ Maturité calculée: T = {option.T:.6f} ans")
    print()
    
    # Créer et construire l'arbre
    print("🔄 Construction de l'arbre...")
    tree = Tree(market=market, option=option, N=N)
    
    # Calculer le prix
    price = tree.get_option_price()
    
    # Afficher les résultats
    print()
    print("=" * 60)
    print("📈 RÉSULTATS:")
    print("=" * 60)
    print(f"💰 Prix de l'option: {price:.6f}€")
    
    # Statistiques de l'arbre
    total_nodes = tree.get_node_count()
    theoretical_nodes = sum(range(1, N+2))  # Nombre théorique sans pruning
    reduction = (1 - total_nodes/theoretical_nodes) * 100 if theoretical_nodes > 0 else 0
    
    print(f"🌳 Nœuds dans l'arbre: {total_nodes:,}")
    print(f"📉 Réduction par pruning: {reduction:.1f}%")
    print("=" * 60)
    
    return price

def test_sans_dividende():
    """
    Test de comparaison sans dividende
    """
    print("\n🔄 Test de comparaison SANS dividende...")
    
    market = Market(S0=100.0, rate=0.05, sigma=0.30, dividend=0.0)
    option = Option(K=102.0, opt_type="call", start_date="2025-09-01", maturity_date="2026-09-01")
    tree = Tree(market=market, option=option, N=400)
    
    price_no_div = tree.get_option_price()
    print(f"💰 Prix SANS dividende: {price_no_div:.6f}€")
    
    return price_no_div

if __name__ == "__main__":
    try:
        # Test principal avec dividende
        price_with_div = test_pricer()
        
        # Test de comparaison sans dividende
        price_no_div = test_sans_dividende()
        
        # Comparaison
        diff = price_no_div - price_with_div
        print(f"\n📊 COMPARAISON:")
        print(f"   • Avec dividende:    {price_with_div:.6f}€")
        print(f"   • Sans dividende:    {price_no_div:.6f}€")
        print(f"   • Différence:        {diff:.6f}€")
        print(f"   • Impact dividende:  {(diff/price_no_div)*100:.2f}%")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()