include "globals.mzn";

% Inputs
int: W;
int: N;
array[1..N, 1..2] of int: CIRCUITS;

% Extract widths 'm' and heights 'n' from matrix
array[1..N] of int: m = [CIRCUITS[i, 1] | i in 1..N];
array[1..N] of int: n = [CIRCUITS[i, 2] | i in 1..N];

% Variables
% Lower bound is the maximum between the optimal height and the maximum width/height
int: min_height = sum([(m[i]*n[i]) | i in 1..N]) div W;

% Upper bound is the sum of all circuit heights, as staking one above the other + the sum of the widths
int: max_height = sum([max(n[i], m[i]) | i in 1..N]);
var min_height..max_height: H;

% Variables to hold the x and y coordinates of each circuit
array[1..N] of var 0..W-min(m): X;
array[1..N] of var 0..max_height-min(n): Y;

% When Rotation is Allowed
% Boolean variables to indicate if the circuit is rotated
array[1..N] of var bool: rot;

% Variables to hold the actual width and height of each circuit
array[1..N] of var 1..max(max(m), max(n)): w_real=
    [if rot[i] then n[i] else m[i] endif |
        i in 1..N];
        
array[1..N] of var 1..max(max(m), max(n)): h_real=
    [if rot[i] then m[i] else n[i] endif |
        i in 1..N];

% Constraints

% Circuit placements must not be overlapping
constraint forall(i, j in 1..N where i < j) (
    X[i] + w_real[i] <= X[j] \/ X[j] + w_real[i] <= X[i] \/
    Y[i] + h_real[i] <= Y[j] \/ Y[j] + h_real[i] <= Y[i]
);

% All circuits must fit on the board:
constraint forall(i in 1..N) (
  X[i] + w_real[i] <= W /\ Y[i] + h_real[i] <= H
);

% Find the x and y coordinates using 'cumulative' global constraints
% The cumulative constraint is used for describing cumulative resource usage. It requires that a set of tasks given by start times s, durations d, and resource requirements r, never require more than a global resource bound b at any one time.
constraint cumulative(X, w_real, h_real, H);
constraint cumulative(Y, h_real, w_real, W);

%Symmetry Breaking       
% Symmetry breaking for circuits with the same dimensions
predicate symm_breaking_same(array[int] of var int: X, array[int] of var int: Y, array[int] of var int: w_real, array[int] of var int: h_real) =
  forall(i, j in 1..N where i < j /\ w_real[i]==w_real[j] /\ h_real[i]==h_real[j])(
    (X[i], Y[i]) <= (X[j], Y[j])
  );


% Compute the symmetry breaking w.r.t. the x or y axis. i.e. Reflection over x-axis and y-axis.
predicate symm_breaking_axes(array[int] of var int: X, array[int] of var int: Y, array[int] of var int: w_real, array[int] of var int: h_real) =
  forall(i in 1..N)(
    (X[i] + w_real[i], Y[i] + h_real[i]) <= (W, H)
  );

%Both the predicates must hold true for the constraint to be satisfied.
constraint symm_breaking_same(X,Y,w_real,h_real) /\ symm_breaking_axes(X,Y,w_real,h_real);
        
% Constraints to avoid infeasible rotations
constraint forall(i in 1..N) (
    if n[i] > W then rot[i] = false else true endif
);
  
% Constraints when the circuit is sqaure              
constraint forall(i in 1..N) (
  (m[i] == n[i]) -> (rot[i] == false)
);       


% Objective function to minimize the height of the board
solve :: seq_search([
            int_search([H], input_order, indomain_min),%::restart_luby(200),
            int_search(X, first_fail, indomain_min),
            int_search(Y, first_fail, indomain_min)])
      minimize H;


% Output solution
output [ show(W)," ", show(H),"\n",   show(N),"\n"];
output ["\(CIRCUITS[i,1]) \(CIRCUITS[i,2]) \(X[i]) \(Y[i]) \(rot[i]) \n" | i in 1..N];
