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


def solve(W, N, M):

  widths = [sub[0] for sub in M]
  heights = [sub[1] for sub in M]

  # Decision variables
  X = [Int('x_%s' % i) for i in range(N)]
  Y = [Int('y_%s' % i) for i in range(N)]
  H = Int('H') 
  rot = [Bool('rot_%d' % i) for i in range(N)]
  w_real = [Int('w_real_%d' % i) for i in range(N)]
  h_real = [Int('h_real_%d' % i) for i in range(N)]

  s = Optimize()
  
  # Constraints
  for i in range(N):
    # Domain constraints
    s.add(X[i] >= 0, X[i] <= W - min(widths + heights))
    s.add(Y[i] >= 0, Y[i] <= H - min(widths + heights))    

    # Constraints on rotation
    s.add(Implies(heights[i] > W, rot[i] == False)) 

    # Squares can not rotate
    s.add(Implies(widths[i] == heights[i], rot[i] == False))

    # Non-overlapping     
    for j in range(i+1, N):
      s.add(Or(X[i] + w_real[i] <= X[j], X[j] + w_real[j] <= X[i], 
              Y[i] + h_real[i] <= Y[j], Y[j] + h_real[j] <= Y[i]))
    
    # Compute actual width and height
    s.add(If(rot[i], w_real[i] == heights[i], w_real[i] == widths[i]))
    s.add(If(rot[i], h_real[i] == widths[i], h_real[i] == heights[i]))

    # Contraints on boundaries
    s.add(X[i] + w_real[i] <= W)
    s.add(Y[i] + h_real[i] <= H)
    s.add(H >= h_real[i])
    
          
  # Objective    
  s.minimize(H)
  s.set(timeout=300000) # 5 minutes 

  solution = {}
  check = s.check()
  if check == sat:  
    print("SAT")
    m = s.model()
    x = [m.evaluate(X[i]).as_long() for i in range(N)]
    y = [m.evaluate(Y[i]).as_long() for i in range(N)]
    solution = format_solution(W, N, m.evaluate(H).as_long(), x, y, [m.evaluate(w).as_long() for w in w_real], [m.evaluate(h).as_long() for h in h_real])
  elif check == unsat:
     print("UNSAT")
  elif check == unknown:
     print("UNKNOWN")
  print("Computation time: ", s.statistics().time )

  return solution


def main(args):
  # Default params
  inst_folder = "../../Instances"
  sol_folder = "../out/rotation"
  img_folder = "../imgs/rotation"
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