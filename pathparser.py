from optimizer1 import Model1

class PathParser:
    # Function that parses path into pure path and cycles (much like flow decomposition)
    @staticmethod
    def parse_path(path, E):
        edge_list = []
        for i in range(len(path)):
            if abs(path[i]) > 1e-6:
                if path[i] > 0:
                    edge_list.append(E[i])
                else:  # backward
                    edge_list.append((E[i][1], E[i][0]))

        # Now, we have list of all edges in the path
        # We can use this to find cycles
        cycles = []
        visited = set()
        for edge in edge_list:
            if edge not in visited:
                cycle = []
                current_edge = edge
                while current_edge not in visited:
                    visited.add(current_edge)
                    cycle.append(current_edge)
                    # Find the next edge that starts where the current edge ends
                    next_edge = None
                    for e in edge_list:
                        if e[0] == current_edge[1] and e not in visited:
                            next_edge = e
                            break
                    if next_edge is None:
                        break
                    current_edge = next_edge
                if len(cycle) > 1:  # Only consider cycles of length > 1
                    cycles.append(cycle)

        # Now we have all cycles, we can find the pure path by removing cycles from edge_list
        pure_path = cycles[0].copy() # Hardcode that the first cycle found is the pure path
        cycles = cycles[1:] # Return the rest as cycles
        return pure_path, cycles
    
    # Dijkstra's algorithm from known node
    @staticmethod
    def dijkstra(V, E, start = 202):
        import heapq
        graph = {v: [] for v in V}
        for (a, b) in E:
            graph[a].append(b)
            graph[b].append(a)

        visited = set()
        queue = [(0, start)]
        distances = {v: float('inf') for v in V}
        distances[start] = 0
        parents = {v: None for v in V}   # new: to store predecessor of each vertex

        while queue:
            current_distance, current_vertex = heapq.heappop(queue)

            if current_vertex in visited:
                continue
            visited.add(current_vertex)

            for neighbor in graph[current_vertex]:
                distance = current_distance + 1
                if distance < distances[neighbor]:
                    parents[neighbor] = current_vertex  # new: record parent
                    distances[neighbor] = distance
                    heapq.heappush(queue, (distance, neighbor))

        return distances, parents
    
    # To reconstruct a path:
    @staticmethod
    def reconstruct_path(parents, start, goal):
        path = []
        cur = goal
        while parents[cur] is not None:
            path.append((parents[cur], cur))
            cur = parents[cur]
        path.reverse()
        return path if path[0][0] == start else None
