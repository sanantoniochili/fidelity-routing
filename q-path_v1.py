
import numpy as np
import os, math
from graph_class import Graph

# Print the size of terminal
Tlen = os.get_terminal_size().columns


neighbours = [
    ### simple example with S-D and two repeaters ###
    {
        'source':['r1', 'r2'], 
        'r1':['source', 'r2', 'destination'], 
        'r2':['source', 'r1', 'destination'], 
        'destination':['r1', 'r2']
    },

    ### more complex example with S-D and 3 repeaters ###
    {
        'source':['r1', 'r3'], 
        'r1':['source', 'r2', 'r3'], 
        'r2':['r1', 'r3', 'destination'], 
        'r3':['source', 'r1', 'r2', 'destination'],
        'destination':['r2', 'r3']
    }
]



# cutoff fidelity 
min_fidelity    = 0.8
# randomly initialize the RNG from some platform-dependent source of entropy
np.random.seed(0)



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



def get_purification_cost(f1, f2, c):
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

        print(f' New pure/tion fidelity: {f1}')
        print(f' Fidelity improvement: {F_improve[-1]}')
        print(f' Capacity after purification: {c}')
        print("-"*Tlen)

    print(f' Fidelity max: {fnew}')
    return F_total, F_improve



def delete_edges(G, F_min):

    E = G.get_edges()
    for edge in E:
        c = G.capacities[edge]
        f1, f2 = G.fidelities[edge], G.fidelities[edge]

        text = f' Edge: {edge} Capacity: {c} Initial fidelities: {f1} '
        decor = "="*(math.floor((Tlen-len(text))/2))
        print(decor+text+decor)
        F_total, F_improve = get_purification_cost(f1, f2, c)

        if F_total[-1] < F_min:
            print(f' --- Removing edge {edge} with max fidelity: {F_total[-1]}')
            # remove edge from data memory
            del G.capacities[edge]
            del G.fidelities[edge]
            # get u and v
            (vertex, neighbour) = edge
            # remove u from the list of neighbours of v and vice versa
            V[vertex].remove(neighbour)
            print(f' --- Deleted {neighbour} from list of {vertex}')
            V[neighbour].remove(vertex)
            print(f' --- Deleted {vertex} from list of {neighbour}')




if __name__=="__main__":

    ''' INITIALISATION '''

    # get graph as vertices and neighbours
    V = neighbours[0]
    # assign to graph
    G = Graph(V)
    # get edges for pre-processing
    E = G.get_edges()
    
    # assign capacities and fidelities to edges
    G.capacities = dict(zip( E, np.random.randint(low=5,high=10,size=len(E)) ))
    print(f'Capacities: {G.capacities}')
    G.fidelities = dict(zip( E, np.random.uniform(low=0.5, high=1, size=len(E)) ))
    print(f'Fidelities: {G.fidelities}')

    # remove illegitimate edges
    text = f' Graph before edge removal: {V}'
    print(text+'-'*(Tlen-len(text)))
    delete_edges(G, min_fidelity)
    text = f' Graph after edge removal: {V}'

    # perform BFS to find min_cost
    min_cost = G.BFS()
