import numpy as np
import gurobipy as gp
from gurobipy import GRB
from scipy.linalg import svd

from grid import GridBuilder

class Model:

    def __init__(self, rows, cols, holes = []):
        self.rows = rows
        self.cols = cols
        self.holes = holes
        self.grid = GridBuilder(rows, cols, holes)
        self.vertices, self.vertdict = self.grid.get_vertices()
        self.edges = self.grid.get_edges()

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
    
    def _create_H(self, tol = 1e-6):
        grid = self.grid
        d1 = grid.build_d1()
        d2 = grid.build_d2()
        L = d1.T @ d1 + d2 @ d2.T

        # SVD to extract null space
        U, S, Vh = svd(L)
        null_mask = (S < tol)
        H = Vh[null_mask].T

        return H
    
    def solve(self, ref_path, tol = 1e-3):

        E = list(self.edges)
        E_rev = [(b, a) for (a, b) in E]
        E_full = E + E_rev

        V = self.vertices
        s = V[0]; t = V[-1]

        x_ref = self._path_vector(ref_path)
        H = self._create_H()
        h_ref = H.T @ x_ref
        cost = self._cost()

        m = gp.Model("homology_constrained_shortest_path")

        x = m.addVars(E_full, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = "x") # LP
        # x = m.addVars(E_full, vtype = GRB.BINARY, name = "x") # IP

        m.setObjective(
            gp.quicksum(cost[e] * x[e] for e in E) +
            gp.quicksum(cost[(b, a)] * x[(b, a)] for (a, b) in E),
            GRB.MINIMIZE
        )

        for v in V:
            inflow = gp.quicksum(x[(u, v)] for (u, v2) in E_full if v2 == v)
            outflow = gp.quicksum(x[(v, w)] for (v1, w) in E_full if v1 == v)
            if v == s:
                m.addConstr(outflow - inflow == 1, name = f"flow_{v}")
            elif v == t:
                m.addConstr(outflow - inflow == -1, name = f"flow_{v}")
            else:
                m.addConstr(outflow - inflow == 0, name = f"flow_{v}")
            
        # Homology constraints (forward minus reverse)
        for k in range(H.shape[1]):
            harmonic_proj = gp.quicksum(
                H[i, k] * (x[E[i]] - x[(E[i][1], E[i][0])])
                for i in range(len(E))
            )
            m.addConstr(harmonic_proj == h_ref[k], name=f"harm_proj_{k}")
            
        m.optimize()

        
        if m.status == GRB.OPTIMAL:
            # Consolidate results into forward-bias
            edges_val = []
            for e in E:
                forward_val = x[e].X
                reverse_val = x[(e[1], e[0])].X
                net_val = forward_val - reverse_val
                if abs(net_val) < tol:
                    net_val = 0.0
                edges_val.append(net_val)

            # Binary indicator of which edges are used
            opt_path = [abs(v) > tol for v in edges_val]

            # Print debug info
            print("✅ Found optimal path:")
            for i, e in enumerate(E):
                if abs(edges_val[i]) > tol:
                    direction = "forward" if edges_val[i] > 0 else "backward"
                    print(f"  Edge {e} used {direction}, value={edges_val[i]:.3f}")
            print(f"Total cost: {m.objVal}")

            return opt_path, m.objVal, edges_val

        else:
            print("❌ No solution found. Computing IIS...")
            m.computeIIS()
            for c in m.getConstrs():
                if c.IISConstr:
                    print(f"  - {c.ConstrName}")
            for v in m.getVars():
                if v.IISLB: print(f"  - {v.VarName} has conflicting lower bound")
                if v.IISUB: print(f"  - {v.VarName} has conflicting upper bound")
            return None
        
    def solveMTZ(self, ref_path, tol = 1e-3):

        E = list(self.edges)
        E_rev = [(b, a) for (a, b) in E]
        E_full = E + E_rev

        V = self.vertices
        s = ref_path[0]; t = ref_path[-1]

        x_ref = self._path_vector(ref_path)
        H = self._create_H()
        h_ref = H.T @ x_ref
        cost = self._cost()

        m = gp.Model("homology_constrained_shortest_path")

        x = m.addVars(E_full, vtype = GRB.BINARY, name = "x") # IP
        # x = m.addVars(E_full, vtype = GRB.CONTINUOUS, lb= 0.0, ub = 1.0, name = "x") # LP
        N = len(V)
        u = m.addVars(V, vtype = GRB.CONTINUOUS, lb = 0.0, ub = N - 1, name = "u") # MTZ variables

        m.setObjective(
            gp.quicksum(cost[e] * x[e] for e in E) +
            gp.quicksum(cost[(b, a)] * x[(b, a)] for (a, b) in E),
            GRB.MINIMIZE
        )

        for v in V:
            inflow = gp.quicksum(x[(u, v)] for (u, v2) in E_full if v2 == v)
            outflow = gp.quicksum(x[(v, w)] for (v1, w) in E_full if v1 == v)
            if v == s:
                m.addConstr(outflow - inflow == 1, name = f"flow_{v}")
            elif v == t:
                m.addConstr(outflow - inflow == -1, name = f"flow_{v}")
            else:
                m.addConstr(outflow - inflow == 0, name = f"flow_{v}")
            
        # Homology constraints (forward minus reverse)
        for k in range(H.shape[1]):
            harmonic_proj = gp.quicksum(
                H[i, k] * (x[E[i]] - x[(E[i][1], E[i][0])])
                for i in range(len(E))
            )
            m.addConstr(harmonic_proj == h_ref[k], name=f"harm_proj_{k}")

        # MTZ constraints to eliminate subtours
        m.addConstr(u[s] == 0, name="u_start")
        for (a, b) in E_full:
            m.addConstr(u[a] - u[b] + N * x[(a, b)] <= N - 1, name=f"mtz_{a}_{b}")
            
        m.optimize()

        
        if m.status == GRB.OPTIMAL:
            # Consolidate results into forward-bias
            edges_val = []
            for e in E:
                forward_val = x[e].X
                reverse_val = x[(e[1], e[0])].X
                net_val = forward_val - reverse_val
                if abs(net_val) < tol:
                    net_val = 0.0
                edges_val.append(net_val)

            # Binary indicator of which edges are used
            opt_path = [abs(v) > tol for v in edges_val]

            # Print debug info
            print("✅ Found optimal path:")
            for i, e in enumerate(E):
                if abs(edges_val[i]) > tol:
                    direction = "forward" if edges_val[i] > 0 else "backward"
                    print(f"  Edge {e} used {direction}, value={edges_val[i]:.3f}")
            print(f"Total cost: {m.objVal}")

            return opt_path, m.objVal, edges_val

        else:
            print("❌ No solution found. Computing IIS...")
            m.computeIIS()
            for c in m.getConstrs():
                if c.IISConstr:
                    print(f"  - {c.ConstrName}")
            for v in m.getVars():
                if v.IISLB: print(f"  - {v.VarName} has conflicting lower bound")
                if v.IISUB: print(f"  - {v.VarName} has conflicting upper bound")
            return None