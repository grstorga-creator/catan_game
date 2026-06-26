"""
Hexagonal Grid System for Settlers of Catan
Implements hex coordinate system and tile management.
"""

from dataclasses import dataclass
from typing import List, Optional, Set
import math


@dataclass(frozen=True)
class HexCoordinate:
    """Hexagonal coordinate using axial (q, r) system."""
    q: int
    r: int
    
    @property
    def s(self) -> int:
        """Cube coordinate s = -q - r."""
        return -self.q - self.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __eq__(self, other):
        if not isinstance(other, HexCoordinate):
            return False
        return self.q == other.q and self.r == other.r
    
    @staticmethod
    def round_hex(q: float, r: float) -> 'HexCoordinate':
        """Round fractional hex coordinates to nearest integer."""
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        
        return HexCoordinate(int(rq), int(rr))
    
    @staticmethod
    def from_dict(data: dict) -> 'HexCoordinate':
        """Create from dictionary."""
        return HexCoordinate(data['q'], data['r'])
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {'q': self.q, 'r': self.r}


class HexTile:
    """Represents a single hexagonal tile on the board."""
    
    def __init__(self, coordinate: HexCoordinate, resource: str, number_token: int = 0):
        """Initialize a hex tile."""
        self.coordinate = coordinate
        self.resource = resource  # 'wood', 'brick', 'sheep', 'wheat', 'ore', 'desert', 'water'
        self.number_token = number_token  # 2-12 (0 for desert/water)
        self.has_robber = False
        self.port = None  # 'generic', 'wood', 'brick', 'sheep', 'wheat', 'ore'
    
    def __hash__(self):
        return hash(self.coordinate)
    
    def __eq__(self, other):
        if not isinstance(other, HexTile):
            return False
        return self.coordinate == other.coordinate
    
    def __repr__(self):
        return f"HexTile({self.coordinate}, {self.resource}, {self.number_token})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'coordinate': self.coordinate.to_dict(),
            'resource': self.resource,
            'number_token': self.number_token,
            'has_robber': self.has_robber,
            'port': self.port
        }


class HexGrid:
    """Manages the hexagonal grid of tiles."""
    
    def __init__(self):
        """Initialize empty grid."""
        self.tiles = {}  # Dictionary of HexCoordinate -> HexTile
    
    def add_tile(self, tile: HexTile):
        """Add a tile to the grid."""
        self.tiles[tile.coordinate] = tile
    
    def get_tile(self, coord: HexCoordinate) -> Optional[HexTile]:
        """Get a tile by coordinate."""
        return self.tiles.get(coord)
    
    def get_neighbors(self, coord: HexCoordinate) -> List[HexCoordinate]:
        """Get the 6 neighboring hexes."""
        q, r = coord.q, coord.r
        neighbors = [
            HexCoordinate(q + 1, r),
            HexCoordinate(q + 1, r - 1),
            HexCoordinate(q, r - 1),
            HexCoordinate(q - 1, r),
            HexCoordinate(q - 1, r + 1),
            HexCoordinate(q, r + 1)
        ]
        return [n for n in neighbors if n in self.tiles]
    
    def get_land_tiles(self) -> List[HexTile]:
        """Get all land tiles (non-water)."""
        return [t for t in self.tiles.values() if t.resource != 'water']
    
    def get_water_tiles(self) -> List[HexTile]:
        """Get all water tiles."""
        return [t for t in self.tiles.values() if t.resource == 'water']
    
    def __contains__(self, coord: HexCoordinate) -> bool:
        """Check if coordinate is in grid."""
        return coord in self.tiles
    
    def __len__(self) -> int:
        """Get number of tiles."""
        return len(self.tiles)
