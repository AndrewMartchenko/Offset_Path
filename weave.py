from vector import Vector
from line_arc import arc_from_points
import math

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
def line_weave(x, L, W, dM, dL, dR):

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


# x is the distance along the circumfrance of the arc
def arc_weave(x, L, W, dM, dL, dR, arc):
    p0, p1, p2 = arc


    # Calculate line weave
    y = line_weave(x, L, W, dM, dL, dR)

    # Map weave result onto arc
    c, r, a0, a2 = arc_from_points(arc)

    # C = 2*pi*r
    # frac = x/C
    # angle = 2*pi*frac
    # which simplifies to:
    angle = x/r

    # Unit vector pointing to start of arc
    u = (p0-c).norm()

    # Rotate unit vector to point to x
    if a0 < a2:
        v = u.rotate(angle)
    else:
        v = u.rotate(-angle)

    # Stretch unit vector by r+y
    xy = (r+y)*v + c
    return xy

# Calculates the length or perimeter of an arc
def arc_perimeter(arc):
    c, r, a0, a2 = arc_from_points(arc)
    return r*abs(a2-a0)





# if __name__ == '__main__':
if True:
    import matplotlib.pyplot as plt


    # Setup plot
    fig = plt.figure(figsize=(12,9))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)



    ## LINE EXAMPLE

    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length

    # Distance of weld weave
    D = 200

    x = []
    y = []

    N = 1000 # Number of arc samples
    for i in range(1000):
        xx = D*i/N
        yy = line_weave(xx, L, W, dM, dL, dR)
        x.append(xx)
        y.append(yy)

    # Make line plot
    ax1.plot(x, y)
    ax1.set(xlim=[0, D], ylim=[-D/2, D/2], aspect=1, adjustable='box')





    ## ARC EXAMPLE

    L = 20 # Length or period of weave
    W = 5  # Width or amplitude of weave
    dM = 3 # Dwell middle length 
    dL = 2 # Dwell left length
    dR = 2 # Dwell right length
    arc = [Vector(0, 0), Vector(0, 200), Vector(200, 200)] # 3 point arc

    # Calculate perimeter of arc
    P = arc_perimeter(arc)

    x = []
    y = []

    N = 1000 # Number of arc samples
    for i in range(1000):
        xx = P*i/N
        pt = arc_weave(xx, L, W, dM, dL, dR, arc)
        x.append(pt.x)
        y.append(pt.y)

    # Make arc plot
    ax2.plot(x, y)
    ax2.set(xlim=[-50, 250], ylim=[-50, 250], aspect=1, adjustable='box')


    # Show plot
    plt.show()

