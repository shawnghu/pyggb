import numpy as np
import geo_types as gt
from typing import List, Tuple, Union, Optional, Any

def angle_ppp(p1: gt.Point, p2: gt.Point, p3: gt.Point) -> gt.Angle:
    return gt.Angle(p2.a, p2.a-p1.a, p2.a-p3.a)

def angular_bisector_ll(l1: gt.Line, l2: gt.Line) -> List[gt.Line]:
    x = intersect_ll(l1, l2)
    n1, n2 = l1.n, l2.n
    if np.dot(n1, n2) > 0: n = n1 + n2
    else: n = n1 - n2
    return [
        gt.Line(vec, np.dot(vec, x.a))
        for vec in (n, gt.vector_perp_rot(n))
    ]

def angular_bisector_ppp(p1: gt.Point, p2: gt.Point, p3: gt.Point) -> gt.Line:
    v1 = p2.a - p1.a
    v2 = p2.a - p3.a
    v1 /= np.linalg.norm(v1)
    v2 /= np.linalg.norm(v2)
    if np.dot(v1, v2) < 0: n = v1-v2
    else: n = gt.vector_perp_rot(v1+v2)
    return gt.Line(n, np.dot(p2.a, n))

def angular_bisector_ss(l1: gt.Segment, l2: gt.Segment) -> List[gt.Line]:
    return angular_bisector_ll(l1, l2)

def are_collinear_ppp(p1: gt.Point, p2: gt.Point, p3: gt.Point) -> gt.Boolean:
    return gt.Boolean(np.linalg.matrix_rank([p1.a-p2.a, p1.a-p3.a]) <= 1)

def are_concurrent_lll(l1: gt.Line, l2: gt.Line, l3: gt.Line) -> gt.Boolean:
    lines = l1,l2,l3
    
    differences = []
    for i in range(3):
        remaining = [l.n for l in lines[:i]+lines[i+1:]]
        prod = np.abs(np.cross(*remaining))
        differences.append((prod, i, lines[i]))

    l1, l2, l3 = tuple(zip(*sorted(differences)))[2]
    x = intersect_ll(l1, l2)
    return gt.Boolean(np.isclose(np.dot(x.a, l3.n), l3.c))

def are_concurrent(o1: Union[gt.Line, gt.Circle], o2: Union[gt.Line, gt.Circle], o3: Union[gt.Line, gt.Circle]) -> gt.Boolean:
    cand = []
    try:
        #if True:
        if isinstance(o1, gt.Line) and isinstance(o2, gt.Line):
            cand = [intersect_ll(o1, o2)]  # Wrap single point in list
        elif isinstance(o1, gt.Line) and isinstance(o2, gt.Circle):
            cand = intersect_lc(o1, o2)
        elif isinstance(o1, gt.Circle) and isinstance(o2, gt.Line):
            cand = intersect_cl(o1, o2)
        elif isinstance(o1, gt.Circle) and isinstance(o2, gt.Circle):
            cand = intersect_cc(o1, o2)
    except: pass

    for p in cand:
        for obj in (o1,o2,o3):
            if not obj.contains(p.a): break
        else: return gt.Boolean(True)

    return gt.Boolean(False)

def are_concyclic_pppp(p1: gt.Point, p2: gt.Point, p3: gt.Point, p4: gt.Point) -> gt.Boolean:
    z1, z2, z3, z4 = (gt.a_to_cpx(p.a) for p in (p1, p2, p3, p4))
    cross_ratio = (z1-z3)*(z2-z4)*(((z1-z4)*(z2-z3)).conjugate())
    return gt.Boolean(np.isclose(cross_ratio.imag, 0))

def are_congruent_aa(a1: gt.Angle, a2: gt.Angle) -> gt.Boolean:
    #print(a1.angle, a2.angle)
    result = np.isclose((a1.angle-a2.angle+1)%(2*np.pi), 1)
    result = (result or np.isclose((a1.angle+a2.angle+1)%(2*np.pi), 1))
    return gt.Boolean(result)

