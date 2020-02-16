import math

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

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

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
