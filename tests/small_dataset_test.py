import numpy as np
import unittest

from typing import Dict, List

from merak.point import Point
from merak.hnsw import HNSW


class TestHNSWSmallData(unittest.TestCase):
    def setUp(self) -> None:
        self._ml = 4
        self._ef = 100
        self._m = 3
        self._m_max = 8
        self._hnsw = HNSW(self._ml)

        self._point_num = 1000
        self._point_dim = 5

        # cook data
        arr = np.random.random((self._point_num, self._point_dim))
        self._points = []
        self._nearest = dict()
        self._k = 10
        for i in range(len(arr)):
            vec = arr[i]
            distance = np.linalg.norm(vec-arr, axis=1)
            index = np.array([k for k in range(len(arr))])
            dis_pairs = list(zip(distance, index))
            dis_pairs.sort(key=lambda x: x[0])

            self._nearest[i] = [Point(x[1], arr[x[1]])
                                for x in dis_pairs[1:self._k+1]]  # first is distance with itself
            p = Point(i, vec)
            self._hnsw.insert(p, self._m, self._m_max, self._ef, self._ml)
            self._points.append(p)

    def test_search(self):
        idx = 1
        knns = self._hnsw.knn_search(self._points[idx], self._k, self._ef)
        for p in knns:
            print(p, sep=" ")
        print()

        for p in self._nearest[idx]:
            print(p, sep=" ")
        print()


if __name__ == '__main__':
    unittest.main()
