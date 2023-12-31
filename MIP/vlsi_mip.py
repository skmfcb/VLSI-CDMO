# -*- coding: utf-8 -*-
"""VLISI-MIP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VsHi_ZtExpcZbXMDnAbJ0QX6ida0B8-1
"""

!pip install gurobipy>=10

from google.colab import drive
drive.mount('/content/drive')

import argparse
import math
import os
import datetime
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from pathlib import Path
from random import randint
from timeit import default_timer as timer
from matplotlib import colors
import matplotlib.pyplot as plt
import math
import numpy as np
from pulp import LpVariable, LpProblem, LpBinary, LpMinimize, lpSum

import numpy as np
from pathlib import Path

def read_input(index_file):
    x = []  # List to store horizontal dimensions of the circuits
    y = []  # List to store vertical dimensions of the circuits
    w = 0   # Width of the silicon plate
    n = 0   # Number of circuits

    # Construct the path to the instance file
    ins_path = Path(f'/content/drive/MyDrive/MIP/instances/ins-{index_file}.txt')

    # Open the instance file for reading
    with open(ins_path, 'r') as f:
        text = f.readlines()

    # Extract the width and number of circuits from the first two lines
    w, n = map(int, text[:2])

    # Loop over lines containing circuit dimensions
    for line in text[2:n+2]:
        circuit_dims = list(map(int, line.split()))  # Extract horizontal and vertical dimensions
        x.append(circuit_dims[0])                   # Append horizontal dimension to list x
        y.append(circuit_dims[1])                   # Append vertical dimension to list y

    # Convert the lists to NumPy arrays of dtype int32
    x = np.array(x, dtype=np.int32)
    y = np.array(y, dtype=np.int32)

    # Return the extracted values
    return w, n, x, y

def write_solution(instance, w, h, n, x, y, x_coord, y_coord, rotation, time):
    # Determine the output directory based on rotation
    path_sol = "/content/drive/MyDrive/MIP/MIP_Res/out-rot-" if rotation else "/content/drive/MyDrive/MIP/MIP_Res/out-"

    # Construct the output file path
    out_path = Path(f'{path_sol}{instance}{"_rotation" if rotation else ""}.txt')

    # Write the solution to the output file
    with open(out_path, 'w') as f:
        # Write the plate dimensions and circuit count
        f.write(f'{w} {h}\n')
        f.write(f'{n}\n')

        # Write circuit details: width, height, x-coordinate, y-coordinate
        for i in range(n):
            f.write(f'{x[i]} {y[i]} {x_coord[i]} {y_coord[i]}\n')

    # Print confirmation message
    print(f"For instance {instance}, the best h value is {h} | execution_time {time}")

def write_log(instance: int, best_h: int , rotation: bool,time):
    path_sol = "/content/drive/MyDrive/MIP/MIP_Res/log_file_rotation" if rotation else "/content/drive/MyDrive/MIP/MIP_Res/log_file"
    out_path = Path(path_sol + ".txt")
    with open(out_path, 'a') as f:
        f.writelines(f'{instance} {best_h} {time} {"VALID" if time < 301.00 else "NOT VALID"}\n')

def write_log_init(rotation: bool):
    path_sol = "/content/drive/MyDrive/MIP/MIP_Res/log_file_rotation" if rotation else "/content/drive/MyDrive/MIP/MIP_Res/log_file"
    out_path = Path(path_sol + ".txt")
    with open(out_path, 'a') as f:
        f.writelines(f'\n- - -\n Test : {datetime.datetime.now()}\n')

def plot_solution(instance, w, h, n, x, y, x_coord, y_coord, rotation):       # path of the output file, board weight, board height, total number of circuits to place
    board = np.empty((h, w))        # h stands for the height of the board and, as a numpy array, it stands for the number of rows
                                    # w stands for the width of the board and, as a numpy array, it stands for the number of columns
    board.fill(n)

    for i in range(n):
        column = x_coord[i]  # position of the circuit on x-axis
        row = y_coord[i]     # position of the circuit on y-axis

        # compute the width and height of the current circuit
        width = x[i]
        height = y[i]

        for rows in range(row, row + height):
            for columns in range(column, column + width):
                board[rows][columns] = i

    cmap = build_cmap(n)
    plt.imshow(board, interpolation='None', cmap=cmap, vmin=0, vmax=n)
    ax = plt.gca()
    ax.invert_yaxis()
    path_plot = "/content/drive/MyDrive/MIP/MIP_Res/out-rot" if rotation else "/content/drive/MyDrive/MIP/MIP_Res/out-"
    image_path = Path(path_plot + str(instance) + f"{'_rotation' if rotation else ''}.png")
    plt.savefig(image_path)

