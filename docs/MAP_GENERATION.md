# Board and Map Generation System

## Overview
The board/map generation system creates balanced Settlers of Catan game boards using hexagonal tile grids. It supports multiple board sizes, automatic balancing of high-value tiles, and port placement.

## Components

### 1. Hexagonal Coordinate System (`shared/hex_grid.py`)

#### HexCoordinate Class
Implements axial coordinate system for hexagonal tiles using "pointy-top" orientation.

**Key Features:**
- Axial coordinates (q, r) with implied s coordinate
- Distance calculation between hexes
- Neighbor finding (6 adjacent hexes)
- Pixel conversion for rendering
- Serialization support

**Example Usage:**
```python
from shared.hex_grid import HexCoordinate

# Create coordinates
center = HexCoordinate(0, 0)
neighbor = HexCoordinate(1, 0)

# Calculate distance
distance = center.distance(neighbor)  # Returns 1

# Get all neighbors
neighbors = center.get_neighbors()  # Returns list of 6 HexCoordinates

# Convert to pixel position (for rendering)
x, y = center.to_pixel(hex_size=50)
```

#### HexTile Class
Represents a single hex tile with resource type, number token, and game state.

**Attributes:**
- `coordinate`: HexCoordinate position
- `resource`: Resource type (wood, brick, sheep, wheat, ore, desert, water)
- `number_token`: Number 2-12 (None for desert/water)
- `has_robber`: Boolean indicating robber presence
- `port`: Port type if on edge (None otherwise)

**Methods:**
- `is_land()`: Check if tile produces resources
- `is_productive()`: Check if currently producing (not blocked by robber)
- `get_production_probability()`: Get probability of producing (based on dice odds)
- `get_resource_value()`: Get pip value for balancing

**Example Usage:**
```python
from shared.hex_grid import HexTile, HexCoordinate

# Create a tile
coord = HexCoordinate(0, 0)
tile = HexTile(coord, 'wheat', number_token=6)

# Check properties
print(tile.is_productive())  # True
print(tile.get_production_probability())  # 0.139 (5/36 chance)
print(tile.get_resource_value())  # 5 pips
```

#### HexGrid Class
Manages a collection of hex tiles forming the game board.

**Key Methods:**
- `add_tile(tile)`: Add tile to grid
- `get_tile(coordinate)`: Get tile at position
- `get_all_tiles()`: Get all tiles
- `get_land_tiles()`: Get only land tiles
- `get_neighbors(coordinate)`: Get neighboring tiles
- `generate_hexagonal_ring(rings)`: Generate hex coordinates for circular board
- `generate_rectangular_grid(width, height)`: Generate rectangular layout
- `get_bounds()`: Get min/max coordinates

**Example Usage:**
```python
from shared.hex_grid import HexGrid, HexTile, HexCoordinate

# Create grid
grid = HexGrid()

# Generate standard 19-hex board (2 rings)
coordinates = grid.generate_hexagonal_ring(2)
print(f"Generated {len(coordinates)} hex positions")

# Add tiles
for coord in coordinates:
    tile = HexTile(coord, 'wood', 6)
    grid.add_tile(tile)

# Query grid
center_tile = grid.get_tile(HexCoordinate(0, 0))
neighbors = grid.get_neighbors(center_tile.coordinate)
```

### 2. Map Generator (`shared/map_generator.py`)

#### MapGenerator Class
Creates complete game boards with balanced resource distribution.

**Key Features:**
- Template-based generation
- Random resource placement
- Automatic number balancing (prevents adjacent 6s and 8s)
- Port placement
- Statistics and validation

**Methods:**
- `generate_map(template_name, randomize)`: Generate complete board
- `get_map_statistics()`: Get board statistics
- `print_map_summary()`: Print human-readable summary
- `export_map()`: Export for network transmission
- `import_map(data)`: Import previously generated map

**Example Usage:**
```python
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings

# Initialize with settings
settings = GameSettings()
generator = MapGenerator(settings)

# Generate standard map
grid = generator.generate_map('standard_3_4_player', randomize=True)

# Get statistics
stats = generator.get_map_statistics()
print(f"Total tiles: {stats['total_tiles']}")
print(f"Land tiles: {stats['land_tiles']}")

# Print summary
generator.print_map_summary()
```

### 3. Board Viewer (`tools/board_viewer.py`)

Interactive terminal tool for visualizing generated maps.

**Features:**
- Color-coded resource display
- Multiple visualization modes
- Detailed tile information
- Statistics display
- Generate new maps on demand

**Usage:**
```bash
python tools/board_viewer.py
```

