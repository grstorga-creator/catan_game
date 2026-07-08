"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_board.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-08 - Gordon - Added file header with edit history tracking; rebuilt for scalable row-based layout
2026-07-08 - Gordon - Created NodKnaKraBoard with row-based hex generation (6-7-8-7-6 default)
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Terrain(Enum):
    """Terrain types"""
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"
    DESERT = "desert"


class PortType(Enum):
    """Port types for trading"""
    GENERIC = "generic"
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"


@dataclass
class HexCoord:
    """Axial hexagonal coordinate system (q, r)"""
    q: int
    r: int
    
    @property
    def s(self) -> int:
        """Cube coordinate s = -q - r"""
        return -self.q - self.r
    
    def neighbors(self) -> List['HexCoord']:
        """Get the 6 neighboring hex coordinates"""
        return [
            HexCoord(self.q + 1, self.r),
            HexCoord(self.q + 1, self.r - 1),
            HexCoord(self.q, self.r - 1),
            HexCoord(self.q - 1, self.r),
            HexCoord(self.q - 1, self.r + 1),
            HexCoord(self.q, self.r + 1)
        ]
    
    def distance(self, other: 'HexCoord') -> int:
        """Distance between two hexes"""
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def __repr__(self):
        return f"({self.q},{self.r})"


@dataclass
class Hex:
    """A single hex on the board"""
    coord: HexCoord
    terrain: Terrain
    number_token: int = 0
    port: Optional[PortType] = None
    
    def __repr__(self):
        token_str = f":{self.number_token}" if self.number_token > 0 else ""
        port_str = f" port:{self.port.value}" if self.port else ""
        return f"{self.terrain.value}{token_str}{port_str}"


