"""
ASCII Visualizer for Settlers of Catan Hex Boards
Displays the game board in the terminal with resources and numbers.
"""

from typing import Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from shared.hex_grid import HexGrid, HexCoordinate, HexTile
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings


class BoardVisualizer:
    """ASCII visualization of hex board."""
    
    # Resource abbreviations and colors (for terminals that support ANSI)
    RESOURCE_SYMBOLS = {
        'wood': 'WD',
        'brick': 'BR',
        'sheep': 'SH',
        'wheat': 'WH',
        'ore': 'OR',
        'desert': 'DS',
        'water': '~~'
    }
    
    # ANSI color codes
    COLORS = {
        'wood': '\033[32m',      # Green
        'brick': '\033[31m',     # Red
        'sheep': '\033[97m',     # White
        'wheat': '\033[93m',     # Yellow
        'ore': '\033[90m',       # Gray
        'desert': '\033[33m',    # Orange/Brown
        'water': '\033[94m',     # Blue
        'reset': '\033[0m'
    }
    
    def __init__(self, grid: HexGrid, use_color: bool = True):
        self.grid = grid
        self.use_color = use_color
    
    def visualize_simple(self):
        """Simple list-based visualization."""
        print("\n=== Board Layout ===\n")
        
        tiles = sorted(self.grid.get_all_tiles(), 
                      key=lambda t: (t.coordinate.r, t.coordinate.q))
        
        current_row = None
        for tile in tiles:
            if current_row != tile.coordinate.r:
                if current_row is not None:
                    print()
                current_row = tile.coordinate.r
                print(f"Row {current_row:2d}: ", end="")
            
            symbol = self.RESOURCE_SYMBOLS.get(tile.resource, '??')
            number = f"{tile.number_token:2d}" if tile.number_token else "  "
            
            if self.use_color:
                color = self.COLORS.get(tile.resource, '')
                reset = self.COLORS['reset']
                print(f"{color}[{symbol} {number}]{reset} ", end="")
            else:
                print(f"[{symbol} {number}] ", end="")
        
        print("\n")
    
    def visualize_hex_shape(self):
        """
        Visualize board in hexagonal shape (works best for hexagonal layouts).
        More visually appealing but requires more space.
        """
        print("\n=== Hexagonal Board Layout ===\n")
        
        # Get bounds
        min_q, max_q, min_r, max_r = self.grid.get_bounds()
        
        # Print legend
        self._print_legend()
        print()
        
        # Print each row
        for r in range(min_r, max_r + 1):
            # Calculate offset for hexagonal display
            # Rows closer to 0 should be more indented
            offset = abs(r - max_r)
            indent = " " * (offset * 6)
            print(indent, end="")
            
            # Collect all tiles in this row
            for q in range(min_q - 2, max_q + 3):
                coord = HexCoordinate(q, r)
                tile = self.grid.get_tile(coord)
                if tile:
                    self._print_tile(tile)
                    print(" ", end="")
            
            print()  # New line after each row
        
        print()
    
    def _print_tile(self, tile: HexTile):
        """Print a single tile with formatting."""
        symbol = self.RESOURCE_SYMBOLS.get(tile.resource, '??')
        number = f"{tile.number_token:2d}" if tile.number_token else "  "
        
        # Add robber marker
        robber = "R" if tile.has_robber else " "
        
        # Add port marker
        port = ""
        if tile.port:
            if 'generic' in tile.port:
                port = "3:1"
            else:
                port = "2:1"
        
        tile_str = f"[{symbol}{number}{robber}]"
        if port:
            tile_str += f"<{port}>"
        
        if self.use_color:
            color = self.COLORS.get(tile.resource, '')
            reset = self.COLORS['reset']
            print(f"{color}{tile_str}{reset}", end="")
        else:
            print(tile_str, end="")
    
    def _print_legend(self):
        """Print legend explaining symbols."""
        print("Legend:")
        print("  Format: [Resource Number Robber]<Port>")
        print("  Resources: WD=Wood, BR=Brick, SH=Sheep, WH=Wheat, OR=Ore, DS=Desert")
        print("  R = Robber present")
        print("  <3:1> = Generic port (3:1 trade)")
        print("  <2:1> = Resource-specific port (2:1 trade)")
    
    def print_detailed_list(self):
        """Print detailed list of all tiles."""
        print("\n=== Detailed Tile List ===\n")
        
        tiles = sorted(self.grid.get_all_tiles(), 
                      key=lambda t: (t.coordinate.r, t.coordinate.q))
        
        for tile in tiles:
            coord_str = f"({tile.coordinate.q:2d}, {tile.coordinate.r:2d})"
            resource_str = f"{tile.resource:8s}"
            number_str = f"#{tile.number_token:2d}" if tile.number_token else "    "
            prob = tile.get_production_probability()
            prob_str = f"{prob:.3f}" if prob > 0 else "-----"
            pips = tile.get_resource_value()
            pips_str = f"{pips}" if pips > 0 else "-"
            
            robber_str = "[ROBBER]" if tile.has_robber else ""
            port_str = f"<{tile.port}>" if tile.port else ""
            
            print(f"{coord_str} {resource_str} {number_str}  "
                  f"Prob: {prob_str}  Pips: {pips_str}  "
                  f"{robber_str}{port_str}")
    
    def print_statistics(self):
        """Print board statistics."""
        print("\n=== Board Statistics ===\n")
        
        # Count resources
        resource_counts = {}
        for tile in self.grid.get_land_tiles():
            resource_counts[tile.resource] = resource_counts.get(tile.resource, 0) + 1
        
        print("Resource Distribution:")
        for resource in sorted(resource_counts.keys()):
            count = resource_counts[resource]
            print(f"  {resource.capitalize():8s}: {count}")
        
        # Number probabilities
        print("\nNumber Token Distribution:")
        number_counts = {}
        for tile in self.grid.get_land_tiles():
            if tile.number_token:
                number_counts[tile.number_token] = number_counts.get(tile.number_token, 0) + 1
        
        for number in sorted(number_counts.keys()):
            count = number_counts[number]
            # Calculate probability
            prob = {2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
                   7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36}
            prob_val = prob.get(number, 0)
            print(f"  {number:2d}: {count} tiles (probability: {prob_val:.3f})")
        
        # Ports
        ports = [t.port for t in self.grid.get_all_tiles() if t.port]
        if ports:
            print(f"\nPorts: {len(ports)} total")
            port_counts = {}
            for port in ports:
                port_counts[port] = port_counts.get(port, 0) + 1
            for port_type, count in sorted(port_counts.items()):
                print(f"  {port_type}: {count}")


