from grid import GridBuilder
from plotter import Plotter
from optimizer import Model
from optimizer1 import Model1
from pathparser import PathParser

import matplotlib.pyplot as plt
import numpy as np

import time

rows = 19
cols = 19
holes = [(4, 4), (14, 4), (14, 14), (9, 9), (4, 14)]
path = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
        37, 56, 75, 94, 113, 132, 151, 170, 189, 208,
        207, 206, 205, 204, 203, 202, 201,
        219, 218, 217, 216, 215, 214, 213, 212, 211,
        191, 190,
        209, 228, 247, 266, 285, 304, 323, 342,
        343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360]

# holes = [(2, 3), (6, 5)]
# path = [0, 1, 2, 3, 4, 5, 6, 7,
#         16, 25, 34, 43, 52, 61,
#         60, 59,
#         50, 41, 32, 23,
#         22, 21, 20, 19,
#         28, 37,
#         47, 57, 67, 77,
#         78, 79, 80] 

grid = GridBuilder(rows, cols, holes)

Vprime, Vprimedict = grid.get_vertices()
RVdict = {v: k for k, v in Vprimedict.items()}
Eprime = grid.get_edges()
Tprime = grid.generate_triangles()

D1 = grid.build_d1()
D2 = grid.build_d2()

plot = Plotter(rows, cols, holes)
# plot.plotfig(path)

# model = Model(rows, cols, holes)
# start1 = time.time()
# opt_path, opt_val, opt_edge_vals = model.solveMTZ(path)
# end1 = time.time()
# print(f"MTZ Model Solve Time: {end1 - start1} seconds")

model = Model(rows, cols, holes)
start1 = time.time()
opt_path, opt_val, opt_edge_vals = model.solveflow(path)
end1 = time.time()
print(f"Flow Model Solve Time: {end1 - start1} seconds")

# plot.plotfig(opt_path, opt_edge_vals, color = "blue")

fig, ax = plt.subplots(figsize=(8, 6))
plot.plotfig(path, color="orange", ax = ax)            # creates Figure 1
plot.plotfig(opt_path, opt_edge_vals, color="blue", ax = ax)          # creates Figure 2
# if ax:
#         ax.legend(["Reference Path", "Optimized Path"])
plt.show()

# BREAK

# model1 = Model1(rows, cols, holes)
# start2 = time.time()
# opt_path1, opt_val1, opt_edge_vals1 = model1.solve_OHCP(path)
# end2 = time.time()
# print(f"Model 2 Solve Time: {end2 - start2} seconds")
# plot.plotfig(opt_path1, opt_edge_vals1, color = "blue")

# print(f"Optimal Path: {opt_path}")
# print(f"Optimal Path Cost: {opt_val}")
# print(f"Optimal Edge Values: {opt_edge_vals}")

# pure_path, cycles = PathParser.parse_path(opt_edge_vals, Eprime) ## edges are directional here
# print(f"Pure Path: {pure_path}")
# print(f"Cycles: {cycles}")

# cycle_vertex_set = set()
# for cycle in cycles:
#     for edge in cycle:
#         cycle_vertex_set.add(edge[0])
#         cycle_vertex_set.add(edge[1])

# print(f"Vertices in cycles: {cycle_vertex_set}")

# from_202_dist, from_202_prev = PathParser.dijkstra(Vprime, Eprime, 202)
# from_360_dist, from_360_prev = PathParser.dijkstra(Vprime, Eprime, 360)

# dist_from_202= {v: from_202_dist[v] for v in cycle_vertex_set}
# dist_to_360 = {v : from_360_dist[v] for v in cycle_vertex_set}

# print(f"Distances from 202: {dist_from_202}")
# print(f"Distances to 360: {dist_to_360}")

# min_total = np.inf
# cycle_list = list(cycle_vertex_set)
# verts = len(cycle_list)
# for i in range(verts):
#     for j in range(verts):
#         if j != i:
#                 cost = dist_from_202[cycle_list[i]] + (j - i) % verts + dist_to_360[cycle_list[j]]
#                 if cost < min_total:
#                         min_total = cost
#                         best_i, best_j = cycle_list[i], cycle_list[j]
# print(f"Best i: {best_i}, Best j: {best_j}, Min Total: {min_total}")

# from_202_path = PathParser.reconstruct_path(from_202_prev, 202, best_i)
# from_360_path = PathParser.reconstruct_path(from_360_prev, 360, best_j)

# print(f"Path from 202 to {best_i}: {from_202_path}")
# print(f"Path from 360 to {best_j}: {from_360_path}")

# path1 = [0, 1, 2, 3, 4, 5, 6, 7, 27, 47, 48, 49, 50, 51, 52, 53, 73, 92, 111, 129, 147, 165, 183, 201, 219, 218, 217, 216, 215, 233, 232, 231, 249, 268, 287, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 337, 338, 339, 359, 360]
# path2 = [0, 1, 2, 3, 4, 5, 6, 7, 27, 47, 48, 49, 50, 51, 52, 53, 73, 92, 111, 129, 147, 165, 183, 202, 201, 219, 218, 217, 216, 215, 233, 232, 231, 249, 268, 287, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 337, 338, 339, 359, 360]

# fig, ax = plt.subplots(figsize=(8, 6))
# plot.plotfig(path, color="orange", ax = ax)            # creates Figure 1
# plot.plotfig(opt_path, opt_edge_vals, color="blue", ax = ax)          # creates Figure 2
# plot.plotfig(path1, color = "green", ax = ax)
# plt.show()

# fig, ax = plt.subplots(figsize=(8, 6))
# plot.plotfig(path, color="orange", ax = ax)            # creates Figure 1
# plot.plotfig(opt_path, opt_edge_vals, color="blue", ax = ax)          # creates Figure 2
# plot.plotfig(path2, color = "red", ax = ax)
# plt.show()

## Trying edge-disjoint paths

