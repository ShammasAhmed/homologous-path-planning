import numpy as np
import gurobipy as gp
from gurobipy import GRB
from scipy.linalg import svd

from grid import GridBuilder

class Model1:

    def __init__(self, rows, cols, holes = []):
        self.rows = rows
        self.cols = cols
        self.holes = holes
        self.grid = GridBuilder(rows, cols, holes)
        self.vertices, self.vertdict = self.grid.get_vertices()
        self.edges = self.grid.get_edges()

    # @staticmethod
    def _cost(self):
        """Create a cost vector for the edges"""
        vdict = self.vertdict
        Rvdict = {v: k for k, v in vdict.items()}
        cost = {}
        for (a, b) in self.edges:
            (x1, y1) = Rvdict[a]
            (x2, y2) = Rvdict[b]
            if x1 == x2 or y1 == y2:
                cost[(a,b)] = 1
                cost[(b,a)] = 1
            else:
                cost[(a, b)] = np.sqrt(2)
                cost[(b, a)] = np.sqrt(2)
        return cost
    
    def _path_vector(self, path):
        path_vec = np.zeros(len(self.edges), dtype = int)
        e_idx = {e : i for i, e in enumerate(self.edges)}

        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            if edge in e_idx:
                path_vec[e_idx[edge]] = 1
            else:
                reverse_edge = (path[i + 1], path[i])
                if reverse_edge in e_idx:
                    path_vec[e_idx[reverse_edge]] = -1
        
        return path_vec
    
    def solve_OHCP(self, path, tol = 1e-3):
        E = list(self.edges)
        T = self.grid.generate_triangles()
        D = self.grid.build_d2()
        
        V = self.vertices
        s = V[0]; t = V[-1]
        x_ref = self._path_vector(path)
        cost = self._cost()

        m = len(E)
        n = len(T)

        print(f"Number of edges: {m}, Number of triangles: {n}")
        print(f"Reference Path Vector: {x_ref}")
        print(f"Reference Path Shape: {x_ref.shape}")

        m = gp.Model("OHCP")

        x_plus = m.addVars(E,  vtype =GRB.CONTINUOUS, lb = 0.0, name="x_plus")
        x_minus = m.addVars(E, vtype =GRB.CONTINUOUS, lb = 0.0, name="x_minus")
        y_plus = m.addVars(T,  vtype =GRB.CONTINUOUS, lb = 0.0, name="y_plus")
        y_minus = m.addVars(T, vtype =GRB.CONTINUOUS, lb = 0.0, name="y_minus")

        m.setObjective(
            gp.quicksum(cost[e] * (x_plus[e] + x_minus[e]) for e in E),
            GRB.MINIMIZE
        )

        for e in E:
            lhs = x_plus[e] - x_minus[e]
            rhs = x_ref[E.index(e)] + gp.quicksum(D[E.index(e), T.index(t)] * (y_plus[t] - y_minus[t]) for t in T)
            m.addConstr(lhs == rhs, name=f"edge_constr_{e}")

        m.optimize()

        if m.status == GRB.OPTIMAL:
            edges_val = []
            for e in E:
                val = x_plus[e].X - x_minus[e].X
                edges_val.append(val)
            
            # Binary indicator of which edges are used
            opt_path = [abs(v) > tol for v in edges_val]

        return opt_path, m.ObjVal, edges_val
