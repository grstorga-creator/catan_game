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
        # Number token distribution for 34-hex board:
        # 1×2, 2×3, 4×4, 5×5, 5×6, 5×8, 4×9, 4×10, 2×11, 1×12 = 33 tokens (34 - 1 desert)
        self.available_numbers = [2, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12]
        
        self.hexes: Dict[HexCoord, Hex] = {}
        self.water_hexes: Dict[HexCoord, Hex] = {}
    
    def get_hex_label(self, coord) -> str:
        """Convert hex coordinate (q,r) to A-G row, 1-x column label"""
        middle_row = self.num_rows // 2
        
        # Row labels A-G based on r coordinate
        row_letter = chr(ord('A') + (coord.r + middle_row + 1))
        
        # Column: count from left within this row
        if coord.r == -middle_row - 1:
            # Top water row
            col_num = coord.q + middle_row + 1
        elif coord.r == middle_row + 1:
            # Bottom water row
            col_num = coord.q + middle_row + 1
        else:
            # Middle rows
            row_idx = coord.r + middle_row
            row_width = self.row_pattern[row_idx]
            offset = abs(middle_row - row_idx)
            col_num = coord.q + offset + 2
        
        return f"{row_letter}{col_num}"
    
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
        
        # SPECIAL: Place desert at D1 (first land hex in row D, the center row)
        # Row D is r=0, first land hex is at q=-1
        desert_coord = HexCoord(-1, 0)
        
        for i, coord in enumerate(land_coords):
            terrain = terrains[i]
            # If this is the desert position, use desert
            if coord == desert_coord:
                self.hexes[coord] = Hex(coord, Terrain.DESERT)
                print(f"[DEBUG] DESERT placed at {self.get_hex_label(coord)}: {coord}")
            else:
                self.hexes[coord] = Hex(coord, terrain)
        
        print(f"[DEBUG] Created {len(self.hexes)} land hexes")
        
        # Distribute number tokens
        self._distribute_number_tokens()
        
        # Generate FIXED water hexes - with special handling for row D
        water_coords = self._generate_water_hex_coordinates()
        
        # Special adjustment for row D (r=0): 
        # - Remove left water at q=-1 (D1, now occupied by desert)
        # - Add water at q=0 (D2, where water moves to)
        water_coords_adjusted = [c for c in water_coords if not (c.r == 0 and c.q == -1)]
        water_coords_adjusted.append(HexCoord(0, 0))  # Add water at D2
        
        print(f"[DEBUG] Generated {len(water_coords_adjusted)} water coordinates")
        print(f"[DEBUG] Water coord sample (first 6): {water_coords_adjusted[:6]}")
        print(f"[DEBUG] Water coord sample (last 6): {water_coords_adjusted[-6:]}")
        
        # Place DESERT at D1 (q=-1, r=0) - replaces the left water that was removed
        desert_at_d1 = HexCoord(-1, 0)
        self.hexes[desert_at_d1] = Hex(desert_at_d1, Terrain.DESERT)
        print(f"[DEBUG] DESERT placed at D1: {desert_at_d1}")
        
        for coord in water_coords_adjusted:
            self.water_hexes[coord] = Hex(coord, Terrain.WATER)
        
        print(f"[DEBUG] Created {len(self.water_hexes)} water hexes")
        
        # Debug: print hex labels
        print(f"\n[DEBUG] Hex label examples:")
        print(f"[DEBUG] ROW A (r=-3, top water):")
        row_a = [c for c in water_coords_adjusted if c.r == -3][:3]
        for coord in row_a:
            print(f"[DEBUG]   {self.get_hex_label(coord)}: {coord}")
        print(f"[DEBUG] ROW D (r=0, with desert at D1 and water at D2):")
        row_d_all = sorted([c for c in self.hexes.keys() if c.r == 0] + [c for c in water_coords_adjusted if c.r == 0], key=lambda x: x.q)
        for i, coord in enumerate(row_d_all[:4], 1):
            if coord in self.hexes:
                hex_obj = self.hexes[coord]
                print(f"[DEBUG]   D{i}: {coord} = {hex_obj.terrain.value}")
            else:
                hex_obj = self.water_hexes[coord]
                port_str = f" port={hex_obj.port.value}" if hex_obj.port else ""
                print(f"[DEBUG]   D{i}: {coord} = water{port_str}")
        
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
        
        # Top water hexes (above top row) - 7 hexes
        top_row_width = self.row_pattern[0]
        top_row_offset = abs(middle_row - 0)
        top_water_coords = []
        for col in range(top_row_width):
            q = col - top_row_offset
            coord = HexCoord(q, -middle_row - 1)
            top_water_coords.append(coord)
            water_coords.append(coord)
        # Add top-left corner
        corner = HexCoord(-top_row_offset - 1, -middle_row - 1)
        top_water_coords.append(corner)
        water_coords.append(corner)
        print(f"[DEBUG] Top row (r={-middle_row - 1}): {top_water_coords}")
        
        # Left and right water hexes for ALL rows
        for row_idx in range(len(self.row_pattern)):
            row_width = self.row_pattern[row_idx]
            offset = abs(middle_row - row_idx)
            r = row_idx - middle_row
            left_q = -offset - 1
            right_q = row_width - offset
            
            left_coord = HexCoord(left_q, r)
            right_coord = HexCoord(right_q, r)
            water_coords.append(left_coord)
            water_coords.append(right_coord)
            print(f"[DEBUG] Row {row_idx} (r={r}): left={left_coord}, right={right_coord}")
        
        # Bottom water hexes (below bottom row) - 7 hexes
        bottom_row_idx = len(self.row_pattern) - 1
        bottom_row_width = self.row_pattern[bottom_row_idx]
        bottom_row_offset = abs(middle_row - bottom_row_idx)
        bottom_water_coords = []
        
        # Add bottom-left corner FIRST
        corner = HexCoord(-bottom_row_offset - 1, middle_row + 1)
        bottom_water_coords.append(corner)
        water_coords.append(corner)
        
        # Then add the 6 main hexes
        for col in range(bottom_row_width):
            q = col - bottom_row_offset
            coord = HexCoord(q, middle_row + 1)
            bottom_water_coords.append(coord)
            water_coords.append(coord)
        
        print(f"[DEBUG] Bottom row (r={middle_row + 1}): {bottom_water_coords}")
        
        print(f"[DEBUG] Total water coords generated: {len(water_coords)}")
        return water_coords
    
    def _create_terrain_distribution(self) -> List[Terrain]:
        terrains = []
        for terrain, count in self.terrain_counts.items():
            terrains.extend([terrain] * count)
        random.shuffle(terrains)
        return terrains
    
    def _distribute_number_tokens(self):
        """Distribute number tokens by shuffling and assigning sequentially"""
        available_numbers = self.available_numbers.copy()
        
        # Debug: show the distribution BEFORE shuffling
        print(f"[DEBUG] Available numbers (unshuffled): {available_numbers}")
        number_counts_before = {}
        for num in available_numbers:
            number_counts_before[num] = number_counts_before.get(num, 0) + 1
        print(f"[DEBUG] Number counts BEFORE: {sorted(number_counts_before.items())}")
        
        # Shuffle once
        random.shuffle(available_numbers)
        print(f"[DEBUG] Shuffled numbers: {available_numbers}")
        
        # Get land hexes sorted by row (r) then column (q) for left-to-right, top-to-bottom ordering
        land_hexes_sorted = sorted(
            [h for h in self.hexes.values() if h.terrain != Terrain.DESERT],
            key=lambda h: (h.coord.r, h.coord.q)
        )
        
        # Assign tokens sequentially
        assigned_numbers = {}
        for i, hex_obj in enumerate(land_hexes_sorted):
            if i < len(available_numbers):
                number = available_numbers[i]
                hex_obj.number_token = number
                assigned_numbers[number] = assigned_numbers.get(number, 0) + 1
        
        # Debug: show final distribution
        print(f"[DEBUG] Number counts AFTER assignment: {sorted(assigned_numbers.items())}")
        print(f"[DEBUG] Total assigned: {sum(assigned_numbers.values())}")
        print(f"[DEBUG] Land hexes without desert: {len(land_hexes_sorted)}")
    
    def _place_ports(self):
        """Place ports in FIXED pattern on water hexes"""
        if not self.water_hexes:
            return
        
        # Sort water coords by position
        water_coords = sorted(list(self.water_hexes.keys()), key=lambda c: (c.r, c.q))
        
        # Specific resources: 6 total, with Sheep appearing twice (opposite ends)
        specific_resources = [PortType.WHEAT, PortType.ORE, PortType.WOOD, PortType.BRICK, PortType.SHEEP, PortType.SHEEP]
        random.shuffle(specific_resources)
        
        # Apply pattern: specific, water, generic, water, specific, water, generic, water, ...
        # Modulo 4: positions 0, 4, 8, 12, 16, 20 = specific (6 total)
        #           positions 2, 6, 10, 14, 18, 22 = generic (6 total)
        #           positions 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23 = water (12 total)
        resource_idx = 0
        for i, coord in enumerate(water_coords):
            pos_in_pattern = i % 4
            
            if pos_in_pattern == 0 and resource_idx < len(specific_resources):
                self.water_hexes[coord].port = specific_resources[resource_idx]
                resource_idx += 1
            elif pos_in_pattern == 2:
                self.water_hexes[coord].port = PortType.GENERIC
            # else (1, 3): plain water (no port)
        
        # Debug: show port distribution
        print(f"\n[DEBUG] Port distribution (water hexes with A-G/1-x labels):")
        ports_by_type = {}
        for coord, hex_obj in self.water_hexes.items():
            if hex_obj.port:
                port_type = hex_obj.port.value
                if port_type not in ports_by_type:
                    ports_by_type[port_type] = []
                label = self.get_hex_label(coord)
                ports_by_type[port_type].append(label)
                print(f"[DEBUG]   {label}: {port_type}")
        
        print(f"\n[DEBUG] Port summary:")
        for port_type in sorted(ports_by_type.keys()):
            print(f"[DEBUG]   {port_type}: {len(ports_by_type[port_type])} ports")
            # else (1, 3): plain water (no port)
    
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
