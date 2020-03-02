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
    fill_lines = []
    t = 0
    while t <= 1:
        # Calculate line parallel to vec
        u = vec.norm()  # Unit vec

        p = (p0+t*(p1-p0)) # Point on line p0-p1
        q0 = p-r*u  # Start of vec line
        q1 = p+r*u  # End of vec line

        points = []
        params = []
        for seg in path:

            if is_line(seg):
                pt, t0 = line_line_intersect([q0, q1], seg)
                if t0 is not None:
                    points.append(pt)
                    params.append(t0)
            elif is_arc(seg):
                pt1, t1 = line_arc_intersect([q0, q1], seg)
                pt2, t2 = line_arc_intersect([q1, q0], seg)

                # Line was passed in in reverse order, so true paremetric value is obtained by subtracting from 1.0 
                if t2 is not None:
                    t2 = 1-t2

                if t1 is not None:
                    points.append(pt1)
                    params.append(t1)

                if t2 is not None:
                    if t1 is None:
                        points.append(pt2)
                        params.append(t2)
                    elif abs(t1-t2)> 0.001:
                        points.append(pt2)
                        params.append(t2)


        # Do some dark python magic
        
        # Determine params index order 
        indexes = sorted(range(len(params)), key=lambda k: params[k])
        
        # Sort points order of params
        sorted_points = [points[i] for i in indexes]


        # Group adjacent fill_lines to form lines
        num_elements = len(sorted_points)
        num_fill_lines = (num_elements//2) # // is an integer divide in python 7//2 = 3
        N = num_fill_lines*2 # number of elements not including last (odd) element

        # Iterate over pairs of sorted points and group them to make a list of lines
        for i in range(0, N-1, 2):
            fill_lines.append([sorted_points[i], sorted_points[i+1]]) 
                

        t += dt

    return fill_lines


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
