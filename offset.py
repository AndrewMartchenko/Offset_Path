import math
from vector import Vector
from line_arc import *


# TODO:
# Process
# 1. extend disjoint offsets to intersect
# 2. offset extended offsests back by small amount
# 3. crop them to their intersection
# 4. use these line segments as the temp new path
# 
#  Write function to add a unit line segment to the start/end of an arc

def segment_intersect(s0, s1):
    if is_line(s0) and is_line(s1):
        pt, _ = line_segment_intersect(s0, s1)
    elif is_line(s0) and is_arc(s1):
        pt, _ = line_segment_arc_intersect([s0[1], s0[0]], s1)
    elif is_arc(s0) and is_line(s1):
        pt, _ = line_segment_arc_intersect(s1, s0)
    elif is_arc(s0) and is_arc(s1):
        pt, _ = arc_arc_intersect([s0[2], s0[1], s0[0]], s1)



def line_line_extend(s0, s1, r):

    
    # Find intersection if offset was extended
    pt, _, _ = line_intersect(s0, s1)
    # Make temp copy of these segments
    s0_temp = [s0[0], pt]
    s1_temp = [pt, s1[1]]

    # Offset segments back (-ve) by r and use
    path0 = offset_segment(s0_temp, -r)
    path1 = offset_segment(s1_temp, -r)

    # Find intersection of segments and use as a temp path
    c, t, s = line_intersect(path0, path1)
    print(t, s)
    path0 = [path0[0], c]
    path1 = [c, path1[1]]

    ss0 = offset_segment(path0, r)
    ss1 = offset_segment(path1, r)

    return ss0, ss1, c


def line_arc_extend(s0, s1, pt, r):
    s0_temp = [s0[0], pt]
    s1_temp = arc_clip(s1, pt, s1[2])

    path0 = offset_segment(s0_temp, -r)
    path1 = offset_segment(s1_temp, -r)

    c, _ = line_arc_intersect(path0[::-1], path1)

    path0 = [path0[0], c]
    path1 = arc_clip(path1, c, path1[2])

    ss0 = offset_segment(path0, r)
    ss1 = offset_segment(path1, r)

    return ss0, ss1, c


