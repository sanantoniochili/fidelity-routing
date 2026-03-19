import networkx as nx
import numpy as np
import os, math
import itertools

try:
    Tlen = os.get_terminal_size().columns
except OSError:
    Tlen = 80

import quantum
import paths

# cutoff fidelity 
min_fidelity = 0.8
np.random.seed(0)

# initialise graph
G = nx.Graph()
debug = False

SDpairs = {
    'simple': [
        ('source','r1'), ('source', 'r2'), 
        ('r1','r2'), ('r1','destination'), 
        ('r2', 'destination'), 
    ],
    'complex': [
        ('source','r1'), ('source','r3'), 
        ('r1','r2'), ('r1','r3'), 
        ('r2','r3'), ('r2','destination'), 
        ('r3','source'), ('r3','destination'),
    ]
}

def generate_allocations(budget, l, max_caps):
    """
    Generator that yields all valid ways to distribute exactly 'budget'
    purification pairs across 'l' edges, such that no edge exceeds its 
    specific max capacity (max_caps).

    Args:
        budget (int): Total extra pairs to distribute.
        l (int): Number of edges.
        max_caps (list): Maximum allowed pairs per edge (its physical capacity limit).
    """
    # Base cases
    if l == 1:
        if budget <= max_caps[0] - 1: # We already consume 1 pair fundamentally
            yield (budget,)
        return

    # Recursive distribution
    for val in range(min(budget, max_caps[0] - 1) + 1):
        for rest in generate_allocations(budget - val, l - 1, max_caps[1:]):
            yield (val,) + rest

def q_path_algorithm(G, source, target, F_th):
    """
    Iterative Routing Design for Single S-D Pair (Q-PATH)
    1. Find absolute minimum hop count H_min (cost base bound).
    2. Iteratively search through costs: H_min, H_min+1,...
    3. For a given expected_cost, find all paths with length L <= expected_cost.
    4. Distribute (expected_cost - L) purification budget across edges.
    5. Return first combination meeting F_th.
    """
    try:
        shortest_path = nx.shortest_path(G, source=source, target=target)
        H_min = len(shortest_path) - 1
    except nx.NetworkXNoPath:
        return None, None, None

    C_max = max(edge[2]['weight'] for edge in G.edges(data=True))
    max_possible_cost = len(G.edges()) * C_max

    for expected_cost in range(H_min, max_possible_cost + 1):
        # We need paths whose unweighted hop count is L <= expected_cost
        # because budget = expected_cost - L and budget cannot be negative.
        # k_shortest_paths from v1/v2 code was broken/simplistic, we use nx Yen
        
        # Generator for simple paths sorted by length (hops)
        # Weight=None treats all edge weights as 1 -> simple hop count
        path_generator = nx.shortest_simple_paths(G, source, target)
        
        for path in path_generator:
            L = len(path) - 1
            if L > expected_cost:
                # since generator is ordered by length, we can break if length exceeds expected_cost
                break 
                
            budget = expected_cost - L
            
            # Extract basic info for the path's edges
            edge_caps = [G[path[i]][path[i+1]]['weight'] for i in range(L)]
            initial_fs = [G[path[i]][path[i+1]]['fidelity'] for i in range(L)]
            
            # Attempt to allocate exactly 'budget' extra pairs 
            # Note: an allocation 'alloc' means 'alloc[i]' EXTRA pairs are consumed
            # on edge i. So total consumed on edge i is 1 + alloc[i].
            for alloc in generate_allocations(budget, L, edge_caps):
                
                path_fidelities = []
                for i in range(L):
                    pairs_consumed = 1 + alloc[i]
                    f_purified = quantum.get_purified_fidelity_for_budget(initial_fs[i], pairs_consumed)
                    path_fidelities.append(f_purified)
                    
                end_to_end_f = quantum.get_end_to_end_fidelity(path_fidelities)
                
                if end_to_end_f >= F_th:
                    # Found the absolute optimal!
                    final_allocations = [1 + a for a in alloc] # real cost vector
                    return path, final_allocations, expected_cost, end_to_end_f
                    
    return None, None, None, None


if __name__=="__main__":

    ''' INITIALISATION '''
    E_plain = SDpairs['simple']
    capacities = np.random.randint(low=5,high=10,size=len(E_plain))
    fidelities = np.random.uniform(low=0.5, high=1, size=len(E_plain))

    E_attributes = [
        (edge[0], edge[1], {'weight': weight, 'fidelity': fidelity}) \
            for (edge, weight, fidelity) in zip(E_plain,capacities,fidelities)
    ]

    G.add_edges_from(E_attributes)
    text = f' Initial Graph:'
    print(text+'-'*(Tlen-len(text)))
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']:.4f}")

    quantum.delete_edges(G, min_fidelity, debug=False)
    
    text = f' Graph after Edge Filtering:'
    print(text+'-'*(Tlen-len(text)))
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']:.4f}")


    ''' Q-PATH ROUTING '''
    print("\n" + "="*Tlen)
    print(" Running Q-PATH Algorithm (Iterative Cost)")
    print("="*Tlen)
    
    path, allocs, cost, final_f = q_path_algorithm(G, 'source', 'destination', min_fidelity)
    
    if path is None:
        print(" [Q-PATH] No valid paths found satisfying the fidelity constraint.")
    else:
        print(f" [Q-PATH] Optimal Path found: {' -> '.join(path)}")
        print(f" [Q-PATH] Total Entangled Pair Cost (minimum): {cost}")
        print(f" [Q-PATH] End-To-End Fidelity Achieved: {final_f:.4f}")
        print(f" [Q-PATH] Purification Capacity Allocation per edge:")
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            print(f"   -> Edge ({u},{v}): {allocs[i]} pairs consumed (Capacity allowed: {G[u][v]['weight']})")