def main():
    """Interactive board viewer."""
    print("=== Settlers of Catan Board Visualizer ===\n")
    
    # Load settings
    settings = GameSettings()
    
    # Show available templates
    print("Available map templates:")
    templates = settings.list_map_templates()
    for i, template_name in enumerate(templates, 1):
        template = settings.get_map_template(template_name)
        print(f"{i}. {template['name']} ({template['total_hexes']} hexes)")
    
    # Get user choice
    choice = input("\nSelect template (1-{}) or Enter for standard: ".format(len(templates))).strip()
    
    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(templates):
            template_name = templates[idx]
        else:
            template_name = 'standard_3_4_player'
    else:
        template_name = 'standard_3_4_player'
    
    # Generate map
    print(f"\nGenerating {template_name}...")
    generator = MapGenerator(settings)
    grid = generator.generate_map(template_name, randomize=True)
    
    # Show statistics
    generator.print_map_summary()
    
    # Visualize
    visualizer = BoardVisualizer(grid, use_color=True)
    
    while True:
        print("\n" + "="*60)
        print("Visualization Options:")
        print("1. Simple list view")
        print("2. Hexagonal shape view")
        print("3. Detailed tile list")
        print("4. Statistics only")
        print("5. Generate new map (same template)")
        print("6. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            visualizer.visualize_simple()
        elif choice == '2':
            visualizer.visualize_hex_shape()
        elif choice == '3':
            visualizer.print_detailed_list()
        elif choice == '4':
            visualizer.print_statistics()
        elif choice == '5':
            print(f"\nGenerating new {template_name}...")
            generator = MapGenerator(settings)
            grid = generator.generate_map(template_name, randomize=True)
            generator.print_map_summary()
            visualizer = BoardVisualizer(grid, use_color=True)
        elif choice == '6':
            print("Exiting.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
