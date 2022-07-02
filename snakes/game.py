import tkinter as tk
from common.geometry import Point, Rectangle
from gui.simplegui import MainWindow
from snakes.behavior import SnakeBehavior
from snakes.composites import SnakeState, create_reward, create_snake
from snakes.config import CONFIG
from snakes.drawer import RewardsDrawer, SnakeDrawer

HAS_PLAYER = False
DEBUG = True


def stagearea(canvas): 
    p = Point(canvas.winfo_width(), canvas.winfo_height())
    return Rectangle(Point(), p)


class Simulation:
    TIMER = 1000 // CONFIG['fps']

    def __init__(self):
        self.active = False
        self.rewards = []
        self.behaviors = []
        self.snakes = []
        self.dead_snakes = set()

    def setup_UI(self, main_frame):
        info = tk.Frame(main_frame, width=400, relief="solid")
        info.pack(fill=tk.Y, expand=False, side=tk.LEFT)
        info_left = tk.Frame(info, width=200, relief="solid")
        info_left.pack(fill=tk.Y, expand=False, side=tk.LEFT)
        self.canvas = tk.Canvas(main_frame, borderwidth=1, relief="solid")
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(10, 10))
        self.snakedrawer = SnakeDrawer(self.canvas, info_left)
        self.rewardsdrawer = RewardsDrawer(self.canvas)
        # self.statsdrawer = StatsDrawer(info_left)

    def start_snake(self, snake=None):
        area = stagearea(self.canvas)
        self.snakes += [snake if snake else create_snake(area, obstacles=self.snakes)]
        self.behaviors += [SnakeBehavior(self.snakes[-1], area)]
        self.process_behavior(self.behaviors[-1])

    def process_behavior(self, behavior):
        if not self.active:
            return
        for child in behavior.act(self.behaviors, self.snakes, self.rewards):
            self.start_snake(child)
        if behavior.snake.state != SnakeState.DEAD:
            delay = int(Simulation.TIMER//behavior.movement.speed)
            self.canvas.after(delay, self.process_behavior, behavior)

    def process_static(self):
        if not self.active:
            return
        n_rewards = int(CONFIG['initial snakes'] * CONFIG['reward per snake'])
        for _ in range(len(self.rewards), n_rewards):
            self.rewards += [create_reward(stagearea(self.canvas),
                                           obstacles=self.rewards + self.snakes)]
        self.process_dead()
        self.snakedrawer.draw(snakes=self.snakes, 
                              behaviors=self.behaviors if CONFIG['debug'] else [], 
                              has_player=CONFIG['player'])
        self.rewardsdrawer.draw(rewards=self.rewards)
        self.active = len(self.behaviors) != 0
        self.canvas.after(Simulation.TIMER, self.process_static)

    def process_dead(self):
        new_dead = {snake for snake in self.snakes if snake.state == SnakeState.DEAD and snake not in self.dead_snakes}
        self.dead_snakes |= new_dead
        self.behaviors = [behavior for behavior in self.behaviors if behavior.snake not in new_dead]
        if len(new_dead):
            self.canvas.after(CONFIG['removal delay']*1000, self.remove_dead, new_dead)

    def remove_dead(self, purged_snakes):
        if not self.active:
            return
        self.snakedrawer.erase(purged_snakes)
        self.snakes = [snake for snake in self.snakes if snake not in purged_snakes]
        self.dead_snakes -= purged_snakes

    def run(self):
        self.active = True
        self.reset()
        for _ in range(CONFIG['initial snakes']):
            self.start_snake()
        self.process_static()

    def stop(self):
        self.active = False

    def reset(self):
        self._player_snake = None
        self.rewards.clear()
        self.behaviors.clear()
        self.snakes.clear()
        self.dead_snakes.clear()
        self.snakedrawer.refresh()
        self.rewardsdrawer.refresh()
        # self.statsdrawer.refresh()

if __name__ == '__main__':
    MainWindow(Simulation()).run()