def are_complementary_aa(a1: gt.Angle, a2: gt.Angle) -> gt.Boolean:
    #print(a1.angle, a2.angle)
    result = np.isclose((a1.angle-a2.angle)%(2*np.pi), np.pi)
    result = (result or np.isclose((a1.angle+a2.angle)%(2*np.pi), np.pi))
    return gt.Boolean(result)

def are_congruent_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Boolean:
    l1, l2 = (
        np.linalg.norm(s.end_points[1] - s.end_points[0])
        for s in (s1, s2)
    )
    return gt.Boolean(np.isclose(l1, l2))

def are_equal_mm(m1: Union[gt.Measure, float, int], m2: Union[gt.Measure, float, int]) -> gt.Boolean:
    # Handle both Measure objects and numeric values
    if isinstance(m1, gt.Measure) and isinstance(m2, gt.Measure):
        assert(m1.dim == m2.dim)
        return gt.Boolean(np.isclose(m1.x, m2.x))
    elif isinstance(m1, gt.Measure):
        # m2 is a numeric value
        return gt.Boolean(np.isclose(m1.x, float(m2)))
    elif isinstance(m2, gt.Measure):
        # m1 is a numeric value
        return gt.Boolean(np.isclose(float(m1), m2.x))
    else:
        # Both are numeric values
        return gt.Boolean(np.isclose(float(m1), float(m2)))

def are_equal_mi(m: gt.Measure, i: int) -> gt.Boolean:
    assert(m.dim == 0)
    return gt.Boolean(np.isclose(m.x, i))

def are_equal_pp(p1: gt.Point, p2: gt.Point) -> gt.Boolean:
    return gt.Boolean(np.isclose(p1.a, p2.a).all())

def are_parallel_ll(l1: gt.Line, l2: gt.Line) -> gt.Boolean:
    if np.isclose(l1.n, l2.n).all(): return gt.Boolean(True)
    if np.isclose(l1.n, -l2.n).all(): return gt.Boolean(True)
    return gt.Boolean(False)

def are_parallel_ls(l: gt.Line, s: gt.Segment) -> gt.Boolean:
    return are_parallel_ll(l, s)

def are_parallel_rr(r1: gt.Ray, r2: gt.Ray) -> gt.Boolean:
    return are_parallel_ll(r1, r2)

def are_parallel_sl(s: gt.Segment, l: gt.Line) -> gt.Boolean:
    return are_parallel_ll(s, l)

def are_parallel_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Boolean:
    return are_parallel_ll(s1, s2)

def are_perpendicular_ll(l1: gt.Line, l2: gt.Line) -> gt.Boolean:
    if np.isclose(l1.n, l2.v).all(): return gt.Boolean(True)
    if np.isclose(l1.n, -l2.v).all(): return gt.Boolean(True)
    return gt.Boolean(False)

def are_perpendicular_lr(l: gt.Line, r: gt.Ray) -> gt.Boolean:
    return are_perpendicular_ll(l, r)

def are_perpendicular_rl(r: gt.Ray, l: gt.Line) -> gt.Boolean:
    return are_perpendicular_ll(r, l)

def are_perpendicular_sl(s: gt.Segment, l: gt.Line) -> gt.Boolean:
    return are_perpendicular_ll(s, l)

def are_perpendicular_ls(l: gt.Line, s: gt.Segment) -> gt.Boolean:
    return are_perpendicular_ll(l, s)

def are_perpendicular_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Boolean:
    return are_perpendicular_ll(s1, s2)

def area(*points: gt.Point) -> gt.Measure:
    p0 = points[0].a
    vecs = [p.a - p0 for p in points[1:]]
    cross_sum = sum(
        np.cross(v1, v2)
        for v1, v2 in zip(vecs, vecs[1:])
    )
    return gt.Measure(abs(cross_sum)/2, 2)

def area_P(polygon: gt.Polygon) -> gt.Measure:
    points = [gt.Point(p) for p in polygon.points]
    return area(*points)

