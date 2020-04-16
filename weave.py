from vector import Vector
from line_arc import arc_from_points, pt_angle_on_arc
import math
from math import sin, cos, atan2, asin, pi
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

# Vic, ABB may already have a function that does Spherical linear interpolation
# This is a slightly modified version of Wikipedia's version of SLERP
def slerp(v0, v1, t):
    """Spherical linear interpolation."""
    # >>> slerp([1,0,0,0], [0,0,0,1], 0.2)

    v0 = np.array(v0)
    v1 = np.array(v1)
    dot = np.sum(v0 * v1)

    if dot < 0.0:
        v1 = -v1
        dot = -dot
    
    DOT_THRESHOLD = 0.9995
    if dot > DOT_THRESHOLD:
        result = v0 + t*(v1 - v0)
        return result/np.linalg.norm(result)
    
    theta_0 = np.arccos(dot)
    sin_theta_0 = np.sin(theta_0)

    theta = theta_0 * t
    sin_theta = np.sin(theta)
    
    s0 = np.cos(theta) - dot * sin_theta / sin_theta_0
    s1 = sin_theta / sin_theta_0
    return (s0*v0) + (s1*v1)

# d is the distance along line
def line_weave(d, L, W, dM, dL, dR, line, quaternions=((0,0,0,0),(0,0,0,0))):
    p0, p1 = line
    quat0, quat1 = quaternions
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

    # Spherical linear interpolation from quat0 to quat1
    quat = slerp(quat0, quat1, t)
    
    return xy, quat

# d is the distance along arc
def arc_weave(d, L, W, dM, dL, dR, arc, quaternions=((0,0,0,0), (0,0,0,0), (0,0,0,0))):
# x is the distance along the circumfrance of the arc

    p0, p1, p2 = arc
    quat0, quat1, quat2 = quaternions

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
        # Reorder to make a2 > a0
        a0 = -a0
        a1 = -a1
        a2 = -a2

    v = u.rotate(angle)
    a = a0+angle

    if a < a1:
        t = (a-a0)/(a1-a0)
        quat = slerp(quat0, quat1, t)
    else:
        t = (a-a1)/(a2-a1)
        quat = slerp(quat1, quat2, t)

    # Stretch unit vector by r+y
    xy = (r+y)*v + c

    return xy, quat

# Calculates the length or perimeter of an arc
def arc_perimeter(arc):
    c, r, a0, a2 = arc_from_points(arc)
    return r*abs(a2-a0)


# Vic, you dont need this function. Only used for plotting
# Returns 3D rotation matrix
def rot_mat(angle_a, angle_b, angle_c):
    c = cos(angle_a)
    s = sin(angle_a)
    A = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    c = cos(angle_b)
    s = sin(angle_b)
    B = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    c = cos(angle_c)
    s = sin(angle_c)
    C = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    R = np.matmul(A, np.matmul(B, C))
    return R

# Vic you dont need this function. Only used for plotting
# Vic, you dont need this function. Only used for plotting
def quaternion_to_euler(quat):
    q0, q1, q2, q3 = quat
    a = atan2(2*(q0*q3 + q1*q2), 1-2*(q2*q2+q3*q3))
    b = asin(2*(q0*q2 - q3*q1))
    c = atan2(2*(q0*q1 + q2*q3), 1-2*(q1*q1+q2*q2))
    return (a, b, c)

# Vic, you dont need this function. Only used for plotting
def euler_to_quaternion(abc):
    a, b, c = abc
    q0 =cos(c/2)*cos(b/2)*cos(a/2)+sin(c/2)*sin(b/2)*sin(a/2)
    q1 =sin(c/2)*cos(b/2)*cos(a/2)-cos(c/2)*sin(b/2)*sin(a/2)
    q2 =cos(c/2)*sin(b/2)*cos(a/2)+sin(c/2)*cos(b/2)*sin(a/2)
    q3 =cos(c/2)*cos(b/2)*sin(a/2)-sin(c/2)*sin(b/2)*cos(a/2)
    return (q0, q1, q2, q3)