class NodKnaKraBoard:
    """Generates scalable row-based hexagon boards"""
    
    BOARD_SIZES = {
        'small': [5, 6, 7, 6, 5],
        'standard': [6, 7, 8, 7, 6],
        'large': [7, 8, 9, 8, 7],
        'xlarge': [5, 6, 7, 8, 7, 6, 5]
    }
    
    def __init__(self, row_pattern: Optional[List[int]] = None, seed: Optional[int] = None):
        """Initialize board generator"""
        if seed is not None:
            random.seed(seed)
        
        self.row_pattern = row_pattern or self.BOARD_SIZES['standard']
        self.num_rows = len(self.row_pattern)
        self.total_hexes = sum(self.row_pattern)
        
        self.terrain_counts = self._calculate_terrain_distribution()
        self.available_numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        
        self.hexes: Dict[HexCoord, Hex] = {}
    
    def _calculate_terrain_distribution(self) -> Dict[Terrain, int]:
        """Calculate proportional terrain distribution based on board size"""
        hexes_without_desert = self.total_hexes - 1
        hexes_per_resource = hexes_without_desert // 5
        remainder = hexes_without_desert % 5
    
        distribution = {
            Terrain.WOOD: hexes_per_resource,
            Terrain.BRICK: hexes_per_resource,
            Terrain.SHEEP: hexes_per_resource,
            Terrain.WHEAT: hexes_per_resource,
            Terrain.ORE: hexes_per_resource,
            Terrain.DESERT: 1
        }
    
        resources = [Terrain.WOOD, Terrain.BRICK, Terrain.SHEEP, Terrain.WHEAT, Terrain.ORE]
        for i in range(remainder):
            distribution[resources[i]] += 1
    
        return distribution
    
    def generate(self) -> Dict[HexCoord, Hex]:
        """Generate a complete board"""
        coords = self._generate_hex_coordinates()
        terrains = self._create_terrain_distribution()
        
        random.shuffle(coords)
        for i, coord in enumerate(coords):
            terrain = terrains[i]
            self.hexes[coord] = Hex(coord, terrain)
        
        self._distribute_number_tokens()
        self._place_ports()
        
        return self.hexes
    
    def _generate_hex_coordinates(self) -> List[HexCoord]:
        """Generate hex coordinates for row-based layout"""
        coords = []
        middle_row = self.num_rows // 2
        
        for row_idx, row_width in enumerate(self.row_pattern):
            offset = abs(middle_row - row_idx)
            
            for col in range(row_width):
                q = col - offset
                r = row_idx - middle_row
                coords.append(HexCoord(q, r))
        
        return coords
    
    def _create_terrain_distribution(self) -> List[Terrain]:
        """Create a list of terrains to distribute"""
        terrains = []
        for terrain, count in self.terrain_counts.items():
            terrains.extend([terrain] * count)
        random.shuffle(terrains)
        return terrains
    
    def _distribute_number_tokens(self):
        """Distribute number tokens (2-12) avoiding adjacent 6/8"""
        available_numbers = self.available_numbers.copy()
        random.shuffle(available_numbers)
        
        land_hexes = [h for h in self.hexes.values() if h.terrain != Terrain.DESERT]
        
        for hex_obj in land_hexes:
            if not available_numbers:
                break
            
            number = available_numbers.pop(0)
            hex_obj.number_token = number
            
            if number in [6, 8]:
                neighbors = hex_obj.coord.neighbors()
                for neighbor_coord in neighbors:
                    if neighbor_coord in self.hexes:
                        neighbor = self.hexes[neighbor_coord]
                        if neighbor.number_token in [6, 8]:
                            swapped = False
                            for i, other_number in enumerate(available_numbers):
                                if other_number not in [6, 8]:
                                    hex_obj.number_token = other_number
                                    available_numbers[i] = number
                                    swapped = True
                                    break
    
    def _place_ports(self):
        """Place ports on edge hexes"""
        port_assignments = [
            PortType.GENERIC,
            PortType.WOOD,
            PortType.BRICK,
            PortType.SHEEP,
            PortType.WHEAT,
            PortType.ORE
        ]
        
        edge_hexes = self._find_edge_hexes()
        random.shuffle(edge_hexes)
        
        for i, hex_coord in enumerate(edge_hexes[:6]):
            if hex_coord in self.hexes:
                self.hexes[hex_coord].port = port_assignments[i]
    
    def _find_edge_hexes(self) -> List[HexCoord]:
        """Find hexes on the edge of the board"""
        edge_hexes = []
        for coord in self.hexes.keys():
            neighbors = coord.neighbors()
            if len([n for n in neighbors if n in self.hexes]) < 6:
                edge_hexes.append(coord)
        return edge_hexes
    
    def print_board(self):
        """Print the board in row format"""
        print("\n" + "="*70)
        print(f"NodKnaKra Board - Rows: {self.row_pattern} ({self.total_hexes} hexes)")
        print("="*70)
        
        rows = {}
        for coord, hex_obj in self.hexes.items():
            if coord.r not in rows:
                rows[coord.r] = []
            rows[coord.r].append((coord, hex_obj))
        
        for r in sorted(rows.keys()):
            row_hexes = sorted(rows[r], key=lambda x: x[0].q)
            spaces = " " * (abs(r - (self.num_rows // 2)) * 2)
            row_str = spaces + "  ".join([
                f"{hex_obj.terrain.value[:3].upper()}{hex_obj.number_token}" if hex_obj.number_token > 0 
                else f"{hex_obj.terrain.value[:3].upper()}"
                for _, hex_obj in row_hexes
            ])
            print(row_str)
        
        print("\n" + "="*70)
        print("Terrain Summary:")
        print("="*70)
        
        terrain_counts = {}
        for hex_obj in self.hexes.values():
            if hex_obj.terrain not in terrain_counts:
                terrain_counts[hex_obj.terrain] = 0
            terrain_counts[hex_obj.terrain] += 1
        
        for terrain in sorted(terrain_counts.keys(), key=lambda x: x.value):
            count = terrain_counts[terrain]
            print(f"  {terrain.value.upper()}: {count}")
        
        print("="*70 + "\n")
    
    def print_stats(self):
        """Print board statistics"""
        print("Board Statistics:")
        print(f"  Total hexes: {self.total_hexes}")
        print(f"  Rows: {self.row_pattern}")
        print(f"  Land hexes: {len([h for h in self.hexes.values() if h.terrain != Terrain.DESERT])}")
        print(f"  Number tokens: {len([h for h in self.hexes.values() if h.number_token > 0])}")
        print()


if __name__ == "__main__":
    print("\nTesting NodKnaKra Scalable Board Generation...\n")
    
    for size_name in ['small', 'standard', 'large']:
        size_pattern = NodKnaKraBoard.BOARD_SIZES[size_name]
        board = NodKnaKraBoard(row_pattern=size_pattern, seed=42)
        hexes = board.generate()
        
        print(f"\n{size_name.upper()} Board ({board.total_hexes} hexes):")
        board.print_board()
        board.print_stats()
    
    print("✓ All board sizes working!")
