from math import log
from random import gauss, random
from snakes.composites import Snake, SnakeState
from snakes.config import CONFIG
from snakes.movement import ChaseRewardMovement, ChaseSnakeMovement


def make_threshold(min_value, factor, value): 
    return (1 - log(max(2, min_value*factor)) / log(max(2, value)))


class Behavior:
    def __init__(self, snake, movement):
        self.snake = snake
        self.movement = movement

    def act(self, behaviors, obstacles, rewards):
        if not self.pre_movement() or \
                not self.movement.move(obstacles, rewards) or \
                not self.post_movement(behaviors, obstacles, rewards):
            self.snake.state = SnakeState.DEAD
        return self.result()


class StarveBehavior(Behavior):
    def __init__(self, snake, area):
        super().__init__(snake, ChaseRewardMovement(snake, area))
        self.starvecounter = 0

    def pre_movement(self):
        self.starvecounter += 1
        size = CONFIG['snake']['default size']
        limit = self.snake.vision_range * size / self.snake.size()
        if self.snake.state == SnakeState.ALIVE and limit < self.starvecounter:
            self.snake.state = SnakeState.STARVING
        return self.starvecounter < limit * size

    def post_movement(self, behaviors, obstacles, rewards):
        hit_rwd = next((rwd for rwd in rewards if self.snake.head().intersect(rwd)), None)
        if hit_rwd is None:
            return True
        rewards.remove(hit_rwd)
        self.snake.grow()
        self.snake.state = SnakeState.ALIVE
        self.starvecounter = 0
        return True

    def merge(self, snake):
        self.starvecounter = 0
        diff = self.snake.tail().center - snake.head().center
        self.snake.parts += [part.displace(diff) for part in snake.parts[1:]]
        self.snake.vision_arc = gauss(mu=(self.snake.vision_arc + snake.vision_arc)*0.5,
                                      sigma=(self.snake.vision_arc + snake.vision_arc)*0.05)
        self.snake.vision_range = gauss(mu=(self.snake.vision_range + snake.vision_range)*0.5,
                                        sigma=(self.snake.vision_range + snake.vision_range)*0.05)
        self.snake.state = SnakeState.MERGED
        self.movement = ChaseRewardMovement(self.snake,
                                            self.movement.area,
                                            self.movement.destination,
                                            self.movement.speed)


class SnakeBehavior(StarveBehavior):
    def pre_movement(self):
        if self.snake.state == SnakeState.ALIVE and \
                random() < make_threshold(CONFIG['snake']['default size'],
                                          CONFIG['chasing factor'],
                                          self.snake.size()):
            self.snake.state = SnakeState.CHASING
            self.starvecounter = 0
            self.movement = ChaseSnakeMovement(self.snake,
                                               self.movement.area,
                                               self.movement.destination,
                                               2 * self.movement.speed)
        return super().pre_movement()

    def post_movement(self, behaviors, obstacles, rewards):
        if self.snake.state != SnakeState.CHASING:
            return super().post_movement(behaviors, obstacles, rewards)
        bit_behavior = next((be for be in behaviors 
                                if be.snake.state != SnakeState.DEAD and 
                                    self.snake.bite(be.snake)), None)
        if bit_behavior is None:
            return True
        bit_behavior.merge(self.snake)
        self.snake.parts.clear()
        return False

    def result(self):
        return self.explode() if self.snake.state == SnakeState.MERGED else []

    def explode(self):
        n_children = (self.snake.size()*10) // (CONFIG['snake']['default size']*10)
        splitsize, remainder = divmod(self.snake.size(), n_children)
        def divpos(i): return (i * splitsize) + min(i, remainder)
        children = [self.snake.parts[divpos(i):divpos(i+1)] for i in range(n_children)]
        if len(children[0]) < self.snake.size():
            self.snake.appendix = self.snake.parts[len(children[0])]
        self.snake.parts = children[0]
        self.snake.state = SnakeState.ALIVE
        return self.__make_children__(children[1:])

    def __make_children__(self, part_list):
        result = []
        for part in part_list:
            s = Snake()
            s.parts = part
            s.vision_arc = gauss(mu=self.snake.vision_arc,
                                 sigma=self.snake.vision_arc * 0.05)
            s.vision_range = gauss(mu=self.snake.vision_range,
                                   sigma=self.snake.vision_range * 0.05)
            result += [s]
        return result
