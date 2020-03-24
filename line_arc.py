import math
from vector import Vector

MAX_LEN_ERROR = 1/1000 # 1/1000th of a mm
MAX_ANGLE_ERROR =  (1/1000)*math.pi/180 # 1/1000th of a degree

NUM_ITER = 20


def is_line(seg):
    if len(seg)==2:
        return True

def is_arc(seg):
    if len(seg)==3:
        return True

def copy_segment(seg):
    return [s.copy() for s in seg]




# Returns angle of point if it lies on the arc
# otherwise returns None
def pt_angle_on_arc(arc, pt):
    # if pt is None:
        # return None
    
    c, r, a0, a2 = arc_from_points(arc)

    if abs((pt-c).length()-r) > MAX_LEN_ERROR:
        return None

    a = (pt-c).angle()-2*math.pi

    if a0 < a2:
        if a0-MAX_ANGLE_ERROR <= a and a <= a2+MAX_ANGLE_ERROR:
            return a
        a += 2*math.pi
        if a0-MAX_ANGLE_ERROR <= a and a <= a2+MAX_ANGLE_ERROR:
            return a
        a += 2*math.pi
        if a0-MAX_ANGLE_ERROR <= a and a <= a2+MAX_ANGLE_ERROR:
            return a
    else:
        if a2-MAX_ANGLE_ERROR <= a and a <= a0+MAX_ANGLE_ERROR:
            return a
        a += 2*math.pi
        if a2-MAX_ANGLE_ERROR <= a and a <= a0+MAX_ANGLE_ERROR:
            return a
        a += 2*math.pi
        if a2-MAX_ANGLE_ERROR <= a and a <= a0+MAX_ANGLE_ERROR:
            return a
    return None

def pt_angle_before_arc(arc, pt):
    c, r, a0, a2 = arc_from_points(arc)

    if abs((pt-c).length()-r) > MAX_LEN_ERROR:
        return None

    a = (pt-c).angle()-2*math.pi

    if a0 < a2:
        if a <= a0:
            return a
        a += 2*math.pi
        if a <= a0:
            return a
        a += 2*math.pi
        if a <= a0:
            return a
    else:
        if a >= a0:
            return a
        a += 2*math.pi
        if a >= a0:
            return a
        a += 2*math.pi
        if a >= a0:
            return a

    print('Before Arc This should never be printed')
    return None

def pt_angle_after_arc(arc, pt):
    c, r, a0, a2 = arc_from_points(arc)

    if abs((pt-c).length()-r) > MAX_LEN_ERROR:
        return None

    a = (pt-c).angle()+2*math.pi


    if a0 < a2:
        # print(a)
        if a >= a2:
            return a
        a -= 2*math.pi
        # print(a)
        if a >= a2:
            return a
        a -= 2*math.pi
        # print(a)
        if a >= a2:
            return a
    else:
        # print(a)
        if a <= a2:
            return a
        a -= 2*math.pi
        # print(a)
        if a <= a2:
            return a
        a -= 2*math.pi
        # print(a)
        if a <= a2:
            return a

    print('After Arc This should never be printed')
    return None
    

# Returns unit vector tangent to start of arc
def arc_start_tangent(arc):
    c, _, a0, a2 = arc_from_points(arc)
    u = (arc[0]-c).normal()
    if a0 > a2:
        u *= -1

    return u

# Returns unit vector tangent to end of arc
def arc_end_tangent(arc):
    c, _, a0, a2 = arc_from_points(arc)
    u = (arc[2]-c).normal()
    if a0 > a2:
        u *= -1
    return u

def line_tangent(line):
    return (line[1]-line[0]).norm()

def segment_clip(seg, start_pt, end_pt):
    if is_line(seg):
        clipped_seg = [start_pt.copy(), end_pt.copy()]
    else:
        clipped_seg = arc_clip(seg, start_pt, end_pt)

    return clipped_seg



