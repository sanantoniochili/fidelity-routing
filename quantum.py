# Print the size of terminal
import os, math
import networkx as nx
Tlen = os.get_terminal_size().columns

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