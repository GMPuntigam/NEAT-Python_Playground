import sys, ctypes
from ctypes import Structure, POINTER, c_double
import numpy as np
import random
import os
from matplotlib import pyplot as plt

class Evaluator(Structure):
    pass

class POINT(Structure):
    _fields_ = [("x", c_double),
                ("y", c_double)]
    
class AdditionalInputs(Structure):
    _fields_ = [("step", c_double),
                ("bias", c_double),
                ("f_change", c_double)]
    
class NetworkResults(Structure):
    _fields_ = [("phi1", c_double),
                ("phi2", c_double),
                ("phi3", c_double)]

prefix = {'win32': ''}.get(sys.platform, 'lib')
extension = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
lib = ctypes.cdll.LoadLibrary(prefix + os.getcwd() + r"\target\debug\py_rust" + extension)

process_array = lib.evaluate_network

lib.construct_network.restype = POINTER(Evaluator)
lib.terminate_evaluator.argtypes = (POINTER(Evaluator), )

process_array.argtypes = [POINT,POINT,POINT,POINT,AdditionalInputs, POINTER(Evaluator)]
process_array.restype = POINTER(NetworkResults)


def x_squared(x):
    return x**2


class Evaluator:
    def __init__(self):
        self.obj = lib.construct_network(os.getcwd().encode('utf-8') + r"\neural_network\neuralnet.json".encode('utf-8'))

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        lib.terminate_evaluator(self.obj)

    def evaluate(self, input_values):
        point1 = POINT(input_values["point1"]["x"], input_values["point1"]["y"])
        point2 = POINT(input_values["point2"]["x"], input_values["point2"]["y"])
        point3 = POINT(input_values["point3"]["x"], input_values["point3"]["y"])
        point4 = POINT(input_values["point4"]["x"], input_values["point4"]["y"])
        additionalInput = AdditionalInputs(input_values["step"],input_values["bias"],input_values["f_change"])
        return_arr = process_array(point1,point2,point3,point4,additionalInput, self.obj).contents
        print(return_arr)
        x_plus = input_values["radius"]*(0.5+return_arr.phi2)
        x_minus = input_values["radius"]*(0.5+return_arr.phi3)
        # radius = (x_plus + x_minus)/2.0
        print(return_arr.phi1)
        x_guess= (return_arr.phi1+(0.5+return_arr.phi2)-(0.5+return_arr.phi3))*(input_values["x_max"]-input_values["x_min"])+input_values["x_min"]
        print("Guess: {}".format(x_guess))
        print("Minus: {}".format(x_minus))
        print("Plus: {}".format(x_plus))
        return [x_guess, x_plus, x_minus]
        # return process_array(point1,point2,point3,additionalInput, self.obj)

def normalise_values(vals):
    x_min = min(vals)
    x_max = max(vals)
    return[(val-x_min)/(x_max-x_min) for val in vals]






def show_step(x_vals, fx_vals, x_guess, x_plus, x_minus):
    fig, ax = plt.subplots()
    ax.set_title("ENN Step Playground")
    t = np.arange(min(x_vals), max(x_vals), (max(x_vals) - min(x_vals))/1000)
    s = x_squared(t)
    ax.plot(x_vals,fx_vals, marker="o")
    ax.plot(x_guess,x_squared(x_guess), marker="o", color="red")
    line, = ax.plot(t, s, lw=2)
    ax.plot([x_guess-x_minus, x_guess+x_plus], [x_squared(x_guess)]*2, lw=2, linestyle="solid", color="red")
    plt.show()

if __name__ == "__main__":
    with Evaluator() as enn:
        x_vals = [20*random.random()-10 for i in range(4)]
        x_vals.sort()
        radius = x_vals[-1] - x_vals[0]
        print("Effective radius {}".format(radius))
        print(x_vals)
        f_vals = [x_squared(x) for x in x_vals]
        x_vals_normalised = normalise_values(x_vals)
        f_vals_normalised = normalise_values(f_vals)
        print(x_vals)
        print(f_vals)
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
        vals = enn.evaluate(input_values)
        show_step(x_vals, f_vals, vals[0],vals[1],vals[2])