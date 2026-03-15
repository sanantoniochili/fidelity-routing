import networkx as nx
import numpy as np
import os, math

try:
    Tlen = os.get_terminal_size().columns
except OSError:
    Tlen = 80

import quantum

# cutoff fidelity (global threshold)
min_fidelity = 0.8
# randomly initialize the RNG from some platform-dependent source of entropy
np.random.seed(0)

# initialise graph
G = nx.Graph()
# flag for debugging
debug = True

# MODEL TOGGLES
CONFIG = {
    'purification': 'bbpssw',   # 'bbpssw' (Paper), 'isotropic' (Repo)
    'fidelity_e2e': 'swapping', # 'swapping' (Paper), 'product' (Repo)
    'use_probs': True            # Note: Q-LEAP cost is fixed, but tput can scale
}

SDpairs = {
    ### simple example with S-D and two repeaters ###
    'simple': [
        ('source','r1'), ('source', 'r2'), 
        ('r1','r2'), ('r1','destination'), 
        ('r2', 'destination'), 
    ],

    ### more complex example with S-D and 3 repeaters ###
    'complex': [
        ('source','r1'), ('source','r3'), 
        ('r1','r2'), ('r1','r3'), 
        ('r2','r3'), ('r2','destination'), 
        ('r3','source'), ('r3','destination'),
    ]
}


def q_leap_metrics(G, source, target, F_th):
    """
    Implements the Q-LEAP pathfinding logic.
    1. Find path with max intrinsic end-to-end fidelity (Extended Dijkstra via NetworkX).
    2. Check if path can meet F_th using average-based purification decision.
    """
    # 1. Best Quality Path Searching (Extended Dijkstra)
    # The paper uses multiplicative metric F_end = 1/4 + 3/4 * prod_i (4*F_i - 1)/3
    # Our goal is to maximize F_end, which is equivalent to maximizing prod_i (4*F_i - 1)/3.
    # To use additive Dijkstra, we minimize sum of -log( (4*F_i-1)/3 ).
    
    def fidelity_weight(u, v, d):
        f = d.get('fidelity', 1.0)
        # Switch weight based on e2e model
        if CONFIG['fidelity_e2e'] == 'product':
            # Maximize product(F) -> Minimize sum(-log(F))
            if f <= 0: return float('inf')
            return -math.log10(f)
        else:
            # Maximize swapping formula -> Minimize sum(-log((4F-1)/3))
            val = (4.0 * f - 1.0) / 3.0
            if val <= 0: return float('inf')
            return -math.log10(val)
        
    try:
        # Use networkx dijkstra with our custom weight function
        path = nx.dijkstra_path(G, source, target, weight=fidelity_weight)
    except nx.NetworkXNoPath:
        return None, None, None

    # Length of routing path (number of hops/edges)
    l = len(path) - 1 
    
    # 2. Purification Decision
    # Average required fidelity per hop
    F_avg = math.pow(F_th, 1.0/l)
    
    total_cost = 0
    bottleneck_edges = []
    
    # Check if this path can be established with available capacities
    for i in range(l):
        u = path[i]
        v = path[i+1]
        edge_data = G[u][v]
        
        initial_f = edge_data['fidelity']
        capacity = edge_data['weight']
        
    # Calculate final success probability
    p_succ = 1.0
    for i in range(l):
        f_init = G[path[i]][path[i+1]]['fidelity']
        f_pure = quantum.get_purified_fidelity_for_budget(f_init, quantum.get_required_purification(f_init, F_avg, model=CONFIG['purification']), model=CONFIG['purification'])
        p_succ *= quantum.get_purification_success_prob(f_pure, model=CONFIG['purification'])
        
    return path, True, (total_cost, p_succ)


if __name__=="__main__":

    ''' INITIALISATION '''
    # We use 'simple' topology
    E_plain = SDpairs['simple']
    capacities = np.random.randint(low=5,high=10,size=len(E_plain))
    fidelities = np.random.uniform(low=0.5, high=1, size=len(E_plain))

    # assign capacities and fidelities
    E_attributes = [
        (edge[0], edge[1], {'weight': weight, 'fidelity': fidelity}) \
            for (edge, weight, fidelity) in zip(E_plain,capacities,fidelities)
    ]

    # create graph
    G.add_edges_from(E_attributes)
    text = f' Initial Graph:'
    print(text+'-'*(Tlen-len(text)))
    print(f" {'Edge':<22}{'Capacity':<12}{'Fidelity'}")
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']:.4f}")

    # Remove completely illegitimate edges (cannot reach min_fidelity even with all pairs)
    # The paper also suggests doing this preliminary filtering for complexity reduction
    quantum.delete_edges(G, min_fidelity, debug=False)
    
    text = f' Graph after Edge Filtering:'
    print(text+'-'*(Tlen-len(text)))
    print(f" {'Edge':<22}{'Capacity':<12}{'Fidelity'}")
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']:.4f}")


    ''' Q-LEAP ROUTING '''
    print("\n" + "="*Tlen)
    print(" Running Q-LEAP Algorithm")
    print("="*Tlen)
    
    path, success, info = q_leap_metrics(G, 'source', 'destination', min_fidelity)
    
    if path is None:
        print(" [Q-LEAP] No path exists between source and destination.")
    else:
        print(f" [Q-LEAP] Best Quality Path found: {' -> '.join(path)}")
        l = len(path) - 1
        F_avg = math.pow(min_fidelity, 1.0/l)
        print(f" [Q-LEAP] Path length (l): {l}")
        print(f" [Q-LEAP] Required average fidelity per hop (F_avg): {F_avg:.4f}")
        
        # Calculate resulting intrinsic end-to-end fidelity (before purification)
        path_intrinsic_fidelities = [G[path[i]][path[i+1]]['fidelity'] for i in range(l)]
        F_intrinsic = quantum.get_end_to_end_fidelity(path_intrinsic_fidelities)
        print(f" [Q-LEAP] Intrinsic end-to-end fidelity (no purification): {F_intrinsic:.4f}")
        
        if success:
            cost, p_succ = info
            print(f" [Q-LEAP] SUCCESS! Path satisfies constraints.")
            print(f" [Q-LEAP] Total Entangled Pair Cost (minimum): {cost}")
            print(f" [Q-LEAP] Success Probability (End-to-End): {p_succ:.4f}")
        else:
            print(f" [Q-LEAP] FAILURE! Path bottlenecked by capacity limitations.")
            for u, v, req, cap in info:
                print(f"   -> Edge ({u},{v}) requires {req} pairs to reach {F_avg:.3f}, but only has {cap} capacity.")
