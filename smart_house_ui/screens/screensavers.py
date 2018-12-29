from .game_of_life import compute_next_step
from random import random
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from datetime import datetime
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class ScreensaverDrawingArea(FloatLayout):
    LOOP_DELAY = 1

    def restart(self):
        self._init()
        self._update()
        Clock.schedule_interval(self._update, self.LOOP_DELAY)

    def stop(self):
        Clock.unschedule(self._update)


class GameOfLifeArea(ScreensaverDrawingArea):
    FIRST_GENERATION_DENSITY = 0.3
    RESTART_EVERY = 180  # seconds
    LOOP_DELAY = 0.4

    CELL_SIZE = 16  # px

    def _init(self, *args):
        self._tempr_label = None

        self._cells_count_x = int(self.width / float(self.CELL_SIZE))
        self._cells_count_y = int(self.height / float(self.CELL_SIZE))
        self._cells = {}

        self.canvas.before.clear()

        with self.canvas.before:
            for x in range(self._cells_count_x):
                for y in range(self._cells_count_y):
                    alpha = 1 if random() < self.FIRST_GENERATION_DENSITY else 0
                    self._cells[(x, y)] = Color(rgba=[0.3, 0.3, 0.3, alpha])
                    Rectangle(
                        size=[self.CELL_SIZE, self.CELL_SIZE],
                        pos=[x * self.CELL_SIZE, y * self.CELL_SIZE],
                    )

    def restart(self):
        super(GameOfLifeArea, self).restart()
        Clock.schedule_interval(self._init, self.RESTART_EVERY)

    def stop(self):
        Clock.unschedule(self._init)
        super(GameOfLifeArea, self).stop()

    def _update(self, *args):
        compute_next_step(self._cells_count_x, self._cells_count_y, self._cells)

        # Updating sensors
        if not self._tempr_label:
            panels = App.get_running_app().main_screen.ids["panels"]
            self._tempr_label = panels.ids["weather"].ids["temp_out"]

        temp = self._tempr_label.text
        if temp and temp.isdigit():
            temp = "Temperature: %s [sup]o[/sup]C" % temp
        else:
            temp = "Temperature Unknown =("

        self.ids["temperature_label"].text = temp

        self.ids["time_label"].text = datetime.now().strftime("%H:%M")
