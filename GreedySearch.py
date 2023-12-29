import tkinter as tk
from tkinter import simpledialog, messagebox
import heapq


# class node has name position and heuristic
class Node:
    def __init__(self, name, x, y, heuristic):
        self.name = name
        self.x = x
        self.y = y
        self.heuristic = heuristic


# cost between two nodes
class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2


class Graph:
    def __init__(self, directed=False):
        self.nodes = {}
        self.edges = {}
        self.heuristics = {}
        self.directed = directed

    def add_node(self, name, node):
        self.nodes[name] = node

    def add_edge(self, node1, node2, __reversed=True):
        try:
            neighbors = self.edges[node1]
        except KeyError:
            neighbors = {}
        neighbors[node2] = node1
        self.edges[node1] = neighbors
        if not self.directed and __reversed:
            self.add_edge(node2, node1, True)

    def neighbors(self, node):
        try:
            return self.edges[node]
        except KeyError:
            return []

    def greedy_search(self, start, goal):
        found, fringe, visited, came_from = False, [(self.heuristics[start], start)], set([start]), {
            start: None}
        print('{:11s} | {}'.format('Expand Node', 'Fringe'))
        print('--------------------')
        print('{:11s} | {}'.format('-', str(fringe[0])))
        while not found and len(fringe):
            _, current = heapq.heappop(fringe)
            print('{:11s}'.format(current), end=' | ')
            if current == goal:
                found = True
                break
            for node in self.neighbors(current):
                if node not in visited:
                    visited.add(node)
                    came_from[node] = current
                    heapq.heappush(fringe, (self.heuristics[node], node))
            print(', '.join([str(n) for n in fringe]))
        if found:
            print()
            return came_from
        else:
            print('No path from {} to {}'.format(start, goal))
            return None, float('inf')


class GUI:
    def __init__(self, root):
        self.root = root
        root.title("GreedySearch")
        self.canvas = tk.Canvas(root, width=900, height=700, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.graph = Graph(directed=True)
        self.path = []
        self.selected_node = None
        self.create_nav_bar()
        self.canvas.bind("<Button-1>", self.handle_click)

    def create_nav_bar(self):
        nav_bar = tk.Frame(self.root, bg="pink", height=40, width=1000)
        nav_bar.pack(side="top", fill="x", anchor="nw")

        home_button = tk.Button(nav_bar, text="Clear", command=self.clear_canvas)
        home_button.pack(side="left", padx=10, pady=5)

        node_button = tk.Button(nav_bar, text="Node", command=self.activate_node_mode)
        node_button.pack(side="left", padx=10, pady=5)

        edge_button = tk.Button(nav_bar, text="Edge", command=self.activate_edge_mode)
        edge_button.pack(side="left", padx=10, pady=5)

        search_button = tk.Button(nav_bar, text="Search", command=self.run_greedy_search)
        search_button.pack(side="left", padx=10, pady=5)

    def activate_node_mode(self):
        self.canvas.bind("<Button-1>", self.add_node)

    def activate_edge_mode(self):
        self.canvas.bind("<Button-1>", self.select_node)

    def add_node(self, event):
        x, y = event.x, event.y
        name = simpledialog.askstring("Node Name", "Enter node name:")
        heuristic = float(simpledialog.askstring("Node Heuristic", "Enter node heuristic:"))
        node = Node(name, x, y, heuristic)
        self.graph.add_node(name, node)
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="pink")
        self.canvas.create_text(x, y, text=name, fill="black")
        self.canvas.create_text(x, y - 20, text=f"{name}\n{heuristic}", fill="white")
        self.graph.heuristics[name] = heuristic

    def select_node(self, event):
        x, y = event.x, event.y
        for name, node in self.graph.nodes.items():
            if abs(x - node.x) <= 15 and abs(y - node.y) <= 15:
                if self.selected_node is None:
                    self.selected_node = node
                    self.canvas.itemconfigure(self.canvas.find_closest(x, y)[0], fill="purple")
                else:
                    self.create_edge(self.selected_node, node)
                    self.selected_node = None
                    self.canvas.delete("selection")

    def create_edge(self, node1, node2):
        self.graph.add_edge(node1.name, node2.name)
        self.canvas.create_line(node1.x, node1.y, node2.x, node2.y, fill="#800080", width=2)
        self.canvas.create_text((node1.x + node2.x) / 2, (node1.y + node2.y) / 2, fill="black")

    def handle_click(self, event):
        x, y = event.x, event.y
        if self.selected_node is None:
            self.node_edit(event)
        else:
            self.select_node(event)
    def run_greedy_search(self):
        start_node_name = simpledialog.askstring("Start Node", "Enter the name of the start node:")
        goal_node_name = simpledialog.askstring("Goal Node", "Enter the name of the goal node:")

        came_from = self.graph.greedy_search(start_node_name, goal_node_name)

        if came_from:
            path = self.reconstruct_path(came_from, goal_node_name)
            messagebox.showinfo("Path", "Path found:\n" + " -> ".join(path))
        else:
            messagebox.showinfo("Path", "No path found")

    def reconstruct_path(self, came_from, goal_node):
        path = [goal_node]
        current_node = goal_node
        while came_from[current_node] is not None:
            current_node = came_from[current_node]
            path.append(current_node)
        path.reverse()
        return path

    def clear_canvas(self):
        self.canvas.delete("all")
        self.graph = Graph(directed=True)
        self.path = []
        self.selected_node = None

    def node_edit(self, event):
        x, y = event.x, event.y
        for name, node in self.graph.nodes.items():
            if abs(x - node.x) <= 15 and abs(y - node.y) <= 15:
                new_heuristic = float(
                    simpledialog.askstring("Edit Node Heuristic", f"Enter new heuristic for {name}:"))
                node.heuristic = new_heuristic
                self.graph.set_heuristics({**self.graph.heuristics, name: new_heuristic})
                self.canvas.itemconfigure(self.canvas.find_closest(x, y)[0], text=f"{name}\n{new_heuristic}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    app.run()