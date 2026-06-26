"""
Map Generator for Settlers of Catan
Creates balanced game boards using hex grids and game settings.
"""

import random
from typing import List, Dict, Optional, Set
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from hex_grid import HexGrid, HexTile, HexCoordinate
from game_settings import GameSettings


class MapGenerator:
    """Generates Settlers of Catan game boards."""
    
    def __init__(self, settings: GameSettings = None):
        if settings is None:
            settings = GameSettings()
        
        self.settings = settings
        self.grid = HexGrid()
        self.ports_placed = []
    
    def generate_map(self, template_name: str = None, randomize: bool = True) -> HexGrid:
        """
        Generate a complete map based on a template.
        
        Args:
            template_name: Name of map template to use (None = use current setting)
            randomize: Whether to randomize resource and number placement
        
        Returns:
            HexGrid with all tiles, resources, and numbers placed
        """
        # Load template
        if template_name:
            self.settings.set_map_template(template_name)
        
        template = self.settings.get_current_map_template()
        if not template:
            # Use map_settings if no template selected
            template = {
                'board_layout': 'hexagonal',
                'hex_rings': 2,
                'total_hexes': 19,
                'hex_distribution': self.settings.settings['map_settings']['hex_distribution'],
                'number_tokens': self.settings.settings['map_settings']['number_token_distribution'],
                'ports': self.settings.settings['map_settings']['ports']
            }
        
        # Generate grid structure
        if template['board_layout'] == 'hexagonal':
            coordinates = self.grid.generate_hexagonal_ring(template.get('hex_rings', 2))
        else:  # rectangular
            width = template.get('board_width', 5)
            height = template.get('board_height', 4)
            coordinates = self.grid.generate_rectangular_grid(width, height)
        
        # Prepare resource and number lists
        resources = self._prepare_resources(template['hex_distribution'])
        numbers = template['number_tokens'].copy()
        
        # Shuffle if randomizing
        if randomize:
            random.shuffle(resources)
            random.shuffle(numbers)
        
        # Place tiles
        number_index = 0
        for i, coord in enumerate(coordinates):
            if i < len(resources):
                resource = resources[i]
                
                # Desert gets no number token
                if resource == 'desert':
                    tile = HexTile(coord, resource, None)
                else:
                    number = numbers[number_index] if number_index < len(numbers) else None
                    tile = HexTile(coord, resource, number)
                    number_index += 1
                
                self.grid.add_tile(tile)
        
        # Balance the board if requested
        if randomize and self.settings.settings.get('map_settings', {}).get('balanced_number_placement', True):
            self._balance_high_numbers()
        
        # Place ports
        self._place_ports(template['ports'])
        
        return self.grid
    
    def _prepare_resources(self, distribution: Dict[str, int]) -> List[str]:
        """Create a list of resources based on distribution counts."""
        resources = []
        for resource, count in distribution.items():
            resources.extend([resource] * count)
        return resources
    
    def _balance_high_numbers(self, max_attempts: int = 100):
        """
        Balance the board so high-probability numbers (6, 8) aren't adjacent.
        Also tries to avoid clusters of similar resources.
        """
        high_numbers = {6, 8}
        
        for attempt in range(max_attempts):
            violations = self._find_violations(high_numbers)
            
            if not violations:
                print(f"✓ Board balanced in {attempt + 1} attempts")
                return
            
            # Swap numbers to fix violations
            violation = random.choice(violations)
            self._swap_numbers(violation)
        
        print(f"⚠ Board partially balanced after {max_attempts} attempts")
    
    def _find_violations(self, high_numbers: Set[int]) -> List[HexTile]:
        """Find tiles with high numbers adjacent to other high numbers."""
        violations = []
        
        for tile in self.grid.get_land_tiles():
            if tile.number_token in high_numbers:
                neighbors = self.grid.get_neighbors(tile.coordinate)
                for neighbor in neighbors:
                    if neighbor.is_land() and neighbor.number_token in high_numbers:
                        violations.append(tile)
                        break
        
        return violations
    
    def _swap_numbers(self, tile: HexTile):
        """Swap the number token of a tile with a random non-adjacent tile."""
        # Get all land tiles that aren't neighbors
        neighbors = set(self.grid.get_neighbors(tile.coordinate))
        neighbor_coords = {n.coordinate for n in neighbors}
        
        valid_swaps = [
            t for t in self.grid.get_land_tiles()
            if t.coordinate not in neighbor_coords
            and t.coordinate != tile.coordinate
            and t.resource != 'desert'
            and t.number_token is not None
        ]
        
        if valid_swaps:
            swap_tile = random.choice(valid_swaps)
            tile.number_token, swap_tile.number_token = swap_tile.number_token, tile.number_token
    
    def _place_ports(self, port_config: Dict[str, int]):
        """
        Place ports around the edge of the board.
        Ports are placed on water tiles adjacent to land.
        """
        self.ports_placed = []
        
        # Find edge tiles (land tiles with water neighbors)
        edge_tiles = self._find_edge_tiles()
        
        if not edge_tiles:
            print("⚠ No edge tiles found for port placement")
            return
        
        # Create port list
        ports = []
        for port_type, count in port_config.items():
            ports.extend([port_type] * count)
        
        random.shuffle(ports)
        random.shuffle(edge_tiles)
        
        # Place ports
        ports_to_place = min(len(ports), len(edge_tiles))
        for i in range(ports_to_place):
            # In a full implementation, ports would be placed on edges/vertices
            # For now, we mark the adjacent land tile
            edge_tiles[i].port = ports[i]
            self.ports_placed.append({
                'type': ports[i],
                'coordinate': edge_tiles[i].coordinate
            })
        
        print(f"✓ Placed {len(self.ports_placed)} ports")
    
    def _find_edge_tiles(self) -> List[HexTile]:
        """
        Find land tiles on the edge of the board.
        Edge tiles have fewer than 6 neighbors or have water neighbors.
        """
        edge_tiles = []
        
        for tile in self.grid.get_land_tiles():
            neighbors = self.grid.get_neighbors(tile.coordinate)
            
            # Tile is on edge if it has fewer than 6 neighbors
            if len(neighbors) < 6:
                edge_tiles.append(tile)
            else:
                # Or if any neighbor is water (for boards with water tiles)
                has_water_neighbor = any(not n.is_land() for n in neighbors)
                if has_water_neighbor:
                    edge_tiles.append(tile)
        
        return edge_tiles
    
    def get_map_statistics(self) -> Dict:
        """Get statistics about the generated map."""
        land_tiles = self.grid.get_land_tiles()
        
        # Resource distribution
        resource_counts = {}
        for tile in land_tiles:
            resource_counts[tile.resource] = resource_counts.get(tile.resource, 0) + 1
        
        # Number distribution
        number_counts = {}
        total_pips = 0
        for tile in land_tiles:
            if tile.number_token:
                number_counts[tile.number_token] = number_counts.get(tile.number_token, 0) + 1
                total_pips += tile.get_resource_value()
        
        # Check for adjacent high numbers
        high_number_violations = len(self._find_violations({6, 8}))
        
        return {
            'total_tiles': len(self.grid.get_all_tiles()),
            'land_tiles': len(land_tiles),
            'resource_distribution': resource_counts,
            'number_distribution': number_counts,
            'total_pip_value': total_pips,
            'ports_placed': len(self.ports_placed),
            'high_number_violations': high_number_violations
        }
    
    def print_map_summary(self):
        """Print a human-readable summary of the map."""
        stats = self.get_map_statistics()
        
        print("\n=== Map Summary ===")
        print(f"Total tiles: {stats['total_tiles']}")
        print(f"Land tiles: {stats['land_tiles']}")
        
        print("\nResource Distribution:")
        for resource, count in sorted(stats['resource_distribution'].items()):
            print(f"  {resource.capitalize()}: {count}")
        
        print("\nNumber Distribution:")
        for number, count in sorted(stats['number_distribution'].items()):
            print(f"  {number}: {count}")
        
        print(f"\nTotal pip value: {stats['total_pip_value']}")
        print(f"Ports placed: {stats['ports_placed']}")
        
        if stats['high_number_violations'] > 0:
            print(f"⚠ Warning: {stats['high_number_violations']} adjacent 6/8 pairs found")
        else:
            print("✓ No adjacent 6/8 violations")
    
    def export_map(self) -> Dict:
        """Export the complete map for network transmission or saving."""
        return {
            'grid': self.grid.to_dict(),
            'ports': self.ports_placed,
            'statistics': self.get_map_statistics()
        }
    
    @staticmethod
    def import_map(data: Dict) -> 'MapGenerator':
        """Import a map from exported data."""
        generator = MapGenerator()
        generator.grid = HexGrid.from_dict(data['grid'])
        generator.ports_placed = data['ports']
        return generator