def center_c(c: gt.Circle) -> gt.Point:
    return gt.Point(c.c)

def circle_pp(center: gt.Point, passing_point: gt.Point) -> gt.Circle:
    return gt.Circle(center.a, np.linalg.norm(center.a - passing_point.a))

def circle_ppp(p1: gt.Point, p2: gt.Point, p3: gt.Point) -> gt.Circle:
    axis1 = line_bisector_pp(p1, p2)
    axis2 = line_bisector_pp(p1, p3)
    center = intersect_ll(axis1, axis2)
    return circle_pp(center, p1)

def circle_pm(p: gt.Point, m: gt.Measure) -> gt.Circle:
    assert(m.dim == 1)
    return gt.Circle(p.a, m.x)

def circle_ps(p: gt.Point, s: gt.Segment) -> gt.Circle:
    return gt.Circle(p.a, s.length)

def contained_by_pc(point: gt.Point, by_circle: gt.Circle) -> gt.Boolean:
    return gt.Boolean(by_circle.contains(point.a))

def contained_by_pl(point: gt.Point, by_line: gt.Line) -> gt.Boolean:
    return gt.Boolean(by_line.contains(point.a))

def distance_pp(p1: gt.Point, p2: gt.Point) -> gt.Measure:
    return gt.Measure(np.linalg.norm(p1.a-p2.a), 1)

def equality_aa(a1: gt.Angle, a2: gt.Angle) -> gt.Boolean:
    return are_congruent_aa(a1, a2)

def equality_mm(m1: gt.Measure, m2: gt.Measure) -> gt.Boolean:
    assert(m1.dim == m2.dim)
    return gt.Boolean(np.isclose(m1.x, m2.x))

def equality_ms(m: gt.Measure, s: gt.Segment) -> gt.Boolean:
    assert(m.dim == 1)
    return gt.Boolean(np.isclose(m.x, s.length))

def equality_mi(m: gt.Measure, i: int) -> gt.Boolean:
    assert(m.dim == 0 or i == 0)
    return gt.Boolean(np.isclose(m.x, i))

def equality_pp(p1: gt.Point, p2: gt.Point) -> gt.Boolean:
    return are_equal_pp(p1, p2)

def equality_Pm(polygon: gt.Polygon, m: gt.Measure) -> gt.Boolean:
    assert(m.dim == 2)
    return gt.Boolean(np.isclose(area_P(polygon).x, m.x))

def equality_PP(poly1: gt.Polygon, poly2: gt.Polygon) -> gt.Boolean:
    return gt.Boolean(np.isclose(area_P(poly1).x, area_P(poly2).x))

def equality_sm(s: gt.Segment, m: gt.Measure) -> gt.Boolean:
    return equality_ms(m,s)

def equality_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Boolean:
    return gt.Boolean(np.isclose(s1.length, s2.length))

def equality_si(s: gt.Segment, i: int) -> None:
    pass # TODO

def intersect_ll(line1: gt.Line, line2: gt.Line) -> gt.Point:
    matrix = np.stack((line1.n, line2.n))
    b = np.array((line1.c, line2.c))
    assert(not np.isclose(np.linalg.det(matrix), 0))
    return gt.Point(np.linalg.solve(matrix, b))

def intersect_lc(line: gt.Line, circle: gt.Circle) -> List[gt.Point]:
    # shift circle to center
    y = line.c - np.dot(line.n, circle.c)
    x_squared = circle.r_squared - y**2
    if np.isclose(x_squared, 0): 
        return [gt.Point(y*line.n + circle.c)]  # Wrap single point in a list
    assert(x_squared > 0)

    x = np.sqrt(x_squared)
    return [
        gt.Point(x*line.v + y*line.n + circle.c),
        gt.Point(-x*line.v + y*line.n + circle.c),
    ]

