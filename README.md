# Factorio Assignment Shubham

## Factory 

### Assumptions

Since in the sample output the number of machines is given as a float, it is assumed that the number of machines need not be integral.

### Notations

The linear programming notations similar to `scipy.optimize.linprog` are used, as mentioned below:

To optimize $min_x (c^T x)$ such that $A_{ub}x \le b_{ub}$, $A_{eq}x = b_{eq}$ with $0 \le x_i \lt \infty$ where $c, b_{ub}, b_{eq}$ are vectors and $A_{ub}, A_{eq}$ are matrices.

### Problem Modelling

Define $x_r$ as **the number of machines used for the $r^{th}$ recipe**. I decided to use this definition of $x_r$ since it helps us solve the problem in one phase itself if the solution exists. It also helps simplify the main optimisation equation to an elegant form of: 
$$min_{x} (c^T x)$$
where $c = [1, 1, 1 ...]$

So, by the above modelling, our solution will be the one with the lesser machine count in case of ties.

- $A_{eq}, b_{eq}$

    - **Intermediates**: For each intermediate, total over all the recipes the rate at which it is produced/consumed. Set this to 0 to ensure a steady state.

    - **Target**: For the target product, total over all the recipes the rate at which it is being produced/consumed. Set this to the target rate. 

- $A_{ub}, b_{ub}$

    - **Supplies**: For each supply, total over all the recipes the rate at which it is being consumed and upper bound it by the maximum rate.

    - **Machines**: For each machine type, set the total number of machines to be upper bound by the maximum number of machines possible for that type.

### Modules

Our aim is to find a solution that satisfies the criteria and uses the minimum number of machines. If we increase the productivity and speed of the machines, it would be beneficial to us since it would decrease the number of machines required. So for all the machines, apply all modules if available.

### Reporting Solution

If the solution exists, the necessary rates of recipe production and supply utilisation are computed using the solution for $x$, which is the number of machines for each recipe.

### Infeasible Solution

If the solution to the above problem does not exist, then our solver fails. In this case, I utilize an important property of monotonicity. If a target flow of $t$ can be achieved, then a target flow of $t' \lt t$ also exists. Using this property, use binary search to determine the maximum possible target flow.

To provide bottleneck hints, I utilize the following property. If a resource is a bottleneck, then in the maximum flow, it must be used at its maximum capacity. So there are supplies at their maximum capacity or a machine type at its maximum count, then report them as bottleneck hints. One important point to note here is that the vice versa is not necessarily true, i.e., a resource at its full capacity may not be a bottleneck. This is the reason why we are reporting these as hints so that the user can further inspect.

## Belts

### Assumptions

Since the input format is not specified, it is assumed to be as follows:

```
{
  "nodes": {
    "a": {"cap": 1000},
    "b": {},
    "sink": {}
  },
  "edges": [
    {"from": "s1", "to": "a", "lo": 0, "hi": 500},
    {"from": "a", "to": "b", "lo": 0, "hi": 400},
    {"from": "b", "to": "sink", "lo": 0, "hi": 400}
  ],
  "sources": {"s1": 300},
  "sink": "sink"
}
```

The parameter `flow_needed` per edge has not been defined in the assignment and has been included in the sample output given. I tried to come up with a definition of it, but there are various ambiguities. For example, if we define it as the increase in the capacities of the edges in the min-cut, then the first aspect that is not clear is how to choose among multiple solutions. This is because there can be **multiple ways the capacities of the edges in the cut can be modified** to reach the target flow. Even if we devise some tie-breaking rules between multiple possible solutions, it is not guaranteed that resolving edges in this min-cut will necessarily increase the flow. This is because **multiple min-cuts can exist in a graph and resolving one min-cut does not resolve all of them**. Hence, it would not be appropriate to define it by only considering the edges in the current min-cut. Considering this level of complexity and lack of description in the problem statement, I assume that `flow_needed` was a typo in the sample output and choose to ignore the field.

Also, according to the sample test cases, the input is assumed to be ints, as detailed in the end of doc, this can very easily be adapted to floats. 

