import os
import sys

from z3 import *  
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


def write_file_output(solution, path):
  f = open(path, "w+")
  if not solution=={}:
    f.write("{} {}\n".format(*solution['sizes_plate']))
    f.write("{}\n".format(solution['n_circuits']))
    for i in range(len(solution['pos_circuits'])):
      f.write("{} {} {} {}\n".format(*solution['sizes_circuits'][i], *solution['pos_circuits'][i]))
  f.close()
  print("-"*40)


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
  #plt.savefig(f"{folder}/solution_{instance_index}.png") 
  plt.show()
  #plt.close()


def format_solution(W, N, H, X, Y, widths, heights):
  solution = {}
  solution['sizes_plate'] = (W, H) 
  solution['n_circuits'] = N
  solution['sizes_circuits'] = list(zip(widths, heights))
  solution['pos_circuits'] = list(zip(X, Y))
  return solution


def solve(W, N, M):

  widths = [sub[0] for sub in M]
  heights = [sub[1] for sub in M]

  X = [Bool('x_%s_%s' % (i,j)) for i in range(N) for j in range(W)]
  Y = [Bool('y_%s_%s' % (i,j)) for i in range(N) for j in range(W)]

  s = Solver()

  # Domain constraints
  for i in range(N):
    or_clause = [X[i*W + j] for j in range(W - min(widths) + 1)]
    s.add(Or(*or_clause))
    
    or_clause = [Y[i*W + j] for j in range(W - min(heights) + 1)]
    s.add(Or(*or_clause))

  # Boundary constraints
  for i in range(N):
    for j in range(W-widths[i]+1, W):
      s.add(Not(X[i*W + j]))
      
    for j in range(W-heights[i]+1, W):
      s.add(Not(Y[i*W + j]))

  # Non-overlapping constraints
  for i in range(N):
    for j in range(N):
      if i != j:
        for k in range(W):
          for l in range(W):
            # If circuit i placed at (k,l), check if inside circuit j
            if X[i*W + k] and Y[i*W + l]:
              x1, y1 = k, l 
              w1, h1 = widths[i], heights[i]

              for m in range(W):
                for n in range(W):
                  
                  # If circuit j placed at (m,n), check bounds
                  if X[j*W + m] and Y[j*W + n]:
                    x2, y2 = m, n
                    w2, h2 = widths[j], heights[j]

                    # Check if (x1, y1) inside bounds of (x2, y2, w2, h2)  
                    s.add(Or(x1 < x2, x1 >= x2 + w2, y1 < y2, y1 >= y2 + h2))
  left = 0
  right = W

  while left < right:
    mid = left + (right - left) // 2
    
    s.push()
    for i in range(N):
       for j in range(mid, W):
         s.add(Not(Y[i*W + j]))
    
    if s.check() == unsat:
      core = s.unsat_core()
      if core:
        min_core_y = min([Y[c.name()] for c in core])
        right = min_core_y // W
      else:
        # Empty core, use middle value
        right = left + (right - left) // 2
    else:
      left = mid + 1

    s.pop()
  
  min_height = left
  
  if s.check() == sat:
    m = s.model()
    x = [0] * N
    y = [0] * N
    for i in range(N):
      for j in range(W):
        if m[X[i*W + j]]:
          x[i] = j
          break
    for i in range(N):
      for j in range(W):
        if m[Y[i*W + j]]:  
          y[i] = j
          break

    solution = format_solution(W, N, min_height, x, y, widths, heights)
        
  else:
    print("No solution found")
    solution = {}
  
  return solution


def main(args):
  # Default params
  inst_folder = "../../Instances"
  sol_folder = "../out/no-rotation"
  img_folder = "../imgs/no-rotation"
  START = 1 
  STOP = len([name for name in os.listdir(inst_folder) if os.path.isfile(os.path.join(inst_folder, name))])

  # Handle input params
  if len(args)>1 : inst_folder = args[1] 
  if len(args)>2 : sol_folder = args[2] 
  if len(args)>3 : START = int(args[3])
  if len(args)>4: STOP = int(args[4])

  # Loop over instances
  for i in range(START, STOP+1):
    print(f"Running instance {i}")
    filename = f"{inst_folder}/ins-{i}.txt"
    solution = solve(*load_instance_from_file(filename))

    write_file_output(solution, f"{sol_folder}/{i}.txt" )  
    if not solution == {}:
      display_solution(solution, f"{i}", img_folder)

  
if __name__ == "__main__":
    main(sys.argv)