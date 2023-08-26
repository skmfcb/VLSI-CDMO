include "globals.mzn";

% Inputs
int: W;
int: N;
array[1..N, 1..2] of int: CIRCUITS;

% Extract widths 'm' and heights 'n' from matrix
array[1..N] of int: m = [CIRCUITS[i, 1] | i in 1..N];
array[1..N] of int: n = [CIRCUITS[i, 2] | i in 1..N];

% Compute the minimum and maximum possible heights of the board
int: min_height = max(max(n), ceil(sum([(m[i]*n[i]) | i in 1..N]) div W));

int: max_height = sum(n);

% Variable to hold the height of the borad
var min_height..max_height: H;  

% Variables to hold the x and y coordinates of each circuit
array[1..N] of var 0..W: X;
constraint forall(i in 1..N)(0 <= X[i] /\ X[i] <= W - m[i]);

array[1..N] of var 0..max_height: Y;
constraint forall(i in 1..N)(0 <= Y[i] /\ Y[i] <= max_height - n[i]);

% Constraints
% Circuit placements must not be overlapping
constraint forall(i, j in 1..N where i < j) (
  X[i] + m[i] <= X[j] \/ X[j] + m[j] <= X[i] \/
  Y[i] + n[i] <= Y[j] \/ Y[j] + n[j] <= Y[i]
);

% All circuits must fit on the board:
constraint forall(i in 1..N)(X[i] + m[i] <= W /\ Y[i] + n[i] <= H);

% Find the x and y coordinates using 'cumulative' global constraints
% The cumulative constraint is used for describing cumulative resource usage. It requires that a set of tasks given by start times s, durations d, and resource requirements r, never require more than a global resource bound b at any one time.
constraint cumulative(X, m, n, H);
constraint cumulative(Y, n, m, W);

% Symmetry breaking
% Symmetry breaking for circuits with the same dimensions
predicate symm_breaking_same(array[int] of var int: X, array[int] of var int: Y, array[int] of int: m, array[int] of int: n) =
  forall(i, j in 1..N where i < j /\ m[i]==m[j] /\ n[i]==n[j])(
    (X[i], Y[i]) <= (X[j], Y[j])
  );


% Compute the symmetry breaking w.r.t. the x or y axis. i.e. Reflection over x-axis and y-axis.
predicate symm_breaking_axes() = 
      let {
            array[1..N] of var int: new_x = [W - X[i] - m[i] | i in 1..N];
            array[1..N] of var int: new_y = [H - Y[i] - n[i] | i in 1..N]
      } in lex_lesseq(X, new_x) /\ lex_lesseq(Y, new_y);
      
%Both the predicates must hold true for the constraint to be satisfied.
constraint symm_breaking_same(X,Y,m,n) /\ symm_breaking_axes();
      
solve :: seq_search([
            int_search([H], input_order, indomain_min),
            int_search(X, input_order, indomain_min),
            int_search(Y, input_order, indomain_min)])
      minimize H;
      
% Output solution
output [ show(W)," ",show(H),"\n",show(N),"\n"];
output ["\(CIRCUITS[i, 1]) \(CIRCUITS[i, 2]) \(X[i]) \(Y[i])\n" | i in 1..N];
