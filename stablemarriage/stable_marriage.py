import random
from enum import IntEnum
import heapq
import matplotlib.pyplot as plt
import networkx as nx
import concurrent.futures
from argparse import ArgumentParser


def get_resources(N, U):
    '''
    Return a uniformly distributed partition of resources,
    based on the number of nodes and devices in the network
    '''
    if U < N:
        raise ValueError(
            'The number of devices must be greater or equal than the number of nodes.'
        )
    return constrained_sum_sample_pos(N, U)


def constrained_sum_sample_pos(n, total):
    '''
    Return a uniformly distributed partition of n integers,
    which sums to total
    '''
    dividers = sorted(random.sample(range(1, total), n - 1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]


def rand_from_set(rset):
    '''
    Return a random element from the given set
    '''
    return random.sample(rset, 1)[0]


class Node():
    '''
    Node of the connected graph
    '''

    last_id = 0

    def __init__(self, resources):
        self.id = Node.last_id
        Node.last_id += 1
        self.resources = resources
        self.devices = []
        self.neighbors = set()

    def add_device(self, device):
        '''
        Assign the given device to the current node,
        if possible
        '''
        if len(self.devices) < self.resources:
            heapq.heappush(self.devices, device)
        else:
            popped_device = heapq.heappushpop(self.devices, device)
            return popped_device
        return None

    def add_neighbor(self, node):
        '''
        Connect the given node to the current node
        '''
        self.neighbors.add(node)

    def get_neighbors(self):
        '''
        Return the list of current's node neighbors
        '''
        return self.neighbors

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'N{self.id}({self.resources})'


class Priority(IntEnum):
    '''
    Device priority representation
    '''
    MIN, MIN_MED, MED, MED_MAX, MAX = range(1, 5 + 1)


class Device():
    '''
    Device of the connected graph
    '''

    last_id = 0

    def __init__(self, node):
        self.id = Device.last_id
        Device.last_id += 1
        self.priority = random.choice([e for e in Priority])
        self.connected_node = node
        self.probe = Probe(self.connected_node)

    def assign_device(self):
        '''
        Find a node to assign the current device to
        '''
        self.probe.find_node(self)

    def __str__(self):
        return f'D{self.id}({self.priority})'

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.priority.value < other.priority.value

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, Device):
            return self.id == other.id
        return False


class Probe():
    '''
    Explore the connected graph, starting form the node
    directly connected to a specific device
    '''

    def __init__(self, node):
        self.distance = 0
        self.frontier = {self.distance: {node}}
        self.visited = set()

    def find_node(self, device):
        '''
        Connect the given device to the first available node
        '''
        self.distance = 0
        self.visited = set()
        while self.distance <= list(self.frontier.keys())[-1]:
            f = self.frontier[self.distance] - self.visited
            if f:
                n = rand_from_set(f)
                self.visited.add(n)
                self.frontier.setdefault(self.distance + 1, set())
                self.frontier[self.distance + 1].update(n.get_neighbors())
                d = n.add_device(device)
                if d is None:
                    break
                elif d != device:
                    d.assign_device()
                    break
            else:
                self.distance += 1


def main():
    # Default number of nodes
    MIN_N = 2
    MAX_N = 20
    N = random.randint(MIN_N, MAX_N)

    # Default number of devices
    MIN_U = N
    MAX_U = 100
    U = random.randint(MIN_U, MAX_U)

    parser = ArgumentParser(description='Stable marriage algorithm.')
    parser.add_argument(
        '--N', type=int, default=N, help='number of nodes in the connected graph'
    )
    parser.add_argument(
        '--U', type=int, default=U, help='number of devices in the connected graph (must be >= N)'
    )
    args = parser.parse_args()
    N = args.N
    U = args.U

    # Number of edges
    # Eventually, it could go up to [N * (N - 1) / 2] (Complete graph)
    E = random.randint(N - 1, 2 * N)

    resources = get_resources(N, U)
    nodes = {Node(resources[i]) for i in range(N)}
    devices = {Device(rand_from_set(nodes)) for _ in range(U)}
    node_set = set()

    # Creating connected graph
    for n in nodes:
        if not node_set:
            rand_n = rand_from_set(nodes - {n})
            node_set.add(rand_n)
        else:
            rand_n = rand_from_set(node_set - {n})
        node_set.add(n)
        n.add_neighbor(rand_n)
        rand_n.add_neighbor(n)

    # Adding extra edges
    for _ in range(E - N + 1):
        n = rand_from_set(nodes)
        rand_n = rand_from_set(node_set - {n})
        n.add_neighbor(rand_n)
        rand_n.add_neighbor(n)

    # Assigning devices
    with concurrent.futures.ThreadPoolExecutor(max_workers=U) as executor:
        for d in devices:
            executor.submit(d.assign_device())

    # Drawing graphs
    graph = nx.Graph()
    final_graph = nx.Graph()
    nodes_colors = []

    for n in nodes:
        graph.add_edges_from((n, v) for v in n.get_neighbors())
        final_graph.add_edges_from((n, v) for v in n.get_neighbors())

    graph.add_edges_from((d, d.connected_node) for d in devices)
    final_graph.add_edges_from((n, d) for n in nodes for d in n.devices)
    nodes_colors.extend(['skyblue'] * N)
    nodes_colors.extend(['yellow'] * U)

    draw_args = {
        'with_labels': True,
        'node_color': nodes_colors,
        'linewidths': 1,
        'font_size': 6,
        'font_weight': "bold",
        'font_color': "black",
        'width': 1,
        'edge_color': "white"
    }

    fig1 = plt.figure(1)
    fig1.canvas.set_window_title("Grafo iniziale")
    nx.draw(graph, **draw_args)
    fig1.set_facecolor("#D3D3D3")

    fig2 = plt.figure(2)
    fig2.canvas.set_window_title("Grafo finale")
    nx.draw(final_graph, **draw_args)
    fig2.set_facecolor("#D3D3D3")
    plt.show()


if __name__ == "__main__":
    main()
