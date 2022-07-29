import unittest
import numpy as np

from merak.point import Point, Points


class TestPointsMethods(unittest.TestCase):
    def setUp(self):
        self.vec0 = np.array([0, 0])
        self.vec1 = np.array([0, 1])
        self.vec2 = np.array([1, 1])
        self.vec3 = np.array([2, 1])

        self.p0 = Point(0, self.vec0)
        self.p1 = Point(1, self.vec1)
        self.p2 = Point(2, self.vec2)
        self.p3 = Point(3, self.vec3)

        self.points = [self.p0, self.p1, self.p2, self.p3]

    def test_base(self):
        points = Points(self.p0, True, self.points)
        self.assertEqual(points.base, self.p0)

    def test_length(self):
        points = Points(self.p0, True, self.points)
        self.assertEqual(len(points), 4)

    def test_contains(self):
        points = Points(self.p0, True, self.points)
        self.assertTrue(self.p0 in points)
        self.assertTrue(self.p1 in points)
        self.assertTrue(self.p2 in points)
        self.assertTrue(self.p3 in points)

    def test_nearest(self):
        points = Points(self.p0, True, self.points)

        try:
            points.pop_furthest()
        except Exception as e:
            self.assertTrue(isinstance(e, AssertionError))

        self.assertEqual(points.furthest(), self.p3)
        self.assertEqual(points.nearest(), self.p0)
        self.assertEqual(points.pop_nearest(), self.p0)

        self.assertEqual(points.furthest(), self.p3)
        self.assertEqual(points.nearest(), self.p1)
        self.assertEqual(points.pop_nearest(), self.p1)

        self.assertEqual(points.furthest(), self.p3)
        self.assertEqual(points.nearest(), self.p2)
        self.assertEqual(points.pop_nearest(), self.p2)

        self.assertEqual(points.furthest(), self.p3)
        self.assertEqual(points.nearest(), self.p3)
        self.assertEqual(points.pop_nearest(), self.p3)

    def test_furthest(self):
        points = Points(self.p0, False, self.points)

        try:
            points.pop_nearest()
        except Exception as e:
            self.assertTrue(isinstance(e, AssertionError))

        self.assertEqual(points.nearest(), self.p0)
        self.assertEqual(points.furthest(), self.p3)
        self.assertEqual(points.pop_furthest(), self.p3)

        self.assertEqual(points.furthest(), self.p2)
        self.assertEqual(points.nearest(), self.p0)
        self.assertEqual(points.pop_furthest(), self.p2)

        self.assertEqual(points.furthest(), self.p1)
        self.assertEqual(points.nearest(), self.p0)
        self.assertEqual(points.pop_furthest(), self.p1)

        self.assertEqual(points.furthest(), self.p0)
        self.assertEqual(points.nearest(), self.p0)
        self.assertEqual(points.pop_furthest(), self.p0)

    def test_values(self):
        points = Points(self.p0, False, self.points)

        self.assertEqual(len(points.values), len(self.points))
        self.assertEqual(type(points.values), type(self.points))
        for val in points.values:
            self.assertTrue(val in self.points)


if __name__ == '__main__':
    unittest.main()
