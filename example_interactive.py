import math
import numpy as np
import cv2
from vector import Vector
from line_arc import *
from offset import *


WHITE = (1, 1, 1)
RED = (0, 0, 1)
GREEN = (0, 1, 0)
DARK_GREEN = (0, 0.5, 0)

def draw_line(img, p0, p1, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.line(img, (round(p0.x), round(y_offset-p0.y)), (round(p1.x), round(y_offset-p1.y)), color=color)


# This draws arcs more accurately than the opencv ellipse function
def draw_arc(img, p0, p1, p2, color=WHITE, step=0.01):
    c, r, a0, a2 = arc_from_points([p0, p1, p2])
    t = 0
    while t < 1:
        pt0 = c + r*Vector(math.cos(a0+t*(a2-a0)), math.sin(a0+t*(a2-a0)))
        t += step
        pt1 = c + r*Vector(math.cos(a0+t*(a2-a0)), math.sin(a0+t*(a2-a0)))
        draw_line(img, pt0, pt1, color)

def draw_circle(img, c, r, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.circle(img, (c.x, y_offset-c.y), r, RED)
    
def draw_segments(img, segments, color=WHITE):
    for seg in segments:
        if is_line(seg):
            draw_line(img, *seg, color)
        elif is_arc(seg):
            draw_arc(img, *seg, color, 0.001)

GRID_SIZE = 20
def draw_grid(img):
    img[::GRID_SIZE,::GRID_SIZE,:] = 0.5

            
# Update key points on click
def on_mouse(event, x, y, img, new_img, mode, path, offsets, guide):


    x = round(x/GRID_SIZE)*GRID_SIZE
    y = round(y/GRID_SIZE)*GRID_SIZE
    
    y_offset = img.shape[0]-1
    y = y_offset-y

    xy = Vector(x, y)

    new_img[:] = img[:]
    if event == cv2.EVENT_MOUSEMOVE:

        # Guide circle
        draw_circle(new_img, xy, 5, RED)

        if mode == LINE:
            if len(guide) == 1:
                draw_line(new_img, guide[0], xy, RED)
        else:
            if len(guide) == 1:
                draw_line(new_img, guide[0], xy, RED)
            elif len(guide) == 2:
                if (guide[1].x != x) and (guide[1].y != y):
                    draw_arc(new_img, guide[0], guide[1], xy, RED)


        cv2.imshow('Canvas', new_img)

    elif event == cv2.EVENT_LBUTTONDOWN:

        img[:,:,:] = 0

        # draw grid
        draw_grid(img)


        draw_circle(img, xy, 5, WHITE)
        
        numel = len(guide)
        if mode == LINE:
            if numel == 0:
                guide.append(xy)
            else:
                path.append([guide[0], xy])

                guide[0] = xy

                offsets.append(offset_segment(path[-1], 30))


        else:  # mode = ARC
            if numel < 2:
                guide.append(xy)
            else:
                path.append([guide[0], guide[1], xy])
                guide[0] = xy
                del(guide[1])
                offsets.append(offset_segment(path[-1], 30))


        joined_offsets = join_offsets(path, offsets)

        draw_segments(img, path, WHITE)
        # draw_segments(img, offsets, DARK_GREEN)
        draw_segments(img, joined_offsets, GREEN)

        
        cv2.imshow('Canvas', img)



LINE = 0
ARC = 1

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
def main():    

    pw = 1165
    pl = 1165
    cv2.namedWindow('Canvas', 0)

    cv2.resizeWindow('Canvas', WINDOW_WIDTH, WINDOW_HEIGHT)
    img = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3))
    new_img = np.zeros_like(img)
    draw_grid(img)

    path = []
    offsets = []
    guide = []
    #           line      arc
    # path = [ (p0, p1), (p0, p1, p2), ... ]
    

    mode = ARC
    

    cv2.setMouseCallback('Canvas', lambda event, x, y, flags, param: on_mouse(event, x, y, img, new_img, mode, path, offsets, guide))

    while True:
        # Break if Esc or 'q' is pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 or k == ord('q'):
            break
        elif k == ord('l'):
            mode = LINE
        elif k == ord('a'):
            mode = ARC

    cv2.destroyAllWindows()

if True:# __name__ == '__main__':
    main()
