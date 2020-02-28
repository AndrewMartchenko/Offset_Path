import math
import numpy as np
import cv2
from vector import Vector
from line_arc import *
from offset import *
from fill import *

LINE = 0
ARC = 1

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

WHITE = (1, 1, 1)
RED = (0, 0, 1)
GREEN = (0, 1, 0)
DARK_GREEN = (0, 0.5, 0)
YELLOW = (0, 1, 1)

def draw_line(img, p0, p1, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.line(img, (round(p0.x), round(y_offset-p0.y)), (round(p1.x), round(y_offset-p1.y)), color=color)

def draw_rect(img, p0, p1, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.rectangle(img, (round(p0.x), round(y_offset-p0.y)) , (round(p1.x), round(y_offset-p1.y)), color=color)


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
    cv2.putText(img, text='(A)rc', org=(0,30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=YELLOW)
    cv2.putText(img, text='(L)ine', org=(0,70), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=YELLOW)
    img[::GRID_SIZE,::GRID_SIZE,:] = 0.5

            
# Update key points on click
def on_mouse(event, x, y, model, view):


    x = round(x/GRID_SIZE)*GRID_SIZE
    y = round(y/GRID_SIZE)*GRID_SIZE
    
    y_offset = view.img.shape[0]-1
    y = y_offset-y

    xy = Vector(x, y)

    view.new_img[:] = view.img[:]
    if event == cv2.EVENT_MOUSEMOVE:

        # Guide circle
        draw_circle(view.new_img, xy, 5, RED)

        if view.mode == LINE:
            if len(view.guide) == 1:
                draw_line(view.new_img, view.guide[0], xy, RED)
        else:
            if len(view.guide) == 1:
                draw_line(view.new_img, view.guide[0], xy, RED)
            elif len(view.guide) == 2:
                if (view.guide[1].x != x) and (view.guide[1].y != y):
                    draw_arc(view.new_img, view.guide[0], view.guide[1], xy, RED)


        cv2.imshow('Canvas', view.new_img)

    elif event == cv2.EVENT_LBUTTONDOWN:

        view.img[:, :, :] = 0

        # draw grid
        draw_grid(view.img)


        draw_circle(view.img, xy, 5, WHITE)
        
        numel = len(view.guide)
        if view.mode == LINE:
            if numel == 0:
                view.guide.append(xy)
            else:
                model.path.append([view.guide[0], xy])

                view.guide[0] = xy

                model.offsets.append(offset_segment(model.path[-1], 30))


        else:  # mode = ARC
            if numel < 2:
                view.guide.append(xy)
            else:
                model.path.append([view.guide[0], view.guide[1], xy])
                view.guide[0] = xy
                del(view.guide[1])
                model.offsets.append(offset_segment(model.path[-1], 30))


        model.joined_offsets = join_offsets(model.path, model.offsets)

        draw_segments(view.img, model.path, WHITE)
        draw_segments(view.img, model.joined_offsets, GREEN)

        bbox = path_bbox(model.joined_offsets)
        if bbox:
            draw_rect(view.img, bbox[0], bbox[1])

        cv2.imshow('Canvas', view.img)


class Model():
    def __init__(self, path=[], offsets=[], guide=[]):
        self.path = path
        self.offsets = offsets
        self.joined_offsets = []
    

class View():
    def __init__(self, width, height, mode=ARC, guide=[]):
        self.img  = np.zeros((height, width, 3))
        self.new_img = np.zeros_like(self.img)
        draw_grid(self.img)
        self.mode = mode
        self.guide = guide   
        

def main():    

    cv2.namedWindow('Canvas', 0)
    cv2.resizeWindow('Canvas', WINDOW_WIDTH, WINDOW_HEIGHT)

    model = Model()
    view = View(WINDOW_WIDTH, WINDOW_HEIGHT)

    #           line      arc
    # path = [ (p0, p1), (p0, p1, p2), ... ]
    
    cv2.setMouseCallback('Canvas', lambda event, x, y, flags, param: on_mouse(event, x, y, model, view))

    while True:
        # Break if Esc or 'q' is pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 or k == ord('q'):
            break
        elif k == ord('l'):
            view.mode = LINE
        elif k == ord('a'):
            view.mode = ARC
        elif k == ord('c'):
            # Close path
            pass
        elif k == ord('f'):
            # Fill
            pass


    cv2.destroyAllWindows()

if True:# __name__ == '__main__':
    main()
