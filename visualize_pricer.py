import matplotlib.pyplot as plt
from Tree import Tree
from Market import Market
from Option import Option
from datetime import datetime

def visualize_tree(tree):
    nodes = []
    values = []

    def traverse(node):
        if node is None or node in nodes:
            return
        nodes.append(node)
        values.append(node.value)
        traverse(node.forward_up_neighbor)
        traverse(node.forward_mid_neighbor)
        traverse(node.forward_down_neighbor)

    traverse(tree.root)

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(values)), values, 'o-', label="Node Values")
    plt.xlabel("Node Index")
    plt.ylabel("Node Value")
    plt.title("Visualization of Tree Nodes")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    today = datetime(2025, 10, 1)
    maturity_date = datetime(2026, 10, 1)
    T = (maturity_date - today).days / 365.0

    market = Market(S0=100, rate=0.03, sigma=0.2)
    option = Option(T=T, K=10, opt_type="call", style="european")

    tree = Tree(market=market, option=option, N=10)
    tree.build_tree()

    visualize_tree(tree)