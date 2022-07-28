#!/usr/bin/env python3

import random
import math
from typing import List, Dict

from graph import LayeredGraph
from point import Point, Points


class HNSW:
    def __init__(self, max_top_layer: int) -> None:
        self._graph = LayeredGraph(max_top_layer)

    def __search_layer(self, q: Point, ep: List[Point], ef: int, l: int) -> List[Point]:
        ''' Search closest ef points in layer l, with ep as the entry point set

        Args:
            q: query element
            ep: entry points
            ef: number of nearest to q points to return
            l: layer number

        Returns:
            ef closest neighbors to q
        '''
        assert isinstance(ep, List)

        visited = {e for e in ep}
        result = Points(q, False, ep)
        candidates = Points(q, True, ep)

        while len(candidates) > 0:
            curr = candidates.pop_nearest()
            furthest_res = result.furthest()

            if curr.distance(q) > furthest_res.distance(q):
                break

            for next in self._graph.get_neighbors(l, curr):
                if next in visited:
                    continue
                visited.add(next)

                furthest_res = result.furthest()
                if next.distance(q) < furthest_res.distance(q) or len(result) < ef:
                    candidates.push(next)
                    result.push(next)
                    while len(result) > ef:
                        result.pop_furthest()

        return result.values

    def __select_neighbors_simple(self, q: Point, candidates: List[Point], m: int) -> List[Point]:
        ''' Select m nearest points from candidates to q 

        Args:
            q: base element
            candidates: candidate points 
            m: number of neighbors to return 

        Returns:
            m nearest points to q
        '''

        assert q is not None
        assert len(candidates) >= m

        points = Points(q, True, candidates)
        return [points.pop_nearest() for i in range(0, m)]

    def __select_neighbors_heuristic(self, q: Point, c: List[Point],
                                     m: int, l: int, extend: bool = True, keep: bool = True) -> List[Point]:
        ''' Select nearest neighbors heuristically

        Args:
            q: base element
            c: candidate points
            m: number of neighbors to return
            l: layer number
            extend: flag indicating whether or not to extend candidate list
            keep: flag indicating whether or not to add discarded points

        Returns:
            m points selected by the heuristic
        '''

        result = Points(q, nearest=True)
        candidates = Points(q, nearest=True, points=c)

        if extend:
            for curr in c:
                for next in self._graph.get_neighbors(l, curr):
                    if next not in candidates:
                        candidates.push(next)

        to_discard = Points(q, nearest=True)
        while len(candidates) > 0 and len(result) < m:
            curr = candidates.pop_nearest()
            # TODO(spw): is this condition right?
            if len(result) == 0 or curr.distance(q) < result.nearest().distance(q):
                result.push(curr)
            else:
                to_discard.push(curr)

        if keep:
            while len(to_discard) > 0 and len(result) < m:
                result.push(to_discard.pop_nearest())

        return result.values

    def knn_search(self, q: Point, k: int, ef: int) -> List[Point]:
        ''' Search the nearest k points for q

        Args:
            q: query element
            k: number of nearest neighbors to return
            ef: size of the dynamic candidate list
        Returns:
            K nearest elements to q
        '''
        entry_points = [] if self._graph.entry_point is None else [self._graph.entry_point]

        for l in range(self._graph.top_layer, 0, -1):
            nearest_points = self.__search_layer(q, entry_points, 1, l)
            entry_points = [Points(q, True, nearest_points).pop_nearest()]
        nearest_points = self.__search_layer(q, entry_points, ef, 0)

        num = min(len(nearest_points), k)
        points = Points(q, True, nearest_points)
        return [points.pop_nearest() for _ in range(num)]

    def insert(self, q: Point, m: int, m_max: int, ef: int, ml: int):
        ''' Insert element to graph with 

        Args:
            q: new element
            m: number of established connections
            m_max: maximum number of connections for each element per layer
            ef: size of the dynamic candidate list
            ml: normalization factor for level generation
        '''

        entry_points: List[Point] = [] if self._graph.entry_point is None else [
            self._graph.entry_point]
        new_layer = 0
        while new_layer < ml and random.randint(0, 10000) % 2 == 1:
            new_layer += 1
        self._graph.add_point(new_layer, q)

        # l in [new_layer+1, top_layer], from top to bottom.
        # only find one entry point for next layer
        for l in range(self._graph.top_layer, new_layer, -1):
            nearest_points = self.__search_layer(q, entry_points, 1, l)
            entry_points = [Points(q, nearest=True, points=nearest_points).nearest()]

        # l in [0, new_layer], from top to bottom.
        # Find a entry point set for next layer
        for l in range(min(self._graph.top_layer, new_layer), -1, -1):
            nearest_points = self.__search_layer(q, entry_points, ef, l)
            neighbors = self.__select_neighbors_heuristic(q, nearest_points, m, l)
            for e in neighbors:
                self._graph.add_edge(l, q, e)

            # shrink connections if old element's edges greater than m_max
            for e in neighbors:
                curr_neighbors = self._graph.get_neighbors(l, e)
                if len(curr_neighbors) > m_max:
                    new_neighbors = self.__select_neighbors_heuristic(
                        e, curr_neighbors, m_max, l)
                    self._graph.set_neighbors(l, e, new_neighbors)
            entry_points = nearest_points
