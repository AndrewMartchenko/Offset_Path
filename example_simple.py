from vector import Vector
# from line_arc import *
from offset import offset_path
from fill import line_fill, arc_fill

# if __name__ == '__main__':
if True:

    # Lines are lists of 2 vectors
    # Arcs are list of 3 vectors
    # For example:
    seg_1 = [Vector(100, 100), Vector(100, 300)] # line
    seg_2 = [Vector(100, 300), Vector(200, 300), Vector(300, 400)] # arc
    seg_3 = [Vector(300, 400), Vector(0, 400)] # line

    # Paths are lists of line and arc segments
    path = [seg_1, seg_2, seg_3]

    # Create the offset path
    joined_offsets = offset_path(path, 20)





    print(len(joined_offsets))

    # Result will be a list of segments
    # joined_offsets = [
    #     [Vector(80.0, 100.0), Vector(80.0, 300.0)],
    #     [Vector(80.0, 300.0), Vector(88.3, 316.2), Vector(106.3, 318.9)],
    #     [Vector(106.3, 318.9), Vector(198.4, 320.6), Vector(269.0, 380.0)],
    #     [Vector(269.0, 380.0), Vector(0.0, 380.0)]
    #                  ]

    # Note: The result contains 4 line segments because additional arc was
    #       added for to smooth out exterior angle.


    fill_lines = fill(joined_offsets, vec=Vector(1,1), space=20)

    # Result will be a list of lines:
    # fill_lines = [
    #     [Vector(80.0, 193.7), Vector(213.7, 327.4)],
    #     [Vector(80.0, 222.0), Vector(171.5, 313.5)],
    #     [Vector(80.0, 250.2), Vector(141.8, 312.1)],
    #     [Vector(80.0, 278.5), Vector(117.2, 315.8)],
    #     [Vector(82.1, 309.0), Vector( 91.0, 317.8)]
    #              ]
