#!/usr/bin/env python3

from merak.point import Point
from typing import List


class hnsw(object):
    def __init__(self) -> None:
        pass

    def insert(self, q: Point, M: int, Mmax: int, ef: int, mL: int):
        assert(False)

    def knn_search(self, q: Point, k: int, ef: int):
        assert(False)

    def __search_layer(self, q: Point, ep: Point, ef: int, lc: int):
        assert(False)

    def __select_neighbors_simple(self, q: Point, C: List[Point], M: int) -> List[Point]:
        assert(False)

    def __select_neighbors_heuristic(self, q: Point, C: List[Point], M: int, lc: int, extendCandidates: bool, keepPrunedConnections: bool):
        assert(False)