### Node Capacity Handling

For each node $v$ which has a cap of $c$ on the in/out flow, split it into two nodes $v_{in}$ and $v_{out}$ and add an edge with capacity $c$ from $v_{in}$ to $v_{out}$. This ensures that the constraint for the node is not violated.

### Edge Lower Bound Handling

For each edge $u \rightarrow v$, with lower bound $lo$ and upper bound $hi$, add an edge of capacity $hi - lo$ from $u$ to $v$. Subtract the balance of $lo$ from $u$ and add the balance of $hi$ from v. By doing this, what we have effectively done is to "add" a flow of $lo$ and restricted max flow to $lo + (hi-lo) = hi$.

### Source Sink Handling

Define a global source $S$ and a global sink node $T$. For nodes that are sources, add balance as the capacity of the source. For nodes that are sinks, add balance equal to negative of the sum of the capacities of the sources. 

### Node Imbalance Handling

For nodes that have a total balance negative, treat them as sources, and for those with a positive balance, treat them as sinks. Connect global S to each source and each sink to T with magnitiude of balance as capacity of edge. This is done because, if there exists a solution to the source-sink problem, then there must exist a solution such that all the outgoing edges of S are saturated and vice versa.

### Max-Flow

Finally, find the max flow from S to T in the modified graph. If this flow saturates all outgoing edges of S, it implies that there exists a solution to our original problem. Recover this solution by adding back the $lo$ flows we had subtracted from the edges and collapsing the nodes that were split.

### Infeasibility Certificate

In case the max flow is not sufficient, by the max-flow-min-cut theorem, this implies that there exists a min-cut such that the value of the cut is less than the required flow, and this cut is acting as the bottleneck. Find the cut by finding the reachable nodes from S. For edges lying on this cut, report them as tight edges, and for nodes that are split into different sides of the cut, report them as tight nodes.

## Numeric approach

### Tolerances
I have used a `TOL=1e-9` and passed it to the linear programming solver also. Also, while comparing whether two quantities are equal, for example, during bottleneck hints, a tolerance is taken into account.

### Solvers/Algorithms

**Factory** Here for checking the existence of the solution, I have used a built-in linear programming solver and hand-coded the binary search part. 

**Belts** The procedure for transforming the graph and handling tolerance has been hand-coded, and the routine for finding max-flow has been used from `scipy`.

**Reason** The built-in algorithms have been used primarily for efficiency purposes because they are implemented in lower-level languages than Python. Also, this saves the rework of writing the same algorithm again. Hand-coding has been done at places where I wanted control and customisation suited for our use case, for example, transforming the graph.

### Tie-breaking and Determinism

**Factory Tie Breaking** Here, I have formulated the problem such that the optimal and reported solution is the one with the minimum number of factories, which takes care of tie-breaking. Also, we rely on the determinism of the solver, which, for the same inputs, would give the same output.

**Determinism** For Determinism, since Python 3.7 onwards, the ordering is preserved in dictionaries. And at places where the return value from the routine used is non-deterministic, I ensure to sort the return value before using it, which enforces Determinism.

## Failure modes & edge cases

**Factory**
- Cycle in recipes: If multiple recipes combine to form a cycle, this is also taken part of the problem formulation itself. Since for each object we are considering its rate of consumption/production in each of the recipes, the steady state equation inherently takes care of this.
- Infeasible raw supplies or machine counts: As a part of the problem formulation, this would then report that the solution is infeasible, then perform a binary search as described above, using which we report the bottleneck hints.
- Degenerate or redundant recipes: These are ignored as a part of the problem formulation itself, since if machines are allocated here, that would be a waste of machines.

**Belts**

- The case of a disconnected graph is by default handled by the formulation of the problem, and the cut reachable from S would be reported the same as in other situations. 
- The current approach will require additional handling for floats. The case of floats can be simply handled by scaling up the values by 1e9 to ints and then scaling down by 1e9 back to floats. This is currently not incorporated since I have assumed ints based on the inputs.
