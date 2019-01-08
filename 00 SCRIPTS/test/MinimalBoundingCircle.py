# 
# Smallest enclosing circle - Test suite (Python)
# 
# Copyright (c) 2017 Project Nayuki
# https://www.nayuki.io/page/smallest-enclosing-circle
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program (see COPYING.txt and COPYING.LESSER.txt).
# If not, see <http://www.gnu.org/licenses/>.

import random
import math
import rhinoscriptsyntax as rs

def make_circle(points):
	# Convert to float and randomize order
	shuffled = [(float(x), float(y)) for (x, y) in points]
	random.shuffle(shuffled)
	
	# Progressively add points to circle or recompute circle
	c = None
	for (i, p) in enumerate(shuffled):
		if c is None or not is_in_circle(c, p):
			c = _make_circle_one_point(shuffled[ : i + 1], p)
	return c

# One boundary point known
def _make_circle_one_point(points, p):
	c = (p[0], p[1], 0.0)
	for (i, q) in enumerate(points):
		if not is_in_circle(c, q):
			if c[2] == 0.0:
				c = make_diameter(p, q)
			else:
				c = _make_circle_two_points(points[ : i + 1], p, q)
	return c

# Two boundary points known
def _make_circle_two_points(points, p, q):
	circ = make_diameter(p, q)
	left = None
	right = None
	px, py = p
	qx, qy = q
	
	# For each point not in the two-point circle
	for r in points:
		if is_in_circle(circ, r):
			continue
		
		# Form a circumcircle and classify it on left or right side
		cross = _cross_product(px, py, qx, qy, r[0], r[1])
		c = make_circumcircle(p, q, r)
		if c is None:
			continue
		elif cross > 0.0 and (left is None or _cross_product(px, py, qx, qy, c[0], c[1]) > _cross_product(px, py, qx, qy, left[0], left[1])):
			left = c
		elif cross < 0.0 and (right is None or _cross_product(px, py, qx, qy, c[0], c[1]) < _cross_product(px, py, qx, qy, right[0], right[1])):
			right = c
	
	# Select which circle to return
	if left is None and right is None:
		return circ
	elif left is None:
		return right
	elif right is None:
		return left
	else:
		return left if (left[2] <= right[2]) else right

def make_circumcircle(p0, p1, p2):
	# Mathematical algorithm from Wikipedia: Circumscribed circle
	print
	ax, ay = p0
	bx, by = p1
	cx, cy = p2
	ox = (min(ax, bx, cx) + max(ax, bx, cx)) / 2.0
	oy = (min(ay, by, cy) + max(ay, by, cy)) / 2.0
	ax -= ox; ay -= oy
	bx -= ox; by -= oy
	cx -= ox; cy -= oy
	d = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2.0
	if d == 0.0:
		return None
	x = ox + ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
	y = oy + ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
	ra = math.hypot(x - p0[0], y - p0[1])
	rb = math.hypot(x - p1[0], y - p1[1])
	rc = math.hypot(x - p2[0], y - p2[1])
	return (x, y, max(ra, rb, rc))

def make_diameter(p0, p1):
	cx = (p0[0] + p1[0]) / 2.0
	cy = (p0[1] + p1[1]) / 2.0
	r0 = math.hypot(cx - p0[0], cy - p0[1])
	r1 = math.hypot(cx - p1[0], cy - p1[1])
	return (cx, cy, max(r0, r1))

def is_in_circle(c, p):
	return c is not None and math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] * (1 + 1e-14)

# Returns the smallest enclosing circle in O(n^4) time using the naive algorithm.
def _smallest_enclosing_circle_naive(points):
	# Degenerate cases
	if len(points) == 0:
		return None
	elif len(points) == 1:
		return (points[0][0], points[0][1], 0)
	
	# Try all unique pairs
	result = None
	for i in range(len(points)):
		p = points[i]
		for j in range(i + 1, len(points)):
			q = points[j]
			c = make_diameter(p, q)
			if (result is None or c[2] < result[2]) and \
					all(is_in_circle(c, r) for r in points):
				result = c
	if result is not None:
		return result  # This optimization is not mathematically proven
	
	# Try all unique triples
	for i in range(len(points)):
		p = points[i]
		for j in range(i + 1, len(points)):
			q = points[j]
			for k in range(j + 1, len(points)):
				r = points[k]
				c = make_circumcircle(p, q, r)
				if c is not None and (result is None or c[2] < result[2]) and \
						all(is_in_circle(c, s) for s in points):
					result = c
	
	if result is None:
		raise AssertionError()
	return result

if __name__ == "__main__":
    pts   = rs.AllObjects()
    ptsList = rs.coerce3dpointlist(pts)
    ptCoords = []
    for pt in ptsList:
        ptCoords.append([pt.X, pt.Y])
    
    results = _smallest_enclosing_circle_naive(ptCoords)
    
    rs.AddCircle((results[0], results[1], 0), results[2])