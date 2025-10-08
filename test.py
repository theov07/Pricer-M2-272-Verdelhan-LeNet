from datetime import datetime
import matplotlib.pyplot as plt
from Market import Market
from Option import Option
from Tree import Tree

# Define the market and option parameters
today = datetime(2025, 10, 1)
maturity_date = datetime(2026, 10, 1)
T = (maturity_date - today).days / 365.0
print(f"T = {T}")

S0 = 100                # initial stock price
k = 80                  # strike price
n = 30                  # Number of steps in the tree

rate = 0.03             # taux sans risque
sigma = 0.2             # volatilité

opt_type = "call"       # "call" or "put"
style = "american"      # "european" or "american"


market = Market(S0=S0, rate=rate, sigma=sigma)

option = Option(T=T, K=k, opt_type=opt_type, style=style)

tree = Tree(market=market, option=option, N=n)



def test_pricer():
    tree.build_tree()
    option_price = tree.calculate_option_price()
    print(f"Option Price with K={option.K}: {option_price:.2f}")



if __name__ == "__main__":
    test_pricer()