# Adjusts the end points of the arc to q0 and q2.
# This function is also used to extend the start and end point of the arc
def arc_clip(arc, q0, q2):
    c, r, a0, a2 = arc_from_points(arc)
    
    b0 = pt_angle_on_arc(arc, q0)
    b2 = pt_angle_on_arc(arc, q2)
    

    if b0 is None:
        b0 = pt_angle_before_arc(arc, q0)

    if b2 is None:
        b2 = pt_angle_after_arc(arc, q2)

    if b0 is None or b2 is None:
        return [None, None, None]
    b1 = (b0+b2)/2
    q1 = c + r*Vector(math.cos(b1), math.sin(b1))

    return [q0.copy(), q1.copy(), q2.copy()]

# # Finds the intersect of a 3 point arc and a 3 point circle
# def arc_circ_intersect(arc, circ):
#     p0, p1, p2 = arc
#     ca, ra, a0, a1 = arc_from_points(arc)
#     c, r, _, _ = arc_from_points(circ)

#     p = lambda t: ca + ra*Vector(math.cos(a0+t*(a1-a0)), math.sin(a0+t*(a1-a0)))
#     dpdt = lambda t: ra*(a1-a0)*Vector(-math.sin(a0+t*(a1-a0)), math.cos(a0+t*(a1-a0)))
#     e = lambda t: r*r - Vector.dot(p(t)-c, p(t)-c)
#     dedt = lambda t: -2*Vector.dot(dpdt(t), p(t)-c)
                         
#     t = newtons_method(0, e, dedt)
    
#     if t < 0 or t > 1:
#         None
#     else:
#         return p(t)


# # Returns first intersection point of line and circle
# def line_circ_intersect(line, circ):
#     p0, p1 = line
#     c, r, a0, a1 = arc_from_points(circ)

#     p = lambda t: p0+t*(p1-p0)
#     dpdt = lambda t: p1-p0
#     e = lambda t: r*r - Vector.dot(p(t)-c, p(t)-c)
#     dedt = lambda t: -2*Vector.dot(dpdt(t), p(t)-c)
                         
#     t = newtons_method(0, e, dedt)

#     if t < 0 or t > 1:
#         None
#     else:
#         return p(t)

# # Newton-Raphson method for finding roots of an function f with derivative df
# # Algorithm will find only one root.
# # x0 needs to be carefuly chosen so that alcorithm converges to correct solution
# def newtons_method(x0, f, df):
#     x = x0
#     for i in range(10):
#         x = x - f(x)/df(x)
#     return x



# Returns the first intersect of arc0 and arc1.
# Note: search starts from arc0[0]
def arc_arc_intersect(arc0, arc1):
    p0, p1 = circ_circ_intersect(arc0, arc1)

    if p0 is not None:
        if pt_angle_on_arc(arc0, p0) is not None and pt_angle_on_arc(arc1, p0) is not None: 
            return p0

    if p1 is not None:
        if pt_angle_on_arc(arc0, p1) is not None and pt_angle_on_arc(arc1, p1) is not None: 
            return p1

    return None


# Returns the first intersect of line and arc.
# Note: search starts from line[0]
def line_arc_intersect(line_seg, arc):
    pt, t = line_circ_intersect(line_seg, arc)
    # If intersection is not on line segment
    if t is None:
        return (None, None)
    # If intersection is not on arc segment
    if pt_angle_on_arc(arc, pt) is None:
        return (None, None)

    return (pt, t)


