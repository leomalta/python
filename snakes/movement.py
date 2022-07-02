from itertools import cycle
from common.geometry import Direction, Point
from snakes.composites import Snake, SnakeState
from snakes.config import CONFIG


class Movement:
    def __init__(self, snake, area, destination=None, speed=1):
        self.snake = snake
        self.area = area
        self.destination = destination if destination else snake.head().center
        self.speed = speed

    def move(self, obstacles, rewards):
        direction = self.__choose_direction__(obstacles, rewards)
        if direction is None:
            return False
        self.snake.move(direction)
        return True

    def __check_direction__(self, direction, obstacles):
        newhead = self.snake.head().move(direction)
        return newhead.outterbox().isinside(self.area) and \
            next((obs for obs in obstacles if obs.intersect(newhead)), None) is None 


class RandomMovement(Movement):
    DIRECTIONS = cycle(list(Direction))

    def __choose_direction__(self, obstacles, rewards):
        for _ in range(len(Direction)):
            dir = next(RandomMovement.DIRECTIONS)
            if self.__check_direction__(dir, obstacles):
                return dir


class ChaseRewardMovement(RandomMovement):
    def __choose_direction__(self, obstacles, rewards):
        def direct(rwd): return self.snake.direction_to(rwd.center)
        eligible_destination = min([(rwd.center, direct(rwd)) for rwd in self.snake.visible_shapes(rewards)
                                    if self.__check_direction__(direct(rwd), obstacles)],
                                   key=lambda x: self.snake.distance_to(x[0]),
                                   default=self.__fake_target__(obstacles, rewards))
        self.destination = eligible_destination[0]
        return eligible_destination[1]

    def __fake_target__(self, obstacles, rewards):
        destination = self.destination
        direction = self.snake.direction_to(destination)
        if not self.__check_direction__(direction, obstacles) or \
            (self.snake.distance_to(destination) < self.snake.vision_range and \
            destination not in rewards):
            direction = super().__choose_direction__(obstacles, rewards)
            if direction is not None:
                displacement = self.snake.vision_range * CONFIG['random distance factor']
                diff = direction.point().scale(displacement) if direction else Point()
                destination = self.area.capture(self.snake.head().center + diff)
        return destination, direction


class ChaseSnakeMovement(ChaseRewardMovement):
    def __choose_direction__(self, obstacles, rewards):
        modified_obstacles = rewards.copy()
        modified_rewards = []
        for obs in obstacles:
            if(isinstance(obs, Snake) and obs != self.snake and obs.state != SnakeState.DEAD):
                modified_rewards += [obs.tail()]
                modified_obstacles += obs.parts[:-1]
            else:
                modified_obstacles += [obs]
        return super().__choose_direction__(modified_obstacles, modified_rewards)
