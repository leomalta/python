import threading
from ctypes import pythonapi, py_object
from common.config import readjson
from gui.simplegui import MainWindow
from life.life import LIFE, partition, advance
from life.rleparser import from_rle, to_rle
from life.simulation import bestfit, simulate
from random import randrange
from tkinter import BOTH, Canvas, Entry, StringVar


CONFIG = readjson(__file__)


def draw(canvas, connected, tag):
    canvas.delete(tag)
    for part in connected:
        color = "#"+("%06x" % randrange(0, 16777215))
        for point in part:
            canvas.create_rectangle(CONFIG['hshift'] + (point.x * CONFIG['size']),
                                    CONFIG['vshift'] + (point.y * CONFIG['size']),
                                    CONFIG['hshift'] + ((point.x + 1) * CONFIG['size']),
                                    CONFIG['vshift'] + ((point.y + 1) * CONFIG['size']),
                                    fill=color, width=1, tag=tag)
    canvas.update()


class Game:
    TIMER = 1000//CONFIG['fps']

    def __init__(self):
        self.reset()

    def setup_UI(self, main_frame):
        self.canvas = Canvas(main_frame, borderwidth=1, relief="solid")
        self.canvas.pack(fill=BOTH, expand=True, padx=(10, 10))
        self.config = StringVar()
        Entry(main_frame, textvariable=self.config, takefocus=True).pack()

    def reset(self):
        self.active = False
        self.cells = set()
        self.rule = LIFE
        self.population = dict()

    def stop(self):
        self.active = False
        self.stopsimulation()

    def run(self):
        self.reset()
        self.active = True
        if CONFIG['simulate']:
            self.simulation = threading.Thread(target=self.runsimulation, daemon=True)
            self.simulation.start()
        draw(self.canvas, [], type(self).__name__)
        self.cells, self.rule = from_rle(self.config.get())
        self.iterate()

    def runsimulation(self):
        while True:
            self.population = simulate(self.population)

    def stopsimulation(self):
        thread_id = self.simulation._thread_id if hasattr(self.simulation, '_thread_id') else \
            next(id for id, thread in threading._active.items()
                 if thread is self.simulation)
        pythonapi.PyThreadState_SetAsyncExc(thread_id, py_object(SystemExit))
        self.simulation.join()

    def iterate(self):
        if not self.active:
            return
        draw(self.canvas, partition(self.cells, 2), type(self).__name__)
        newcells = advance(self.cells, self.rule)
        if newcells == self.cells:
            _, (self.cells, self.rule) = bestfit(self.population)
            self.config.set(to_rle(self.cells, self.rule))
        else:
            self.cells = newcells
        self.canvas.after(Game.TIMER, self.iterate)


if __name__ == '__main__':
    MainWindow(Game()).run()
