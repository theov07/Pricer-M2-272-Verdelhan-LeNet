import matplotlib.pyplot as plt
from test import setup_pricer

from Tree import Tree
from Market import Market
from Option import Option


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
    
    S0, T, k, n, rate, sigma, opt_type, style, ex_div_date = setup_pricer()

    market = Market(S0=S0, rate=rate, sigma=sigma, ex_div_date=ex_div_date)
    option = Option(T=T, K=k, opt_type=opt_type, style=style)
    tree = Tree(market=market, option=option, N=n)

    tree.build_tree()
    visualize_tree(tree)