**Visualization Modes:**
1. **Simple List View**: Organized by row with colors
2. **Hexagonal Shape View**: Spatial hex layout
3. **Detailed Tile List**: Complete tile information with probabilities
4. **Statistics Only**: Resource and number distribution

## Board Generation Process

### Step 1: Template Selection
```python
settings = GameSettings()
settings.set_map_template('standard_3_4_player')
template = settings.get_current_map_template()
```

Templates define:
- Board size (number of hexes)
- Layout shape (hexagonal or rectangular)
- Resource distribution (how many of each resource)
- Number token distribution
- Port configuration

### Step 2: Coordinate Generation
```python
if template['board_layout'] == 'hexagonal':
    coordinates = grid.generate_hexagonal_ring(template['hex_rings'])
else:
    coordinates = grid.generate_rectangular_grid(width, height)
```

Creates the spatial structure of the board.

### Step 3: Resource Assignment
```python
resources = ['wood', 'wood', 'brick', 'sheep', ...]  # From template
random.shuffle(resources)  # If randomize=True

for coord, resource in zip(coordinates, resources):
    # Assign resource to tile
```

### Step 4: Number Token Assignment
```python
numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, ...]  # From template
random.shuffle(numbers)  # If randomize=True

# Assign numbers, skipping desert tiles
```

### Step 5: Board Balancing
```python
# Automatically swap tiles to prevent adjacent 6s and 8s
generator._balance_high_numbers()
```

The balancing algorithm:
1. Finds tiles with 6 or 8 adjacent to another 6 or 8
2. Swaps one tile's number with a non-adjacent tile
3. Repeats until no violations or max attempts reached

### Step 6: Port Placement
```python
# Find edge tiles
edge_tiles = generator._find_edge_tiles()

# Place ports on edges
ports = ['generic_3_1', 'wood_2_1', ...]
# Assign to edge tiles
```

## Map Templates

### Standard (3-4 Players)
- **Hexes**: 19 (2 rings)
- **Resources**: 4 wood, 3 brick, 4 sheep, 4 wheat, 3 ore, 1 desert
- **Numbers**: Full 2d6 distribution
- **Ports**: 9 total (4 generic, 5 specific)

### Extended (5-6 Players)
- **Hexes**: 30 (3 rings)
- **Resources**: Proportionally increased
- **Numbers**: Extended distribution with duplicates
- **Ports**: 11 total

### Large (7-8 Players)
- **Hexes**: 37 (4 rings)
- **Resources**: Even more resources
- **Numbers**: Full extended distribution
- **Ports**: 16 total

### Small (2 Players)
- **Hexes**: 13 (2 rings, reduced)
- **Resources**: Fewer of each type
- **Numbers**: Reduced distribution
- **Ports**: 6 total

### Custom Rectangular
- **Shape**: Non-hexagonal layout
- **Size**: Customizable width × height
- **Resources**: Standard distribution adapted to size

## Balancing Algorithms

### Number Token Balancing
Prevents overpowered positions by ensuring:
- No adjacent 6 and 8 tiles
- Attempts to distribute high-value numbers evenly
- Maximum attempts: 100 swaps

### Resource Distribution
Standard distribution follows classic Catan ratios:
- Desert: Low (1-3 tiles)
- Brick/Ore: Medium (3-7 tiles)
- Wood/Sheep/Wheat: Medium-High (4-7 tiles)

### Pip Value Calculation
Each number has a pip value representing probability:
```
2, 12: 1 pip  (1/36 chance)
3, 11: 2 pips (2/36 chance)
4, 10: 3 pips (3/36 chance)
5, 9:  4 pips (4/36 chance)
6, 8:  5 pips (5/36 chance)
```

Total pip value helps assess board balance.

## Serialization and Network Support

### Export Map
```python
exported = generator.export_map()
# Returns: {
#   'grid': {...},
#   'ports': [...],
#   'statistics': {...}
# }

import json
json_data = json.dumps(exported)
```

### Import Map
```python
import json
data = json.loads(json_data)
generator = MapGenerator.import_map(data)
```

This allows:
- Saving maps to files
- Transmitting maps over network
- Sharing specific board layouts
- Replaying games with same board

## Coordinate System Details

### Axial Coordinates
- **q**: Column (increases right)
- **r**: Row (increases down-left)
- **s**: -q - r (derived, ensures q + r + s = 0)

### Directions
```
     (-1,-1)   (0,-1)
        \      /
(-1,0) -- (0,0) -- (1,0)
        /      \
     (0,1)    (1,1)
```

