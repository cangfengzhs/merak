import typing as T
from hnsw.element import Element
import random


class Node:
    def __init__(self, value: Element, id: int, top_layer: int):
        self.id = id
        self.top_layer = top_layer
        self.value = value

    @property
    def id(self) -> int:
        return self.id

    @property
    def value(self) -> Element:
        return self.val

    @property
    def top_layer(self) -> int:
        return self.top_layer


class LayeredGraph:
    '''
    should not insert duplicate nodes
    '''

    def __init_(self, max_top_layer: int):
        # layer in [0, top_layer], having top_layer+1 layers totally
        self.max_top_layer = max_top_layer
        self.curr_top_layer = -1

        self.next_node_id: int = 0
        self.ids: T.Dict[Element, int] = {}
        self.nodes: T.Dict[int, Node] = {}
        self.edges: T.List[T.Dict[int, T.List[int]]] = [
            None] * (self.top_layer+1)

        self.entry_point: Element = None

    @property
    def top_layer(self) -> int:
        return self.curr_top_layer

    @property
    def max_top_layer(self) -> int:
        return self.max_top_layer

    def entry_point(self) -> Element:
        return self.entry_point

    def set_entry_point(self, e: Element):
        assert e in self.ids
        assert self.ids[e] in self.nodes

        node = self.nodes[self.ids[e]]
        assert node.top_layer == self.curr_top_layer

        self.entry_point = e

    def random_node(self) -> Node:
        if self.next_node_id <= 0:
            return None

        rand_id = random.randint(0, self.next_node_id-1)
        return self.ids[rand_id]

    def insert_node(self, node: Node) -> int:
        assert node.value not in self.element_set
        assert 0 <= node.top_layer <= self.max_top_layer

        node.id = self.next_node_id
        self.next_node_id += 1
        self.nodes[node.id] = node
        self.ids[node.value] = node.id
        return node.id

    def add_edge(self, layer: int, node1: Element, node2: Element):
        assert node1 in self.ids
        assert node2 in self.ids

        id1, id2 = self.ids[node1], self.ids[node2]
        self.add_edge_id(layer, id1, id2)

    def add_edge_id(self, layer: int, id1: int, id2: int):
        ''' Add a undirected edge
        '''
        assert id1 in self.nodes and id2 in self.nodes
        assert 0 <= layer <= self.nodes[id1].top_layer
        assert 0 <= layer <= self.nodes[id2].top_layer

        self.edges[layer][id1].append(id2)
        self.edges[layer][id2].append(id1)

    def remove_edge_id(self, layer: int, id1: int, id2: int):
        ''' Remove a undirected edge
        '''
        assert id1 in self.nodes and id2 in self.nodes
        assert 0 <= layer <= self.nodes[id1].top_layer
        assert 0 <= layer <= self.nodes[id2].top_layer

        self.edges[layer][id1].remove(id2)
        self.edges[layer][id2].remove(id1)

    def set_neighbors(self, layer: int, e: Element, new_neighbors: T.List[Element]):
        id = self.ids[e]
        neighbor_ids = self.edges[layer][id]
        for next_id in neighbor_ids:
            self.remove_edge_id(layer, id, next_id)

        for new_next_id in [self.ids[new_next] for new_next in new_neighbors]:
            self.add_edge_id(layer, id, new_next_id)

    def get_neighbors(self, layer: int, e: Element) -> T.List[Element]:
        assert e in self.ids
        assert 0 <= layer <= self.max_top_layer
        assert self.ids[e] in self.edges[layer]

        neighbor_ids = self.edges[layer][self.ids[e]]
        neighbor_nodes = [self.nodes[i] for i in neighbor_ids]
        return [node.value for node in neighbor_nodes]
