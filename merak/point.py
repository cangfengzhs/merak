#!/usr/bin/env python3

import heapq
import numpy as np
from typing import List, Set, Union
from collections import defaultdict


class Point(object):
    def __init__(self, id: int, vec: np.ndarray = []) -> None:
        self.id = id
        self.vector = vec
        self.neighbors = defaultdict(list)

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: 'Point') -> bool:
        assert type(self) == type(other)
        return self.id == other.id

    def __gt__(self, other: 'Point') -> bool:
        assert type(self) == type(other)
        return self.id > other.id

    def __str__(self) -> str:
        return f'point-{self.id}'

    def __repr__(self) -> str:
        return f'point-{self.id}'

    def distance(self, other: 'Point') -> float:
        if self.id ==0 or other.id == 0:
            return float('inf')
        return np.linalg.norm(self.vector - other.vector)