# Testing and examples
if __name__ == "__main__":
    print("=== Map Generator Test ===\n")
    
    # Initialize with settings
    settings = GameSettings()
    generator = MapGenerator(settings)
    
    # Test 1: Generate standard 3-4 player map
    print("--- Generating Standard Map (3-4 players) ---")
    settings.set_map_template('standard_3_4_player')
    grid = generator.generate_map(randomize=True)
    generator.print_map_summary()
    
    # Test 2: Generate large map
    print("\n--- Generating Large Map (7-8 players) ---")
    generator2 = MapGenerator(settings)
    grid2 = generator2.generate_map('large_7_8_player', randomize=True)
    generator2.print_map_summary()
    
    # Test 3: Show some tile details
    print("\n--- Sample Tiles ---")
    sample_tiles = list(grid.get_land_tiles())[:5]
    for tile in sample_tiles:
        prob = tile.get_production_probability()
        pip = tile.get_resource_value()
        print(f"{tile} - Probability: {prob:.3f}, Pips: {pip}")
    
    # Test 4: Export and import
    print("\n--- Export/Import Test ---")
    exported = generator.export_map()
    print(f"Exported map with {len(exported['grid']['tiles'])} tiles")
    
    imported_generator = MapGenerator.import_map(exported)
    print(f"Imported map with {len(imported_generator.grid.get_all_tiles())} tiles")
    
    # Test 5: Check neighbors of center tile
    print("\n--- Neighbor Test ---")
    center = grid.get_tile(HexCoordinate(0, 0))
    if center:
        neighbors = grid.get_neighbors(center.coordinate)
        print(f"Center tile ({center.resource}) has {len(neighbors)} neighbors:")
        for neighbor in neighbors:
            print(f"  - {neighbor.resource} #{neighbor.number_token}")