def build_cmap(n):
    colors_list = []

    for i in range(n):
        colors_list.append('#%06X' % randint(0, 0xFFFFFF))

    colors_list.append('#FFFFFF')

    return colors.ListedColormap(colors_list)

def check_rotation_w(width,height,rotation: bool):
    if rotation:
        return height
    else:
        return width

def check_rotation_h(width,height,rotation: bool):
    if rotation:
        return width
    else:
        return height

def solver(w, n, x, y, rotation: bool, index_f, plot: bool):
    print(f"\n================================\n\nINSTANCE: {index_f}\n")
    print(f"width plate: {w}\n")
    print(f"number of circuits: {n}\n")

    # Display chip dimensions
    for a in range(n):
        print(f"{a}) chip dimension: {x[a]} X {y[a]}\n")

    h_Max = sum(y)
    h_min = math.ceil((sum([x[i] * y[i] for i in range(n)]) / w))
    area_min = sum((x[i] * y[i]) for i in range(n))
    area_max = h_Max * w

    if not rotation:
        model = gp.Model("MIP")
        model.setParam("TimeLimit", 5 * 60)  # 5 minutes for each instance
        model.setParam("Symmetry", -1)  # -1: auto, 0:off , 1: conservative, 2:aggressive

        # === VARIABLES === #
        x_cord = model.addVars(n, lb=0, ub=w - np.amin(x), vtype=GRB.INTEGER, name="x_coordinates")
        y_cord = model.addVars(n, lb=0, ub=h_Max - np.amin(y), vtype=GRB.INTEGER, name="y_coordinates")
        h = model.addVar(lb=h_min, ub=h_Max, vtype=GRB.INTEGER, name="height")  # our variable to minimize
        s = model.addVars(n, n, 4, vtype=GRB.BINARY, name="s")  # used for big M method

        # === CONSTRAINTS === #
        # 1) constraint that checks whether the chip dimensions do not exceed from the plate in both height (h) and width (w)
        model.addConstrs((x_cord[i] + x[i] <= w for i in range(n)), name="inside_plate_x")
        model.addConstrs((y_cord[i] + y[i] <= h for i in range(n)), name="inside_plate_y")

        # 2) constraint no overlap
        model.addConstrs((x_cord[i] + x[i] <= x_cord[j] + w * s[i, j, 0] for i in range(n) for j in range(i + 1, n)), "no_ov1")
        model.addConstrs((y_cord[i] + y[i] <= y_cord[j] + h * s[i, j, 1] for i in range(n) for j in range(i + 1, n)), "no_ov2")
        model.addConstrs((x_cord[j] + x[j] <= x_cord[i] + w * s[i, j, 2] for i in range(n) for j in range(i + 1, n)), "no_ov3")
        model.addConstrs((y_cord[j] + y[j] <= y_cord[i] + h * s[i, j, 3] for i in range(n) for j in range(i + 1, n)), "no_ov4")
        model.addConstrs((gp.quicksum(s[i, j, k] for k in range(4)) <= 3 for i in range(n) for j in range(n)), "no_overlap")

        area = w * h
        model.addConstr(area <= area_max, name="ub_area")
        model.addConstr(area >= area_min, name="lb_area")

        # Objective function
        model.setObjective(h, GRB.MINIMIZE)

        # Solver
        start_time = timer()
        model.optimize()
        solve_time = timer() - start_time
        model.write(f'file_mip/out-{index_f}.ls')

        # Solution
        x_sol = [int(model.getVarByName(f"x_coordinates[{i}]").X) for i in range(n)]
        y_sol = [int(model.getVarByName(f"y_coordinates[{i}]").X) for i in range(n)]
        h_sol = int(model.ObjVal)

        print(f'\nSolution: {h_sol}\n')

        # Writing solution
        write_solution(index_f, w, h_sol, n, x, y, x_sol, y_sol, False, solve_time)
        write_log(index_f, h_sol, False, solve_time)

        if plot:
            plot_solution(index_f, w, h_sol, n, x, y, x_sol, y_sol, False)

    # Similarly, Rest of the code for rotation case

# Define the arguments within the notebook
first_instance = 1
last_instance = 40
allow_rotation = False
plot_solution = True

# Loop through instances and call solver function
for a in range(first_instance, last_instance + 1):
    w, n, x, y = read_input(a)
    solver(w, n, x, y, allow_rotation, a, plot_solution)

