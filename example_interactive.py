import math
import numpy as np
import cv2
from vector import Vector
from line_arc import *
from offset import *
from fill import line_fill, arc_fill
import time


LINE = 0
ARC = 1

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1200

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 127, 0)
YELLOW = (0, 255, 255)

def draw_arrow_head(img, p, v, size=10, color=WHITE):
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
def draw_grid(img, x=0, y=0):

    font_scale = 0.6

    # Grid
    img[::GRID_SIZE,::GRID_SIZE,:] = GRAY

    # Help text
    y = 10
    dy = 25
    text = [
        '* PATH/OFFSET *',
        '  (a)rc',
        '  (l)ine',
        '  (p)lus offset',
        '  (m)inus offset',
        ' ',
        '* FILL *',
        '  (A)rc',
        '  (L)ine',
        '  (+/-) gap size',
        '  (Arrow Keys) position',
        ' ',
        '* MAIN *',
        '  (d)elete',
        '  (q)uit',
    ]
    for line in text:
        y += dy
        cv2.putText(img, text=line, org=(0, y),fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale, color=YELLOW, lineType=cv2.LINE_AA)
    draw_mouse_position(img, x, y)

def draw_mouse_position(img, x, y):
    # Mouse position
    font_scale = 0.6
    cv2.rectangle(img, pt1=(0, WINDOW_HEIGHT-50), pt2=(140, WINDOW_HEIGHT), color=BLACK, thickness=cv2.FILLED)
    cv2.putText(img, text=f'({x:4d}, {y:4d})', org=(0, WINDOW_HEIGHT-20),fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=font_scale, color=YELLOW, lineType=cv2.LINE_AA)

# Update key points on click
def on_mouse(event, x, y, model, view):

    x = round(x/GRID_SIZE)*GRID_SIZE
    y = round(y/GRID_SIZE)*GRID_SIZE-1

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
                if is_coincident(view.guide[:2], [view.guide[1], xy]):
                    guide = [view.guide[0], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_line(view.new_img, guide[0], guide[1], GRAY, arrow=True)
                    draw_line(view.new_img, offset[0], offset[1], DARK_GREEN, arrow=True)

                else:
                    guide = [view.guide[0], view.guide[1], xy]
                    offset = offset_segment(guide, model.gap)
                    draw_arc(view.new_img, guide[0], guide[1], guide[2], GRAY, arrow=True)
                    draw_arc(view.new_img, offset[0], offset[1], offset[2], DARK_GREEN, arrow=True)

        draw_mouse_position(view.new_img, x, y)

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
                if is_coincident(view.guide[:2], [view.guide[1], xy]):
                    model.path.append([[view.guide[0], xy], model.gap])
                else:
                    model.path.append([[view.guide[0], view.guide[1], xy], model.gap])
                view.guide[0] = xy
                del(view.guide[1])



    if event == "redraw" or event == cv2.EVENT_LBUTTONDOWN:

        view.img[:, :, :] = 0
        # draw grid
        draw_grid(view.img, x, y)
        
        model.joined_offsets = offset_path(model.path)


        draw_path(view.img, model.path, WHITE)
        draw_segments(view.img, model.joined_offsets, GREEN)

        # bbox = path_bbox(model.joined_offsets)
        # if bbox:
            # draw_rect(view.img, bbox[0], bbox[1])


        if view.fill == LINE:
            vec = Vector.from_polar(1, model.angle)
            fill_lines = line_fill(model.joined_offsets, vec, model.fill_space)
            for line in fill_lines:
                draw_line(view.img, line[0], line[1], YELLOW, arrow=True)
        else:
            guide_arc = [Vector(0, 1) + model.center,
                         Vector(1, 0) + model.center,
                         Vector(0, -1) + model.center]

            fill_arcs = arc_fill(model.joined_offsets, guide_arc, model.fill_space)
            for arc in fill_arcs:
                draw_arc(view.img, arc[0], arc[1], arc[2], color=YELLOW, arrow=True)


        # Print path to avoid having to draw one every time.
        # print(model.path)


        cv2.imshow('Canvas', view.img)



class Model():
    def __init__(self, path=[], guide=[]):
        self.path = path
        self.joined_offsets = []
        self.angle = 0 #math.pi/4
        self.fill_space = 5
        self.gap = 20 # Offset gap
        self.center = Vector(600, 400)
    

class View():
    def __init__(self, width, height, mode=LINE, fill=LINE, guide=[]):
        self.img  = np.zeros((height, width, 3), dtype=np.uint8)
        self.new_img = np.zeros_like(self.img)
        draw_grid(self.img)
        self.mode = mode
        self.fill = fill
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

    # model.path = [[[Vector(480, 280), Vector(480, 460)], 20], [[Vector(480, 460), Vector(720, 460)], 20], [[Vector(720, 460), Vector(720, 320)], 20], [[Vector(720, 320), Vector(860, 320)], 20], [[Vector(860, 320), Vector(860, 480)], 20], [[Vector(860, 480), Vector(1040, 480)], 20], [[Vector(1040, 480), Vector(1040, 320)], 20], [[Vector(1040, 320), Vector(1040, 200)], 20], [[Vector(1040, 200), Vector(700, 200)], 20], [[Vector(700, 200), Vector(480, 200)], 20], [[Vector(480, 200), Vector(480, 280)], 20]]


    
    

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
        elif k == ord('L'): # Line Fill
            view.fill = LINE
            on_mouse("redraw", 0, 0, model, view)
        elif k == ord('A'): # Arc Fill
            view.fill = ARC
            on_mouse("redraw", 0, 0, model, view)
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
        elif k == ord('+'):
            model.fill_space += 1
            on_mouse("redraw", 0, 0, model, view)
        elif k == ord('-'):
            if model.fill_space > 1:
                model.fill_space -= 1
            on_mouse("redraw", 0, 0, model, view)
        elif k == UP_KEY:
            model.center.y += 10
            on_mouse("redraw", 0, 0, model, view)
        elif k == DOWN_KEY:
            if model.fill_space > 0:
                model.center.y -= 10
            on_mouse("redraw", 0, 0, model, view)
        elif k == LEFT_KEY:
            model.angle += 2*math.pi/100
            model.center.x -= 10
            on_mouse("redraw", 0, 0, model, view)
        elif k == RIGHT_KEY:
            model.angle -= 2*math.pi/100
            model.center.x += 10
            on_mouse("redraw", 0, 0, model, view)

        # Call waitKey again to redraw canvas
        k = cv2.waitKeyEx(20)

    cv2.destroyAllWindows()

if True:# __name__ == '__main__':
    main()


