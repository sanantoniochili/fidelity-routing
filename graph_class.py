class Graph:

    capacities = {}
    fidelities = {}

    def __init__(self, neighbours):
        self.V = neighbours

    def get_edges(self):
        E, visited_vertices = [], []
        for vertex in self.V:
            for neighbour in self.V[vertex]:
                if (neighbour not in visited_vertices):
                    E.append((vertex, neighbour))
                    visited_vertices.append(vertex)
        return E
    
    def BFS(self):

        # mark all the vertices as not visited
        cost = {vertex:0 for vertex in self.V.keys()}

        # create a vertex queue for BFS
        queue = []

        # mark the source visited and enqueue it
        vertex = 'source'
        queue.append(vertex)
        cost[vertex] = 0

        while queue:

            # Dequeue a vertex from
            # queue and print it
            vertex = queue.pop(0)

            # Get all adjacent vertices of the
            # dequeued vertex.
            # If an adjacent has not been visited,
            # then mark it visited and enqueue it
            for neighbour in self.V[vertex]:

                if ((cost[neighbour]==0) & (neighbour!='source')):
                    queue.append(neighbour)
                    cost[neighbour] = cost[vertex]+1

                if (cost[vertex]+1<cost[neighbour]):
                    cost[neighbour] = cost[vertex]+1

        return min(cost.values())
