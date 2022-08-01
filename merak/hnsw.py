#!/usr/bin/env python3

import pprint
import random
from typing import List, Tuple
import heapq
from merak.point import Point
from merak.point_store import PointStore
from merak.candidate_set import CandidateSet
import logging


class HNSWConfig:
    def __init__(self) -> None:
        self.root_point = 0
        self.degree = 5
        self.max_degree = 10
        self.layer_factor = 4
        self.max_layer = 5
        self.candidate_set_size = 100
        self.insert_candidate_set_size = 1
        self.enable_heuristic = False


class HNSW:
    def __init__(self, config: HNSWConfig, point_store: PointStore) -> None:
        self.config_ = config
        self.point_store = point_store

    # def __init__(self, max_top_layer: int) -> None:
    #     self._graph = LayeredGraph(max_top_layer)

    def __search_layer(self, q: Point, candidates: List[Point], candidate_count: int, layer: int) -> List[Point]:
        ''' Search closest ef points in layer l, with ep as the entry point set

        Args:
            q: query element
            ep: entry points
            ef: number of nearest to q points to return
            l: layer number

        Returns:
            ef closest neighbors to q
        '''
        # assert isinstance(ep, List)

        visited = set([p.id for p in candidates])

        result: List[Tuple(float, Point)] = []

        # ep = [self._graph.get_point(id)
        #       for id in ep]  # transform from id to point
        # result = Points(q, False, ep)
        # candidates = Points(q, True, ep)

        candidate_set = CandidateSet(
            q, candidates, candidate_count, self.point_store)
        while True:
            p = candidate_set.pop()
            if p is None:
                break
            pushed = False
            pair = (-p.distance(q), p)
            if len(result) < candidate_count:
                heapq.heappush(result, pair)
                pushed = True
            else:
                x = heapq.heappushpop(result, pair)
                pushed = x[1]!=p
            if pushed:
                new_point_ids = []
                for n in p.neighbors[layer]:
                    if n in visited:
                        continue
                    visited.add(n)
                    new_point_ids.append(n)
                candidate_set.add(new_point_ids)
        result.sort(key=lambda x: -x[0])
        return [x[1] for x in result[:candidate_count]]

    def __select_neighbors_simple(self, q: Point, points: List[Point], m: int) -> List[Point]:
        ''' Select m nearest points from candidates to q 

        Args:
            q: base element
            candidates: candidate points 
            m: number of neighbors to return 

        Returns:
            m nearest points to q
        '''
        assert q is not None
        points.sort(key=lambda x: x.distance(q))
        return points[:m]

    # def __select_neighbors_heuristic(self, q: Point, c: List[int],
    #                                  m: int, l: int, extend: bool = True, keep: bool = True) -> List[Point]:
    #     ''' Select nearest neighbors heuristically

    #     Args:
    #         q: base element
    #         c: candidate points
    #         m: number of neighbors to return
    #         l: layer number
    #         extend: flag indicating whether or not to extend candidate list
    #         keep: flag indicating whether or not to add discarded points

    #     Returns:
    #         m points selected by the heuristic
    #     '''

    #     candidate_points = [self._graph.get_point(id) for id in c]
    #     result = Points(q, nearest=True)
    #     candidates = Points(q, nearest=True, points=candidate_points)

    #     if extend:
    #         for p in candidate_points:
    #             for next_id in self._graph.get_neighbor_ids(l, p.id):
    #                 if next_id not in candidates:
    #                     next_point = self._graph.get_point(next_id)
    #                     candidates.push(next_point)

    #     to_discard = Points(q, nearest=True)
    #     while len(candidates) > 0 and len(result) < m:
    #         curr = candidates.pop_nearest()
    #         # TODO(spw): is this condition right?
    #         if len(result) == 0 or curr.distance(q) < result.nearest().distance(q):
    #             if curr != q:
    #                 result.push(curr)
    #         else:
    #             to_discard.push(curr)

    #     if keep:
    #         while len(to_discard) > 0 and len(result) < m:
    #             curr = to_discard.pop_nearest()
    #             if curr != 1:
    #                 result.push(curr)

    #     return result.values

    def knn_search(self, q: Point, k: int, candidate_count: int = None, high_layer_condidate_count: int = 1) -> List[Point]:
        ''' Search the nearest k points for q

        Args:
            q: query element
            k: number of nearest neighbors to return
            ef: size of the dynamic candidate list
        Returns:
            K nearest elements to q
        '''

        if candidate_count is None:
            candidate_count = k*2

        root: Point = self.point_store.get_point(0, True)
        entry_points: List[Point] = [root]
        for l in range(self.config_.max_layer, 0, -1):
            nearest_points = self.__search_layer(
                q, entry_points, high_layer_condidate_count, l)
            entry_points = nearest_points
        nearest_points = self.__search_layer(
            q, entry_points, candidate_count, 0)

        return self.__select_neighbors_simple(q, nearest_points, k)

    def insert(self, q: Point,):
        ''' Insert element to graph with 
        '''
        new_layer = 0

        while new_layer < self.config_.max_layer and random.randint(0, self.config_.layer_factor-1) == 0:
            new_layer += 1

        # l in [new_layer+1, top_layer], from top to bottom.
        # only find one entry point for next layer
        root: Point = self.point_store.get_point(self.config_.root_point, True)
        entry_points: List[Point] = [root]

        for layer in range(self.config_.max_layer, new_layer, -1):
            nearest_points: List[Point] = self.__search_layer(
                q, entry_points, self.config_.insert_candidate_set_size, layer)
            entry_points = nearest_points

        # l in [0, new_layer], from top to bottom.
        # Find a entry point set for next layer
        for layer in range(min(self.config_.max_layer, new_layer), -1, -1):
            nearest_points: List[Point] = self.__search_layer(
                q, entry_points, self.config_.candidate_set_size, layer)
            if self.config_.enable_heuristic:
                neighbors: List[Point] = self.__select_neighbors_heuristic(
                    q, nearest_points, self.config_.degree, layer)
            else:
                neighbors: List[Point] = self.__select_neighbors_simple(
                    q, nearest_points, self.config_.degree)
            for n in neighbors:
                q.neighbors[layer].append(n.id)
            entry_points = nearest_points
        self.point_store.save_point(q)