# This is the Non-"Functional" way to do the above
def circ_circ_intersect(circA, circB):
    p0, p1, p2 = circA
    ca, ra, a0, a1 = arc_from_points(circA)
    cb, rb, _, _ = arc_from_points(circB)

    # If too far apart
    if (ca-cb).length() > ra+rb:
        return (None, None)

    # If circle is inside arc
    if (ca-cb).length()+rb < ra:
        return (None, None)

    # If arc is inside circle
    if (ca-cb).length()+ra < rb:
        return (None, None)
    
    
    t = 0.0
    for i in range(NUM_ITER):

        p = ca + ra*Vector(math.cos(a0+t*(a1-a0)), math.sin(a0+t*(a1-a0)))
        dpdt =  ra*(a1-a0)*Vector(-math.sin(a0+t*(a1-a0)), math.cos(a0+t*(a1-a0)))
        e =  rb*rb - Vector.dot(p-cb, p-cb)
        dedt =  -2*Vector.dot(dpdt, p-cb)
        t = t - e/dedt
        
    pt1 = ca + ra*Vector(math.cos(a0+t*(a1-a0)), math.sin(a0+t*(a1-a0)))

    pt2 = mirror_pt([ca, cb], pt1)

    return (pt1, pt2)

def segment_intersect(s0, s1):
    if is_line(s0) and is_line(s1):
        pt, _ = line_segment_intersect(s0[::-1], s1)
    elif is_line(s0) and is_arc(s1):
        pt, _ = line_segment_arc_intersect(s0[::-1], s1)
        # pt, _ = line_segment_arc_intersect(s0, s1)
    elif is_arc(s0) and is_line(s1):
        # pt, _ = line_segment_arc_intersect(s1, s0)
        pt, _ = line_segment_arc_intersect(s1, s0[::-1])
    elif is_arc(s0) and is_arc(s1):
        pt = arc_arc_intersect(s0[::-1], s1)
        # pt = arc_arc_intersect(s0, s1)

    return pt


def line_circ_intersect(line, circ):
    p0, p1 = line
    c, r, a0, a1 = arc_from_points(circ)

    dist = line_point_distance(line, c)

    # if line and circ do not intersect
    if dist > r:
        return (None, None)
    
    t = 0.0
    for i in range(NUM_ITER):

        p = p0+t*(p1-p0)
        dpdt = p1-p0
        e = r*r - Vector.dot(p-c, p-c)
        dedt = -2*Vector.dot(dpdt, p-c)
        t = t - e/dedt

    p = p0+t*(p1-p0)
    

    return (p, t)

# Returns smallest distance from line to point
def line_point_distance(line, pt):
    p0, p1 = line
    u = (p1-p0).normal()
    return abs(Vector.dot(u, pt-p0))


def line_segment_circ_intersect(line_seg, circ):
    p, t = line_circ_intersect(line_seg, circ)
    if t is None:
        return (None, None)
    if t < 0 or t > 1:
        return (None, None)

    return (p, t)

# Returns the first intersect of line and arc.
# Note: search starts from line[0]
def line_segment_arc_intersect(line_seg, arc):
    pt, t = line_circ_intersect(line_seg, arc)
    # If intersection is not on line segment
    if t is None:
        return (None, None)
    if t < 0 or t > 1:
        return (None, None)
    # If intersection is not on arc segment
    if pt_angle_on_arc(arc, pt) is None:
        return (None, None)

    return (pt, t)



    
# Intersection of two line segments 
def line_intersect(line0, line1):
    p0, p1 = line0
    q0, q1 = line1

    v0 = p1-p0
    v1 = q1-q0

    # Parrametric equations for lines are
    # p = p0 + t*v0
    # q = q0 + s*v1

    # If lines are co-linear
    if Vector.cross(v1, v0) == 0:
        # lines intersect everywhere
        return (p1, 1, 0) # Not sure if we should return the end point on line0 when lines are co-linear

        
    # solve for s and t when p and q are equal
    s = Vector.cross(v0, q0-p0)/Vector.cross(v1, v0)
    t = Vector.cross(v1, p0-q0)/Vector.cross(v0, v1)

    return (p0+t*v0, t, s)

def line_segment_intersect(line_seg0, line_seg1):
    pt, t, s = line_intersect(line_seg0, line_seg1)

    if 0 <= t and t <= 1 and 0 <= s and s <= 1:
        return pt, t
    else:
        return (None, None)


