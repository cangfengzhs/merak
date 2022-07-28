from typing import Dict, List
from point import Point


class Node:
    def __init__(self, top_layer: int, point: Point):
        self._top_layer = top_layer
        self._point = point

    def __str__(self) -> str:
        return f'top_layer:{self._top_layer}, {self._point}'

    @property
    def id(self) -> int:
        return self._point.id

    @property
    def point(self) -> Point:
        return self._point

    @property
    def top_layer(self) -> int:
        return self._top_layer


class LayeredGraph:
    '''
    should not insert duplicate nodes
    '''

    def __init__(self, max_top_layer: int):
        # layer in [0, top_layer], having top_layer+1 layers totally
        self._max_top_layer = max_top_layer
        self._curr_top_layer = -1

        self._nodes: Dict[int, Node] = {}
        self._edges: List[Dict[int, List[int]]] = [None] * (self._max_top_layer+1)

        self._entry_point: Point = None

    @property
    def top_layer(self) -> int:
        return self._curr_top_layer

    @property
    def max_top_layer(self) -> int:
        return self._max_top_layer

    @property
    def entry_point(self) -> Point:
        return self._entry_point

    @entry_point.setter
    def set_entry_point(self, p: Point):
        assert p.id in self._nodes
        node = self._nodes[p.id]

        assert node.top_layer == self._curr_top_layer
        self._entry_point = p

    def add_point(self, top_layer: int, p: Point):
        assert p.id not in self._nodes
        assert 0 <= top_layer <= self._max_top_layer
        if top_layer > self._curr_top_layer:
            self._curr_top_layer = top_layer

        node = Node(top_layer, p)
        self._nodes[p.id] = node

    def add_edge(self, layer: int, p1: Point, p2: Point):
        ''' Add a undirected edge, do not allow self loop
        '''
        assert p1.id != p2.id
        assert p1.id in self._nodes
        assert p2.id in self._nodes
        assert 0 <= layer <= self._nodes[p1.id].top_layer
        assert 0 <= layer <= self._nodes[p2.id].top_layer

        if self._edges[layer] is None:
            self._edges[layer] = {}
        if p1.id not in self._edges[layer]:
            self._edges[layer][p1.id] = []
        if p2.id not in self._edges[layer]:
            self._edges[layer][p2.id] = []

        self._edges[layer][p1.id].append(p2.id)
        self._edges[layer][p2.id].append(p1.id)

    def remove_edge(self, layer: int, p1: Point, p2: Point):
        ''' Remove a undirected edge
        '''
        self.remove_edge_by_id(layer, p1.id, p2.id)

    def remove_edge_by_id(self, layer: int, id1: int, id2: int):
        assert id1 != id2
        assert id1 in self._nodes
        assert id2 in self._nodes
        assert 0 <= layer <= self._nodes[id1].top_layer
        assert 0 <= layer <= self._nodes[id2].top_layer

        self._edges[layer][id1].remove(id2)
        self._edges[layer][id2].remove(id1)

    def set_neighbors(self, layer: int, p: Point, new_neighbors: List[Point]):
        id = p.id
        neighbor_ids = self._edges[layer][id].copy()  # Warn: python array is reference
        for next_id in neighbor_ids:
            self.remove_edge_by_id(layer, id, next_id)

        for new_next in new_neighbors:
            self.add_edge(layer, p, new_next)

    def get_neighbors(self, layer: int, p: Point) -> List[Point]:
        assert p.id in self._nodes
        assert 0 <= layer <= self._max_top_layer
        assert 0 <= layer <= self._nodes[p.id].top_layer
        assert p.id in self._edges[layer]

        neighbor_ids = self._edges[layer][p.id]
        return [self._nodes[next].point for next in neighbor_ids]
