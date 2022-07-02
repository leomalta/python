from enum import Enum
from math import degrees
from tkinter import PIESLICE, Label
from common.geometry import Circle
from snakes.composites import SnakeState


class SnakeColor(Enum):
    HEAD = 'green'
    BODY = 'cyan'
    DEAD = 'black'
    DEAD_HEAD = 'green'
    REWARD = 'magenta'
    VISION = 'blue'
    TARGET = 'cyan'
    DESTINATION = 'black'
    STARVE = 'blue'
    PLAYER = 'red'
    CHASE = 'purple'


class Drawer:
    def __init__(self, canvas, tag="all"):
        self.canvas = canvas
        self.tag = tag

    def refresh(self): self.canvas.delete(self.tag)

    def circle(self, shape, color, tag):
        self.canvas.create_oval(shape.center.x - shape.radius, shape.center.y - shape.radius,
                                shape.center.x + shape.radius, shape.center.y + shape.radius,
                                fill=color.value, tags=[tag, self.tag])

    def arc(self, center, range, start, extent, color, tag):
        self.canvas.create_arc(center.x - range, center.y - range,
                               center.x + range, center.y + range,
                               start=degrees(start), extent=degrees(extent),
                               outline=color.value, tags=[tag, self.tag],
                               dash=(7, 1, 1, 1), style=PIESLICE)

    def line(self, point1, point2, color, tag):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y,
                                fill=color.value, tags=[tag, self.tag])


class SnakeDrawer(Drawer):
    def __init__(self, canvas, info_panel):
        super().__init__(canvas, type(self).__name__)
        self.info = info_panel
        self.snake_info_container = dict()

    def refresh(self):
        for label in list(self.snake_info_container.values()):
            label.destroy()
        super().refresh()

    def erase(self, snakes):
        for snake in snakes:
            snake_tag = type(snake).__name__ + str(snake.id)
            self.canvas.delete(snake_tag)
            self.snake_info_container[snake].destroy()

    def draw(self, snakes=[], behaviors=[], has_player=False):
        if has_player:
            self.__draw_snake__(snakes[0], SnakeColor.PLAYER)
            self.__draw_info__(snakes[0])
        for snake in snakes[has_player:]:
            self.__draw_snake__(snake, SnakeColor.BODY)
            self.__draw_info__(snake)
        for behavior in (b for b in behaviors if b.snake.state != SnakeState.DEAD):
            self.__draw_vision__(behavior.snake)
            self.__draw_target__(behavior.snake, behavior.movement.destination)
        self.canvas.update()

    def tag(snake):
        return type(snake).__name__ + str(snake.id)

    def __draw_snake__(self, snake, color):
        snake_tag = SnakeDrawer.tag(snake)
        self.canvas.delete(snake_tag)
        if len(snake.parts) == 0: return
        head_color = SnakeColor.HEAD if snake.state != SnakeState.DEAD else SnakeColor.DEAD_HEAD
        self.circle(snake.head(), head_color, snake_tag)
        if snake.state == SnakeState.STARVING:
            color = SnakeColor.STARVE
        elif snake.state == SnakeState.CHASING:
            color = SnakeColor.CHASE
        elif snake.state == SnakeState.DEAD:
            color = SnakeColor.DEAD
        for part in snake.body():
            self.circle(part, color, snake_tag)

    def __draw_info__(self, snake):
        snake_info_str = str(snake)
        if snake not in self.snake_info_container:
            self.snake_info_container[snake] = Label(self.info, text=snake_info_str)
            self.snake_info_container[snake].pack(expand=False)
        self.snake_info_container[snake]['text'] = snake_info_str
        if snake.state == SnakeState.DEAD:
            self.snake_info_container[snake]['bg'] = 'red'
        elif snake.state == SnakeState.CHASING:
            self.snake_info_container[snake]['bg'] = 'cyan'

    def __draw_vision__(self, snake):
        self.arc(snake.head().center, snake.vision_range,
                 -(snake.direction.to_radians() + (snake.vision_arc / 2)),
                 snake.vision_arc, SnakeColor.VISION, tag=SnakeDrawer.tag(snake))

    def __draw_target__(self, snake, destination):
        snake_tag = SnakeDrawer.tag(snake)
        self.circle(Circle(center=destination, radius=1),
                    color=SnakeColor.DESTINATION, tag=snake_tag)
        self.line(destination, snake.head().center,
                  color=SnakeColor.DESTINATION, tag=snake_tag)


class RewardsDrawer(Drawer):
    def __init__(self, canvas):
        super().__init__(canvas, type(self).__name__)

    def draw(self, rewards):
        self.refresh()
        for rwd in rewards:
            self.circle(rwd, SnakeColor.REWARD, tag="rwd")
        self.canvas.update()