def arc_line_extend(s0, s1, pt, r):
    s0_temp = arc_clip(s0, s0[0], pt)
    s1_temp = [pt, s1[1]]

    path0 = offset_segment(s0_temp, -r)
    path1 = offset_segment(s1_temp, -r)

    c, _ = line_arc_intersect(path1, path0)

    path0 = arc_clip(path0, path0[0], c)
    path1 = [c, path1[1]]

    ss0 = offset_segment(path0, r)
    ss1 = offset_segment(path1, r)

    return ss0, ss1, c


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

        d0 = path[j][1]
        d1 = path[j+1][1]


        if is_line(s0):
            u0 = line_tangent(s0) 
        else:
            u0 = arc_end_tangent(s0)

        if is_line(s1):
            u1 = line_tangent(s1) 
        else:
            u1 = arc_start_tangent(s1)


        angle = Vector.angle_between(u0, u1)

        # print('ANGLE: ', angle*180/math.pi)
        if angle > 0:  # Interior angle

            # Lines are expected to intersec, but this won't always be the
            # case if offsets are different.

            if is_line(s0) and is_line(s1):
                pt, _, _ =line_intersect(s0, s1)
                s0[1] = pt.copy()
                s1[0] = pt.copy()


            elif is_line(s0) and is_arc(s1):
                pt, _ = line_segment_arc_intersect([s0[1], s0[0]], s1)
                if pt:
                    s0[1] = pt.copy()
                    s1[:] = arc_clip(s1, pt.copy(), s1[2].copy())
                else:
                    if d0 > d1:  # Extend the line
                        pt, _ = line_arc_intersect([s0[1], s0[0]], s1)
                        s0[1] = pt.copy()
                        s1[:] = arc_clip(s1, pt.copy(), s1[2].copy())
                    else:  # Add extra line to start of arc
                        joined_offsets.insert(i+1, [s1[0]-u1, s1[0]])
                        s1 = joined_offsets[i+1]
                        pt, _, _ =line_intersect(s0, s1)
                        s0[1] = pt.copy()
                        s1[0] = pt.copy()
                        i += 1
                        n += 1
                        

            elif is_arc(s0) and is_line(s1):
                pt, _ = line_segment_arc_intersect(s1, s0)
                if pt:
                    s1[0] = pt.copy()
                    s0[:] = arc_clip(s0, s0[0].copy(), pt.copy())
                else:
                    if d0 > d1:  # Add extra line to end of arc0
                        joined_offsets.insert(i+1, [s0[2], s0[2]+u0])
                        s0 = joined_offsets[i+1]
                        pt, _, _ = line_intersect(s0, s1)
                        s0[1] = pt.copy()
                        s1[0] = pt.copy()
                        i += 1
                        n += 1
                    else: # Extend line
                        pt, _ = line_arc_intersect(s1, s0)
                        s0[2] = pt.copy()
                        s1[:] = arc_clip(s0, s0[0].copy(), pt.copy())

            elif is_arc(s0) and is_arc(s1):
                pt, _ = arc_arc_intersect([s0[2], s0[1], s0[0]], s1)
                if pt:
                    s0[:] = arc_clip(s0, s0[0].copy(), pt.copy())
                    s1[:] = arc_clip(s1, pt.copy(), s1[2].copy())
                else:
                    if d0 > d1:  # Add line to s0
                        joined_offsets.insert(i+1, [s0[2], s0[2]+u0])
                        s0 = joined_offsets[i+1]
                        pt, _ = line_arc_intersect(s0, s1)
                        s0[1] = pt.copy()
                        s1[:] = arc_clip(s1, pt, s1[2])

                        i += 1
                        n += 1
                    else:  # Add extra line to s1
                        joined_offsets.insert(i+1, [s1[0]-u1, s1[0]])
                        s1 = joined_offsets[i+1]
                        pt, _ = line_arc_intersect(s1, s0)
                        s0[:] = arc_clip(s0, s0[0], pt)
                        s1[0] = pt.copy()
                        i += 1
                        n += 1

            
        else:  # Exterior angle
            arc_i = i+1 # Exterior arc index
            
            if d0 == d1:
                # Draw arc between segments

                p0 = s0[-1].copy() # Copy last point
                p2 = s1[0].copy()
                r = path[j][1]
                c = path[j+1][0][0]
                
            else:


                r = min(d0, d1)
                
                
                if is_line(s0) and is_line(s1):
                    s0[:], s1[:], c = line_line_extend(s0, s1, r)
                    p0 = s0[1]
                    p2 = s1[0]

                elif is_line(s0) and is_arc(s1):

                    pt, _ = line_arc_intersect(s0[::-1], s1)
                    
                    # If line and arc intersect by extending line
                    if pt_angle_on_arc(s1, pt) is None:
                        # Extend arc (s1)
                        joined_offsets.insert(i+1, [s1[0]-u1, s1[0]])
                        s1 = joined_offsets[i+1]
                        s0[:], s1[:], c = line_line_extend(s0, s1, r)
                        p0 = s0[1]
                        p2 = s1[0]
                        i += 1
                        n += 1

                    else:
                        s0[:], s1[:], c = line_arc_extend(s0, s1, pt, r)

                        p0 = s0[1]
                        p2 = s1[0]

                        
                elif is_arc(s0) and is_line(s1):
                    pt, _ = line_arc_intersect(s1, s0)
                    
                    # If line and arc intersect by extending line
                    if pt_angle_on_arc(s0, pt) is None:
                        # Extend arc (s0)
                        joined_offsets.insert(i+1, [s0[2], s0[2]+u0])
                        s0 = joined_offsets[i+1]
                        s0[:], s1[:], c = line_line_extend(s0, s1, r)
                        p0 = s0[1]
                        p2 = s1[0]
                        i += 1
                        arc_i +=1 # because we inserted a line befor the arc
                        n += 1

                    else:

                        s0[:], s1[:], c = arc_line_extend(s0, s1, pt, r)
                        p0 = s0[2]
                        p2 = s1[0]

                elif is_arc(s0) and is_arc(s1):

                    if d0 < d1:  # Add line to s0
                        # add line to end of s0
                        joined_offsets.insert(i+1, [s0[2], s0[2]+u0])
                        s0 = joined_offsets[i+1]
                        i += 1
                        arc_i += 1
                        n += 1
                        pt, _ = line_arc_intersect(s0, s1)
                        if pt_angle_on_arc(s1, pt) is None:
                            # if still no intersect, extend s1 also

                            # Angle is acute. Need to handle this better 
                            joined_offsets.insert(i+1, [s1[0]-u1, s1[0]])
                            s1 = joined_offsets[i+1]
                            i += 1
                            n += 1
                            s0[:], s1[:], c = line_line_extend(s0, s1, r)
                            p0 = s0[1]
                            p2 = s1[0]
                        else:
                            s0[:], s1[:], c = line_arc_extend(s0, s1, pt, r)
                            p0 = s0[1]
                            p2 = s1[0]

                         
                    else:
                        # Add line to start of s1
                        joined_offsets.insert(i+1, [s1[0]-u1, s1[0].copy()])
                        s1 = joined_offsets[i+1]
                        i += 1
                        n += 1
                        pt, _ = line_arc_intersect(s1, s0)
                        if pt_angle_on_arc(s0, pt) is None:
                            # Extend arc (s0)
                            # Angle is acute. Need to handle this better
                            print('here i am')
                            joined_offsets.insert(i, [s0[2].copy(), s0[2]+u0])
                            s0 = joined_offsets[i]
                            i += 1
                            arc_i += 1
                            n += 1
                            s0[:], s1[:], c = line_line_extend(s0, s1, r)
                            # _, _, c = line_line_extend(s0, s1, r)
                            p0 = s0[1]
                            p2 = s1[0]

                        else:
                            
                            s0[:], s1[:], c = arc_line_extend(s0, s1, pt, r)
                            p0 = s0[2]
                            p2 = s1[0]



            # Add the exterior arc
            m = (p0+p2)/2
            p1 = r*(m-c).norm()+c
            joined_offsets.insert(arc_i, [p0, p1, p2])
            i += 1
            n += 1
                
        i += 1
        j += 1

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

