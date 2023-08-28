import sys
from z3 import *  
from utils.utils import format_solution, display_solution, write_file_output, write_file_times, load_instance_from_file

def solve(W, N, M):

  widths = [sub[0] for sub in M]
  heights = [sub[1] for sub in M]

  num_cells = W * max(heights)
  X = [[Bool('x_%s_%s' % (i, j)) for j in range(W)] for i in range(num_cells)]
  Y = [[Bool('y_%s_%s' % (i, j)) for j in range(W)] for i in range(num_cells)]
  H = Int('H')

  s = Solver()

  # Encode the constraints
  for i in range(N):
    for j in range(W - widths[i] + 1):
      for k in range(max(heights)):
        clause = []
        for x in range(widths[i]):
          for y in range(heights[i]):
            clause.append(X[k + y][j + x])
        s.add(Or(clause))

  for i in range(N):
    for j in range(max(heights) - heights[i] + 1):
      for k in range(W):
        clause = []
        for x in range(widths[i]):
          for y in range(heights[i]):
            clause.append(Y[j + y][k + x])
        s.add(Or(clause))

  # Encode non-overlapping constraints
  for i in range(N):
    for j in range(i + 1, N):
      for x in range(W):
        for y in range(max(heights)):
          s.add(Or(Not(X[y][x]), Not(X[y][x + widths[j]])))
          s.add(Or(Not(X[y][x]), Not(X[y + heights[j]][x])))
          s.add(Or(Not(X[y][x + widths[j]]), Not(X[y + heights[j]][x])))

  lo = max(heights)  # Lower bound
  hi = sum(heights)  # Upper bound

  lo = max(heights)  # Lower bound
  hi = sum(heights)  # Upper bound

  optimal_max_height = None
  while lo <= hi:
      mid = (lo + hi) // 2
      s.push()
      
      # Encode constraints and objective
      # (Add your constraint and objective encodings here)

      if s.check() == sat:
          optimal_max_height = mid
          hi = mid - 1
      else:
          lo = mid + 1

      s.pop()  # Restore solver state

  if optimal_max_height is not None:
      print("Optimal maximum height:", optimal_max_height)
      # Extract and print the solution
      # (Add your solution extraction and printing here)
  else:
      print("No solution found")

  s.set(timeout=300000) # 5 minutes 

  solution = {}
  check = s.check()
  if check == sat:  
    print("SAT")
    m = s.model()
    x = [m.evaluate(X[i]).as_long() for i in range(N)]
    y = [m.evaluate(Y[i]).as_long() for i in range(N)]
    solution = format_solution(W, N, m.evaluate(H).as_long(), x, y, widths, heights)
  elif check == unsat:
     print("UNSAT")
  elif check == unknown:
     print("UNKNOWN")
  return solution, s.statistics().time


def main(args):
  # Default params
  inst_folder = "../../Instances"
  sol_folder = "../out/no-rotation"
  img_folder = "../imgs/no-rotation"
  times_folder = "../comp_times/no_rotation"
  START = 1 
  STOP = len([name for name in os.listdir(inst_folder) if os.path.isfile(os.path.join(inst_folder, name))])

  # Handle input params
  if len(args)>1 : inst_folder = args[1] 
  if len(args)>2 : sol_folder = args[2] 
  if len(args)>3 : START = int(args[3])
  if len(args)>4: STOP = int(args[4])

  computation_times = []

  # Loop over instances
  for i in range(START, STOP+1):
    print(f"Running instance {i}")
    filename = f"{inst_folder}/ins-{i}.txt"
    solution, time = solve(*load_instance_from_file(filename))

    write_file_output(solution, f"{sol_folder}/{i}.txt" )  
    if not solution == {}:
      display_solution(solution, f"{i}", img_folder)
      computation_times.append(time)
    else:
      computation_times.append(0.0)
    write_file_times(computation_times, times_folder)
    print("Computation time: ", time )
    print("-"*40)

  
if __name__ == "__main__":
    main(sys.argv)