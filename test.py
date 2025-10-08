from datetime import datetime
from Market import Market
from Option import Option
from Tree import Tree

## 11.9368

def setup_pricer():
    
    today = datetime(2025, 9, 1)
    maturity_date = datetime(2026, 9, 1)
    T = (maturity_date - today).days / 365.0
    print(f"T = {T}")

    S0 = 100                # initial stock price
    k = 102                  # strike price
    n = 400                   # Number of steps in the tree

    rate = 0.05             # taux sans risque
    sigma = 0.3             # volatilité

    opt_type = "call"       # "call" or "put"
    style = "american"      # "european" or "american"

    ex_div_date = datetime(2026, 4, 21)     # Ex-dividend date

    return S0, T, k, n, rate, sigma, opt_type, style, ex_div_date





S0, T, k, n, rate, sigma, opt_type, style, ex_div_date = setup_pricer()
market = Market(S0=S0, rate=rate, sigma=sigma, ex_div_date=ex_div_date)
option = Option(T=T, K=k, opt_type=opt_type, style=style)
tree = Tree(market=market, option=option, N=n)



def test_pricer():
    tree.build_tree()
    option_price = tree.calculate_option_price()
    
    print(f"Option Price with K={option.K}: {option_price:.2f}")


if __name__ == "__main__":
    test_pricer()
