from vector import Vector
from line_arc import arc_from_points, pt_angle_on_arc
import math
import numpy as np

#             dL
#  W......  ------                                                         
#         /:      :\                                                       
#        / :      : \                                                     
#       /  :      :  \                                                     
#      /   :      :   \   dM                      dM                           
#  0..:    :      :    :------:    :      :    :------:                      
#     0    a      b    c      d\   e      f   /g      h (or L)                
#                               \  :      :  /                              
#                                \ :      : /                               
#                                 \:      :/                                
#                                   ------
#                                      dR
def weave(x, L, W, dM, dL, dR):

    # Since function is periodic, calculate remainder
    # which will map x to into the first period as xx
    xx = x % L # modulus

    # Calculate x values as per sketch above
    a = (L - (dM + dM + dL + dR))/4
    b = a + dL
    c = b + a
    d = c + dM
    e = d + a
    f = e + dR
    g = f + a
    h = g + dM # or h = L

    assert xx >= 0, 'xx should not be less than zero here.'
    assert xx <= h, 'xx should not be greater than h here.'

    # Calculate y values as per plot
    if xx <= a:
        frac = (xx-0)/a
        return frac*W
    elif xx <= b:
        return W
    elif xx <= c:
        frac = (xx-b)/a
        return W - frac*W
    elif xx <= d:
        return 0
    elif xx <= e:
        frac = (xx-d)/a
        return -frac*W
    elif xx <= f:
        return -W
    elif xx <= g:
        frac = (xx-f)/a
        return -W + frac*W
    elif xx <= h:
        return 0

    # Program should never get here
    return 0

# Linear intERPolation
def angle_lerp(abc0, abc1, t):
    a0, b0, c0 = abc0
    a1, b1, c1 = abc1
    a = a0 + t*(a1-a0)
    b = b0 + t*(b1-b0)
    c = c0 + t*(c1-c0)
    return (a, b, c)
    
# d is the distance along line
def line_weave(d, L, W, dM, dL, dR, line, abcs=((0,0,0),(0,0,0))):
    p0, p1 = line

    # Calculate weave
    y = weave(d, L, W, dM, dL, dR)

    line_length = (p1-p0).length()
    t = d/line_length
    
    # Unit vector pointing to start of arc
    u = (p1-p0).normal()

    # Point on line
    pt = p0 + t*(p1-p0)
    
    # Stretch away from pt by y in direction u
    xy = y*u + pt

    # Linear interpolation through abcs
    abc = angle_lerp(abcs[0], abcs[1], t)
    
    return xy, abc

# d is the distance along arc
def arc_weave(d, L, W, dM, dL, dR, arc, abcs=((0,0,0), (0,0,0), (0,0,0))):
# x is the distance along the circumfrance of the arc

    p0, p1, p2 = arc


    # Calculate weave
    y = weave(d, L, W, dM, dL, dR)

    # Map weave result onto arc
    c, r, a0, a2 = arc_from_points(arc)
    a1 = pt_angle_on_arc(arc, p1)

    # C = 2*pi*r
    # frac = d/C
    # angle = 2*pi*frac
    # which simplifies to:
    angle = d/r # angle measured from a0

    # Unit vector pointing to start of arc
    u = (p0-c).norm()

    if a0 > a2:
        angle *= -1

    v = u.rotate(angle)
    a = a0+angle
    if a < a1:
        t = (a-a0)/(a1-a0)
        abc = angle_lerp(abcs[0], abcs[1], t)
    else:
        t = (a-a1)/(a2-a1)
        abc = angle_lerp(abcs[1], abcs[2], t)

    # Stretch unit vector by r+y
    xy = (r+y)*v + c

    
    return xy, abc

# Calculates the length or perimeter of an arc
def arc_perimeter(arc):
    c, r, a0, a2 = arc_from_points(arc)
    return r*abs(a2-a0)


# Returns 3D rotation matrix
def rot_mat(angle_a, angle_b, angle_c):
    c = math.cos(angle_a)
    s = math.sin(angle_a)
    A = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    c = math.cos(angle_b)
    s = math.sin(angle_b)
    B = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    c = math.cos(angle_c)
    s = math.sin(angle_c)
    C = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    R = np.matmul(A, np.matmul(B, C))
    return R