def intersect_cc(circle1: gt.Circle, circle2: gt.Circle) -> List[gt.Point]:
    center_diff = circle2.c - circle1.c
    center_dist_squared = np.dot(center_diff, center_diff)
    center_dist = np.sqrt(center_dist_squared)
    relative_center = (circle1.r_squared - circle2.r_squared) / center_dist_squared
    center = (circle1.c + circle2.c)/2 + relative_center*center_diff/2

    rad_sum  = circle1.r + circle2.r
    rad_diff = circle1.r - circle2.r
    det = (rad_sum**2 - center_dist_squared) * (center_dist_squared - rad_diff**2)
    if np.isclose(det, 0): 
        return [gt.Point(center)]  # Already returning a list
    assert(det > 0)
    center_deviation = np.sqrt(det)
    center_deviation = np.array(((center_deviation,),(-center_deviation,)))

    return [
        gt.Point(center + center_dev)
        for center_dev in center_deviation * 0.5*gt.vector_perp_rot(center_diff) / center_dist_squared
    ]

def intersect_cl(c: gt.Circle, l: gt.Line) -> List[gt.Point]:
    return intersect_lc(l,c)

def intersect_Cl(arc: gt.Arc, line: gt.Line) -> List[gt.Point]:
    results = intersect_lc(line, arc)
    return [x for x in results if arc.contains(x.a)]

def intersect_cs(circle: gt.Circle, segment: gt.Segment) -> List[gt.Point]:
    results = intersect_lc(segment, circle)
    return [x for x in results if segment.contains(x.a)]

def intersect_lr(line: gt.Line, ray: gt.Ray) -> gt.Point:
    result = intersect_ll(line, ray)
    assert(ray.contains(result.a))
    return result

def intersect_ls(line: gt.Line, segment: gt.Segment) -> gt.Point:
    result = intersect_ll(line, segment)
    assert(segment.contains(result.a))
    return result

def intersect_rl(ray: gt.Ray, line: gt.Line) -> gt.Point:
    result = intersect_ll(ray, line)
    assert(ray.contains(result.a))
    return result

def intersect_rr(r1: gt.Ray, r2: gt.Ray) -> gt.Point:
    result = intersect_ll(r1, r2)
    assert(r1.contains(result.a))
    assert(r2.contains(result.a))
    return result

def intersect_rs(ray: gt.Ray, segment: gt.Segment) -> gt.Point:
    result = intersect_ll(ray, segment)
    assert(ray.contains(result.a))
    assert(segment.contains(result.a))
    return result

def intersect_sl(segment: gt.Segment, line: gt.Line) -> gt.Point:
    return intersect_ls(line, segment)

def intersect_sr(segment: gt.Segment, ray: gt.Ray) -> gt.Point:
    return intersect_rs(ray, segment)

def intersect_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Point:
    result = intersect_ll(s1, s2)
    assert(s1.contains(result.a))
    assert(s2.contains(result.a))
    return result

def line_bisector_pp(p1: gt.Point, p2: gt.Point) -> gt.Line:
    p = (p1.a+p2.a)/2
    n = p2.a-p1.a
    assert((n != 0).any())
    return gt.Line(n, np.dot(n,p))

def line_bisector_s(segment: gt.Segment) -> gt.Line:
    p1, p2 = segment.end_points
    p = (p1+p2)/2
    n = p2-p1
    return gt.Line(n, np.dot(n,p))

def line_pl(point: gt.Point, line: gt.Line) -> gt.Line:
    return gt.Line(line.n, np.dot(line.n, point.a))

def line_pp(p1: gt.Point, p2: gt.Point) -> gt.Line:
    assert((p1.a != p2.a).any())
    n = gt.vector_perp_rot(p1.a-p2.a)
    return gt.Line(n, np.dot(p1.a, n))

def line_pr(point: gt.Point, ray: gt.Ray) -> gt.Line:
    return line_pl(point, ray)

def line_ps(point: gt.Point, segment: gt.Segment) -> gt.Line:
    return line_pl(point, segment)

def midpoint_pp(p1: gt.Point, p2: gt.Point) -> gt.Point:
    return gt.Point((p1.a+p2.a)/2)

