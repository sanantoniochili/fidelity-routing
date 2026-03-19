import networkx as nx
import numpy as np
import os, math
Tlen = os.get_terminal_size().columns
import quantum, paths

# cutoff fidelity 
min_fidelity    = 0.8
# randomly initialize the RNG from some platform-dependent source of entropy
np.random.seed(0)
# initialise graph
G = nx.Graph()
# flag for debugging
debug = True

# MODEL TOGGLES (User can switch between Paper and Repo logic)
CONFIG = {
    'purification': 'bbpssw',   # 'bbpssw' (Paper default), 'isotropic' (Repo)
    'fidelity_e2e': 'swapping', # 'swapping' (Paper default), 'product' (Repo)
    'use_probs': True            # Scale throughput by success probability
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


if __name__=="__main__":

    ''' INITIALISATION '''

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
    text = f' Graph before edge removal:'
    print(text+'-'*(Tlen-len(text)))
    print(f" {'Edge':<22}{'Capacity':<12}{'Fidelity (min)'}")
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']}")

    # remove illegitimate edges
    quantum.delete_edges(G, min_fidelity, debug)
    text = f' Graph after edge removal:'
    print(text+'-'*(Tlen-len(text)))
    print(f" {'Edge':<22}{'Capacity':<12}{'Fidelity (min)'}")
    for edge in G.edges(data=True):
        print(f" {f'({edge[0]},{edge[1]})':<22}{edge[2]['weight']:<12}{edge[2]['fidelity']}")

    ''' MIN COST & K SHORTEST PATHS'''

    # Configuration for search
    source, destination = "source", "destination"
    f_threshold = 0.85
    search_type = 'optimal' # 'optimal' (DP) or 'greedy' (Repo-style)

    # 1. BFS for lower bound hop count
    try:
        shortest_path = nx.shortest_path(G, source=source, target=destination)
        H_cost = len(shortest_path) - 1
    except nx.NetworkXNoPath:
        print("No path found!")
        exit()

    print('-'*(Tlen))
    print(f' Target Fidelity: {f_threshold} | Mode: {CONFIG["purification"]}/{CONFIG["fidelity_e2e"]}')
    print(f' Initial H_min: {H_cost}')

    def get_greedy_boost_cost(path, f_th, config):
        """Official Repo's greedy purification algorithm."""
        l = len(path) - 1
        # Current purification levels (total pairs used per link)
        # Start with 1 pair per link
        alloc = [1] * l
        
        while True:
            # Calculate current path fidelity
            fidelities = [quantum.get_purified_fidelity_for_budget(G[path[i]][path[i+1]]['fidelity'], alloc[i], model=config['purification']) for i in range(l)]
            f_e2e = quantum.get_end_to_end_fidelity(fidelities, model=config['fidelity_e2e'])
            
            if f_e2e >= f_th:
                cost = sum(alloc)
                # Throughput logic with P_succ
                p_succ = 1.0
                for f_p in fidelities:
                    p_succ *= quantum.get_purification_success_prob(f_p, model=config['purification'])
                return cost, f_e2e, p_succ
            
            # Boost the link with the LOWEST current fidelity
            target_idx = np.argmin(fidelities)
            # Check capacity
            u, v = path[target_idx], path[target_idx+1]
            if alloc[target_idx] >= G[u][v]['weight']:
                # Cannot boost further on this bottleneck link
                # Try boosting next lowest? (Official repo just fails or continues)
                # For robustness, we'll try to find a link that DOES have capacity
                sorted_indices = np.argsort(fidelities)
                found = False
                for idx in sorted_indices:
                    if alloc[idx] < G[path[idx]][path[idx+1]]['weight']:
                        alloc[idx] += 1
                        found = True
                        break
                if not found: return float('inf'), 0, 0
            else:
                alloc[target_idx] += 1

    # Search for min cost
    best_cost = float('inf')
    best_res = None

    # Iterate through increasing cost budget C
    C_max = sum(nx.get_edge_attributes(G, 'weight').values())
    
    found_solution = False
    for cost_budget in range(H_cost, C_max + 1):
        # In Q-PATH, we explore paths that have hop count L <= cost_budget
        # For simplicity, we search all paths with cutoff up to budget
        for path in nx.all_simple_paths(G, source, destination, cutoff=cost_budget):
            if search_type == 'greedy':
                cost, fid, prob = get_greedy_boost_cost(path, f_threshold, CONFIG)
            else:
                # Use our DP cost function from verify_fig6
                from verify_fig6 import get_q_path_cost
                cost, fid, prob = get_q_path_cost(G, path, f_threshold, 100, CONFIG)
            
            if cost <= cost_budget:
                print(f"\n[SUCCESS] Found path: {path}")
                print(f"Total Cost: {cost} pairs")
                print(f"Final Fidelity: {fid:.4f}")
                print(f"Success Probability: {prob:.4f}")
                tput = (1.0 * prob) / cost if CONFIG['use_probs'] else (1.0 / cost)
                print(f"Normalized Throughput: {tput:.5f}")
                found_solution = True
                break
        if found_solution: break

    if not found_solution:
        print("\nNo valid purification allocation found for given threshold.")



