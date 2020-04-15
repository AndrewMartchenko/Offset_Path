import math
from vector import Vector
from line_arc import *

# Function assumes that polysegment is closed.
def is_pt_in_closed_polysegment(pt, segments):

    # Create horizontal line from p0
    # Give it slight slope so that it is less likely that it is parallel
    # to a line segment (May not be necessery if parallel lines are treated correctly)
    line = [pt, pt + Vector.from_polar(magnitude=1, angle=0.0001)]
    
    intersect_count = 0
    for seg in segments:

        # Find all of the intersects that the line makes with all the line segments
        pB = tB = None
        if is_line(seg):
            pA, tA = line_line_segment_intersect(line, seg)
        else:
            pA, tA, pB, tB = line_arc_intersect(line, seg)
            # TODO: line may intersect arc twice need to test both

        # If intersect is found, only count it if it has t value > 0
        # In onther words treat the line like a ray
        if tA is not None and tA >= 0:
            intersect_count += 1
            
        if tB is not None and tB >= 0:
            intersect_count += 1

    # if the modulus 2 is odd then the point is inside the polysegment
    if intersect_count % 2 == 1:
        # If odd number of intersects
        return True
    else:
        return False
        
def arc_fill(path, arc, space):

    if len(path) == 0:# 
        return []

    tl, br = path_bbox(path)
    # Get the other two corners of bounding box
    bl = Vector(tl.x, br.y)
    tr = Vector(br.x, tl.y)

    c = center3(*arc) # TODO: make argument list rather than 3 points

    r = space
    fill_lines = []
    while True:
        # Make a left and right semicircles/arcs
        arc_rhs = [Vector(0, r) + c, Vector(r, 0) + c, Vector(0, -r) +c]
        arc_lhs = [Vector(0, -r) + c, Vector(-r, 0) + c, Vector(0, r) +c] 

        points = []
        angles = []
        for seg in path:

            # pA, pB = segment_intersect(arc_rhs, seg)
            
            if is_line(seg):
                pA, pB = line_segment_circ_intersect(seg, arc_rhs)
            else:
                pA, pB = arc_circ_intersect(seg, arc_rhs)
                


            if pA is not None:
                angle_A = (pA-c).angle()
                points.append(pA)
                angles.append(angle_A)

            if pB is not None:
                angle_B = (pB-c).angle()
                points.append(pB)
                angles.append(angle_B)


        if len(points) == 0:
            # check if middle circ point is inside of path
            if is_pt_in_closed_polysegment(arc_rhs[1], path):
                fill_lines.append(arc_rhs)
                fill_lines.append(arc_lhs)
            else:
                if (tl-c).length() < r and \
                   (tr-c).length() < r and \
                   (bl-c).length() < r and \
                   (br-c).length() < r:
                    # If path bbox is inside circle
                    break

        elif len(points)%2 == 0:
            # sort the points
            # Find midpoint of each pair and save.
        
            # Determine params index order 
            indexes = sorted(range(len(angles)), key=lambda k: angles[k])

            # Sort points order of angles
            sorted_points = [points[i] for i in indexes]
            sorted_angles = [angles[i] for i in indexes]

            a1 = (sorted_angles[0]+sorted_angles[1])/2
            p = Vector.from_polar(r, a1)+c

            if not is_pt_in_closed_polysegment(p, path):
                # make copy of first point and angle
                # move point and angle copy to end of list and add 2pi to angle
                sorted_points.append(sorted_points[0].copy())
                sorted_angles.append(sorted_angles[0]+2*math.pi)
                del(sorted_points[0])
                del(sorted_angles[0])

            
            # Group adjacent fill_lines to form lines
            num_elements = len(sorted_points)
            num_fill_arcs = (num_elements//2) # // is an integer divide in python 7//2 = 3
            N = num_fill_arcs*2 # number of elements not including last (odd) element

            # breakpoint()
            # Iterate over pairs of sorted points and group them to make a list of lines
            for i in range(0, N-1, 2):
                a1 = (sorted_angles[i]+sorted_angles[i+1])/2
                p = Vector.from_polar(r, a1)+c
                fill_lines.append([sorted_points[i], p, sorted_points[i+1]]) 
                

        r += space

    return fill_lines



def line_fill(path, vec, space):

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
        line = [q0, q1]
        
        points = []
        params = []
        for seg in path:

            if is_line(seg):

                # if lines are coincident, then continue on to next segment
                if is_coincident(line, seg):
                    continue
                
                pt, t0 = line_line_segment_intersect(line, seg)
                if t0 is not None:
                    points.append(pt)
                    params.append(t0)
            elif is_arc(seg):
                pt1, t1, pt2, t2 = line_arc_intersect(line, seg)

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



### TEST CODE
pt = Vector(2, 2)
segments = [
    [Vector(0,0), Vector(0, 5)],
    [Vector(0,5), Vector(5, 5)],
    [Vector(5,5), Vector(5, 0)],
    [Vector(5,0), Vector(0, 0)],
    ]

is_pt_in_closed_polysegment(pt, segments)
