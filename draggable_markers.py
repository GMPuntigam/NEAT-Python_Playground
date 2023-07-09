# -*- coding: utf-8 -*-

import math

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from rust_in_python import Evaluator


def normalise_values(vals):
    x_min = min(vals)
    x_max = max(vals)
    return[(val-x_min)/(x_max-x_min) for val in vals]

def process_step(plot, enn):
    if len(plot._points) == 4:

    # with Evaluator() as enn:
    # x_vals = [20*random.random()-10 for i in range(3)]
        x_vals, f_vals = zip(*sorted(plot._points.items()))
        # x_vals.sort()
        radius = x_vals[-1] - x_vals[0]
        print("Effective radius {}".format(radius))
        print(x_vals)
        # f_vals = [x_squared(x) for x in x_vals]
        x_vals_normalised = normalise_values(x_vals)
        f_vals_normalised = normalise_values(f_vals)
        print(x_vals_normalised)
        print(f_vals_normalised)
        input_values = {
            "point1" : {"x":x_vals_normalised[0], "y": f_vals_normalised[0]},
            "point2" : {"x":x_vals_normalised[1], "y": f_vals_normalised[1]},
            "point3" : {"x":x_vals_normalised[2], "y": f_vals_normalised[2]},
            "point4" : {"x":x_vals_normalised[3], "y": f_vals_normalised[3]},
            "radius": radius,
            "x_min": x_vals[0],
            "x_max": x_vals[-1],
            "step": 1.0,
            "bias": 1.0,
            "f_change": 0.0
        }
        return enn.evaluate(input_values)
    else:
        return None
        # show_step(x_vals, f_vals, x_guess, x_plus, x_minus)

class DraggablePlotExample(object):
    u""" An example of plot with draggable markers """

    def __init__(self):
        self._figure, self._axes, self._line = None, None, None, 
        self._err_lines = None
        self.x_guess = None
        self._dragging_point = None
        self._points = {}
        self.enn = Evaluator()

        self._init_plot()

    def _init_plot(self):
        self._figure = plt.figure("Example plot")
        axes = plt.subplot(1, 1, 1)
        axes.set_xlim(-20, 20)
        axes.set_ylim(0, 100)
        axes.set_title("ENN Step Playground")
        axes.grid(which="both")
        self._axes = axes

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        plt.show()

    def _update_plot(self):
        if not self._points:
            self._line.set_data([], [])
        else:
            x, y = zip(*sorted(self._points.items()))
            # Add new plot
            if not self._line:
                self._line, = self._axes.plot(x, y, "b", marker="o", markersize=10)
            # Update current plot
            else:
                self._line.set_data(x, y)
                vals = process_step(self, self.enn)
                if vals != None:
                    # self._axes.plot(x_vals,fx_vals, marker="o")
                    if not self.x_guess:
                        self.x_guess, = self._axes.plot(vals[0],25, marker="o", color="red")
                    else:
                        self.x_guess.set_data(vals[0],25)
                    # line, = self._axes.plot(t, s, lw=2)
                    if not self._err_lines:
                        self._err_lines, = self._axes.plot([vals[0]-vals[2], vals[0]+vals[1]], [25]*2, lw=2, linestyle="solid", color="red")
                    else:
                        self._err_lines.set_data([vals[0]-vals[2], vals[0]+vals[1]], [25]*2)
        self._figure.canvas.draw()

    def _add_point(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)
        self._points[x] = y
        return x, y

    def _remove_point(self, x, _):
        if x in self._points:
            self._points.pop(x)

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position

        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 3.0
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for x, y in self._points.items():
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, event):
        u""" callback method for mouse click event

        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
            elif len(self._points) == 4:
                pass
            else:
                self._add_point(event)
            self._update_plot()
        # right click
        elif event.button == 3 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._remove_point(*point)
                self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event

        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self._dragging_point:
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event

        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._remove_point(*self._dragging_point)
        self._dragging_point = self._add_point(event)
        self._update_plot()


if __name__ == "__main__":
    plot = DraggablePlotExample()