# if __name__ == '__main__':
if True:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    ######################
    ## 2D WEAVE EXAMPLE ##
    #####################
    # Setup plot
    fig1 = plt.figure(1)

    ax1 = fig1.add_subplot(111)
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
    for i in range(N):
        xx = D*i/N
        yy = weave(xx, L, W, dM, dL, dR)
        x.append(xx)
        y.append(yy)

    # Make line plot
    ax1.plot(x, y, linewidth=1.0)
    ax1.set(xlim=[0, D], ylim=[-2*W, 2*W], aspect='equal', adjustable='box')


    ###########################
    ## 3D LINE WEAVE EXAMPLE ##
    ###########################
    # Setup plot
    fig3 = plt.figure(3)

    ax3 = fig3.add_subplot(111, projection='3d')
    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length
    line = [Vector(0, 0), Vector(200, 200)]
    abc0 = (0, 0, 0)
    abc1 = (pi, pi, pi/2)
    quat0 = euler_to_quaternion(abc0)
    quat1 = euler_to_quaternion(abc1)

    # Calculate perimeter of arc
    P = (line[1]-line[0]).length()

    x = []
    y = []
    xx = np.array([10, 0, 0])
    yy = np.array([0, 10, 0])
    zz = np.array([0, 0, 20])
    N = 1000 # Number of arc samples
    for i in range(N):
        d = P*i/N # Distance along line
        pt, quat = line_weave(d, L, W, dM, dL, dR, line, (quat0, quat1))
        abc = quaternion_to_euler(quat)
        x.append(pt.x)
        y.append(pt.y)

        # Every 100th point, draw an ax3is
        if i%100==0 or i==N-1:
            a, b, c = abc
            Rxx = np.matmul(rot_mat(a, b, c), xx.T)
            ax3.plot([pt.x, pt.x+Rxx[0]], [pt.y, pt.y+Rxx[1]], [0, 0+Rxx[2]], linewidth=1.0, color='r')
            Ryy = np.matmul(rot_mat(a, b, c), yy.T)
            ax3.plot([pt.x, pt.x+Ryy[0]], [pt.y, pt.y+Ryy[1]], [0, 0+Ryy[2]], linewidth=1.0, color='g')
            Rzz = np.matmul(rot_mat(a, b, c), zz.T)
            ax3.plot([pt.x, pt.x+Rzz[0]], [pt.y, pt.y+Rzz[1]], [0, 0+Rzz[2]], linewidth=1.0, color='orange')

    # Make arc plot
    ax3.plot(x, y, linewidth=1.0)
    ax3.set(xlim=[0, 200], ylim=[0, 200], zlim=[-100, 100], adjustable='box')
    ax3.set_title('Quaternion Slerp')
    ax3.set_axis_off()

    ##########################
    ## 3D ARC WEAVE EXAMPLE ##
    ##########################
    # Setup plot
    fig5 = plt.figure(5)

    ax5 = fig5.add_subplot(111, projection='3d')
    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length
    arc = [Vector(0, 0), Vector(0, 200), Vector(200, 200)] # 3 point arc
    arc = arc[::-1]
    abc0 = (0, 0, pi/2)
    abc1 = (0, 0, 0)
    abc2 = (pi, -pi/2, 0)
    quat0 = euler_to_quaternion(abc0)
    quat1 = euler_to_quaternion(abc1)
    quat2 = euler_to_quaternion(abc2)

    # Calculate perimeter of arc
    P = arc_perimeter(arc)

    x = []
    y = []

    N = 1000 # Number of arc samples
    for i in range(N):
        d = P*i/N # Distance along arc
        pt, quat = arc_weave(d, L, W, dM, dL, dR, arc, (quat0, quat1, quat2))
        abc = quaternion_to_euler(quat)
        x.append(pt.x)
        y.append(pt.y)

        # Every 100th point, draw an axis
        if i%100==0 or i==N-1:
            a, b, c = abc
            Rxx = np.matmul(rot_mat(a, b, c), xx.T)
            ax5.plot([pt.x, pt.x+Rxx[0]], [pt.y, pt.y+Rxx[1]], [0, 0+Rxx[2]], linewidth=1.0, color='r')
            Ryy = np.matmul(rot_mat(a, b, c), yy.T)
            ax5.plot([pt.x, pt.x+Ryy[0]], [pt.y, pt.y+Ryy[1]], [0, 0+Ryy[2]], linewidth=1.0, color='g')
            Rzz = np.matmul(rot_mat(a, b, c), zz.T)
            ax5.plot([pt.x, pt.x+Rzz[0]], [pt.y, pt.y+Rzz[1]], [0, 0+Rzz[2]], linewidth=1.0, color='orange')

    # Make arc plot
    ax5.plot(x, y, linewidth=1.0)
    ax5.set(xlim=[-50, 250], ylim=[-50, 250], zlim=[-150, 150], adjustable='box')
    ax5.set_title('Quaternion Slerp')
    # ax5.set_axis_off()


    #Show plots
    plt.tight_layout()
    plt.show()

