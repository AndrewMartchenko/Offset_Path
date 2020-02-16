import math
from vector import Vector
from line_arc import *

def join_offsets(path, offsets):

    # copy segments
    joined_offsets = []
    for s in offsets:
        joined_offsets.append(copy_segment(s))
        
    if len(joined_offsets) < 2:
        return joined_offsets


    n = len(joined_offsets)
    i = 0 # offsets index
    j = 0 # path index
    while(i < n-1):
        s0 = joined_offsets[i]
        s1 = joined_offsets[i+1]

        if is_line(s0) and is_line(s1):
            pt = line_line_intersect(s0, s1)
            if pt:
                s0[-1] = pt.copy()
                s1[0] = pt.copy()
                
        if is_line(s0) and is_arc(s1):
            pt = line_arc_intersect(s0[::-1], s1)
            if pt:
                s0[-1] = pt.copy()
                s1[:] = arc_clip(s1, pt.copy(), s1[2].copy())
            
        if is_arc(s0) and is_line(s1):
            pt = line_arc_intersect(s1, s0)
            if pt:
                s1[0] = pt.copy()
                s0[:] = arc_clip(s0, s0[0].copy(), pt.copy())

        if is_arc(s0) and is_arc(s1):
            pt = arc_arc_intersect(s0[::-1], s1)
            if pt:
                s0[:] = arc_clip(s0, s0[0].copy(), pt.copy())
                s1[:] = arc_clip(s1, pt.copy(), s1[2].copy())

        if pt is None:
            # Draw arc between segments
            p0 = s0[-1].copy()
            p2 = s1[0].copy()

            c = path[j][-1]
            r = (p0-c).length()

            m = (p0+p2)/2
            p1 = r*(m-c).norm()+c
            joined_offsets.insert(i+1, [p0, p1, p2])
            i += 1
            n += 1
                
        i += 1
        j += 1

    return joined_offsets


def offset_segment(seg, dist):

    if is_line(seg): # line
        p0, p1 = seg

        u = (p1-p0).normal()*dist

        q0 = p0+u
        q1 = p1+u

        return [q0, q1]

    elif is_arc(seg): # arc
        p0, p1, p2 = seg

        c, r, a0, a2 = arc_from_points(seg)

        v0 = (p0-c).norm()
        v1 = (p1-c).norm()
        v2 = (p2-c).norm()

        m02 = (p2+p0)/2

        pm = p1 - m02
        u = (p2-p0).normal()

        if Vector.dot(u, pm) > 0:
            r += dist
        else:
            r -= dist
        
        q0 = c + r*v0
        q1 = c + r*v1
        q2 = c + r*v2
        
        return [q0, q1, q2]

def offset_path(path, dist):
    offsets = []
    for seg in path:
        offsets.append(offset_segment(seg, dist))

    joined_offsets = join_offsets(path, offsets)
    return joined_offsets

