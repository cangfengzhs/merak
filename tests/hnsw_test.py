import numpy as np
import unittest

from merak.point import Point
from merak.hnsw import HNSW


class TestHNSW(unittest.TestCase):
    def setUp(self) -> None:
        self._ml = 4
        self._ef = 4
        self._m = 3
        self._m_max = 8
        self._hnsw = HNSW(self._ml)

        self._p0 = Point(0, np.array([0, 0]))
        self._hnsw.insert(self._p0, self._m, self._m_max, self._ef, self._ml)
        self._p1 = Point(1, np.array([-1, 0]))
        self._hnsw.insert(self._p1, self._m, self._m_max, self._ef, self._ml)
        self._p2 = Point(2, np.array([1, 0]))
        self._hnsw.insert(self._p2, self._m, self._m_max, self._ef, self._ml)
        self._p3 = Point(3, np.array([0, -1]))
        self._hnsw.insert(self._p3, self._m, self._m_max, self._ef, self._ml)
        self._p4 = Point(4, np.array([0, 1]))
        self._hnsw.insert(self._p4, self._m, self._m_max, self._ef, self._ml)

    def test_search(self):
        knns = self._hnsw.knn_search(self._p0, 4, self._ef)
        for p in knns:
            print(p)

        q = Point(5, np.array([0, 2]))
        knns = self._hnsw.knn_search(q, 2, self._ef)
        for p in knns:
            print(p)


if __name__ == '__main__':
    unittest.main()
