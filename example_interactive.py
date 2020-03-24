
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

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1200

WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 127, 0)
YELLOW = (0, 255, 255)

def draw_arrow_head(img, p, v, size=5, color=WHITE):
    u = v.norm()
    a = size*u.rotate(0.9*math.pi) + p
    b = size*u.rotate(-0.9*math.pi) + p

    y_offset = img.shape[0]-1
    pts = np.array([(round(p.x), round(y_offset-p.y)), (round(a.x), round(y_offset-a.y)), (round(b.x), round(y_offset-b.y))])
    cv2.fillPoly(img, [pts], color=color, lineType=cv2.LINE_AA) 
    

def draw_line(img, p0, p1, color=WHITE, arrow=False):
    y_offset = img.shape[0]-1
    cv2.line(img, (round(p0.x), round(y_offset-p0.y)), (round(p1.x), round(y_offset-p1.y)), color=color, lineType=cv2.LINE_AA)
    if arrow:
        draw_arrow_head(img, p1, p1-p0, color=color)

def draw_rect(img, p0, p1, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.rectangle(img, (round(p0.x), round(y_offset-p0.y)) , (round(p1.x), round(y_offset-p1.y)), color=color)


# This draws arcs more accurately than the opencv ellipse function
def draw_arc(img, p0, p1, p2, color=WHITE, step=0.01, arrow=False):
    c, r, a0, a2 = arc_from_points([p0, p1, p2])
    t = 0
    while t < 1:
        pt0 = c + r*Vector(math.cos(a0+t*(a2-a0)), math.sin(a0+t*(a2-a0)))
        t += step
        pt1 = c + r*Vector(math.cos(a0+t*(a2-a0)), math.sin(a0+t*(a2-a0)))
        draw_line(img, pt0, pt1, color)
    if arrow:
        draw_arrow_head(img, pt1, pt1-pt0, color=color)

    # draw_circle(img, p0, 4, color=color)
    draw_circle(img, p1, 4, color=color)
    # draw_circle(img, p2, 4, color=color)

def draw_circle(img, c, r, color=WHITE):
    y_offset = img.shape[0]-1
    cv2.circle(img, (round(c.x), round(y_offset-c.y)), r, color, lineType=cv2.LINE_AA)
    
def draw_segments(img, segments, color=WHITE):
    for seg in segments:
        if is_line(seg):
            draw_line(img, *seg, color, arrow=True)
        elif is_arc(seg):
            draw_arc(img, *seg, color, 0.001, arrow=True)


def draw_path(img, path, color=WHITE):
    for seg, _ in path:
        if is_line(seg):
            draw_line(img, *seg, color, arrow=True)
        elif is_arc(seg):
            draw_arc(img, *seg, color, 0.001, arrow=True)
            
GRID_SIZE = 20
def draw_grid(img):
    y = 10
    dy = 30
   
    text = ['(A)rc', '(L)ine', '(P)lus Offset', '(M)inus Offset', '(D)elete', '(Q)uit']
    for line in text:
        y += dy
        cv2.putText(img, text=line, org=(0, y),fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5, color=YELLOW, lineType=cv2.LINE_AA)
    
    img[::GRID_SIZE,::GRID_SIZE,:] = GRAY

            
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
                    draw_line(view.new_img, guide[0], guide[1], GRAY, arrow=True)
                    draw_line(view.new_img, offset[0], offset[1], DARK_GREEN, arrow=True)
        else:
            if len(view.guide) == 1:
                if (view.guide[0].x != x) or (view.guide[0].y != y):
                    guide = [view.guide[0], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_line(view.new_img, guide[0], guide[1], GRAY, arrow=True)
                    draw_line(view.new_img, offset[0], offset[1], DARK_GREEN, arrow=True)
            elif len(view.guide) == 2:
                # if (view.guide[1].x != x) and (view.guide[1].y != y):
                if not Vector.is_collinear(view.guide[0], view.guide[1], xy):
                    guide = [view.guide[0], view.guide[1], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_arc(view.new_img, guide[0], guide[1], guide[2], GRAY, arrow=True)
                    draw_arc(view.new_img, offset[0], offset[1], offset[2], DARK_GREEN, arrow=True)



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
            draw_line(view.img, line[0], line[1], YELLOW, arrow=True)

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
        self.img  = np.zeros((height, width, 3), dtype=np.uint8)
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

    model.path = [[[Vector(300, 279), Vector(240, 499), Vector(420, 439)], 40], [[Vector(420, 439), Vector(520, 279), Vector(760, 279)], 40], [[Vector(760, 279), Vector(800, 399), Vector(780, 519)], 75], [[Vector(780, 519), Vector(900, 419), Vector(900, 319)], 100], [[Vector(900, 319), Vector(920, 139), Vector(940, 79)], 50]]

    
    
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


    # model.path = [[[Vector(140, 219), Vector(280, 339), Vector(340, 359)], 75], [[Vector(340, 359), Vector(420, 259), Vector(520, 119)], 45]]

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


