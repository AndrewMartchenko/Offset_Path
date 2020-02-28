import math
from vector import Vector
from line_arc import *

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
        print('north', pt_angle_on_arc(arc, north))
    if pt_angle_on_arc(arc, west) is not None:
        top_left.x = west.x
        print('west', pt_angle_on_arc(arc, west))
    if pt_angle_on_arc(arc, south) is not None:
        bottom_right.y = south.y
        print('south', pt_angle_on_arc(arc, south))
    if pt_angle_on_arc(arc, east) is not None:
        bottom_right.x = east.x
        print('east', pt_angle_on_arc(arc, east))


    return top_left, bottom_right

# resizes bbox to include box
def resize_bbox(bbox, box):
    if bbox is None:
        return box
    left = min(bbox[0].x, box[0].x)
    top = max(bbox[0].y, box[0].y)
    right = max(bbox[1].x, box[1].x)
    bottom = min(bbox[1].y, box[1].y)

    return Vector(left, top), Vector(right, bottom)

def path_bbox(path):
    bbox = None
    for seg in path:
        if is_line(seg):
            box = line_bbox(seg)
        elif is_arc(seg):
            box = arc_bbox(seg)
            
        bbox = resize_bbox(bbox, box)
    return bbox
