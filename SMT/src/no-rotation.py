import sys
from z3 import *  
from utils.utils import format_solution, display_solution, write_file_output, write_file_times, load_instance_from_file

def solve(W, N, M):

  widths = [sub[0] for sub in M]
  heights = [sub[1] for sub in M]

  # Decision variables
  X = [Int('x_%s' % i) for i in range(N)]
  Y = [Int('y_%s' % i) for i in range(N)]
  H = Int('H') 

  s = Optimize()
  
  # Constraints
  for i in range(N):
    # Domain constraints
    s.add(X[i] >= 0, X[i] <= W - min(widths))
    s.add(Y[i] >= 0, Y[i] <= H - min(heights))
    # Constraints on plate boundaries
    s.add(X[i] + widths[i] <= W)
    s.add(Y[i] + heights[i] <= H)   
    for j in range(i+1, N):
      # Non-overlapping constraints  
      s.add(Or(X[i] + widths[i] <= X[j], 
              X[j] + widths[j] <= X[i],
              Y[i] + heights[i] <= Y[j],  
              Y[j] + heights[j] <= Y[i]))
  
  # H lower and upper bound
  s.add(H >= max(heights))
  s.add(H <= sum(heights))
          
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