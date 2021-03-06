import math

MAX_ERROR = 1e-3 # mm

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    @staticmethod
    def max_error():
        return MAX_ERROR

    @staticmethod
    def from_polar(magnitude, angle):
        m = abs(magnitude)
        return Vector(m*math.cos(angle), m*math.sin(angle))

    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    def sum(self):
        return self.x+self.y

    def length2(self):
        return self.x*self.x + self.y*self.y


    
    def norm(self):
        return self/self.length()

    def angle(self):
        return math.atan2(self.y, self.x)

    def rotate(self, a):
        c = math.cos(a)
        s = math.sin(a)
        return Vector(c*self.x-s*self.y, s*self.x+c*self.y)

    def tangent(self):
        return Vector(-self.y, self.x)

    def normal(self):
        return self.norm().tangent()

    @staticmethod
    def dot(lhs, rhs):
        return lhs.x*rhs.x + lhs.y*rhs.y

    # Cross product
    @staticmethod
    def cross(lhs, rhs):
        return lhs.x*rhs.y-lhs.y*rhs.x

    # Calculates the angle from v0 to v1
    def angle_between(v0, v1):
        u0 = v0.norm()
        u1 = v1.norm()
        # Calculate the direction of the angle
        delta = 1.0 if Vector.cross(u0, u1) > 0.0 else -1.0
        u0_dot_u1 = Vector.dot(u0, u1)
        # Due to roundoff error result could be 1.000002
        # so need to bring it back to 1.0 for it to be in range
        # of acos()
        if u0_dot_u1 > 1.0: 
            u0_dot_u1 = 1.0
        angle = math.acos(u0_dot_u1)*delta
        return angle
    
    def copy(self):
        return Vector(self.x, self.y)

    def __add__(self, rhs):
        if type(rhs) is Vector:
            return Vector(self.x+rhs.x, self.y+rhs.y)
        else:
            return Vector(self.x+rhs, self.y+rhs)

    def __radd__(self, lhs):
        return self+lhs

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __sub__(self, rhs):
        return self + (-rhs)
    
    def __truediv__(self, rhs):
        return Vector(self.x/rhs, self.y/rhs)

    def __mul__(self, rhs):
        if type(rhs) is Vector:
            return Vector(self.x*rhs.x, self.y*rhs.y)
        else:
            return Vector(self.x*rhs, self.y*rhs)

    def __rmul__(self, lhs):
        return self*lhs

    def __eq__(self, rhs):
        return (self-rhs).length() < MAX_LEN_ERROR

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
