import sys
from z3 import *  
import time
import signal
from utils.utils import format_solution, display_solution, write_file_output, write_file_times, load_instance_from_file, timeout_handler

def solve(W, N, M):

  best_solver = Solver()

  widths = [sub[0] for sub in M]
  heights = [sub[1] for sub in M]             

  low = max(max(heights), math.ceil(sum([widths[i]*heights[i] for i in range(N)]) / W)) # Lower bound
  high = sum(heights) # Upper bound

  optimal_max_height = None

  for lo in range(low, high + 1):

    solver = Solver()
    
    x_max = W - min(widths)
    # x[i][v] means X[i] = v
    X = [[Bool('x_%s_%s' %(i,v)) for v in range(x_max + 1)] for i in range(N)]

    y_max = lo - min(heights)
    # y[i][v] means Y[i] = v
    Y = [[Bool('y_%s_%s' %(i,v)) for v in range(y_max + 1)] for i in range(N)]

    # Constraints 
    for i in range(N):
      # At least one X[i][v] must be true
      solver.add(Or([X[i][v] for v in range(len(X[i]))]))
      # At least one Y[i][v] must be true
      solver.add(Or([Y[i][v] for v in range(len(Y[i]))]))
      
      # At most one X[i][v] can be true
      for v1 in range(len(X[i])):
        for v2 in range(v1+1, len(X[i])):
          solver.add(Not(And(X[i][v1], X[i][v2])))
      
      # At most one Y[i][v] can be true
      for v1 in range(len(Y[i])):
        for v2 in range(v1+1, len(Y[i])):
          solver.add(Not(And(Y[i][v1], Y[i][v2])))              

      # Non-overlapping constraints
      for i in range(N):
        for j in range(i+1, N):
          for v1 in range(len(X[i])):
            for v2 in range(len(X[j])):
              for v3 in range(len(Y[i])):
                for v4 in range(len(Y[j])):
                  solver.add(
                    Implies(And(Y[i][v3], Y[j][v4], v3 == v4, X[i][v1], X[j][v2]),  
                            And(v1 != v2, Or(v1 + widths[i] <= v2, v2 + widths[j] <= v1 )))
                    )
                  solver.add( 
                    Implies(And(X[i][v1], X[j][v2], v1 == v2, Y[i][v3], Y[j][v4]),  
                            And(v3 != v4, Or(v3 + heights[i] <= low, v4 + heights[j] <= low), Or(v3 + heights[i] <= v4, v4 + heights[j] <= v3 )))
                    )
                  solver.add( 
                    Implies(And(X[i][v1], X[j][v2], v1 != v2, Y[i][v3], Y[j][v4], v3 != v4),  
                            And(Or(v3 + heights[i] <= low, v4 + heights[j] <= low), Or(v3 + heights[i] <= v4, v4 + heights[j] <= v3 )))
                    )
              
              
    if solver.check() == sat:
      optimal_max_height = lo
      best_solver = solver
      print("SAT")
      print("Optimal height:", optimal_max_height)
      
      break

  if optimal_max_height is not None:
    
    model = best_solver.model()
    
    x_vals = [-1 for _ in range(N)]
    y_vals = [-1 for _ in range(N)]
      
    for i in range(N):
      for v in range(len(X[i])):
        if model.evaluate(X[i][v]):
          x_vals[i] = v
                
      for v in range(len(Y[i])):
        if model.evaluate(Y[i][v]):
          y_vals[i] = v

    solution = format_solution(W, N, optimal_max_height, x_vals, y_vals, widths, heights)
    return solution
  else:
    print("UNSAT")
    solution = {}
    return solution
  

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

    start_time = time.time()
    solution = solve(*load_instance_from_file(f"{inst_folder}/ins-{i}.txt"))
    comp_time = time.time() - start_time
  
    solution = {}

    write_file_output(solution, f"{sol_folder}/{i}.txt" )  
    
    if not solution == {}:
      display_solution(solution, f"{i}", img_folder)
      computation_times.append(comp_time)
    else:
      computation_times.append(0.0)

    print("Computation time: ", comp_time )
    print("-"*40)

  write_file_times(computation_times, times_folder)

  
if __name__ == "__main__":
    main(sys.argv)