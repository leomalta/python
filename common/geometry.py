from enum import Enum, auto
from math import atan2, hypot, pi, sin, cos
from random import choice, randint
from typing import NamedTuple


class Direction(Enum):
    EAST = auto()
    SOUTHEAST = auto()
    SOUTH = auto()
    SOUTHWEST = auto()
    WEST = auto()
    NORTHWEST = auto()
    NORTH = auto()
    NORTHEAST = auto()

    def rand(): return choice(list(Direction))

    def arcrange():
        return (2 * pi) / len(Direction)

    def from_radians(angle):
        return next(d for d in Direction if d.contains(angle, Direction.arcrange()))

    def to_radians(self):
        return (self.value - 1) * Direction.arcrange()

    def point(self):
        return Point(1, 0).rotate(self.to_radians())

    def opposite(self):
        return Direction(1 + (self.value - 1 + (len(Direction) // 2)) % len(Direction))

    def contains(self, angle, range):
        min_angle = (self.to_radians() - (range/2)) % (2*pi)
        max_angle = min_angle + range
        angle = angle  % (2*pi)
        return min_angle <= angle + (2*pi)*(angle < min_angle) <= max_angle


class Point(NamedTuple):
    x: float = 0
    y: float = 0

    def rand(xlimit, ylimit): return Point(randint(0,xlimit), randint(0,ylimit))

    def __neg__(self): return Point(-self.x, -self.y)
    def __add__(self, other): return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Point(self.x - other.x, self.y - other.y)

    def shift(self, scalar): return Point(self.x + scalar, self.y + scalar)
    def scale(self, scalar): return Point(self.x * scalar, self.y * scalar)
    def transpose(self): return Point(self.y, self.x)

    def distance(self, other=None):
        return hypot(*(self - (other if other else Point())))

    def angle(self, other=None):
        return atan2(*((other if other else Point()) - self).transpose())

    def rotate(self, angle):
        return Point(cos(angle) * self.x - sin(angle) * self.y,
                     sin(angle) * self.x + cos(angle) * self.y)

    def direction(self, other):
        return Direction.from_radians(self.angle(other))


class Circle(NamedTuple):
    center: Point = Point(0, 0)
    radius: int = 0

    def rand(xlimit, ylimit, radius):
        return Circle(Point.rand(xlimit, ylimit), radius)

    def intersect(self, other):
        return self.center.distance(other.center) < self.radius + other.radius - 0.01

    def outterbox(self):
        return Rectangle(self.center.shift(-self.radius), self.center.shift(self.radius))

    def move(self, direction=Direction.rand(), distance=None):
        distance = distance if distance else 2 * self.radius
        return Circle(direction.point().scale(distance) + self.center, self.radius)

    def displace(self, point):
        return Circle(self.center + point, self.radius)


class Rectangle(NamedTuple):
    topleft: Point = Point(0, 0)
    bottomright: Point = Point(0, 0)

    def width(self): return abs(self.topleft.x - self.bottomright.x)
    def height(self): return abs(self.topleft.y - self.bottomright.y)

    def isinside(self, other):
        return  other.topleft.x <= self.topleft.x <= other.bottomright.x and \
                other.topleft.x <= self.bottomright.x <= other.bottomright.x and \
                other.topleft.y <= self.topleft.y <= other.bottomright.y and \
                other.topleft.y <= self.bottomright.y <= other.bottomright.y

    def capture(self, point):
        return Point(min(max(self.topleft.x, point.x), self.bottomright.x),
                    min(max(self.topleft.y, point.y), self.bottomright.y))

