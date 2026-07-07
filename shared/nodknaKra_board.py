"""
NodKnaKra Board Generation
Creates a 37-hex board (36 terrain + 1 desert) with ports and balanced number tokens.
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
    """Generates and manages a 37-hex NodKnaKra board"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize board generator"""
        if seed is not None:
            random.seed(seed)
        
        self.hexes: Dict[HexCoord, Hex] = {}
        self.terrain_counts = {
            Terrain.WOOD: 7,
            Terrain.BRICK: 7,
            Terrain.SHEEP: 7,
            Terrain.WHEAT: 7,
            Terrain.ORE: 8,
            Terrain.DESERT: 1
        }
        self.available_numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
    
    def generate(self) -> Dict[HexCoord, Hex]:
        """Generate a complete board"""
        coords = self._generate_hex_ring()
        terrains = self._create_terrain_distribution()
        
        random.shuffle(coords)
        for i, coord in enumerate(coords):
            terrain = terrains[i]
            self.hexes[coord] = Hex(coord, terrain)
        
        self._distribute_number_tokens()
        self._place_ports()
        
        return self.hexes
    
    def _generate_hex_ring(self) -> List[HexCoord]:
        """Generate 37 hexes in concentric rings"""
        coords = []
        coords.append(HexCoord(0, 0))  # Center
        
        for distance in range(1, 4):
            # Generate all hexes at this distance
            for q in range(-distance, distance + 1):
                for r in range(-distance, distance + 1):
                    s = -q - r
                    if max(abs(q), abs(r), abs(s)) == distance:
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
        """Place ports around the edge"""
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
        """Print the board"""
        print("\n" + "="*60)
        print("NodKnaKra Board (37 Hexes)")
        print("="*60)
        
        rows = {}
        for coord, hex_obj in self.hexes.items():
            if coord.r not in rows:
                rows[coord.r] = []
            rows[coord.r].append((coord, hex_obj))
        
        for r in sorted(rows.keys()):
            row_hexes = sorted(rows[r], key=lambda x: x[0].q)
            padding = " " * (3 - r) if r < 3 else ""
            row_str = padding + "  ".join([
                f"{hex_obj.terrain.value[:3].upper()}{hex_obj.number_token}" if hex_obj.number_token > 0 
                else f"{hex_obj.terrain.value[:3].upper()}"
                for _, hex_obj in row_hexes
            ])
            print(row_str)
        
        print("\n" + "="*60)
        print("Terrain Summary:")
        print("="*60)
        
        terrain_counts = {}
        for hex_obj in self.hexes.values():
            if hex_obj.terrain not in terrain_counts:
                terrain_counts[hex_obj.terrain] = 0
            terrain_counts[hex_obj.terrain] += 1
        
        for terrain in sorted(terrain_counts.keys(), key=lambda x: x.value):
            count = terrain_counts[terrain]
            print(f"  {terrain.value.upper()}: {count}")
        
        print("\n" + "="*60 + "\n")
    
    def print_stats(self):
        """Print board statistics"""
        print("Board Statistics:")
        print(f"Total hexes: {len(self.hexes)}")
        print(f"Land hexes: {len([h for h in self.hexes.values() if h.terrain != Terrain.DESERT])}")
        print(f"Number tokens: {len([h for h in self.hexes.values() if h.number_token > 0])}\n")


if __name__ == "__main__":
    print("\nTesting NodKnaKra Board Generation...\n")
    
    board = NodKnaKraBoard(seed=42)
    hexes = board.generate()
    
    print(f"✓ Generated board with {len(hexes)} hexes")
    
    board.print_board()
    board.print_stats()
    
    print("✓ Board generation working!")
