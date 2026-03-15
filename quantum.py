# Print the size of terminal
import os, math
import networkx as nx
try:
    Tlen = os.get_terminal_size().columns
except OSError:
    Tlen = 80

def get_purification_fidelity(x1, x2):
    """Return the fidelity of the final pair
    after the purification protocol consumes two 
    entanglement pairs with initial fidelities x1, x2.

    Args:
        x1 (_type_): Fidelity of pair 1.
        x2 (_type_): Fidelity of pair 2.

    Returns:
        _type_: Fidelity of purified pair.
    """    
    return x1*x2/(x1*x2 + (1-x1)*(1-x2))



def get_purification_cost(f1, f2, c, debug=False):
    """Calculate the maximum fidelity of the
    current edge after C-1 iterations of purification.

    Args:
        f1 (_type_): Fidelity of pair 1.
        f2 (_type_): Fidelity of pair 2.
        C (_type_): Capacity of the current edge.

    Returns:
        F: Array of fidelities after each purification iteration.
        F_improve: Array of fidelity improvement after each iteration.
    """    
    F_total = []
    F_improve = []
    fnew = f1

    while(c>1):
        c -= 1
        fnew = get_purification_fidelity(f1, f2)
        F_total.append(fnew)
        F_improve.append(fnew-f1)
        f1 = fnew

        if debug:
            print(f' New pure/tion fidelity: {f1}')
            print(f' Fidelity improvement: {F_improve[-1]}')
            print(f' Capacity after purification: {c}')
            print("-"*Tlen)

    print(f' Fidelity max: {fnew}')
    return F_total, F_improve



def delete_edges(G:nx.Graph, F_min, debug=False):

    edges_to_remove = []
    for edge in G.edges(data=True):
        pass
        c = edge[2]['weight']
        f1, f2 = edge[2]['fidelity'], edge[2]['fidelity']

        text = f' Edge: {edge} Capacity: {c} Initial fidelities: {f1} '
        decor = "="*(math.floor((Tlen-len(text))/2))
        print(decor+text+decor)
        F_total, F_improve = get_purification_cost(f1, f2, c, debug)

        if F_total[-1] < F_min:
            print(f' *** Removing edge {edge} with max fidelity: {F_total[-1]}')
            # remove edge from graph
            edges_to_remove.append(edge)

    G.remove_edges_from(edges_to_remove)

def get_required_purification(f_initial, f_target):
    if f_initial >= f_target:
        return 1
    c = 1
    f_current = f_initial
    while f_current < f_target:
        f_next = get_purification_fidelity(f_current, f_initial)
        if f_next <= f_current + 1e-9:
            return float('inf')
        f_current = f_next
        c += 1
    return c

def get_end_to_end_fidelity(path_fidelities):
    if not path_fidelities:
        return 0.0
    n = len(path_fidelities)
    if n == 1:
        return path_fidelities[0]
    prod = 1.0
    for F_i in path_fidelities:
        prod *= (4.0 * F_i - 1.0) / 3.0
    return 0.25 + 0.75 * prod



def get_purified_fidelity_for_budget(f_initial, pairs_consumed):
    if pairs_consumed <= 1:
        return f_initial
    f_current = f_initial
    for _ in range(pairs_consumed - 1):
        f_current = get_purification_fidelity(f_current, f_initial)
    return f_current

