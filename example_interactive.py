
import math
import numpy as np
import cv2
from vector import Vector
from line_arc import *
from offset import *
from fill import *
import time


LINE = 0
ARC = 1

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

WHITE = (1, 1, 1)
GRAY = (0.5, 0.5, 0.5)
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
    cv2.circle(img, (round(c.x), round(y_offset-c.y)), r, color)
    
def draw_segments(img, segments, color=WHITE):
    for seg in segments:
        if is_line(seg):
            draw_line(img, *seg, color)
        elif is_arc(seg):
            draw_arc(img, *seg, color, 0.001)


def draw_path(img, path, color=WHITE):
    for seg, _ in path:
        if is_line(seg):
            draw_line(img, *seg, color)
        elif is_arc(seg):
            draw_arc(img, *seg, color, 0.001)
            
GRID_SIZE = 20
def draw_grid(img):
    y = 10
    dy = 30
    y += dy
    cv2.putText(img, text='(A)rc', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    y += dy
    cv2.putText(img, text='(L)ine', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    y += dy
    cv2.putText(img, text='(P)lus Offset', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    y += dy
    cv2.putText(img, text='(M)inus Offset', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    y += dy
    cv2.putText(img, text='(D)elete', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    y += dy
    cv2.putText(img, text='(Q)uit', org=(0, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=YELLOW)
    img[::GRID_SIZE,::GRID_SIZE,:] = 0.5

            
# Update key points on click
def on_mouse(event, x, y, model, view):

    x = round(x/GRID_SIZE)*GRID_SIZE
    y = round(y/GRID_SIZE)*GRID_SIZE

    view.old_x = x
    view.old_y = y
    
    y_offset = view.img.shape[0]-1
    y = y_offset-y

    xy = Vector(x, y)

    view.new_img[:] = view.img[:]
    if event == cv2.EVENT_MOUSEMOVE:

        # Guide circle
        draw_circle(view.new_img, xy, 5, RED)

        if view.mode == LINE:
            if len(view.guide) == 1:
                if (view.guide[0].x != x) or (view.guide[0].y != y):
                    guide = [view.guide[0], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_line(view.new_img, guide[0], guide[1], GRAY)
                    draw_line(view.new_img, offset[0], offset[1], DARK_GREEN)
        else:
            if len(view.guide) == 1:
                if (view.guide[0].x != x) or (view.guide[0].y != y):
                    guide = [view.guide[0], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_line(view.new_img, guide[0], guide[1], GRAY)
                    draw_line(view.new_img, offset[0], offset[1], DARK_GREEN)
            elif len(view.guide) == 2:
                # if (view.guide[1].x != x) and (view.guide[1].y != y):
                if not Vector.is_collinear(view.guide[0], view.guide[1], xy):
                    guide = [view.guide[0], view.guide[1], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_arc(view.new_img, guide[0], guide[1], guide[2], GRAY)
                    draw_arc(view.new_img, offset[0], offset[1], offset[2], DARK_GREEN)



        cv2.imshow('Canvas', view.new_img)

    elif event == cv2.EVENT_LBUTTONDOWN:

        


        draw_circle(view.img, xy, 5, WHITE)
        
        numel = len(view.guide)
        if view.mode == LINE:
            if numel == 0:
                view.guide.append(xy)
            else:
                model.path.append([[view.guide[0], xy], model.gap])

                view.guide[0] = xy



        else:  # mode = ARC
            if numel < 2:
                view.guide.append(xy)
            else:
                model.path.append([[view.guide[0], view.guide[1], xy], model.gap])
                view.guide[0] = xy
                del(view.guide[1])



    if event == "redraw" or event == cv2.EVENT_LBUTTONDOWN:

        view.img[:, :, :] = 0
        # draw grid
        draw_grid(view.img)
        
        model.joined_offsets = offset_path(model.path)


        draw_path(view.img, model.path, WHITE)
        draw_segments(view.img, model.joined_offsets, GREEN)

        # bbox = path_bbox(model.joined_offsets)
        # if bbox:
            # draw_rect(view.img, bbox[0], bbox[1])

        vec = Vector(math.cos(model.angle), math.sin(model.angle))
        fill_lines = fill(model.joined_offsets, vec, model.space)

        # Print path to avoid having to draw one every time.
        # print(model.path)

        for line in fill_lines:
            draw_line(view.img, line[0], line[1], YELLOW)

        cv2.imshow('Canvas', view.img)



class Model():
    def __init__(self, path=[], guide=[]):
        self.path = path
        self.joined_offsets = []
        self.angle = math.pi/4
        self.space = 20
        self.gap = 40 # Offset gap
    

class View():
    def __init__(self, width, height, mode=LINE, guide=[]):
        self.img  = np.zeros((height, width, 3))
        self.new_img = np.zeros_like(self.img)
        draw_grid(self.img)
        self.mode = mode
        self.guide = guide
        self.old_x = 0
        self.old_y = 0


    def clear(self):
        self.img[:,:,:]  = np.zeros_like(self.img)
        self.new_img = np.zeros_like(self.img)
        draw_grid(self.img)
        self.guide = []

# Key codes
UP_KEY = 2490368
DOWN_KEY = 2621440
LEFT_KEY = 2424832
RIGHT_KEY =  2555904


def main():    

    cv2.namedWindow('Canvas', 0)
    cv2.resizeWindow('Canvas', WINDOW_WIDTH, WINDOW_HEIGHT)

    model = Model()
    model.path = []

    model.path = [[[Vector(240, 179), Vector(360, 379)], 65], [[Vector(360, 379), Vector(560, 379)], 125], [[Vector(560, 379), Vector(640, 299)], 35], [[Vector(640, 299), Vector(620, 199)], 35], [[Vector(620, 199), Vector(240, 179)], 15]]
    
    # model.path = [[[Vector(140, 179), Vector(60, 219), Vector(180, 279)], 30],
    #               [[Vector(180, 279), Vector(340, 239)], 10],
    #               [[Vector(340, 239), Vector(260, 479)], 40],
    #               [[Vector(260, 479), Vector(400, 359)], 20],
    #               [[Vector(400, 359), Vector(540, 339), Vector(560, 459)], 30],
    #               [[Vector(560, 459), Vector(680, 439), Vector(700, 279)], 10],
    #               [[Vector(700, 279), Vector(640, 99)], 5],
    #               [[Vector(640, 99), Vector(560, 159)], 10],
    #               [[Vector(560, 159), Vector(580, 219)], 10],
    #               [[Vector(580, 219), Vector(460, 259)], 10],
    #               [[Vector(460, 259), Vector(380, 99)], 10],
    #               [[Vector(380, 99), Vector(220, 39)], 10],
    #               [[Vector(220, 39), Vector(140, 179)], 10]]
    
    view = View(WINDOW_WIDTH, WINDOW_HEIGHT)

    #            line           arc
    # path = [ [(p0, p1), d], [(p0, p1, p2), d], ... ]
    
    cv2.setMouseCallback('Canvas', lambda event, x, y, flags, param: on_mouse(event, x, y, model, view))

    on_mouse("redraw", 0, 0, model, view)

    k = 0
    while True:
        
        # Break if Esc or 'q' is pressed


        if k == 27 or k == ord('q'):
            break
        elif k == ord('l'): # Line
            view.mode = LINE
        elif k == ord('a'): # Arc
            view.mode = ARC
        elif k == ord('d'): # Delete
            view.clear()
            model.path = []
            model.joined_offsets = []
            on_mouse("redraw", 0, 0, model, view)
        elif k == ord('p'):  # plus
            model.gap += 5
            on_mouse(cv2.EVENT_MOUSEMOVE, view.old_x, view.old_y, model, view)
        elif k == ord('m'):  # minus
            if model.gap > 5:
                model.gap -= 5
            on_mouse(cv2.EVENT_MOUSEMOVE, view.old_x, view.old_y, model, view)
        elif k == UP_KEY:
            model.space += 1
            on_mouse("redraw", 0, 0, model, view)
            # time.sleep(0.1)
        elif k == DOWN_KEY:
            if model.space > 0:
                model.space -= 1
            on_mouse("redraw", 0, 0, model, view)
        elif k == LEFT_KEY:
            model.angle += 2*math.pi/100
            on_mouse("redraw", 0, 0, model, view)
        elif k == RIGHT_KEY:
            model.angle -= 2*math.pi/100
            on_mouse("redraw", 0, 0, model, view)

        # Call waitKey again to redraw canvas
        k = cv2.waitKeyEx(20)

    cv2.destroyAllWindows()

if True:# __name__ == '__main__':
    main()


