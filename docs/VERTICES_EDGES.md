# Vertex and Edge System

## Overview
The vertex and edge system defines where buildings can be placed on the hexagonal board. Vertices (corners) are where settlements and cities go, while edges (sides) are where roads go.

## Visual Guide

### Hexagon Structure
```
For a flat-top hexagon, vertices and edges are numbered 0-5:

         Vertex 0
           /  \
    Edge 5/    \Edge 0
         /      \
  Vertex5       Vertex1
        |        |
  Edge 4|        |Edge 1
        |        |
  Vertex4       Vertex2
         \      /
    Edge 3\    /Edge 2
           \  /
         Vertex 3
```

### Example Board Layout
```
    Hex(-1,-1)    Hex(0,-1)    Hex(1,-1)
         *           *           *
        / \         / \         / \
       *---*-------*---*-------*---*
        \ /         \ /         \ /
         *           *           *
    Hex(-1,0)     Hex(0,0)     Hex(1,0)
         *           *           *
        / \         / \         / \
       *---*-------*---*-------*---*
        \ /         \ /         \ /
         *           *           *
    Hex(-1,1)     Hex(0,1)     Hex(1,1)

* = Vertices (settlements/cities)
--- = Edges (roads)
```

## Components

### 1. Vertex Class (`shared/board_topology.py`)

#### What is a Vertex?
A vertex is a corner where three hexagons meet. This is where settlements and cities are placed.

**Identification:**
```python
vertex = Vertex(HexCoordinate(0, 0), direction=0)
# hex_coord: Which hex this vertex belongs to
# direction: 0-5, which corner of that hex
```

**Key Methods:**
```python
# Get the 3 hexes that touch this vertex
adjacent_hexes = vertex.get_adjacent_hexes()

# Get the 3 vertices connected by edges (where you could build roads to)
adjacent_vertices = vertex.get_adjacent_vertices()

# Example:
vertex = Vertex(HexCoordinate(0, 0), 0)
hexes = vertex.get_adjacent_hexes()
# Returns: [Hex(0,0), Hex(0,-1), Hex(1,-1)]
```

### 2. Edge Class (`shared/board_topology.py`)

#### What is an Edge?
An edge is a side of a hexagon, where two hexes meet. This is where roads are placed.

**Identification:**
```python
edge = Edge(HexCoordinate(0, 0), direction=1)
# hex_coord: Which hex this edge belongs to
# direction: 0-5, which side of that hex
```

**Key Methods:**
```python
# Get the 2 hexes on either side of this edge
adjacent_hexes = edge.get_adjacent_hexes()

# Get the 2 vertices at the ends of this edge
v1, v2 = edge.get_vertices()

# Get the 4 edges adjacent to this one
adjacent_edges = edge.get_adjacent_edges()
```

### 3. BoardTopology Class

#### What is BoardTopology?
BoardTopology manages all vertices and edges on a game board. It tracks which buildings are where and validates placement rules.

**Creating:**
```python
from shared.board_topology import BoardTopology
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings

# Generate a board
settings = GameSettings()
generator = MapGenerator(settings)
grid = generator.generate_map('standard_3_4_player')

# Create topology
topology = BoardTopology(grid)

print(f"Vertices: {len(topology.vertices)}")  # ~114 for standard board
print(f"Edges: {len(topology.edges)}")        # ~114 for standard board
```

## Building Placement Rules

### Settlement Placement

**Rules:**
1. Vertex must be valid and empty
2. **Distance Rule**: No settlements on adjacent vertices (minimum 2 edges apart)
3. Must be connected to your road network (except during setup)

**Code:**
```python
# Check if can place
if topology.can_place_settlement(vertex, player_id, is_setup=False):
    # Place it
    topology.place_settlement(vertex, player_id, is_setup=False)
    print("Settlement placed!")
```

**During Setup:**
```python
# First settlements don't need road connection
topology.place_settlement(vertex, player_id, is_setup=True)
```

### City Placement (Upgrade)

**Rules:**
1. Must have your settlement at this vertex

**Code:**
```python
# Upgrade settlement to city
if topology.can_place_city(vertex, player_id):
    topology.place_city(vertex, player_id)
    print("Upgraded to city!")
```

### Road Placement

**Rules:**
1. Edge must be valid and empty
2. Must connect to your existing road or settlement/city (except setup)
3. Cannot connect through opponent's settlements

