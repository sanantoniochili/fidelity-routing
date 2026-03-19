# Fidelity-Based Quantum Routing Project

## Overview
This project implements quantum internet routing algorithms that optimize path selection based on **entanglement fidelity** and edge **capacity constraints** in quantum networks. The framework determines reliable routes between source and destination nodes while maintaining minimum fidelity thresholds required for quantum communication.

## Project Goals
- Develop quantum routing protocols that account for entanglement fidelity degradation
- Implement entanglement purification strategies to improve fidelity on network edges
- Find optimal paths through quantum networks considering fidelity, capacity, and success probability
- Support both theoretical (Paper) and implemented (GitHub) models
- Verify results against US Backbone topology (39 nodes, 121 edges)

## Key Concepts

### Quantum Entanglement Fidelity
- Represents the quality of entangled pairs between neighboring nodes
- Ranges from 0 to 1 (1 = perfect fidelity)
- Degrades over distance and storage time
- Can be improved through purification protocols

### Entanglement Purification
- A quantum protocol that consumes two imperfect entangled pairs to produce one higher-fidelity pair
- Formula: `F_purified = (F1 × F2) / (F1 × F2 + (1-F1) × (1-F2))`
- Limited by edge capacity (number of available entangled pairs)
- Improves overall network reliability

### Edge Capacity
- Number of entangled pairs available on each link
- Constrains how many purification iterations can be performed
- Randomly initialized between 5-10 in current implementation

## Project Structure

### Core Modules

#### `graph_class.py`
- **Graph Class**: Represents the quantum network topology
- **Attributes**:
  - `V`: Dictionary of vertices and their neighbors
  - `capacities`: Dict mapping edges to available pair capacity
  - `fidelities`: Dict mapping edges to entanglement fidelity values
- **Key Methods**:
  - `get_edges()`: Extract all edges from adjacency list
  - `BFS()`: Breadth-first search to find minimum hop count from source to all nodes

#### `quantum.py`
- `get_purification_fidelity(x1, x2)`: Calculates fidelity of a purified entangled pair
- `get_purification_cost(f1, f2, c, debug)`: Simulates purification process and tracks fidelity improvements
- `delete_edges(G, F_min, debug)`: Removes edges that cannot meet minimum fidelity threshold after purification
- Utility for formatting terminal output

#### `paths.py`
- `k_shortest_paths(G, source, target, min_cost)`: Finds all shortest paths of equal length
- Uses Yen's algorithm (via NetworkX) for path enumeration
- Filters paths by hop count

#### `q-path_v1.py`
- Main execution script
- **Workflow**:
  1. Initialize network topology from predefined neighbors list
  2. Randomly assign capacities and fidelities to edges
  3. Simulate entanglement purification on each edge
  4. Remove edges failing minimum fidelity threshold
  5. Perform BFS to determine minimum hop count to destination
- Supports multiple network topologies (simple 2-repeater and 3-repeater configurations)

#### `q-path_v2.py`
- Alternative/extended version (implementation details pending review)

## Network Topologies

### Simple Topology (S-D with 2 Repeaters)
```
Source ←→ Repeater1 ←→ Destination
  ↓    ↘    ↓    ↙    ↓
     Repeater2

### US Backbone Network (Ref [39])
A 39-node network with 121 directed edges representing the core US fiber backbone. Used for large-scale verification in `verify_fig6.py`.
```

### Complex Topology (S-D with 3 Repeaters)
```
Source ←→ Repeater1 ←→ Repeater2 ←→ Destination
  ↓      ↘    ↓    ↙      ↓
     Repeater3  ←→  ────────────
```

## Algorithm Workflow

1. **Graph Initialization**: Set up network topology with quantum repeaters
2. **Resource Assignment**: Randomly initialize edge capacities (5-10 pairs) and fidelities (0.5-1.0)
3. **Purification & Validation**: 
   - For each edge, calculate maximum achievable fidelity through purification
   - Compare against minimum fidelity threshold (0.8)
   - Remove edges that fail to meet threshold
4. **Path Finding**: Compute shortest path(s) from source to destination
5. **Output**: Display graph state at each stage and fidelity improvements

## Parameters
- **min_fidelity**: 0.8 (minimum acceptable fidelity threshold)
- **capacity range**: [5, 10] entangled pairs per edge
- **initial fidelity range**: [0.5, 1.0] per edge
- **random seed**: Fixed at 2 for reproducibility

## Output Information
The scripts print:
- Initial edge capacities and fidelities
- Purification progress for each edge (fidelity improvements at each iteration)
- Final achievable fidelity after purification
- Edges removed due to insufficient fidelity
- Updated graph topology after filtering
- Minimum hop count to destination

## Use Cases
- Quantum key distribution (QKD) network routing
- Quantum internet alliance (QIA) network optimization
- Investigation of trade-offs between path length, fidelity, and success probability
- Simulation of entanglement purification strategies in large networks (US Backbone)
- Comparison against official paper implementations (DEJMPS vs BBPSSW)

## Dependencies
- `numpy`: Numerical computations and random number generation
- `networkx`: Graph algorithms and path finding
- Python standard library: `os`, `math`

## Future Enhancements
- Dynamic routing based on real-time fidelity measurements
- Multi-path routing with load balancing
- Integration with quantum repeater scheduling
- Performance metrics (throughput, latency, reliability)
- Visualization of network topology and path selection
