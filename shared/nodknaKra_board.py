"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_board.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-10 - Gordon - Complete rewrite: define ALL hexes upfront (land + FIXED water positions)
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Terrain(Enum):
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"
    DESERT = "desert"
    WATER = "water"


class PortType(Enum):
    GENERIC = "generic"
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"


@dataclass
class HexCoord:
    q: int
    r: int
    
    def neighbors(self) -> List['HexCoord']:
        return [
            HexCoord(self.q + 1, self.r),
            HexCoord(self.q + 1, self.r - 1),
            HexCoord(self.q, self.r - 1),
            HexCoord(self.q - 1, self.r),
            HexCoord(self.q - 1, self.r + 1),
            HexCoord(self.q, self.r + 1)
        ]
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def __repr__(self):
        return f"({self.q},{self.r})"


@dataclass
class Hex:
    coord: HexCoord
    terrain: Terrain
    number_token: int = 0
    port: Optional[PortType] = None


class NodKnaKraBoard:
    BOARD_SIZES = {
        'small': [5, 6, 7, 6, 5],
        'standard': [6, 7, 8, 7, 6],
        'large': [7, 8, 9, 8, 7],
        'xlarge': [5, 6, 7, 8, 7, 6, 5]
    }
    
    def __init__(self, row_pattern: Optional[List[int]] = None, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.row_pattern = row_pattern or self.BOARD_SIZES['standard']
        self.num_rows = len(self.row_pattern)
        self.total_hexes = sum(self.row_pattern)
        
        self.terrain_counts = self._calculate_terrain_distribution()
        self.available_numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        
        self.hexes: Dict[HexCoord, Hex] = {}
        self.water_hexes: Dict[HexCoord, Hex] = {}
    
    def _calculate_terrain_distribution(self) -> Dict[Terrain, int]:
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
        """Generate complete board with FIXED land and water positions"""
        # Generate land hex coordinates
        land_coords = self._generate_land_hex_coordinates()
        print(f"[DEBUG] Generated {len(land_coords)} land coordinates")
        print(f"[DEBUG] Land coord sample: {land_coords[:5]}")
        
        # Assign randomized terrain to land hexes
        terrains = self._create_terrain_distribution()
        random.shuffle(land_coords)
        
        for i, coord in enumerate(land_coords):
            terrain = terrains[i]
            self.hexes[coord] = Hex(coord, terrain)
        
        print(f"[DEBUG] Created {len(self.hexes)} land hexes")
        
        # Distribute number tokens
        self._distribute_number_tokens()
        
        # Generate FIXED water hexes
        water_coords = self._generate_water_hex_coordinates()
        print(f"[DEBUG] Generated {len(water_coords)} water coordinates")
        print(f"[DEBUG] Water coord sample (first 6): {water_coords[:6]}")
        print(f"[DEBUG] Water coord sample (last 6): {water_coords[-6:]}")
        
        for coord in water_coords:
            self.water_hexes[coord] = Hex(coord, Terrain.WATER)
        
        print(f"[DEBUG] Created {len(self.water_hexes)} water hexes")
        
        # Place ports
        self._place_ports()
        
        return self.hexes
    
    def _generate_land_hex_coordinates(self) -> List[HexCoord]:
        """Generate land hex coordinates in row-based layout"""
        coords = []
        middle_row = self.num_rows // 2
        
        for row_idx, row_width in enumerate(self.row_pattern):
            offset = abs(middle_row - row_idx)
            for col in range(row_width):
                q = col - offset
                r = row_idx - middle_row
                coords.append(HexCoord(q, r))
        
        return coords
    
    def _generate_water_hex_coordinates(self) -> List[HexCoord]:
        """Generate FIXED water hex coordinates surrounding the land (24 total)"""
        water_coords = []
        middle_row = self.num_rows // 2
        
        print(f"[DEBUG] Board rows: {self.row_pattern}, middle_row: {middle_row}")
        
        # Top water hexes (above top row)
        top_row_idx = 0
        top_row_width = self.row_pattern[top_row_idx]
        top_row_offset = abs(middle_row - top_row_idx)
        print(f"[DEBUG] Top row (above): width={top_row_width}, offset={top_row_offset}, r={-middle_row - 1}")
        for col in range(top_row_width):
            q = col - top_row_offset
            water_coords.append(HexCoord(q, -middle_row - 1))
        
        # Left and right water hexes for ALL rows (including top and bottom)
        print(f"[DEBUG] All rows (left/right):")
        for row_idx in range(len(self.row_pattern)):
            row_width = self.row_pattern[row_idx]
            offset = abs(middle_row - row_idx)
            r = row_idx - middle_row
            left_q = -offset - 1
            right_q = row_width - offset
            print(f"[DEBUG]   row_idx={row_idx}, r={r}, width={row_width}, offset={offset}, left_q={left_q}, right_q={right_q}")
            
            # Left
            water_coords.append(HexCoord(left_q, r))
            # Right
            water_coords.append(HexCoord(right_q, r))
        
        # Bottom water hexes (below bottom row)
        bottom_row_idx = len(self.row_pattern) - 1
        bottom_row_width = self.row_pattern[bottom_row_idx]
        bottom_row_offset = abs(middle_row - bottom_row_idx)
        print(f"[DEBUG] Bottom row (below): width={bottom_row_width}, offset={bottom_row_offset}, r={middle_row + 1}")
        for col in range(bottom_row_width):
            q = col - bottom_row_offset
            water_coords.append(HexCoord(q, middle_row + 1))
        
        print(f"[DEBUG] Total water coords generated: {len(water_coords)}")
        print(f"[DEBUG] ALL water coordinates:")
        for i, coord in enumerate(water_coords):
            print(f"[DEBUG]   {i:2d}: {coord}")
        return water_coords
    
    def _create_terrain_distribution(self) -> List[Terrain]:
        terrains = []
        for terrain, count in self.terrain_counts.items():
            terrains.extend([terrain] * count)
        random.shuffle(terrains)
        return terrains
    
    def _distribute_number_tokens(self):
        available_numbers = self.available_numbers.copy()
        random.shuffle(available_numbers)
        
        land_hexes = [h for h in self.hexes.values() if h.terrain != Terrain.DESERT]
        
        for hex_obj in land_hexes:
            if not available_numbers:
                break
            
            number = available_numbers.pop(0)
            hex_obj.number_token = number
            
            if number in [6, 8]:
                for neighbor_coord in hex_obj.coord.neighbors():
                    if neighbor_coord in self.hexes:
                        neighbor = self.hexes[neighbor_coord]
                        if neighbor.number_token in [6, 8]:
                            for i, other_number in enumerate(available_numbers):
                                if other_number not in [6, 8]:
                                    hex_obj.number_token = other_number
                                    available_numbers[i] = number
                                    break
    
    def _place_ports(self):
        """Place ports in FIXED pattern on water hexes"""
        if not self.water_hexes:
            return
        
        # Sort water coords by position
        water_coords = sorted(list(self.water_hexes.keys()), key=lambda c: (c.r, c.q))
        
        # Randomize specific resources
        specific_resources = [PortType.WOOD, PortType.BRICK, PortType.SHEEP, PortType.WHEAT, PortType.ORE]
        random.shuffle(specific_resources)
        
        # Apply pattern: specific, water, generic, specific, water, generic, ...
        resource_idx = 0
        for i, coord in enumerate(water_coords):
            pos_in_pattern = i % 3
            
            if pos_in_pattern == 0 and resource_idx < len(specific_resources):
                self.water_hexes[coord].port = specific_resources[resource_idx]
                resource_idx += 1
            elif pos_in_pattern == 2:
                self.water_hexes[coord].port = PortType.GENERIC
    
    def get_all_hexes(self) -> Dict[HexCoord, Hex]:
        return {**self.hexes, **self.water_hexes}
    
    def print_stats(self):
        print("Board Statistics:")
        print(f"  Total land hexes: {self.total_hexes}")
        print(f"  Water hexes: {len(self.water_hexes)}")
        print(f"  Total: {len(self.get_all_hexes())}")
        print()


if __name__ == "__main__":
    board = NodKnaKraBoard(seed=42)
    hexes = board.generate()
    board.print_stats()
    print("✓ Board generated!")