**Code:**
```python
# Check if can place
if topology.can_place_road(edge, player_id, is_setup=False):
    # Place it
    topology.place_road(edge, player_id, is_setup=False)
    print("Road placed!")
```

**During Setup:**
```python
# Setup roads just need to connect to the settlement you just placed
topology.place_road(edge, player_id, is_setup=True)
```

## Validation Examples

### Example 1: Valid Settlement Placement
```python
# Player has a road network
topology.place_road(Edge(HexCoordinate(0, 0), 0), player_id=1)

# Adjacent vertex is connected to the road
vertex = Vertex(HexCoordinate(0, 0), 0)
if topology.can_place_settlement(vertex, player_id=1):
    topology.place_settlement(vertex, player_id=1)
    # ✓ Valid: Connected to road network
```

### Example 2: Invalid - Distance Rule
```python
# Place first settlement
v1 = Vertex(HexCoordinate(0, 0), 0)
topology.place_settlement(v1, player_id=1, is_setup=True)

# Try to place adjacent settlement
v2 = Vertex(HexCoordinate(0, 0), 1)  # Adjacent to v1
if not topology.can_place_settlement(v2, player_id=2, is_setup=True):
    print("✗ Invalid: Too close (distance rule)")
    # Settlements must be at least 2 edges apart
```

### Example 3: Road Connectivity
```python
# Place settlement
v1 = Vertex(HexCoordinate(0, 0), 0)
topology.place_settlement(v1, player_id=1, is_setup=True)

# Place road from settlement
e1 = Edge(HexCoordinate(0, 0), 0)
topology.place_road(e1, player_id=1, is_setup=True)

# Place another road connected to first road
e2 = Edge(HexCoordinate(0, 0), 1)
if topology.can_place_road(e2, player_id=1):
    topology.place_road(e2, player_id=1)
    # ✓ Valid: Connected to existing road
```

## Longest Road Calculation

The system automatically calculates the longest continuous road for each player.

```python
# Get longest road length
length = topology.get_longest_road(player_id=1)
print(f"Longest road: {length} segments")

# Minimum for "Longest Road" achievement: 5 segments
if length >= 5:
    print("Eligible for Longest Road bonus!")
```

**How it works:**
- Uses depth-first search (DFS) to find longest path
- Roads connected through opponent's settlements don't count
- Handles branching road networks correctly

## Resource Production

Get which resources a settlement/city would produce:

```python
vertex = Vertex(HexCoordinate(0, 0), 0)
resources = topology.get_vertex_resources(vertex)
print(f"Resources: {resources}")
# Example: ['wood', 'brick', 'sheep']

# Settlements get 1 of each resource when those hexes produce
# Cities get 2 of each resource when those hexes produce
```

## Integration with Game Logic

### With GameState
```python
from shared.game_state import GameState
from shared.board_topology import BoardTopology

game = GameState()
game.setup_game(["Alice", "Bob"])

# Create topology for the board
topology = BoardTopology(game.grid)

# Store in game state
game.topology = topology
```

### Building During Game
```python
# Player wants to build settlement
player = game.get_current_player()
vertex = Vertex(HexCoordinate(1, 0), 2)

# Check cost
cost = game.settings.get_building_cost('settlement')
if not player.has_resources(cost):
    print("Not enough resources!")
elif not topology.can_place_settlement(vertex, player.player_id):
    print("Cannot place here!")
else:
    # Pay and build
    player.pay_resources(cost)
    topology.place_settlement(vertex, player.player_id)
    player.build_settlement(vertex)
    print("Settlement built!")
```

### Resource Distribution
```python
# When dice are rolled
dice_total = 6

# Find all tiles with that number
for tile in game.grid.get_land_tiles():
    if tile.number_token == dice_total and not tile.has_robber:
        resource = tile.resource
        
        # Check all vertices of this hex
        for direction in range(6):
            vertex = Vertex(tile.coordinate, direction)
            
            # Settlement gets 1 resource
            if vertex in topology.settlements:
                player_id = topology.settlements[vertex]
                player = game.players[player_id]
                player.add_resource(resource, 1)
            
            # City gets 2 resources
            elif vertex in topology.cities:
                player_id = topology.cities[vertex]
                player = game.players[player_id]
                player.add_resource(resource, 2)
```

## Coordinate Conversion for Rendering

To draw buildings on the visual board:

