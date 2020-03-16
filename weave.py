from vector import Vector
from line_arc import arc_from_points
import math

#         dL
#       ------                                                         
#     /:      :\                                                       
#    / :      : \                                                     
#   /  :      :  \                                                     
#  /   :      :   \   dM                      dM                           
# :    :      :    :------:    :      :    :------:                      
# 0    a      b    c      d\   e      f   /g      h (or L)                
#                           \  :      :  /                              
#                            \ :      : /                               
#                             \:      :/                                
#                               ------
#                                  dR
def linear_weave(xx, L, W, dM, dL, dR):

    # Since function is periodic, calculate remainder
    # which will map xx to into the first period as x
    x = xx%L # modulus

    # Calculate values as per sketch above
    a = (L - (dM + dM + dL + dR))/4
    b = a + dL
    c = b + a
    d = c + dM
    e = d + a
    f = e + dR
    g = f + a
    h = g + dM # or h = L

    assert x >= 0, 'x should not be less than zero here.'
    assert x <= h, 'x should not be greater than h here.'

    if x <= a:
        frac = (x-0)/a
        return frac*W
    elif x <= b:
        return W
    elif x <= c:
        frac = (x-b)/a
        return W - frac*W
    elif x <= d:
        return 0
    elif x <= e:
        frac = (x-d)/a
        return -frac*W
    elif x <= f:
        return -W
    elif x <= g:
        frac = (x-f)/a
        return -W + frac*W
    elif x <= h:
        return 0

    # Program should never get here
    return 0


# xx is the distance along the circumfrance of the arc
def arc_weave(xx, L, W, dM, dL, dR, arc):
    p0, p1, p2 = arc


    # Calculate linear weave
    y = linear_weave(xx, L, W, dM, dL, dR)

    c, r, a0, a2 = arc_from_points(arc)

    # Map weave result onto arc

    # C = 2*pi*r
    # frac = xx/C
    # angle = 2*pi*frac
    # which simplifies to:
    angle = xx/r

    u = (p0-c).norm()
    if a0 < a2:
        v = u.rotate(angle)
    else:
        v = u.rotate(-angle)

    xy = (r+y)*v + c

    return xy




## Test

import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.mlab as mlab
# import matplotlib.gridspec as gridspec



# x = np.arange(0, 300, 0.5)
# y = np.zeros_like(x)
# xa = []
# ya = []

# L = 20
# W = 5
# dM = 3
# dL = 2
# dR = 2
# arc = [Vector(0, 0), Vector(0, 200), Vector(200, 200)]

# for i, xx in enumerate(x):
#     y[i] = linear_weave(xx, L, W, dM, dL, dR)
    
#     pt = arc_weave(xx, L, W, dM, dL, dR, arc)
#     xa.append(pt.x)
#     ya.append(pt.y)

# # plt.subplot(211)
# # plt.plot(x, y)
# plt.subplot(111)
# plt.plot(xa, ya)

# plt.show()









L = 20
W = 5
dM = 3
dL = 2
dR = 2
arc = [Vector(0, 0), Vector(0, 200), Vector(200, 200)]


c, r, a0, a2 = arc_from_points(arc)

arc_length = r*abs(a2-a0)

perim  = np.arange(0, arc_length, 0.5)
x = np.zeros_like(perim)
y = np.zeros_like(perim)

for i, xx in enumerate(perim):
    xy = arc_weave(xx, L, W, dM, dL, dR, arc)
    x[i] = xy.x
    y[i] = xy.y

plt.subplot(111)
plt.plot(x, y)

plt.show()
















