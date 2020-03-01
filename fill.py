import math
from vector import Vector
from line_arc import *


def fill(path, vec, space):

    if len(path) == 0:
        return []
    
    tl, br = path_bbox(path)
    
    # calculate bbox center
    c = (tl+br)/2
    
    # calculate bbox diagonal radius
    r = (tl-c).length()

    # calculate tangent line to vector
    u = vec.normal() # tangent unit vector
    p0 = c-r*u # Start of line
    p1 = c+r*u # End of line

    dist = (p0-p1).length()

    dt = space/dist # Parametric step size
    groups = []
    t = 0
    while t <= 1:
        print(t, dt)
        # Calculate line parallel to vec
        u = vec.norm()  # Unit vec

        p = (p0+t*(p1-p0)) # Point on line p0-p1
        q0 = p-r*u  # Start of vec line
        q1 = p+r*u  # End of vec line

        group = []
        for seg in path:

            if is_line(seg):
                pt = line_line_intersect([q0, q1], seg)
                if pt is not None:
                    group.append(pt)
            elif is_arc(seg):
                pt1 = line_arc_intersect([q0, q1], seg)
                pt2 = line_arc_intersect([q1, q0], seg)

                if pt1 is not None:
                    group.append(pt1)
                
                if pt2 is not None:
                    if pt1 is None:
                        group.append(pt2)
                    elif (pt1-pt2).length()> 0.001:
                        group.append(pt2)

        print(group)
        if len(group)>0:
            groups.append(group)

        t += dt

    return groups
    
    # for each line segment:
       # from bbox center move along the tangent line +/- diagonal radius, draw lines along vec and record intersects
       # order intersections 
       # pair up adjacent intersections and store their line segments

    # done




# Returns bounding box of a line
def line_bbox(line):
    left = min(line[0].x, line[1].x)
    right = max(line[0].x, line[1].x)
    bottom = min(line[0].y, line[1].y)
    top = max(line[0].y, line[1].y)
    return Vector(left, top), Vector(right, bottom)

# Returns bounding box of an arc_arc_intersect
def arc_bbox(arc):
    # Assume arc is close to linear, bbox is then given by
    top_left, bottom_right = line_bbox([arc[0], arc[2]])

    c, r, a0, a2 = arc_from_points(arc)

    # Compass points
    north = r*Vector(0, 1) + c
    south = r*Vector(0, -1) + c
    east = r*Vector(1, 0) + c
    west = r*Vector(-1, 0) + c

    # Test if compas points lie on arc
    if pt_angle_on_arc(arc, north) is not None:
        top_left.y = north.y
    if pt_angle_on_arc(arc, west) is not None:
        top_left.x = west.x
    if pt_angle_on_arc(arc, south) is not None:
        bottom_right.y = south.y
    if pt_angle_on_arc(arc, east) is not None:
        bottom_right.x = east.x


    return top_left, bottom_right

# join bboxes 
def join_bboxes(bbox_a, bbox_b):
    if bbox_a is None:
        return bbox_b
    left = min(bbox_a[0].x, bbox_b[0].x)
    top = max(bbox_a[0].y, bbox_b[0].y)
    right = max(bbox_a[1].x, bbox_b[1].x)
    bottom = min(bbox_a[1].y, bbox_b[1].y)

    return Vector(left, top), Vector(right, bottom)

def path_bbox(path):
    bbox_a = None
    for seg in path:
        if is_line(seg):
            box_b = line_bbox(seg)
        elif is_arc(seg):
            box_b = arc_bbox(seg)
            
        bbox_a = join_bboxes(bbox_a, box_b)
    return bbox_a