# if __name__ == '__main__':
if True:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # Setup plot
    fig = plt.figure()

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(223, projection='3d')
    ax3 = fig.add_subplot(224, projection='3d')



    ## WEAVE EXAMPLE

    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length

    # Distance of weld weave
    D = 400

    x = []
    y = []

    N = 1000 # Number of arc samples
    for i in range(1000):
        xx = D*i/N
        yy = weave(xx, L, W, dM, dL, dR)
        x.append(xx)
        y.append(yy)

    # Make line plot
    ax1.plot(x, y, linewidth=1.0)
    ax1.set(xlim=[0, D], ylim=[-2*W, 2*W], aspect='equal', adjustable='box')


    ## LINE WEAVE EXAMPLE

    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length
    line = [Vector(0, 0), Vector(200, 200)]
    abc0 = (0, 0, 0)
    abc1 = (math.pi/4, 0, math.pi/4)

    # Calculate perimeter of arc
    P = (line[1]-line[0]).length()

    x = []
    y = []
    xx = np.array([10, 0, 0])
    yy = np.array([0, 10, 0])
    zz = np.array([0, 0, 20])
    N = 1000 # Number of arc samples
    for i in range(1000):
        d = P*i/N # Distance along line
        pt, abc = line_weave(d, L, W, dM, dL, dR, line, (abc0, abc1))
        x.append(pt.x)
        y.append(pt.y)

        # Every 100th point, draw an axis
        if i%100==0:
            a, b, c = abc
            Rxx = np.matmul(rot_mat(a, b, c), xx.T)
            ax2.plot([pt.x, pt.x+Rxx[0]], [pt.y, pt.y+Rxx[1]], [0, 0+Rxx[2]], linewidth=1.0, color='r')
            Ryy = np.matmul(rot_mat(a, b, c), yy.T)
            ax2.plot([pt.x, pt.x+Ryy[0]], [pt.y, pt.y+Ryy[1]], [0, 0+Ryy[2]], linewidth=1.0, color='g')
            Rzz = np.matmul(rot_mat(a, b, c), zz.T)
            ax2.plot([pt.x, pt.x+Rzz[0]], [pt.y, pt.y+Rzz[1]], [0, 0+Rzz[2]], linewidth=1.0, color='orange')

    # Make arc plot
    ax2.plot(x, y, linewidth=1.0)
    ax2.set(xlim=[0, 200], ylim=[0, 200], zlim=[-100, 100], adjustable='box')
    ax2.set_axis_off()




    ## ARC WEAVE EXAMPLE

    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length
    arc = [Vector(0, 0), Vector(0, 200), Vector(200, 200)] # 3 point arc
    abc0 = (0, 0, 0)
    abc1 = (math.pi/4, 0, math.pi/4)
    abc2 = (-math.pi/2, 0, math.pi/4)

    # Calculate perimeter of arc
    P = arc_perimeter(arc)

    x = []
    y = []

    N = 1000 # Number of arc samples
    for i in range(1000):
        d = P*i/N # Distance along arc
        pt, abc = arc_weave(d, L, W, dM, dL, dR, arc, (abc0, abc1, abc2))
        x.append(pt.x)
        y.append(pt.y)

        # Every 100th point, draw an axis
        if i%100==0:
            a, b, c = abc
            Rxx = np.matmul(rot_mat(a, b, c), xx.T)
            ax3.plot([pt.x, pt.x+Rxx[0]], [pt.y, pt.y+Rxx[1]], [0, 0+Rxx[2]], linewidth=1.0, color='r')
            Ryy = np.matmul(rot_mat(a, b, c), yy.T)
            ax3.plot([pt.x, pt.x+Ryy[0]], [pt.y, pt.y+Ryy[1]], [0, 0+Ryy[2]], linewidth=1.0, color='g')
            Rzz = np.matmul(rot_mat(a, b, c), zz.T)
            ax3.plot([pt.x, pt.x+Rzz[0]], [pt.y, pt.y+Rzz[1]], [0, 0+Rzz[2]], linewidth=1.0, color='orange')

    # Make arc plot
    ax3.plot(x, y, linewidth=1.0)
    ax3.set(xlim=[-50, 250], ylim=[-50, 250], zlim=[-150, 150], adjustable='box')
    ax3.set_axis_off()


    # Show plot
    plt.tight_layout()
    plt.show()

