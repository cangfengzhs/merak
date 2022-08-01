#!/usr/bin/env python3

from asyncio import futures
from concurrent.futures.thread import _worker
from merak.point import Point
from typing import List, Tuple
from merak.point_store import PointStore
import heapq
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent

executor = ThreadPoolExecutor(max_workers=40)

class CandidateSet(object):
    def __init__(self, target: Point, points: List[Point], max_size: int, point_store: PointStore) -> None:
        global executor
        self.target = target
        self.max_size = max_size
        self.point_store = point_store
        self.executor = executor
        self.points: List[Tuple(float, Point)] = [(
            p.distance(self.target), p) for p in points]
        self.points.sort(key=lambda x: x[0])
        self.visited = set([p.id for p in points])
        self.furthest = self.points[-1]

    def pop(self) -> Point:

        # if len(self.futures) != 0:
        #     ret = concurrent.futures.wait(
        #         self.futures, return_when=concurrent.futures.FIRST_COMPLETED)
        #     done = ret.done
        #     self.futures = ret.not_done
        #     for f in done:
        #         point: Point = f.result()
        #         if point.id in self.visited:
        #             continue
        #         if len(self.points) < self.max_size:
        #             heapq.heappush(
        #                 self.points, (point.distance(self.target), point))
        #         else:
        #             heapq.heappushpop(
        #                 self.points, point.distance(self.target), point)
        if len(self.points) == 0:
            return None
        ret = heapq.heappop(self.points)
        return ret[1]

    def add(self, id_list: List[int]):
        points = self.executor.map(self.worker,id_list)
        for point in points:
            if point.id in self.visited:
                return
            self.visited.add(point.id)
            x = (point.distance(self.target), point)
            self.points.append(x)
        self.points.sort(key=lambda x:x[0])
        self.points = self.points[0:self.max_size]



    def worker(self, id: int) -> Point:
        point = self.point_store.get_point(id, True)
        return point