# Calculates center of a 3 point circle
def center3(p0, p1, p2):
    # midpoints
    m1 = (p0+p1)/2
    m2 = (p1+p2)/2

    # unit vectos
    # perpendicular unit vectors
    v1 = (p0-p1).normal()
    v2 = (p1-p2).normal()

    # solving intersection of two parametric linear equations c = m1+s*v1 and c = m2+t*v2 
    t = (v1.x*(m2.y-m1.y) - v1.y*(m2.x-m1.x))/(v2.x*v1.y - v2.y*v1.x)

    # center
    c = m2+t*v2

    return c

# # Function needs better name!
# # Converts 3 point arc to center, radius, start angle and end angle
# def arc_from_points(arc):
#     p0, p1, p2 = arc
#     c = center3(p0, p1, p2)
#     v0 = p0-c
#     v1 = p1-c
#     v2 = p2-c
#     r = v0.length()
#     a0 = v0.angle()
#     a1 = a0 + Vector.angle_between(v0, v1)
#     a2 = a1 + Vector.angle_between(v1, v2)

    return c, r, a0, a2

##Old version of the above.
def arc_from_points(arc):
    p0, p1, p2 = arc
    c = center3(p0, p1, p2)
    r = (p0-c).length()
    a0 = (p0-c).angle()
    a1 = (p1-c).angle()
    a2 = (p2-c).angle()

    #  A             B             C             D             E             F
    #      a1|           a2|             |           a1|           a0|             |       
    #        |   a2        |             |             |   a0        |             |       
    #  a0    |       a1    |       a2    |       a2    |       a1    |       a0    |       
    #  ------+------ ------+------ ------+------ ------+------ ------+------ ------+------ 
    #        |       a0    |       a1    |             |       a2    |       a1    |       
    #        |             |             |             |             |             |       
    #        |             |           a0|             |             |           a2|       
    #        
    #  a2<a1<a0      a0<a2<a1      a1<a0<a2      a0<a1<a2      a2<a0<a1      a1<a2<a0
    # 

    # Angles can +ve or -ve depending on quadrant. Therefore they may apear out of order
    # Following adds 2*pi to the angles as required to preserve angle order

    if a2<a1 and a1<a0:   # A
        pass
    elif a0<a2 and a2<a1: # B
        a0 += 2*math.pi
    elif a1<a0 and a0<a2: # C
        a0 += 2*math.pi
        a1 += 2*math.pi
    elif a0<a1 and a1<a2: # D
        pass
    elif a2<a0 and a0<a1: # E
        a2 += 2*math.pi
    elif a1<a2 and a2<a0: # F
        a1 += 2*math.pi
        a2 += 2*math.pi

    return c, r, a0, a2

def mirror_pt(line, pt):
    g = project_pt_on_line(line, pt)
    v = pt-g
    qt = g - v
    return qt

def project_pt_on_line(line, pt):
    p1, p0 = line
    u = (p1-p0).norm()
    a = pt-p0
    proj_dist = Vector.dot(a, u)
    proj_pt = p0+proj_dist*u
    return proj_pt




#######################################################
##                 NOT USED                          ##
#######################################################

def radius3(p0, p1, p2):
    c = center3(p0, p1, p2)
    r = (p0-c).length()
    return r

def arc_point_distance(arc, pt):
    p0, p1, p2 = arc
    c = center3(p0, p1, p2)
    r = (p0-c).length()
    d = (pt-c).length()

    dist = abs(d-r)
    return dist


def is_pt_on_line(line, pt):
    p0, p1 = line
    a = pt-p0
    b = p1-p0
    u = b.norm()
    s = Vector.dot(a, u)

    if abs(s-a.length()) < MAX_LEN_ERROR:
        return True
    else:
        return False

def closest_pt(pt, points):

    d_min = 999999999
    p_min = None
    for p in points:
        d = (pt-p).length()
        if d < d_min:
            d_min = d
            p_min = p
    return p_min

