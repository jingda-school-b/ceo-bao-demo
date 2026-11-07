# -*- coding: utf-8 -*-
"""射线法单元测试。运行：python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fence import distance_to_ring, point_in_polygon, point_in_polygon_fast  # noqa: E402

SQUARE = [[113.0, 34.0], [114.0, 34.0], [114.0, 35.0], [113.0, 35.0]]
TRIANGLE = [[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]]


class TestPointInPolygon(unittest.TestCase):
    def test_inside(self):
        self.assertTrue(point_in_polygon(113.5, 34.5, SQUARE))

    def test_outside(self):
        self.assertFalse(point_in_polygon(115.0, 34.5, SQUARE))

    def test_outside_below(self):
        self.assertFalse(point_in_polygon(113.5, 33.0, SQUARE))

    def test_vertex_counts_once(self):
        # 射线正好穿过右侧两个顶点，半开区间写法保证不重复计数
        self.assertTrue(point_in_polygon(113.5, 34.0, SQUARE))

    def test_triangle_hypotenuse_side(self):
        self.assertTrue(point_in_polygon(1.0, 1.0, TRIANGLE))
        self.assertFalse(point_in_polygon(6.0, 6.0, TRIANGLE))

    def test_degenerate(self):
        self.assertFalse(point_in_polygon(1.0, 1.0, [[0, 0], [1, 1]]))

    def test_fast_path_same_as_slow(self):
        for p in [(113.5, 34.5), (115, 34.5), (113.0, 34.0), (112.9, 34.5)]:
            self.assertEqual(point_in_polygon(*p, SQUARE),
                             point_in_polygon_fast(*p, SQUARE))

    def test_distance_to_edge(self):
        d = distance_to_ring(113.5, 34.0, SQUARE)
        self.assertAlmostEqual(d, 0.0, places=9)


if __name__ == '__main__':
    unittest.main()
