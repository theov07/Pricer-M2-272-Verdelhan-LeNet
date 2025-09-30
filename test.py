## trinomial tree class otion pricing
import math
from datetime import datetime
import Market
from Node import Node
from Option import Option
import Tree




   
today = datetime(2025, 9, 24)
maturity_date = datetime(2026, 9, 24)

T = (maturity_date - today).days / 365.0  

market = Market(S0=100, r=0.03, sigma=0.2)
tree = Tree(N=10, T=T, market=market)

option = Option(T=T, K=105, opt_type="call", style="european") 





if __name__ == "__main__":
    tree.build_tree()
    option_price = tree.price_option(option)
    print(f"Option Price: {option_price:.2f}")
