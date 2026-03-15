# Quantum Routing Algorithms: Q-LEAP and Q-PATH

This document provides a detailed technical description of the **Q-LEAP** and **Q-PATH** algorithms used for fidelity-guaranteed entanglement routing in quantum networks.

---

## 1. Key Formulas and Metrics

Before describing the algorithms, we define the core physical models:

### A. Entanglement Purification (BBPSSW Model)
When consuming two entangled pairs with fidelities $F_1$ and $F_2$, the fidelity of the resulting pair $F_{new}$ is:
$$F_{new} = \frac{F_1 F_2}{F_1 F_2 + (1-F_1)(1-F_2)}$$

### B. End-to-End Fidelity (Swapping Formula)
For a path $P$ consisting of $L$ hops with purified fidelities $\{F_1, F_2, \dots, F_L\}$, the end-to-end fidelity $F_{e2e}$ is:
$$F_{e2e} = \frac{1}{4} + \frac{3}{4} \prod_{i=1}^L \frac{4F_i - 1}{3}$$

---

## 2. Q-LEAP: Multiplicative-Metric Routing (Low-Complexity)

**Q-LEAP** is a low-complexity routing algorithm that treats entanglement fidelity as a multiplicative metric to find the path with the highest potential quality.

### Algorithm Steps:
1.  **Metric Computation**:
    *   For each edge $(u,v)$ with fidelity $F$, assign a weight: $w(u,v) = -\log_{10}\left(\frac{4F-1}{3}\right)$.
    *   *Note: This transforms the maximize-product problem into a minimize-sum problem.*
2.  **Best Quality Path Search**:
    *   Run **Dijkstra's Algorithm** using the weights $w(u,v)$ to find the path $P$ from $S$ to $D$ that minimizes the sum of weights.
    *   This path $P$ has the maximum "intrinsic" end-to-end fidelity $F_{intrinsic}$.
3.  **Purification Requirement**:
    *   Calculate the average required fidelity per hop: $F_{avg} = \sqrt[L]{\frac{4F_{th}-1}{3} \cdot \frac{4}{3} \dots}$ (derived from the swapping formula).
4.  **Feasibility Check**:
    *   For each hop in $P$, calculate the number of pairs needed to reach $F_{avg}$ using the BBPSSW purification formula.
    *   If any hop requires more pairs than its physical capacity $C$, the path is rejected.
5.  **Output**: Return path $P$ and success/failure status.

---

## 3. Q-PATH: Iterative Routing with Budget Optimization

**Q-PATH** finds the optimal path and purification allocation that minimizes the total entangled pair cost while satisfying a global fidelity threshold $F_{th}$.

### Algorithm Steps:
1.  **Input**: Network graph $G$, source $S$, destination $D$, and threshold $F_{th}$.
2.  **Bound Initialization**:
    *   Calculate the minimum hop count $H_{min}$ using BFS/Dijkstra.
    *   Define $C_{max}$ as the sum of all edge capacities in the network.
3.  **Iterative Search**:
    *   For each total pair budget $B$ from $H_{min}$ to $C_{max}$:
        1. Find all candidate paths $P$ where the hop count $L$ satisfies $L \leq B$.
        2. For each candidate path $P$:
           *   Calculate the purification budget: $Budget = B - L$.
           *   **Optimization Sub-problem**: Find a distribution of $Budget$ across the $L$ edges such that the resulting $F_{e2e} \geq F_{th}$.
           *   *Note: This can be solved via Dynamic Programming (DP) or exhaustive search for small budgets.*
           *   If a valid distribution is found:
             *   **Return** $P$, the edge-wise allocations, and total cost $B$.
4.  **Termination**: If no budget $B$ up to $C_{max}$ yields a solution, return **NO PATH FOUND**.

### DP Sub-problem (Optimal Budget Allocation):
To maximize $F_{e2e}$ for a path of length $L$ with total budget $B$:
*   **State**: $DP[i][b]$ = Maximum fidelity achievable for the first $i$ hops using a total of $b$ pairs.
*   **Transition**: $DP[i][b] = \max_{j \in [1, b-(i-1)]} \{ \text{Combine}(DP[i-1][b-j], \text{Purify}(F_{i}, j)) \}$
*   **Goal**: Find smallest $b$ such that $DP[L][b] \geq F_{th}$.

---

## 4. Q-LEAP (Low-Complexity Alternative)

While not requested specifically, the project includes **Q-LEAP** which simplifies the search:
1.  **Metric**: Use Dijkstra with link weight $w = -\log(\frac{4F-1}{3})$ to find the path with the best intrinsic quality.
2.  **Allocation**: Apply a uniform target fidelity per hop $F_{avg} = \sqrt[L]{(4F_{th}-1)/3 \dots}$ (or similar derived average) and check if the physical capacities allow it.
