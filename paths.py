import networkx as nx



def k_shortest_paths(G, source, target, min_cost):
    """Find all shortest paths with same length 
    ignoring weights using Yen's algorithm.

    Args:
        G (networkx.Graph): Networkx graph.
        source (_type_): Source vertex.
        target (_type_): Destination vertex.
        min_cost (_type_): Expected cost of paths.

    Returns:
        List of paths: Paths with the same unweighted cost.
    """    
    generator = nx.shortest_simple_paths(G, source, target)
    equal_cost_paths = []
    
    for p in generator:

        if len(p)-1 == min_cost:
            equal_cost_paths.append(p)
        else:
            break

    return equal_cost_paths