def midpoint_s(segment: gt.Segment) -> gt.Point:
    p1, p2 = segment.end_points
    return gt.Point((p1+p2)/2)

def minus_mm(m1: Union[gt.Measure, float, int], m2: Union[gt.Measure, float, int]) -> gt.Measure:
    # Handle both Measure objects and numeric values
    if isinstance(m1, gt.Measure) and isinstance(m2, gt.Measure):
        assert(m1.dim == m2.dim)
        return gt.Measure(m1.x - m2.x, m1.dim)
    elif isinstance(m1, gt.Measure):
        # m2 is a numeric value
        # Assume m2 has the same dimension as m1
        return gt.Measure(m1.x - float(m2), m1.dim)
    elif isinstance(m2, gt.Measure):
        # m1 is a numeric value
        # Assume m1 has the same dimension as m2
        return gt.Measure(float(m1) - m2.x, m2.dim)
    else:
        # Both are numeric values - assume they are dimensionless
        return gt.Measure(float(m1) - float(m2), 0)

def minus_ms(m: gt.Measure, s: gt.Segment) -> gt.Measure:
    assert(m.dim == 1)
    return gt.Measure(m.x-s.length, 1)

def minus_sm(s: gt.Segment, m: gt.Measure) -> gt.Measure:
    assert(m.dim == 1)
    return gt.Measure(s.length-m.x, 1)

def minus_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Measure:
    return gt.Measure(s1.length-s2.length, 1)

def mirror_cl(circle: gt.Circle, by_line: gt.Line) -> gt.Circle:
    return gt.Circle(
        center = circle.c + by_line.n*2*(by_line.c - np.dot(circle.c, by_line.n)),
        r = circle.r,
    )

def mirror_cp(circle: gt.Circle, by_point: gt.Point) -> gt.Circle:
    return gt.Circle(
        center = 2*by_point.a - circle.c,
        r = circle.r
    )

def mirror_ll(line: gt.Line, by_line: gt.Line) -> gt.Line:
    n = line.n - by_line.n * 2*np.dot(line.n, by_line.n)
    return gt.Line(n, line.c + 2*by_line.c * np.dot(n, by_line.n) )

def mirror_lp(line: gt.Line, by_point: gt.Point) -> gt.Line:
    return gt.Line(line.n, 2*np.dot(by_point.a, line.n) - line.c)

def mirror_pc(point: gt.Point, by_circle: gt.Circle) -> gt.Point:
    v = point.a - by_circle.c
    assert(not np.isclose(v,0).all())
    return gt.Point(by_circle.c + v * (by_circle.r_squared / gt.square_norm(v)) )

def mirror_pl(point: gt.Point, by_line: gt.Line) -> gt.Point:
    return gt.Point(point.a + by_line.n*2*(by_line.c - np.dot(point.a, by_line.n)))

def mirror_pp(point: gt.Point, by_point: gt.Point) -> gt.Point:
    return gt.Point(2*by_point.a - point.a)

def mirror_ps(point: gt.Point, segment: gt.Segment) -> gt.Point:
    return mirror_pl(point, segment)

def orthogonal_line_pl(point: gt.Point, line: gt.Line) -> gt.Line:
    return gt.Line(line.v, np.dot(line.v, point.a))

def orthogonal_line_pr(point: gt.Point, ray: gt.Ray) -> gt.Line:
    return orthogonal_line_pl(point, ray)

def orthogonal_line_ps(point: gt.Point, segment: gt.Segment) -> gt.Line:
    return orthogonal_line_pl(point, segment)

def point_() -> gt.Point:
    return gt.Point(np.random.normal(size = 2))

def point_c(circle: gt.Circle) -> gt.Point:
    return gt.Point(circle.c + circle.r * gt.random_direction())

def point_l(line: gt.Line) -> gt.Point:
    return gt.Point(line.c * line.n + line.v * np.random.normal() )

def point_s(segment: gt.Segment) -> gt.Point:
    return gt.Point(gt.interpolate(segment.end_points[0], segment.end_points[1], np.random.random()))