### Distance Formula
```python
distance = (abs(q1 - q2) + abs(r1 - r2) + abs(s1 - s2)) // 2
```

### Pixel Conversion
For rendering hexagons:
```python
x = hex_size * (3/2 * q)
y = hex_size * (sqrt(3)/2 * q + sqrt(3) * r)
```

## Usage Examples

### Generate and View a Map
```python
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings
from tools.board_viewer import BoardVisualizer

# Generate map
settings = GameSettings()
generator = MapGenerator(settings)
grid = generator.generate_map('standard_3_4_player', randomize=True)

# Visualize
visualizer = BoardVisualizer(grid)
visualizer.visualize_simple()
visualizer.print_statistics()
```

### Create Custom Template
```python
# Add to map_templates.json
{
  "my_custom_map": {
    "name": "My Custom Map",
    "description": "A custom configuration",
    "recommended_players": [4],
    "hex_rings": 2,
    "total_hexes": 19,
    "hex_distribution": {
      "wood": 5,
      "brick": 5,
      "sheep": 3,
      "wheat": 3,
      "ore": 2,
      "desert": 1
    },
    ...
  }
}

# Use it
settings.set_map_template('my_custom_map')
```

### Check Board Balance
```python
stats = generator.get_map_statistics()

if stats['high_number_violations'] == 0:
    print("✓ Well balanced board!")
else:
    print(f"⚠ {stats['high_number_violations']} adjacent 6/8 pairs")

print(f"Total pip value: {stats['total_pip_value']}")
```

### Access Individual Tiles
```python
# Get center tile
center = grid.get_tile(HexCoordinate(0, 0))
print(f"Center: {center.resource} #{center.number_token}")

# Get neighbors
neighbors = grid.get_neighbors(center.coordinate)
for neighbor in neighbors:
    prob = neighbor.get_production_probability()
    print(f"  {neighbor.resource} #{neighbor.number_token} ({prob:.3f})")
```

## Integration with Other Systems

### With Game Settings
```python
# Settings determine board generation
settings.set_map_template('large_7_8_player')
settings.set_victory_points_to_win(15)  # Match VP to board size

generator = MapGenerator(settings)
grid = generator.generate_map()
```

### With Development Cards
```python
# Map affects resource availability
# More resource tiles = more card purchases possible
stats = generator.get_map_statistics()
resource_abundance = stats['land_tiles'] - stats['resource_distribution'].get('desert', 0)
```

### Network Protocol (Future)
```python
# Server generates and sends map
server_generator = MapGenerator()
grid = server_generator.generate_map('standard_3_4_player')
map_data = server_generator.export_map()

# Send to clients...
# Clients reconstruct identical board
client_generator = MapGenerator.import_map(map_data)
```

## Testing and Validation

### Run Tests
```bash
# Test hex grid
python shared/hex_grid.py

# Test map generator
python shared/map_generator.py

# Interactive viewer
python tools/board_viewer.py
```

### Validate Generated Maps
```python
stats = generator.get_map_statistics()

assert stats['total_tiles'] == 19  # For standard map
assert stats['high_number_violations'] == 0  # Should be balanced
assert sum(stats['resource_distribution'].values()) == stats['land_tiles']
```

## Best Practices

1. **Always balance high numbers** - Use randomize=True for fair boards
2. **Match map size to player count** - Use appropriate templates
3. **Test custom templates** - Verify resource/number counts match
4. **Save interesting boards** - Use export_map() for reproducibility
5. **Visualize before use** - Check balance with board_viewer

## Troubleshooting

**Board not balanced after generation?**
- Increase max_attempts in `_balance_high_numbers()`
- Check template has appropriate number distribution
- Some configurations may be impossible to perfectly balance

**Ports not appearing?**
- Ensure template has port configuration
- Check edge tiles exist (board can't be all-interior)
- Verify port types match expected format

**Wrong number of tiles?**
- Check template's total_hexes matches resource distribution sum
- Verify hex_rings matches expected tile count (1+6r for r rings)
- For rectangular: verify width × height matches template

## Future Enhancements

Potential additions:
- Water tiles for Seafarers expansion
- Island generation
- Custom port positioning
- Terrain types (mountains, forests)
- Special tiles (gold hexes, etc.)
- Fairness scoring algorithm
- Multiple robber placement rules

## Performance Notes

- Board generation: O(n) where n = number of tiles
- Balancing: O(attempts × tiles) typically 100-1000 operations
- Serialization: O(n) JSON encoding
- Memory: ~100 bytes per tile

All operations are very fast even for large boards (37+ hexes).
