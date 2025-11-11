import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import Polygon
from grid import GridBuilder

class Plotter:

    def __init__(self, rows, cols, holes = []):
        self.rows = rows
        self.cols = cols
        self.holes = holes
        self.grid = GridBuilder(rows, cols, holes)

    def plotfig(self, path = None, opt_edge_vals = None, color = "orange",ax = None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        
        vertices, Vdict = self.grid.get_vertices()
        RVdict = {v: k for k, v in Vdict.items()}
        edges = self.grid.get_edges()

        for v in vertices:
            x = RVdict[v][0]
            y = RVdict[v][1]
            ax.plot(x, y, 'ko', ms = 1.5)
            # plt.text(x + 0.1, y + 0.1, str(v), fontsize = 8, color = 'blue')

        ax.plot(0, 0, 'k*', ms = 9)
        ax.plot(self.cols - 1, self.rows - 1, 'k*', ms = 9)

        for edge in edges:
            x_values = [RVdict[edge[0]][0], RVdict[edge[1]][0]]
            y_values = [RVdict[edge[0]][1], RVdict[edge[1]][1]]
            ax.plot(x_values, y_values, 'k-', lw = 0.5)  # 'k-' means black color, solid line

        ax.set_xlim(-1, self.cols)
        ax.set_ylim(-1, self.rows)
        ax.set_aspect('equal', adjustable='box')

        if self.holes: # filling the holes
            for (i, j) in self.holes:
                # shape_coords = [(i-1, j-1), (i+1, j-1), (i+1, j+1), (i-1, j+1)]  # Square vertices
                shape_coords = [(i-1, j-2), (i+1, j-2), (i+2, j-1), (i+2, j+1), (i+1, j+2), (i-1, j+2), (i-2, j+1), (i-2, j-1)]  # Octagon vertices
                polygon = Polygon(shape_coords, closed=True, color='gray', alpha=0.3)
                ax.add_patch(polygon)

        # Plot the path with arrows
        if path:
            if len(path) != len(edges):
                self._plot_path_with_arrows_some_edges(path, color, label='Reference Path', ax = ax)
            else:
                self._plot_path_with_arrows_all_edges(path, opt_edge_vals, color, label='Reference Path', ax = ax)

 
        ax.set_title(f"{self.rows} x {self.cols} Grid with Holes and Path")
        ax.grid(False)
        
        return ax

    def _plot_path_with_arrows_some_edges(self, path, color = "orange", label = None, ax = None):
        if ax is None:
            ax = plt.gca()
        
        _, Vdict = self.grid.get_vertices()
        RVdict = {v: k for k, v in Vdict.items()}

        for i in range(len(path) - 1):
            x1, y1 = RVdict[path[i]][0], RVdict[path[i]][1]
            x2, y2 = RVdict[path[i + 1]][0], RVdict[path[i + 1]][1]
            arrow = FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle='->',
                color=color,
                linewidth=2,
                mutation_scale= 10,  # scales the arrowhead
                zorder=10
            )
            ax.add_patch(arrow)

        if label:
            ax.plot([], [], color=color, label=label)
    
    def _plot_path_with_arrows_all_edges(self, path, opt_edge_vals, color = "orange", label = None, ax = None):
        if ax is None:
            ax = plt.gca()
        
        _, Vdict = self.grid.get_vertices()
        RVdict = {v: k for k, v in Vdict.items()}
        E = self.grid.get_edges()
        edges_val = opt_edge_vals

        # Modify _plot_path_with_arrows_all_edges:
        for i in range(len(edges_val)):
            if abs(edges_val[i]) > 1e-6:
                if edges_val[i] > 0:
                    x1, y1 = RVdict[E[i][0]][0], RVdict[E[i][0]][1]
                    x2, y2 = RVdict[E[i][1]][0], RVdict[E[i][1]][1]
                else:  # backward
                    x1, y1 = RVdict[E[i][1]][0], RVdict[E[i][1]][1]
                    x2, y2 = RVdict[E[i][0]][0], RVdict[E[i][0]][1]
                arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->', color=color, linewidth=2, mutation_scale=10, zorder=10)
                ax.add_patch(arrow)

        if label:
            ax.plot([], [], color=color, label=label)