def point_at_distance(point: gt.Point, distance: Union[gt.Measure, float, int]) -> gt.Point:
    """
    Create a point at a specified distance from an existing point.
    The direction is chosen randomly.
    """
    # Handle both Measure objects and numeric values
    if isinstance(distance, gt.Measure):
        assert(distance.dim == 1 and distance.x > 0)
        dist_value = distance.x
    else:
        # If it's a direct numeric value
        dist_value = float(distance)
        assert(dist_value > 0)
        
    return gt.Point(point.a + dist_value * gt.random_direction())


def polar_pc(point: gt.Point, circle: gt.Circle) -> gt.Line:
    n = point.a - circle.c
    assert(not np.isclose(n, 0).all())
    return gt.Line(n, np.dot(n, circle.c) + circle.r_squared)

def polygon_ppi(p1: gt.Point, p2: gt.Point, n: int) -> List[Union[gt.Polygon, gt.Segment, gt.Point]]:
    p1c,p2c = (gt.a_to_cpx(p.a) for p in (p1,p2))
    alpha = 2*np.pi/n
    center = p2c + (p1c-p2c)/(1-np.exp(-alpha*1j))
    v = p2c-center
    points = [gt.Point(gt.cpx_to_a(center + v*np.exp(i*alpha*1j))) for i in range(1,n-1)]
    raw_points = [p.a for p in [p1,p2]+points]
    segments = [
        gt.Segment(p1, p2)
        for p1,p2 in zip(raw_points, raw_points[1:] + raw_points[:1])
    ]
    return [gt.Polygon(raw_points)] + segments + points

def polygon(*points: gt.Point) -> List[Union[gt.Polygon, gt.Segment]]:
    raw_points = [p.a for p in points]
    segments = [
        gt.Segment(p1, p2)
        for p1,p2 in zip(raw_points, raw_points[1:] + raw_points[:1])
    ]
    return [gt.Polygon(raw_points)] + segments

def power_mi(m: gt.Measure, i: int) -> gt.Measure:
    assert(i == 2)
    return gt.Measure(m.x ** i, m.dim*i)

def power_si(s: gt.Segment, i: int) -> gt.Measure:
    return gt.Measure(s.length ** i, i)

def prove_b(x: gt.Boolean) -> gt.Boolean:
    print(x.b)
    return x

def radius_c(circle: gt.Circle) -> gt.Measure:
    return gt.Measure(circle.r, 1)

def ratio_mm(m1: gt.Measure, m2: gt.Measure) -> gt.Measure:
    assert(not np.isclose(m1.x, 0))
    return gt.Measure(m1.x / m2.x, m1.dim - m2.dim)

def ray_pp(p1: gt.Point, p2: gt.Point) -> gt.Ray:
    return gt.Ray(p1.a, p2.a-p1.a)

def rotate_pap(point: gt.Point, angle: gt.Angle, by_point: gt.Point) -> gt.Point:
    return gt.Point(by_point.a + gt.rotate_vec(point.a - by_point.a, angle.angle))

def rotate_pAp(point: gt.Point, angle_size: gt.AngleSize, by_point: gt.Point) -> gt.Point:
    return gt.Point(by_point.a + gt.rotate_vec(point.a - by_point.a, angle_size.x))

def segment_pp(p1: gt.Point, p2: gt.Point) -> gt.Segment:
    return gt.Segment(p1.a, p2.a)

def semicircle(p1: gt.Point, p2: gt.Point) -> gt.Arc:
    vec = gt.a_to_cpx(p1.a - p2.a)
    return gt.Arc(
        (p1.a + p2.a)/2,
        abs(vec)/2,
        [np.angle(v) for v in (-vec, vec)]
    )

