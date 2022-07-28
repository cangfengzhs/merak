import unittest
import numpy as np

from point import Point
from graph import LayeredGraph, Node


class TestLayeredGraph(unittest.TestCase):
    def setUp(self) -> None:
        self._max_top_layer = 4
        self._graph = LayeredGraph(self._max_top_layer)

        # level 0, 1, 2
        self._p0 = Point(0, np.array([0, 0]))
        self._graph.add_point(2, self._p0)
        # level 0, 1
        self._p1 = Point(1, np.array([-1, 0]))
        self._graph.add_point(1, self._p1)
        self._p2 = Point(2, np.array([1, 0]))
        self._graph.add_point(1, self._p2)
        # level 0
        self._p3 = Point(3, np.array([0, -1]))
        self._graph.add_point(0, self._p3)
        self._p4 = Point(4, np.array([0, 1]))
        self._graph.add_point(0, self._p4)

        self._graph.add_edge(0, self._p0, self._p1)
        self._graph.add_edge(0, self._p0, self._p2)
        self._graph.add_edge(0, self._p0, self._p3)
        self._graph.add_edge(0, self._p0, self._p4)
        self._graph.add_edge(1, self._p0, self._p1)
        self._graph.add_edge(1, self._p0, self._p2)

    def test_add_edges(self):
        neighbors0 = self._graph.get_neighbors(0, self._p0)
        self.assertEqual(len(neighbors0), 4)
        for p in [self._p1, self._p2, self._p3, self._p4]:
            self.assertTrue(p in neighbors0)

        neighbors1 = self._graph.get_neighbors(1, self._p0)
        self.assertEqual(len(neighbors1), 2)
        for p in [self._p1, self._p2]:
            self.assertTrue(p in neighbors1)

    def test_set_neighbors(self):
        self._graph.set_neighbors(0, self._p0, [self._p1, self._p2])
        neighbors0 = self._graph.get_neighbors(0, self._p0)
        self.assertEqual(len(neighbors0), 2)
        for p in [self._p1, self._p2]:
            self.assertTrue(p in neighbors0)


if __name__ == '__main__':
    unittest.main()
