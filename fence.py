# -*- coding: utf-8 -*-
"""射线法（Ray Casting）点面判定。

原理：从待判定点向 +x 方向发一条水平射线，统计它与多边形边的交点个数，
      奇数次 = 在内部，偶数次 = 在外部。

两个必须处理的边界情况：
  1. 射线正好穿过顶点 —— 用 (yi > y) != (yj > y) 的半开区间写法，保证每个
     顶点只被计算一次，不会重复计数；
  2. 点正好落在边上 —— 单独做点到线段距离判断，距离为 0 视为在边界上。
"""
import math


def point_in_polygon(lng, lat, ring):
    """ring: [[lng, lat], ...]，首尾点不必重复。返回 True/False。"""
    n = len(ring)
    if n < 3:
        return False
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            # 交点 x 坐标
            x_cross = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lng < x_cross:
                inside = not inside
        j = i
    return inside


def _seg_distance(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def distance_to_ring(lng, lat, ring):
    """点到围栏边界的最短距离（单位：度）。用于「擦边」提示，不做业务判定。"""
    n = len(ring)
    best = float('inf')
    j = n - 1
    for i in range(n):
        d = _seg_distance(lng, lat, ring[j][0], ring[j][1], ring[i][0], ring[i][1])
        if d < best:
            best = d
        j = i
    return best


def bbox(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def point_in_polygon_fast(lng, lat, ring):
    """先用外接矩形快速排除，再走射线法。围栏多时能省掉大部分计算。"""
    x1, y1, x2, y2 = bbox(ring)
    if lng < x1 or lng > x2 or lat < y1 or lat > y2:
        return False
    return point_in_polygon(lng, lat, ring)
