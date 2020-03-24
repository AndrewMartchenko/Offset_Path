import math
from vector import Vector
from line_arc import *


def join_offsets(path, offsets):

    # Copy segments
    joined_offsets = []
    for s in offsets:
        joined_offsets.append(copy_segment(s))
        
    if len(joined_offsets) < 2:
        return joined_offsets


    n = len(joined_offsets)
    i = -1 # offsets index
    j = -1 # path index
    while(i+1 < n-1):
        i += 1
        j += 1
        s0 = joined_offsets[i]
        s1 = joined_offsets[i+1]


        pt = segment_intersect(s0, s1)

        # If s0 and s1 intersect:
        if pt is not None:

            # breakpoint()
            s0[:] = segment_clip(s0, s0[0], pt)
            s1[:] = segment_clip(s1, pt, s1[-1])
            continue

        # else
        

        d0 = path[j][1]
        d1 = path[j+1][1]

        # Create the three possible addons

        if d0 >= d1:
            if is_line(s0):
                u = line_tangent(s0) 
            else:
                u = arc_end_tangent(s0)

            # Create arc_join_1
            c = s0[-1]+d1*u.rotate(-math.pi/2)
            arc_join_1 = [s0[-1].copy(), c+d1*u.rotate(math.pi/4), c+d1*u]
            joined_offsets.insert(i+1, arc_join_1)
            i += 1
            n += 1

            if d0 == d1:
                arc_join_1[:] = segment_clip(arc_join_1, arc_join_1[0], s1[0])
                continue


            pt = segment_intersect(arc_join_1, s1)
            if pt is not None:
                arc_join_1[:] = segment_clip(arc_join_1, arc_join_1[0], pt)
                s1[:] = segment_clip(s1, pt, s1[-1])
                continue


            # Create line_join
            line_join = [arc_join_1[-1].copy(), s0[-1] + d1*u + d0*u.rotate(-math.pi/2)]
            joined_offsets.insert(i+1, line_join)
            i += 1
            n += 1

            pt = segment_intersect(line_join, s1)
            if pt is not None:
                line_join[:] = segment_clip(line_join, line_join[0], pt)
                s1[:] = segment_clip(s1, pt, s1[-1])
                continue

            # Create arc_join_2
            c =  line_join[-1]-d1*u
            arc_join_2 = [line_join[-1].copy(), c+d1*u.rotate(-math.pi/4), c+d1*u.rotate(-math.pi/2)]
            joined_offsets.insert(i+1, arc_join_2)
            i += 1
            n += 1

            arc_join_2[:] = segment_clip(arc_join_2, arc_join_2[0], s1[0])




            
        else:
            if is_line(s1):
                u = line_tangent(s1) 
            else:
                u = arc_start_tangent(s1)
                
            c = s1[0]+d0*u.rotate(-math.pi/2)
            arc_join_1 = [c-d0*u, c+d0*u.rotate(3*math.pi/4), s1[0].copy()]
            joined_offsets.insert(i+1, arc_join_1)
            i += 1
            n += 1

            # breakpoint()
            pt = segment_intersect(s0, arc_join_1)

            if pt is not None:
                print('We have arc arc intersection')
                arc_join_1[:] = segment_clip(arc_join_1, pt, arc_join_1[-1])
                s0[:] = segment_clip(s0, s0[0], pt)
                continue
            
            line_join = [s1[0] - d0*u + d1*u.rotate(-math.pi/2), arc_join_1[0].copy()]
            joined_offsets.insert(i, line_join)
            i += 1
            n += 1

            pt = segment_intersect(s0, line_join)
            if pt is not None:
                line_join[:] = segment_clip(line_join, pt, line_join[-1])
                s0[:] = segment_clip(s0, s0[0], pt)
                continue
            
            c = line_join[0]+d0*u
            arc_join_2 = [c+d0*u.rotate(-math.pi/2), c+d0*u.rotate(-3*math.pi/4), line_join[0].copy() ]
            joined_offsets.insert(i-1, arc_join_2)
            i += 1
            n += 1

            arc_join_2[:] = segment_clip(arc_join_2, s0[-1], arc_join_2[-1])




  

    return joined_offsets


def offset_segment(seg, dist):

    # TODO: if last last point and first point are equlal, then assume that segments are joined

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

def offset_path(path):
    print(path)
    closed_path = False
    numel = len(path)
    # If first point is equlal to last point
    if (numel>1) and ((path[0][0][0]-path[-1][0][-1]).length() <= 0.001):
        # Assume path is closed
        closed_path = True
        # Copy first segment and append to the end
        # to make a smooth conection between start and end
        path.append([copy_segment(path[0][0]), path[0][1]])
    offsets = []

            
    for seg, dist in path:
        offsets.append(offset_segment(seg, dist))

    joined_offsets = join_offsets(path, offsets)

    if closed_path:
        # copy the starting point of the last element back to the first element as it may have been cropped
        joined_offsets[0][0] = joined_offsets[-1][0]

        # Remove last segments as they are copies 
        del(path[-1])
        del(joined_offsets[-1])

        # Note: the first segments could have been deleted above, however it is
        # better to preserv segment order by copying the last element to the first position
        # and deleting the last.

    return joined_offsets

