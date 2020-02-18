import math
from vector import Vector

def is_line(seg):
    if len(seg)==2:
        return True

def is_arc(seg):
    if len(seg)==3:
        return True

def copy_segment(seg):
    return [s.copy() for s in seg]

# Returns andgle of point if it lies on the arc
# otherwise returns None
def pt_angle_on_arc(arc, pt):
    if pt is None:
        return None
    
    c, r, a0, a2 = arc_from_points(arc)

    if abs((pt-c).length()-r)>0.001:
        return None

    err = 2*math.pi/1000

    a = (pt-c).angle()
    if a2 > a0:
        if a0-err <= a and a <= a2+err:
            return a
        a += 2*math.pi
        if a0-err <= a and a <= a2+err:
            return a
    else:
        if a2-err <= a and a <= a0+err:
            return a
        a += 2*math.pi
        if a2-err <= a and a <= a0+err:
            return a
        
    return None


# Adjusts the end points of the arc to q0 and q2
def arc_clip(arc, q0, q2):
    c, r, a0, a2 = arc_from_points(arc)
    
    b0 = pt_angle_on_arc(arc, q0)
    b2 = pt_angle_on_arc(arc, q2)

    assert b0 is not None, 'q0 must lie on arc'
    assert b2 is not None, 'q2 must lie on arc'

    m = (q0+q2)/2
    u = (m-c).norm()

    if abs(b2-b0) < math.pi:
        q1 = c + r*u
    else:
        q1 = c - r*u
    
    return [q0, q1, q2]

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


# This is the Non-"Functional" way to do the above
def arc_circ_intersect(arc, circ):
    p0, p1, p2 = arc
    ca, ra, a0, a1 = arc_from_points(arc)
    c, r, _, _ = arc_from_points(circ)
    
    t = 0
    for i in range(10):

        p = ca + ra*Vector(math.cos(a0+t*(a1-a0)), math.sin(a0+t*(a1-a0)))
        dpdt =  ra*(a1-a0)*Vector(-math.sin(a0+t*(a1-a0)), math.cos(a0+t*(a1-a0)))
        e =  r*r - Vector.dot(p-c, p-c)
        dedt =  -2*Vector.dot(dpdt, p-c)
        t = t - e/dedt

    p = ca + ra*Vector(math.cos(a0+t*(a1-a0)), math.sin(a0+t*(a1-a0)))
    
    if t < 0 or t > 1:
        None
    else:
        return p


def line_circ_intersect(line, circ):
    p0, p1 = line
    c, r, a0, a1 = arc_from_points(circ)
    t = 0
    for i in range(10):

        p = p0+t*(p1-p0)
        dpdt = p1-p0
        e = r*r - Vector.dot(p-c, p-c)
        dedt = -2*Vector.dot(dpdt, p-c)
        t = t - e/dedt

    p = p0+t*(p1-p0)
    
    if t < 0 or t > 1:
        None
    else:
        return p


# Returns the first intersect of line and arc.
# Note: search starts from line[0]
def line_arc_intersect(line, arc):
    pt = line_circ_intersect(line, arc)
    if pt_angle_on_arc(arc, pt):
        return pt
    else:
        return None
     
# Returns the first intersect of arc0 and arc1.
# Note: search starts from arc0[0]
def arc_arc_intersect(arc0, arc1):
    pt = arc_circ_intersect(arc0, arc1)
    if pt_angle_on_arc(arc1, pt):
        return pt
    else:
        return None

# Intersection of two line segments 
def line_line_intersect(line0, line1):
    p0, p1 = line0
    q0, q1 = line1

    v0 = p1-p0
    v1 = q1-q0

    # Parrametric equations are for lines are
    # p = p0 + t*v0
    # q = q0 + s*v1

    # If lines are co-linear
    if Vector.cross(v1, v0) == 0:
        # lines intersect everywhere
        return p1

        
    # solve for s and t when p and q are equal
    s = Vector.cross(v0, q0-p0)/Vector.cross(v1, v0)
    t = Vector.cross(v1, p0-q0)/Vector.cross(v0, v1)

    if 0<=t and t<=1 and 0<=s and s<=1:
        return p0 + t*v0
    else:
        return None

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

# Function needs better name!
# Converts 3 point arc to center, radius, start angle and end angle
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


#######################################################
##                 NOT USED                          ##
#######################################################

def radius3(p0, p1, p2):
    c = center3(p0, p1, p2)
    r = (p0-c).length()
    return r

def mirror_pt(line, pt):
    g = project_pt_on_line(line, pt)
    v = pt-g
    qt = g - v
    return qt

# Returns smallest distance from line to point
def line_point_distance(line, pt):
    p0, p1 = line
    u = (p1-p0).normal()
    return abs(Vector.dot(u, pt-p0))

def arc_point_distance(arc, pt):
    p0, p1, p2 = arc
    c = center3(p0, p1, p2)
    r = (p0-c).length()
    d = (pt-c).length()

    dist = abs(d-r)
    return dist

def project_pt_on_line(line, pt):
    p1, p0 = line
    u = (p1-p0).norm()
    a = pt-p0
    proj_dist = Vector.dot(a, dot(u))
    proj_pt = p0+proj_dist*u
    return proj_pt

def is_pt_on_line(line, pt):
    p0, p1 = line
    a = pt-p0
    b = p1-p0
    u = b.norm()
    s = Vector.dot(a, u)

    if abs(s-a.length()) < 0.001:
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
