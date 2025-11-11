import numpy as np

class GridBuilder:
    """
    This class instantiates grid objects. Each grid object has some rows, columns and may have holes in it
    """

    def __init__(self, rows, cols, holes = []):
        """Initialize a grid object"""
        self.rows = rows
        self.cols = cols
        self.holes = holes
    
    def get_vertices(self):
        """ Create a list of vertices with unique signatures (node IDs) for the grid. Accounts for holes
        
            Output: A list of indices, one for each vertex"""
        vertices = []
        vert_dict = {}
        for j in range(self.rows):
            for i in range(self.cols):
                vert_idx = j * self.cols + i
                if (i, j) not in self.holes:
                    vert_dict[(i, j)] = vert_idx
                    vertices.append(vert_idx)
        return vertices, vert_dict
    
    def get_edges(self):
        """ Create a list of edges between nodes in the grid. Horizontal, vertical and diagonal edges
        
            Output: A list of edges. Each element is of the form (from_node, to_node)"""
        V, Vdict = self.get_vertices()
        edges = []

        # First nested loop that creates all possible edges
        for j in range(self.rows):
            for i in range(self.cols):
                if (i, j) not in Vdict:
                    continue
                edges.append(((i, j), (i, j + 1))) if j + 1 < self.cols else None
                edges.append(((i, j), (i + 1, j))) if i + 1 < self.rows else None
                if (i + j) % 2 == 1:
                    edges.append(((i, j), (i - 1, j + 1))) if i > 0 and j + 1 < self.cols else None
                    edges.append(((i, j), (i + 1, j + 1))) if i + 1 < self.rows and j + 1 < self.cols else None
            
        removal_edges = []
        # Second loop that removes edges connected to holes
        for (a, b) in edges:
            if a in self.holes or b in self.holes:
                removal_edges.append((a, b))
        for edge in removal_edges:
            edges.remove(edge)

        # Third loop that deals with holes that aren't connected to hole but still in the square
        for (i, j) in self.holes:
            if (i + j)%2 == 0:
                edges.remove(((i - 1, j), (i, j + 1)))
                edges.remove(((i + 1, j), (i, j + 1)))
                edges.remove(((i, j - 1), (i - 1, j)))
                edges.remove(((i, j - 1), (i + 1, j)))

        # Fourth loop to deal with the bigger holes . REMOVE IF YOU WANT SQUARES
        more_holes = []
        for (i, j) in self.holes:
            more_holes.append((i - 1, j))
            more_holes.append((i + 1, j))
            more_holes.append((i, j - 1))
            more_holes.append((i, j + 1))
            more_holes.append((i - 1, j - 1))
            more_holes.append((i - 1, j + 1))
            more_holes.append((i + 1, j - 1))
            more_holes.append((i + 1, j + 1))
        more_removal_edges = []
        for (a, b) in edges:
            if a in more_holes or b in more_holes:
                more_removal_edges.append((a, b))
        for edge in more_removal_edges:
            edges.remove(edge)
        
        # Fifth loop that converts edges from (i,j) format to node ID format
        final_edges = []
        for (a, b) in edges:
            final_edges.append((Vdict[a], Vdict[b]))

        return final_edges
    
    def generate_triangles(self):
        """
        Generate triangles from edges in the grid.

        Returns: A list of tuples, each representing a triangle as three nodes
        """
        E = self.get_edges()
        V, Vdict = self.get_vertices()
        ReverseVdict = {v: k for k, v in Vdict.items()}

        triangles = []

        for (u, v) in E:
            for (v2, w) in E:
                if v2 != v:
                    continue
                if (w, u) in E or (u, w) in E:
                    p1 = ReverseVdict[u]
                    p2 = ReverseVdict[v]
                    p3 = ReverseVdict[w]
                    if (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]) > 0: #is_ccw?
                        triangles.append((u, v, w))
                    else:
                        triangles.append((u, w, v))
        
        return triangles
    
    def build_d1(self):
        """Making boundary matrix d1: vertices to edges"""
        m = len(self.get_vertices()[0])
        n = len(self.get_edges())
        d1 = np.zeros((m, n), dtype = int)

        for i, (u, v) in enumerate(self.get_edges()):
            d1[self.get_vertices()[0].index(u), i] = -1
            d1[self.get_vertices()[0].index(v), i] = 1

        return d1
    
    def build_d2(self):
        """Making boundary matrix d2: edges to triangles"""
        edges = self.get_edges()
        triangles = self.generate_triangles()

        d2 = np.zeros((len(edges), len(triangles)), dtype = int)

        for j, (u, v, w) in enumerate(triangles):
            for (a, b) in [(u, v), (v, w), (w, u)]:
                if (a, b) in edges:
                    d2[edges.index((a, b)), j] = 1
                elif (b, a) in edges:
                    d2[edges.index((b, a)), j] = -1
                else:
                # should not happen; a defensive check
                    raise ValueError(f"Triangle edge {(a,b)} or {(b,a)} not found in edges")

        return d2