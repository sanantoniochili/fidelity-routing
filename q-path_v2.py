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

    # bfs for calculating lower bound cost
    shortest_path = nx.shortest_path(G, source="source", target="destination")
    H_cost = len(shortest_path)-1
    print('-'*(Tlen))
    print(f' Expected cost: {H_cost}')

    # get upper bound cost
    C_max = max([edge[2]['weight'] for edge in G.edges(data=True)])
    for min_cost in range(H_cost, len(G.edges())*C_max):

        # Get multiple shortest paths with same cost
        path_set = paths.k_shortest_paths(G, 'source', 'destination', min_cost)
        print(path_set)



