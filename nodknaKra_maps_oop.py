"""
NodKnaKra Maps - OOP Pre-built Configuration
Three symmetric map sizes with pre-defined hex layouts
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional


class HexType(Enum):
    """Types of hexes on the board"""
    WATER = "Water"
    WOOD = "Wood"
    BRICK = "Brick"
    SHEEP = "Sheep"
    WHEAT = "Wheat"
    ORE = "Ore"
    DESERT = "Desert"


class HarborType(Enum):
    """Port types on water hexes"""
    NONE = None
    GENERIC_3_1 = "3:1"
    WOOD_2_1 = "Wood 2:1"
    BRICK_2_1 = "Brick 2:1"
    SHEEP_2_1 = "Sheep 2:1"
    WHEAT_2_1 = "Wheat 2:1"
    ORE_2_1 = "Ore 2:1"


@dataclass
class HexTemplate:
    """Template for a single hex in a map"""
    position: str  # e.g., "A1", "D5"
    hex_type: HexType
    harbor: Optional[HarborType] = None
    number_token: Optional[int] = None
    adjacent_terrain_positions: List[str] = None  # For water hexes: which terrain hexes they border
    
    def __post_init__(self):
        if self.adjacent_terrain_positions is None:
            self.adjacent_terrain_positions = []


class MapConfiguration:
    """Pre-built map configuration"""
    
    def __init__(self, name: str, hexes: List[HexTemplate]):
        self.name = name
        self.hexes = hexes
        self.terrain_hexes = [h for h in hexes if h.hex_type != HexType.WATER]
        self.water_hexes = [h for h in hexes if h.hex_type == HexType.WATER]
    
    def show_shape(self):
        """Display the map shape"""
        print(f"\n{'='*70}")
        print(f"{self.name.upper()} MAP CONFIGURATION")
        print(f"{'='*70}")
        
        # Organize by row
        rows = {}
        for hex_template in self.hexes:
            row_letter = hex_template.position[0]
            if row_letter not in rows:
                rows[row_letter] = []
            rows[row_letter].append(hex_template)
        
        # Display each row
        for row_letter in sorted(rows.keys()):
            hex_list = rows[row_letter]
            # Sort by column number
            hex_list.sort(key=lambda h: int(h.position[1:]))
            
            hex_display = []
            for hex_t in hex_list:
                if hex_t.hex_type == HexType.WATER:
                    # Show water with port info if applicable
                    if len(hex_t.adjacent_terrain_positions) > 0:
                        hex_display.append(f"~({len(hex_t.adjacent_terrain_positions)})")
                    else:
                        hex_display.append("~")
                elif hex_t.hex_type == HexType.DESERT:
                    hex_display.append("D")
                else:
                    # First letter of terrain
                    hex_display.append(hex_t.hex_type.value[0])
            
            print(f"Row {row_letter}: {' '.join(hex_display)}")
        
        # Summary
        print(f"\nTerrain hexes: {len(self.terrain_hexes) - 1} (excluding desert)")
        print(f"Desert hexes: 1")
        print(f"Water hexes: {len(self.water_hexes)}")
        print(f"Total hexes: {len(self.hexes)}")


# ============================================================================
# SMALL MAP (28 terrain + 1 desert + 22 water = 51 total)
# ============================================================================
SMALL_MAP_HEXES = [
    # Row A - 6 water hexes
    HexTemplate("A1", HexType.WATER, adjacent_terrain_positions=["B2", "B3"]),
    HexTemplate("A2", HexType.WATER, adjacent_terrain_positions=["B3", "B4"]),
    HexTemplate("A3", HexType.WATER, adjacent_terrain_positions=["B4", "B5"]),
    HexTemplate("A4", HexType.WATER, adjacent_terrain_positions=["B5", "B6"]),
    HexTemplate("A5", HexType.WATER, adjacent_terrain_positions=["B6"]),
    HexTemplate("A6", HexType.WATER),
    
    # Row B - 7 hexes (1 water + 5 terrain + 1 water)
    HexTemplate("B1", HexType.WATER, adjacent_terrain_positions=["B2", "C2"]),
    HexTemplate("B2", HexType.WOOD),
    HexTemplate("B3", HexType.WHEAT),
    HexTemplate("B4", HexType.ORE),
    HexTemplate("B5", HexType.BRICK),
    HexTemplate("B6", HexType.SHEEP),
    HexTemplate("B7", HexType.WATER, adjacent_terrain_positions=["B6", "C6"]),
    
    # Row C - 8 hexes (1 water + 6 terrain + 1 water)
    HexTemplate("C1", HexType.WATER, adjacent_terrain_positions=["C2", "D2"]),
    HexTemplate("C2", HexType.BRICK),
    HexTemplate("C3", HexType.SHEEP),
    HexTemplate("C4", HexType.WOOD),
    HexTemplate("C5", HexType.WHEAT),
    HexTemplate("C6", HexType.ORE),
    HexTemplate("C7", HexType.BRICK),
    HexTemplate("C8", HexType.WATER, adjacent_terrain_positions=["C7", "D7"]),
    
    # Row D - 9 hexes: DESERT + 6 TERRAIN + 2 WATER - CENTER ROW
    HexTemplate("D1", HexType.DESERT),  # DESERT - ISOLATED, NO TERRAIN
    HexTemplate("D2", HexType.WATER, adjacent_terrain_positions=["C2", "D3"]),  # Left water
    HexTemplate("D3", HexType.SHEEP),
    HexTemplate("D4", HexType.WOOD),
    HexTemplate("D5", HexType.WHEAT),
    HexTemplate("D6", HexType.ORE),
    HexTemplate("D7", HexType.BRICK),
    HexTemplate("D8", HexType.SHEEP),
    HexTemplate("D9", HexType.WATER, adjacent_terrain_positions=["D8", "E7"]),  # Right water
    
    # Row E - 8 hexes (1 water + 6 terrain + 1 water)
    HexTemplate("E1", HexType.WATER, adjacent_terrain_positions=["D2", "E2"]),
    HexTemplate("E2", HexType.BRICK),
    HexTemplate("E3", HexType.ORE),
    HexTemplate("E4", HexType.WHEAT),
    HexTemplate("E5", HexType.WOOD),
    HexTemplate("E6", HexType.SHEEP),
    HexTemplate("E7", HexType.BRICK),
    HexTemplate("E8", HexType.WATER, adjacent_terrain_positions=["E7", "F6"]),
    
    # Row F - 7 hexes (1 water + 5 terrain + 1 water)
    HexTemplate("F1", HexType.WATER, adjacent_terrain_positions=["E2", "F2"]),
    HexTemplate("F2", HexType.SHEEP),
    HexTemplate("F3", HexType.BRICK),
    HexTemplate("F4", HexType.ORE),
    HexTemplate("F5", HexType.WHEAT),
    HexTemplate("F6", HexType.WOOD),
    HexTemplate("F7", HexType.WATER, adjacent_terrain_positions=["F6"]),
    
    # Row G - 6 water hexes
    HexTemplate("G1", HexType.WATER, adjacent_terrain_positions=["F2", "F3"]),
    HexTemplate("G2", HexType.WATER, adjacent_terrain_positions=["F3", "F4"]),
    HexTemplate("G3", HexType.WATER, adjacent_terrain_positions=["F4", "F5"]),
    HexTemplate("G4", HexType.WATER, adjacent_terrain_positions=["F5", "F6"]),
    HexTemplate("G5", HexType.WATER, adjacent_terrain_positions=["F6"]),
    HexTemplate("G6", HexType.WATER),
]

# ============================================================================
# STANDARD MAP (33 terrain + 1 desert + 24 water = 58 total)
# ============================================================================
STANDARD_MAP_HEXES = [
    # Row A - 7 water hexes (outer ring)
    HexTemplate("A1", HexType.WATER, adjacent_terrain_positions=["B2", "B3"]),
    HexTemplate("A2", HexType.WATER, adjacent_terrain_positions=["B3", "B4"]),
    HexTemplate("A3", HexType.WATER, adjacent_terrain_positions=["B4", "B5"]),
    HexTemplate("A4", HexType.WATER, adjacent_terrain_positions=["B5", "B6"]),
    HexTemplate("A5", HexType.WATER, adjacent_terrain_positions=["B6", "B7"]),
    HexTemplate("A6", HexType.WATER, adjacent_terrain_positions=["B7", "B8"]),
    HexTemplate("A7", HexType.WATER, adjacent_terrain_positions=["B8"]),
    
    # Row B - 8 hexes (1 water left + 6 terrain + 1 water right)
    HexTemplate("B1", HexType.WATER, adjacent_terrain_positions=["B2", "C2"]),
    HexTemplate("B2", HexType.WOOD),
    HexTemplate("B3", HexType.WHEAT),
    HexTemplate("B4", HexType.ORE),
    HexTemplate("B5", HexType.BRICK),
    HexTemplate("B6", HexType.SHEEP),
    HexTemplate("B7", HexType.WOOD),
    HexTemplate("B8", HexType.WATER, adjacent_terrain_positions=["B7", "C8"]),
    
    # Row C - 9 hexes (1 water + 7 terrain + 1 water)
    HexTemplate("C1", HexType.WATER, adjacent_terrain_positions=["C2", "D2"]),
    HexTemplate("C2", HexType.BRICK),
    HexTemplate("C3", HexType.SHEEP),
    HexTemplate("C4", HexType.WOOD),
    HexTemplate("C5", HexType.WHEAT),
    HexTemplate("C6", HexType.ORE),
    HexTemplate("C7", HexType.BRICK),
    HexTemplate("C8", HexType.SHEEP),
    HexTemplate("C9", HexType.WATER, adjacent_terrain_positions=["C8", "D9"]),
    
    # Row D - 10 hexes: DESERT + 7 TERRAIN + 2 WATER
    HexTemplate("D1", HexType.DESERT),  # DESERT - ISOLATED, NO TERRAIN
    HexTemplate("D2", HexType.WATER, adjacent_terrain_positions=["C2", "D3"]),  # Left water
    HexTemplate("D3", HexType.SHEEP),
    HexTemplate("D4", HexType.WOOD),
    HexTemplate("D5", HexType.WHEAT),
    HexTemplate("D6", HexType.ORE),
    HexTemplate("D7", HexType.BRICK),
    HexTemplate("D8", HexType.SHEEP),
    HexTemplate("D9", HexType.WOOD),
    HexTemplate("D10", HexType.WATER, adjacent_terrain_positions=["D9", "E9"]),  # Right water
    
    # Row E - 9 hexes (1 water + 7 terrain + 1 water)
    HexTemplate("E1", HexType.WATER, adjacent_terrain_positions=["D2", "E2"]),
    HexTemplate("E2", HexType.BRICK),
    HexTemplate("E3", HexType.ORE),
    HexTemplate("E4", HexType.WHEAT),
    HexTemplate("E5", HexType.WOOD),
    HexTemplate("E6", HexType.SHEEP),
    HexTemplate("E7", HexType.BRICK),
    HexTemplate("E8", HexType.SHEEP),
    HexTemplate("E9", HexType.WATER, adjacent_terrain_positions=["E8", "F7"]),
    
    # Row F - 8 hexes (1 water + 6 terrain + 1 water)
    HexTemplate("F1", HexType.WATER, adjacent_terrain_positions=["E2", "F2"]),
    HexTemplate("F2", HexType.SHEEP),
    HexTemplate("F3", HexType.BRICK),
    HexTemplate("F4", HexType.ORE),
    HexTemplate("F5", HexType.WHEAT),
    HexTemplate("F6", HexType.WOOD),
    HexTemplate("F7", HexType.BRICK),
    HexTemplate("F8", HexType.WATER, adjacent_terrain_positions=["F7", "G6"]),
    
    # Row G - 7 water hexes (outer ring)
    HexTemplate("G1", HexType.WATER, adjacent_terrain_positions=["F2"]),
    HexTemplate("G2", HexType.WATER, adjacent_terrain_positions=["F2", "F3"]),
    HexTemplate("G3", HexType.WATER, adjacent_terrain_positions=["F3", "F4"]),
    HexTemplate("G4", HexType.WATER, adjacent_terrain_positions=["F4", "F5"]),
    HexTemplate("G5", HexType.WATER, adjacent_terrain_positions=["F5", "F6"]),
    HexTemplate("G6", HexType.WATER, adjacent_terrain_positions=["F6", "F7"]),
    HexTemplate("G7", HexType.WATER, adjacent_terrain_positions=["F7"]),
]

# ============================================================================
# LARGE MAP (43 terrain + 1 desert + 28 water = 72 total)
# ============================================================================
LARGE_MAP_HEXES = [
    # Row A - 9 water hexes
    HexTemplate("A1", HexType.WATER, adjacent_terrain_positions=["B2", "B3"]),
    HexTemplate("A2", HexType.WATER, adjacent_terrain_positions=["B3", "B4"]),
    HexTemplate("A3", HexType.WATER, adjacent_terrain_positions=["B4", "B5"]),
    HexTemplate("A4", HexType.WATER, adjacent_terrain_positions=["B5", "B6"]),
    HexTemplate("A5", HexType.WATER, adjacent_terrain_positions=["B6", "B7"]),
    HexTemplate("A6", HexType.WATER, adjacent_terrain_positions=["B7", "B8"]),
    HexTemplate("A7", HexType.WATER, adjacent_terrain_positions=["B8", "B9"]),
    HexTemplate("A8", HexType.WATER, adjacent_terrain_positions=["B9", "B10"]),
    HexTemplate("A9", HexType.WATER, adjacent_terrain_positions=["B10"]),
    
    # Row B - 10 hexes (1 water + 8 terrain + 1 water)
    HexTemplate("B1", HexType.WATER, adjacent_terrain_positions=["B2", "C2"]),
    HexTemplate("B2", HexType.WOOD),
    HexTemplate("B3", HexType.WHEAT),
    HexTemplate("B4", HexType.ORE),
    HexTemplate("B5", HexType.BRICK),
    HexTemplate("B6", HexType.SHEEP),
    HexTemplate("B7", HexType.WOOD),
    HexTemplate("B8", HexType.WHEAT),
    HexTemplate("B9", HexType.BRICK),
    HexTemplate("B10", HexType.WATER, adjacent_terrain_positions=["B9", "C10"]),
    
    # Row C - 11 hexes (1 water + 9 terrain + 1 water)
    HexTemplate("C1", HexType.WATER, adjacent_terrain_positions=["C2", "D2"]),
    HexTemplate("C2", HexType.BRICK),
    HexTemplate("C3", HexType.SHEEP),
    HexTemplate("C4", HexType.WOOD),
    HexTemplate("C5", HexType.WHEAT),
    HexTemplate("C6", HexType.ORE),
    HexTemplate("C7", HexType.BRICK),
    HexTemplate("C8", HexType.SHEEP),
    HexTemplate("C9", HexType.WOOD),
    HexTemplate("C10", HexType.WHEAT),
    HexTemplate("C11", HexType.WATER, adjacent_terrain_positions=["C10", "D11"]),
    
    # Row D - 12 hexes: DESERT + 9 TERRAIN + 2 WATER - CENTER ROW
    HexTemplate("D1", HexType.DESERT),  # DESERT - ISOLATED, NO TERRAIN
    HexTemplate("D2", HexType.WATER, adjacent_terrain_positions=["C2", "D3"]),  # Left water
    HexTemplate("D3", HexType.SHEEP),
    HexTemplate("D4", HexType.WOOD),
    HexTemplate("D5", HexType.WHEAT),
    HexTemplate("D6", HexType.ORE),
    HexTemplate("D7", HexType.BRICK),
    HexTemplate("D8", HexType.SHEEP),
    HexTemplate("D9", HexType.WOOD),
    HexTemplate("D10", HexType.WHEAT),
    HexTemplate("D11", HexType.ORE),
    HexTemplate("D12", HexType.WATER, adjacent_terrain_positions=["D11", "E11"]),  # Right water
    
    # Row E - 11 hexes (1 water + 9 terrain + 1 water)
    HexTemplate("E1", HexType.WATER, adjacent_terrain_positions=["D2", "E2"]),
    HexTemplate("E2", HexType.BRICK),
    HexTemplate("E3", HexType.ORE),
    HexTemplate("E4", HexType.WHEAT),
    HexTemplate("E5", HexType.WOOD),
    HexTemplate("E6", HexType.SHEEP),
    HexTemplate("E7", HexType.BRICK),
    HexTemplate("E8", HexType.SHEEP),
    HexTemplate("E9", HexType.WOOD),
    HexTemplate("E10", HexType.WHEAT),
    HexTemplate("E11", HexType.WATER, adjacent_terrain_positions=["E10", "F10"]),
    
    # Row F - 10 hexes (1 water + 8 terrain + 1 water)
    HexTemplate("F1", HexType.WATER, adjacent_terrain_positions=["E2", "F2"]),
    HexTemplate("F2", HexType.SHEEP),
    HexTemplate("F3", HexType.BRICK),
    HexTemplate("F4", HexType.ORE),
    HexTemplate("F5", HexType.WHEAT),
    HexTemplate("F6", HexType.WOOD),
    HexTemplate("F7", HexType.BRICK),
    HexTemplate("F8", HexType.SHEEP),
    HexTemplate("F9", HexType.ORE),
    HexTemplate("F10", HexType.WATER, adjacent_terrain_positions=["F9"]),
    
    # Row G - 9 water hexes
    HexTemplate("G1", HexType.WATER, adjacent_terrain_positions=["F2", "F3"]),
    HexTemplate("G2", HexType.WATER, adjacent_terrain_positions=["F3", "F4"]),
    HexTemplate("G3", HexType.WATER, adjacent_terrain_positions=["F4", "F5"]),
    HexTemplate("G4", HexType.WATER, adjacent_terrain_positions=["F5", "F6"]),
    HexTemplate("G5", HexType.WATER, adjacent_terrain_positions=["F6", "F7"]),
    HexTemplate("G6", HexType.WATER, adjacent_terrain_positions=["F7", "F8"]),
    HexTemplate("G7", HexType.WATER, adjacent_terrain_positions=["F8", "F9"]),
    HexTemplate("G8", HexType.WATER, adjacent_terrain_positions=["F9", "F10"]),
    HexTemplate("G9", HexType.WATER, adjacent_terrain_positions=["F10"]),
]


# Create map objects
SMALL = MapConfiguration("Small", SMALL_MAP_HEXES)
STANDARD = MapConfiguration("Standard", STANDARD_MAP_HEXES)
LARGE = MapConfiguration("Large", LARGE_MAP_HEXES)


if __name__ == "__main__":
    print("\nNodKnaKra - Three Pre-Built Symmetric Maps\n")
    
    SMALL.show_shape()
    STANDARD.show_shape()
    LARGE.show_shape()
    
    print(f"\n{'='*70}")
    print("LEGEND:")
    print("  ~ = Water hex")
    print("  ~(2) = Water hex with 2 adjacent terrain (has 2 ports)")
    print("  ~(1) = Water hex with 1 adjacent terrain (has 1 port)")
    print("  D = Desert (isolated, no ports)")
    print("  W/B/S/O/R = Wood/Brick/Sheep/Ore/wheaT (terrain)")
    print(f"{'='*70}\n")
