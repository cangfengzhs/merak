#!/usr/bin/env python3

import typing as T
import math
import heapq
import numpy as np
from typing import List, Dict


class Point(object):
    def __init__(self, id: int, vec: np.ndarray, *args, **kwargs) -> None:
        self._id = id
        self._vec = vec
        self.__dict__.update(kwargs)

    def __hash__(self) -> int:
        return self._id

    def __eq__(self, other: 'Point') -> bool:
        if type(self) != type(other):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        return f'point-{self._id}'

    @property
    def id(self):
        return self._id

    @property
    def vec(self):
        return self._vec

    def distance(self, other: 'Point') -> float:
        return np.linalg.norm(self.vec - other.vec)


class Points:
    ''' Helper class to get the nearest and furthest element in an element vector.
    '''

    def __init__(self, base: Point, nearest: bool = True, points: T.List[Point] = []):
        self._points_pair: T.List[(int, Point)] = []
        self._points_set: T.Set[int] = set()
        self._base = base
        self._nearest = nearest
        for p in points:
            self.push(p)

    def __len__(self) -> int:
        return len(self._points_pair)

    def __contains__(self, p: Point) -> bool:
        return p.id in self._points_set

    @property
    def base(self) -> Point:
        return self._base

    @property
    def values(self) -> T.List[Point]:
        return [pair[1] for pair in self._points_pair]

    def push(self, p: Point):
        assert p.id not in self._points_set

        if self._nearest:
            heapq.heappush(self._points_pair, (p.distance(self._base), p))
        else:
            heapq.heappush(self._points_pair, (-p.distance(self._base), p))

        self._points_set.add(p.id)

    def pop_nearest(self) -> Point:
        assert self._nearest is True
        _, p = heapq.heappop(self._points_pair)
        self._points_set.remove(p.id)
        return p

    def nearest(self) -> Point:
        if self._nearest:
            return self._points_pair[0][1]
        else:
            return max(self._points_pair)[1]

    def pop_furthest(self) -> Point:
        assert self._nearest is False
        _, p = heapq.heappop(self._points_pair)
        self._points_set.remove(p.id)
        return p

    def furthest(self) -> Point:
        if self._nearest is False:
            return self._points_pair[0][1]
        else:
            return max(self._points_pair)[1]
