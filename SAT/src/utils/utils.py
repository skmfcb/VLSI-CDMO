import os

import matplotlib.pyplot as plt

def load_instance_from_file(filename):
  with open(filename, 'r') as file:
    instance_data = file.readlines()

    w = int(instance_data[0])
    n = int(instance_data[1])
    
    M = []
    for line in instance_data[2:]:
      row = list(map(int, line.split()))
      M.append(row)

    return w, n, M

def write_file_times(times, path):
  with open(path+".txt", 'w') as f:
    f.writelines("COMPUTATION TIME")
    f.writelines("\n%s" % t for t in times)
    f.writelines("\n"+"-"*5)
  f.close()


def write_file_output(solution, path):
  f = open(path, "w+")
  if not solution=={}:
    f.write("{} {}\n".format(*solution['sizes_plate']))
    f.write("{}\n".format(solution['n_circuits']))
    for i in range(len(solution['pos_circuits'])):
      f.write("{} {} {} {}\n".format(*solution['sizes_circuits'][i], *solution['pos_circuits'][i]))
  f.close()


def display_solution(solution, instance_index, folder):
  fig, ax = plt.subplots()
  ax.set_aspect('equal')
  cmap = plt.colormaps['rainbow']
  ax = plt.gca()
  plt.title(f"Solution {instance_index}")
  if len(solution['pos_circuits']) > 0:
    for i in range(solution['n_circuits']):
      rect = plt.Rectangle(solution['pos_circuits'][i], *solution['sizes_circuits'][i], edgecolor="#333", facecolor=cmap(i / (solution['n_circuits'] - 1)))
      ax.add_patch(rect)
  ax.set_xlim(0, solution['sizes_plate'][0])
  ax.set_ylim(0, solution['sizes_plate'][1] + 1)
  ax.set_xticks(range(solution['sizes_plate'][0] + 1))
  ax.set_yticks(range(solution['sizes_plate'][1] + 1))
  ax.set_xlabel('width_plate')
  ax.set_ylabel('height_plate')
  
  if not os.path.exists(folder):
    os.makedirs(folder)
  plt.savefig(f"{folder}/solution_{instance_index}.png") 
  #plt.show()
  plt.close()


def format_solution(W, N, H, X, Y, widths, heights):
  solution = {}
  solution['sizes_plate'] = (W, H) 
  solution['n_circuits'] = N
  solution['sizes_circuits'] = list(zip(widths, heights))
  solution['pos_circuits'] = list(zip(X, Y))
  return solution

def timeout_handler(signum, frame):
    raise TimeoutError("[*] ABORT - The solving has taken too long.")