def sum_mm(m1: Union[gt.Measure, float, int], m2: Union[gt.Measure, float, int]) -> gt.Measure:
    # Handle both Measure objects and numeric values
    if isinstance(m1, gt.Measure) and isinstance(m2, gt.Measure):
        assert(m1.dim == m2.dim)
        return gt.Measure(m1.x + m2.x, m1.dim)
    elif isinstance(m1, gt.Measure):
        # m2 is a numeric value
        # Assume m2 has the same dimension as m1
        return gt.Measure(m1.x + float(m2), m1.dim)
    elif isinstance(m2, gt.Measure):
        # m1 is a numeric value
        # Assume m1 has the same dimension as m2
        return gt.Measure(float(m1) + m2.x, m2.dim)
    else:
        # Both are numeric values - assume they are dimensionless
        return gt.Measure(float(m1) + float(m2), 0)

def sum_ms(m: gt.Measure, s: gt.Segment) -> gt.Measure:
    assert(m.dim == 1)
    return gt.Measure(m.x + s.length, 1)

def sum_mi(m: gt.Measure, i: int) -> gt.Measure:
    assert(m.dim == 0)
    return gt.Measure(m.x + i, 0)

def sum_ss(s1: gt.Segment, s2: gt.Segment) -> gt.Measure:
    return gt.Measure(s1.length + s2.length, 1)

def tangent_pc(point: gt.Point, circle: gt.Circle) -> List[gt.Line]:
    polar = polar_pc(point, circle)
    intersections = intersect_lc(polar, circle)
    if len(intersections) == 2:
        return [line_pp(point, x) for x in intersections]
    else: 
        return [polar]  # Wrap single line in a list

def touches_cc(c1: gt.Circle, c2: gt.Circle) -> gt.Boolean:
    lens = c1.r, c2.r, np.linalg.norm(c1.c-c2.c)
    return gt.Boolean(np.isclose(sum(lens), 2*max(lens)))

def touches_lc(line: gt.Line, circle: gt.Circle) -> gt.Boolean:
    return gt.Boolean(
        np.isclose(circle.r, np.abs(np.dot(line.n, circle.c) - line.c) )
    )

def touches_cl(circle: gt.Circle, line: gt.Line) -> gt.Boolean:
    return touches_lc(line, circle)

def translate_pv(point: gt.Point, vector: gt.Vector) -> gt.Point:
    return gt.Point(point.a + vector.v)

def vector_pp(p1: gt.Point, p2: gt.Point) -> gt.Vector:
    return gt.Vector((p1.a, p2.a))

def measure(x: Any) -> Any:
    """
    Marks an element as the final measurement for a construction file.
    Simply returns the input element.
    """
    return x

def point_at_distance_along_line(line: gt.Line, reference_point: gt.Point, distance: float) -> gt.Point:
    """Create a point on a line at a specified distance from the closest point on the line to a reference point."""
    # Project reference point onto the line
    closest_pt = line.c * line.n - np.dot(reference_point.a, line.n) * line.n + reference_point.a
    # Move along line direction by the specified distance
    return gt.Point(closest_pt + line.v * distance)

def point_pmpm(point: gt.Point, measure: gt.Measure) -> gt.Point:
    """Create a point at a specified distance from an existing point in a random direction."""
    assert(measure.dim == 1 and measure.x > 0)
    return gt.Point(point.a + measure.x * gt.random_direction())

# New measurement functions

def magnitude_v(vector: gt.Vector) -> gt.Measure:
    """Measure the magnitude (length) of a vector and return as a Measure object."""
    return gt.Measure(np.linalg.norm(vector.v), 1)  # Dimension 1 for length

def arc_length_C(arc: gt.Arc) -> gt.Measure:
    """Measure the length of an arc and return as a Measure object."""
    angle_diff = abs(arc.angles[1] - arc.angles[0])
    return gt.Measure(arc.r * angle_diff, 1)  # Dimension 1 for length

def central_angle_C(arc: gt.Arc) -> gt.Measure:
    """Measure the central angle of an arc in radians and return as a Measure object."""
    angle_diff = abs(arc.angles[1] - arc.angles[0])
    return gt.Measure(angle_diff, 0)  # Dimension 0 for angle