```python
from client.renderer import HexRenderer

renderer = HexRenderer(hex_size=60)

# Get pixel position for hex
hex_x, hex_y = renderer.hex_to_pixel(vertex.hex_coord)

# Calculate vertex offset based on direction
# Each vertex is at a specific angle around the hex
angles = [30, 90, 150, 210, 270, 330]  # degrees
angle = angles[vertex.direction]

import math
radius = renderer.hex_size
vertex_x = hex_x + radius * math.cos(math.radians(angle))
vertex_y = hex_y + radius * math.sin(math.radians(angle))

# Draw settlement at (vertex_x, vertex_y)
```

## Serialization

Save and load building positions:

```python
# Save
data = topology.to_dict()
import json
with open('board_state.json', 'w') as f:
    json.dump(data, f)

# Data format:
{
  "settlements": {
    "0,0,0": 1,  # "q,r,direction": player_id
    "1,1,2": 2
  },
  "cities": {
    "0,0,0": 1
  },
  "roads": {
    "0,0,0": 1,
    "0,0,1": 1
  }
}
```

## Debugging and Visualization

### Print All Valid Positions
```python
print("Valid Vertices:")
for vertex in topology.get_all_vertices():
    hexes = vertex.get_adjacent_hexes()
    resources = topology.get_vertex_resources(vertex)
    print(f"{vertex}: {resources}")
```

### Check Specific Position
```python
vertex = Vertex(HexCoordinate(0, 0), 0)
print(f"Valid: {topology.is_valid_vertex(vertex)}")
print(f"Occupied: {vertex in topology.settlements or vertex in topology.cities}")
print(f"Can place: {topology.can_place_settlement(vertex, player_id=1)}")
```

### Find Building Positions
```python
# Find all player 1's settlements
player_settlements = [v for v, pid in topology.settlements.items() if pid == 1]
print(f"Player 1 settlements: {len(player_settlements)}")

# Find all player 1's roads
player_roads = [e for e, pid in topology.roads.items() if pid == 1]
print(f"Player 1 roads: {len(player_roads)}")
```

## Performance

- **Topology Generation**: O(n) where n = number of hexes
  - Standard board (19 hexes): ~114 vertices, ~114 edges
  - Large board (37 hexes): ~216 vertices, ~216 edges

- **Placement Validation**: O(1) for most checks
  - Distance rule: O(3) - check 3 adjacent vertices
  - Road connectivity: O(k) where k = number of adjacent edges (~4)

- **Longest Road**: O(V + E) where V = vertices, E = edges
  - Uses DFS with memoization
  - Typically completes in < 1ms even for large boards

## Common Patterns

### Setup Phase - Initial Placement
```python
# Round 1: Each player places settlement + road (order: 1,2,3,4)
# Round 2: Each player places settlement + road (reverse: 4,3,2,1)

for round in [1, 2]:
    players = game.players if round == 1 else reversed(game.players)
    
    for player in players:
        # Player chooses vertex
        vertex = get_player_choice_vertex()
        
        if topology.place_settlement(vertex, player.player_id, is_setup=True):
            player.build_settlement(vertex)
            
            # In round 2, give resources
            if round == 2:
                resources = topology.get_vertex_resources(vertex)
                for resource in resources:
                    player.add_resource(resource, 1)
            
            # Player chooses adjacent edge for road
            edge = get_player_choice_edge()
            
            if topology.place_road(edge, player.player_id, is_setup=True):
                player.build_road(edge)
```

### Finding Valid Settlement Positions
```python
def get_valid_settlement_positions(topology, player_id):
    """Get all vertices where player can legally place a settlement."""
    valid = []
    for vertex in topology.get_all_vertices():
        if topology.can_place_settlement(vertex, player_id):
            valid.append(vertex)
    return valid

# During player's turn
valid_positions = get_valid_settlement_positions(topology, player.player_id)
print(f"Can place settlement at {len(valid_positions)} positions")
```

### Finding Valid Road Positions
```python
def get_valid_road_positions(topology, player_id):
    """Get all edges where player can legally place a road."""
    valid = []
    for edge in topology.get_all_edges():
        if topology.can_place_road(edge, player_id):
            valid.append(edge)
    return valid
```

## Next Steps

With vertices and edges defined, we can now:
1. ✅ Validate building placement
2. ✅ Calculate longest road
3. ✅ Connect buildings to resource production
4. ⏳ Add visual building placement to the Pygame renderer
5. ⏳ Create interactive UI for clicking to place buildings
6. ⏳ Implement complete setup phase
7. ⏳ Full resource distribution logic

The topology system is complete and ready to be integrated with the visual renderer and game UI!
