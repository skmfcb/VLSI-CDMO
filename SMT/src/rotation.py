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

  # H lower and upper bounds
  s.add(H >= sum([widths[i]*heights[i] for i in range(N)]) // W)
  s.add(H <= sum([max(widths[i],heights[i]) for i in range(N)]))
          
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

  return solution, s.statistics().time


def main(args):
  # Default params
  inst_folder = "../../Instances"
  sol_folder = "../out/rotation"
  img_folder = "../imgs/rotation"
  times_folder = "../comp_times/rotation"
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