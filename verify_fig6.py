import networkx as nx
import numpy as np
import quantum
import itertools
import random
import math

# ==============================================================================
# OPTIMIZED SIMULATION
# ==============================================================================

def get_q_path_cost(G, path, f_th, capacity, config):
    l = len(path) - 1
    f_inits = [G[path[i]][path[i+1]]['fidelity'] for i in range(l)]
    dp = [{} for _ in range(l + 1)]
    p_model = config['purification']
    f_model = config['fidelity_e2e']
    
    for p in range(1, capacity + 1):
        f_pure = quantum.get_purified_fidelity_for_budget(f_inits[0], p, model=p_model)
        prob = quantum.get_purification_success_prob(f_pure, model=p_model)**(p-1)
        dp[1][p] = (f_pure, prob)
        
    for i in range(2, l + 1):
        for p_total in range(i, capacity + 1):
            max_f = -1.0
            best_prob = 0.0
            for j in range(1, p_total - (i - 1) + 1):
                f_prev, prob_prev = dp[i-1][p_total - j]
                f_curr_hop = quantum.get_purified_fidelity_for_budget(f_inits[i-1], j, model=p_model)
                prob_curr = quantum.get_purification_success_prob(f_curr_hop, model=p_model)**(j-1)
                f_comb = quantum.get_end_to_end_fidelity([f_prev, f_curr_hop], model=f_model)
                if f_comb > max_f:
                    max_f = f_comb
                    best_prob = prob_prev * prob_curr
            dp[i][p_total] = (max_f, best_prob)
            
    for p in range(l, capacity + 1):
        f_achieved, prob_achieved = dp[l][p]
        if f_achieved >= f_th: return p, f_achieved, prob_achieved
    return float('inf'), 0.0, 0.0

def simulate(mu, sigma, trials, f_thresholds, config):
    print(f"\n--- Simulation: {config['purification'].upper()} | {config['fidelity_e2e'].upper()} | Trials={trials} ---")
    print(f"{'F_th':<6} | {'Tput':<8} | {'Fid':<8} | {'P_succ':<8}")
    print("-" * 40)
    
    for f_th in f_thresholds:
        t_list, f_list, p_list = [], [], []
        np.random.seed(42)
        for _ in range(trials):
            f1 = np.clip(np.random.normal(mu, sigma), 0.5, 0.999)
            f2 = np.clip(np.random.normal(mu, sigma), 0.5, 0.999)
            G = nx.Graph()
            G.add_edge('S', 'R', fidelity=f1)
            G.add_edge('R', 'D', fidelity=f2)
            
            cost, fid, prob = get_q_path_cost(G, ['S', 'R', 'D'], f_th, 50, config)
            if cost != float('inf'):
                tput = (50 * prob) / cost if config['use_probs'] else (50 / cost)
                t_list.append(tput); f_list.append(fid); p_list.append(prob)
            else:
                t_list.append(0); f_list.append(0); p_list.append(0)
        print(f"{f_th:<6.2f} | {np.mean(t_list):<8.2f} | {np.mean(f_list):<8.3f} | {np.mean(p_list):<8.3f}")

if __name__ == "__main__":
    f_ths = [0.55, 0.65, 0.75, 0.85, 0.90]
    # Test Paper Logic
    simulate(0.8, 0.1, 200, f_ths, {'purification': 'bbpssw', 'fidelity_e2e': 'swapping', 'use_probs': True})
    # Test Repo Logic
    simulate(0.9, 0.1, 200, f_ths, {'purification': 'isotropic', 'fidelity_e2e': 'product', 'use_probs': True})
