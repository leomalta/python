from enum import Enum, auto
from math import degrees, radians
from common.geometry import Circle, Direction
from snakes.config import CONFIG

class SnakeState(Enum):
    DEAD = auto(),
    ALIVE = auto(),
    STARVING = auto(),
    CHASING = auto(),
    MERGED = auto()   


class Snake:
    __instances__ = 0

    def rand(area, size, radius):
        return Snake(size, Circle.rand(area.width(), area.height(), radius), Direction.rand())

    def __init__(self, size=0, shape=None, direction=Direction.rand()):
        Snake.__instances__ += 1
        self.id = Snake.__instances__
        self.state = SnakeState.ALIVE
        self.direction = direction
        self.vision_range = CONFIG['snake']['vision range']
        self.vision_arc = radians(CONFIG['snake']['vision arc'])
        self.parts = []
        self.appendix = None
        if size and shape:
            self.parts += [shape]
            for _ in range(1, size):
                self.parts += [self.parts[-1].move(direction.opposite())]

    def __str__(self): 
        return type(self).__name__ \
            + "_"  + "{:04d}".format(self.id) \
            + ": " + "{:4d}".format(self.size()) \
            + "| " + "{:3d}".format(int(self.vision_range)) \
            + "| " + "{:3d}".format(int(degrees(self.vision_arc)))

    def size(self): return len(self.parts)
    def head(self): return self.parts[0]
    def tail(self): return self.parts[-1]
    def body(self): return self.parts[1:]

    def distance_to(self, point):
        return self.head().center.distance(point)

    def direction_to(self, point):
        return self.head().center.direction(point)

    def move(self, direction=None):
        if direction: self.direction = direction
        self.appendix = self.tail()
        self.parts = [self.head().move(self.direction)] + self.parts[:-1]
    
    def grow(self):
        if self.appendix: self.parts += [self.appendix]
        self.appendix = None

    def intersect(self, shape):
        return next((part for part in self.parts if shape.intersect(part)), None) is not None

    def visible_shapes(self, shapes):
        return [shape for shape in shapes 
                if self.distance_to(shape.center) < self.vision_range and \
                    self.direction.contains(self.head().center.angle(shape.center), self.vision_arc)]

    def bite(self, snake): 
        return self.head().intersect(snake.tail())


def create_snake(area, 
                size=CONFIG['snake']['default size'], 
                radius=CONFIG['snake']['default radius'], 
                obstacles=None):
    while True:
        new_snake = Snake.rand(area, size, radius)
        if next((obs for obs in obstacles if new_snake.intersect(obs)), None):
            continue
        return new_snake


def create_reward(area, radius=CONFIG['snake']['default radius'], obstacles=None):
    while True:
        result = Circle.rand(area.width(), area.height(), radius)
        if not result.outterbox().isinside(area) or \
            next((obs for obs in obstacles if obs.intersect(result)), None):
            continue
        return result