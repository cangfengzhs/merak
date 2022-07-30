from typing import Dict, List, Tuple
import numpy as np

from merak.point import Point
from merak.client import Client


class Node:
    def __init__(self, point: Point, neighbors: Dict[int, List[int]]):
        self._point = point
        self._neighbors = neighbors

    def __str__(self) -> str:
        return f'{self._point}'

    @property
    def id(self) -> int:
        return self._point.id

    @property
    def point(self) -> Point:
        return self._point

    @property
    def layer(self) -> int:
        return self._layer

    @property
    def layer_neighbors(self, layer: int) -> List[int]:
        assert layer in self._neighbors
        return self._neighbors[layer]


class AddBatch:
    def __init__(self):
        self._points: List[Point] = []
        self._edges: List[Tuple[int, int, int]] = []

    def add_point(self, p: Point):
        self._points.append(p)

    def add_edge(self, layer: int, src: int, dst: int):
        self._edges.append((layer, src, dst))

    @property
    def points(self) -> List[Point]:
        return self._points

    @property
    def edges(self) -> List[Tuple(int, int, int)]:
        return self._edges


class LayeredGraph:
    '''
    should not insert duplicate nodes
    '''

    def __init__(self, max_top_layer: int, client: Client):
        self._client = client
        # layer in [0, top_layer], having top_layer+1 layers totally
        self._max_top_layer = max_top_layer
        self._curr_top_layer = -1

        self._nodes: Dict[int, Node] = {}  # TODO(spw): should convert to cache
        self._entry_point: int = -1

    @property
    def top_layer(self) -> int:
        return self._curr_top_layer

    @property
    def max_top_layer(self) -> int:
        return self._max_top_layer

    @property
    def entry_point(self) -> Point:
        return self._entry_point

    # maybe no need this, will be set in add_point
    @entry_point.setter
    def set_entry_point(self, p: Point):
        assert p.id in self._nodes
        node = self._nodes[p.id]

        assert node.top_layer == self._curr_top_layer
        self._entry_point = p

    def add_batch(self) -> AddBatch:
        return AddBatch()

    def add(self, batch: AddBatch):
        b = self._client.insert_batch()
        for p in batch.points:
            b.insert_vertex(p.id, p.vec_str)
        for e in batch.edges:
            layer, src, dst = e
            b.insert_edge(layer, src, dst)
            if layer > self._curr_top_layer:
                self._curr_top_layer = layer
                self._entry_point = src
        self._client.insert(b)

    def get_point(self, id: int) -> Point:
        vec_str, neighbor_ids = self._client.get_neighbors(id)
        vec = np.fromstring(vec_str)
        p = Point(id, vec)
        self._nodes[id] = Node(p, neighbor_ids)
        return p

    def get_neighbor_ids(self, layer: int, id: int) -> List[int]:
        assert id in self._nodes and layer in self._nodes[id]
        assert 0 <= layer <= self._max_top_layer

        return self._nodes[id][layer]
