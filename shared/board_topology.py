"""
Vertex and Edge System for Settlers of Catan
Defines vertices (intersection points) and edges (between hexes) for building placement.
"""

from typing import List, Set, Tuple, Optional, Dict
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from hex_grid import HexCoordinate, HexGrid


@dataclass(frozen=True)
class Vertex:
    """
    Represents a vertex (corner) where three hexes meet.
    Vertices are where settlements and cities are placed.
    
    A vertex is identified by a primary hex and a direction (0-5).
    Each vertex is shared by up to 3 hexes.
    """
    hex_coord: HexCoordinate
    direction: int  # 0-5, representing which corner of the hex
    
    def __hash__(self):
        return hash((self.hex_coord, self.direction))
    
    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.hex_coord == other.hex_coord and self.direction == other.direction
    
    def __repr__(self):
        return f"Vertex({self.hex_coord}, dir={self.direction})"
    
    def get_adjacent_hexes(self) -> List[HexCoordinate]:
        r"""
        Get the up-to-3 hexes that touch this vertex.
        
        Vertex directions match rendering angles:
        Direction 0 = 0° (right/east)
        Direction 1 = 60° (bottom-right/southeast)  
        Direction 2 = 120° (bottom-left/southwest)
        Direction 3 = 180° (left/west)
        Direction 4 = 240° (top-left/northwest)
        Direction 5 = 300° (top-right/northeast)
        
        Visual layout:
              4     5
               \   /
            3 --HEX-- 0
               /   \
              2     1
        """
        q, r = self.hex_coord.q, self.hex_coord.r
        
        # Each vertex touches 3 hexes
        # Direction 0: Right/East vertex
        if self.direction == 0:
            return [
                HexCoordinate(q, r),       # Center hex
                HexCoordinate(q + 1, r - 1),  # Top-right hex
                HexCoordinate(q + 1, r)    # Bottom-right hex
            ]
        # Direction 1: Bottom-Right/Southeast vertex
        elif self.direction == 1:
            return [
                HexCoordinate(q, r),
                HexCoordinate(q + 1, r),
                HexCoordinate(q, r + 1)
            ]
        # Direction 2: Bottom-Left/Southwest vertex
        elif self.direction == 2:
            return [
                HexCoordinate(q, r),
                HexCoordinate(q, r + 1),
                HexCoordinate(q - 1, r + 1)
            ]
        # Direction 3: Left/West vertex
        elif self.direction == 3:
            return [
                HexCoordinate(q, r),
                HexCoordinate(q - 1, r + 1),
                HexCoordinate(q - 1, r)
            ]
        # Direction 4: Top-Left/Northwest vertex
        elif self.direction == 4:
            return [
                HexCoordinate(q, r),
                HexCoordinate(q - 1, r),
                HexCoordinate(q, r - 1)
            ]
        # Direction 5: Top-Right/Northeast vertex
        else:  # direction == 5
            return [
                HexCoordinate(q, r),
                HexCoordinate(q, r - 1),
                HexCoordinate(q + 1, r - 1)
            ]
    
    def get_adjacent_vertices(self) -> List['Vertex']:
        """
        Get the 3 vertices adjacent to this one (connected by edges).
        These are the vertices you can build roads to.
        
        Each vertex connects to the two neighboring vertices on the same hex,
        plus one vertex on an adjacent hex.
        """
        q, r = self.hex_coord.q, self.hex_coord.r
        
        # Direction 0 (right): connects to directions 5 and 1 on same hex
        if self.direction == 0:
            return [
                Vertex(HexCoordinate(q, r), 5),  # Counter-clockwise neighbor
                Vertex(HexCoordinate(q, r), 1),  # Clockwise neighbor
                Vertex(HexCoordinate(q + 1, r - 1), 2)  # On adjacent hex
            ]
        # Direction 1 (bottom-right): connects to 0 and 2 on same hex
        elif self.direction == 1:
            return [
                Vertex(HexCoordinate(q, r), 0),
                Vertex(HexCoordinate(q, r), 2),
                Vertex(HexCoordinate(q + 1, r), 3)
            ]
        # Direction 2 (bottom-left): connects to 1 and 3 on same hex
        elif self.direction == 2:
            return [
                Vertex(HexCoordinate(q, r), 1),
                Vertex(HexCoordinate(q, r), 3),
                Vertex(HexCoordinate(q, r + 1), 4)
            ]
        # Direction 3 (left): connects to 2 and 4 on same hex
        elif self.direction == 3:
            return [
                Vertex(HexCoordinate(q, r), 2),
                Vertex(HexCoordinate(q, r), 4),
                Vertex(HexCoordinate(q - 1, r + 1), 5)
            ]
        # Direction 4 (top-left): connects to 3 and 5 on same hex
        elif self.direction == 4:
            return [
                Vertex(HexCoordinate(q, r), 3),
                Vertex(HexCoordinate(q, r), 5),
                Vertex(HexCoordinate(q - 1, r), 0)
            ]
        # Direction 5 (top-right): connects to 4 and 0 on same hex
        else:  # direction == 5
            return [
                Vertex(HexCoordinate(q, r), 4),
                Vertex(HexCoordinate(q, r), 0),
                Vertex(HexCoordinate(q, r - 1), 1)
            ]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'hex': self.hex_coord.to_dict(),
            'direction': self.direction
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Vertex':
        """Create from dictionary."""
        return Vertex(
            HexCoordinate.from_dict(data['hex']),
            data['direction']
        )


@dataclass(frozen=True)
class Edge:
    """
    Represents an edge (side) between two hexes.
    Edges are where roads are placed.
    
    An edge is identified by a hex and a direction (0-5).
    """
    hex_coord: HexCoordinate
    direction: int  # 0-5, representing which edge of the hex
    
    def __hash__(self):
        return hash((self.hex_coord, self.direction))
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return self.hex_coord == other.hex_coord and self.direction == other.direction
    
    def __repr__(self):
        return f"Edge({self.hex_coord}, dir={self.direction})"
    
    def get_adjacent_hexes(self) -> List[HexCoordinate]:
        """
        Get the 2 hexes on either side of this edge.
        
        Edge directions match vertex directions:
        Edge 0 connects vertices 0-5 (right/northeast edge)
        Edge 1 connects vertices 0-1 (southeast edge)
        Edge 2 connects vertices 1-2 (south edge)
        Edge 3 connects vertices 2-3 (southwest edge)
        Edge 4 connects vertices 3-4 (west/northwest edge)
        Edge 5 connects vertices 4-5 (north edge)
        """
        q, r = self.hex_coord.q, self.hex_coord.r
        
        # Edge between vertices 0 and 5
        if self.direction == 0:
            return [HexCoordinate(q, r), HexCoordinate(q + 1, r - 1)]
        # Edge between vertices 0 and 1  
        elif self.direction == 1:
            return [HexCoordinate(q, r), HexCoordinate(q + 1, r)]
        # Edge between vertices 1 and 2
        elif self.direction == 2:
            return [HexCoordinate(q, r), HexCoordinate(q, r + 1)]
        # Edge between vertices 2 and 3
        elif self.direction == 3:
            return [HexCoordinate(q, r), HexCoordinate(q - 1, r + 1)]
        # Edge between vertices 3 and 4
        elif self.direction == 4:
            return [HexCoordinate(q, r), HexCoordinate(q - 1, r)]
        # Edge between vertices 4 and 5
        else:  # direction == 5
            return [HexCoordinate(q, r), HexCoordinate(q, r - 1)]
    
    def get_vertices(self) -> Tuple[Vertex, Vertex]:
        """
        Get the 2 vertices at the ends of this edge.
        Edge N connects vertices N and (N+1) mod 6
        """
        # Edge connects consecutive vertex directions
        v1_dir = self.direction
        v2_dir = (self.direction + 1) % 6
        
        return (
            Vertex(self.hex_coord, v1_dir),
            Vertex(self.hex_coord, v2_dir)
        )
    
    def get_adjacent_edges(self) -> List['Edge']:
        """
        Get the 4 edges adjacent to this one.
        Two at each end vertex.
        """
        v1, v2 = self.get_vertices()
        
        # Get edges connected to each vertex
        edges = []
        
        # Edges from v1 (excluding this edge)
        for adj_v in v1.get_adjacent_vertices():
            if adj_v != v2:  # Don't include the edge we came from
                # Find edge between v1 and adj_v
                edges.extend(self._get_edge_between_vertices(v1, adj_v))
        
        # Edges from v2 (excluding this edge)
        for adj_v in v2.get_adjacent_vertices():
            if adj_v != v1:
                edges.extend(self._get_edge_between_vertices(v2, adj_v))
        
        return edges
    
    @staticmethod
    def _get_edge_between_vertices(v1: Vertex, v2: Vertex) -> List['Edge']:
        """Helper to find edge connecting two vertices."""
        # Try all edge directions from v1's hex
        for direction in range(6):
            edge = Edge(v1.hex_coord, direction)
            edge_verts = edge.get_vertices()
            if (v1 in edge_verts and v2 in edge_verts):
                return [edge]
        return []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'hex': self.hex_coord.to_dict(),
            'direction': self.direction
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Edge':
        """Create from dictionary."""
        return Edge(
            HexCoordinate.from_dict(data['hex']),
            data['direction']
        )


class BoardTopology:
    """
    Manages all vertices and edges on the board.
    Handles building placement validation and connectivity.
    """
    
    def __init__(self, grid: HexGrid):
        """Initialize board topology from a hex grid."""
        self.grid = grid
        
        # All valid vertices and edges
        self.vertices: Set[Vertex] = set()
        self.edges: Set[Edge] = set()
        
        # Buildings placed on the board
        self.settlements: Dict[Vertex, int] = {}  # vertex -> player_id
        self.cities: Dict[Vertex, int] = {}       # vertex -> player_id
        self.roads: Dict[Edge, int] = {}          # edge -> player_id
        
        # Generate all valid positions
        self._generate_topology()
    
    def _generate_topology(self):
        """Generate all valid vertices and edges from the hex grid."""
        # For each hex, add its 6 vertices and 6 edges
        for tile in self.grid.get_all_tiles():
            if tile.is_land():  # Only land tiles have buildable positions
                for direction in range(6):
                    # Add vertex
                    vertex = Vertex(tile.coordinate, direction)
                    self.vertices.add(vertex)
                    
                    # Add edge
                    edge = Edge(tile.coordinate, direction)
                    self.edges.add(edge)
        
        # Filter out water-only vertices (all 3 adjacent hexes are water or missing)
        valid_vertices = set()
        for vertex in self.vertices:
            adjacent_hexes = vertex.get_adjacent_hexes()
            has_land = False
            for hex_coord in adjacent_hexes:
                tile = self.grid.get_tile(hex_coord)
                if tile and tile.is_land():
                    has_land = True
                    break
            if has_land:
                valid_vertices.add(vertex)
        
        self.vertices = valid_vertices
        
        print(f"Generated {len(self.vertices)} vertices and {len(self.edges)} edges")
    
    def get_all_vertices(self) -> Set[Vertex]:
        """Get all valid vertices on the board."""
        return self.vertices.copy()
    
    def get_all_edges(self) -> Set[Edge]:
        """Get all valid edges on the board."""
        return self.edges.copy()
    
    def is_valid_vertex(self, vertex: Vertex) -> bool:
        """Check if vertex exists on the board."""
        return vertex in self.vertices
    
    def is_valid_edge(self, edge: Edge) -> bool:
        """Check if edge exists on the board."""
        return edge in self.edges
    
    def can_place_settlement(self, vertex: Vertex, player_id: int, is_setup: bool = False) -> bool:
        """
        Check if a settlement can be placed at this vertex.
        
        Rules:
        - Vertex must be valid and empty
        - Distance rule: No other settlement within 1 vertex (adjacent vertices must be empty)
        - Must be connected to player's road network (except during setup)
        """
        # Vertex must be valid
        if not self.is_valid_vertex(vertex):
            return False
        
        # Vertex must be empty
        if vertex in self.settlements or vertex in self.cities:
            return False
        
        # Distance rule: adjacent vertices must be empty
        for adj_vertex in vertex.get_adjacent_vertices():
            if adj_vertex in self.settlements or adj_vertex in self.cities:
                return False
        
        # During setup, no road connection required
        if is_setup:
            return True
        
        # Must be connected to player's road network
        return self.is_connected_to_road_network(vertex, player_id)
    
    def can_place_city(self, vertex: Vertex, player_id: int) -> bool:
        """
        Check if a city can be placed (upgrading a settlement).
        
        Rules:
        - Must have player's settlement at this vertex
        """
        return self.settlements.get(vertex) == player_id
    
    def can_place_road(self, edge: Edge, player_id: int, is_setup: bool = False) -> bool:
        """
        Check if a road can be placed at this edge.
        
        Rules:
        - Edge must be valid and empty
        - Must connect to player's existing road or settlement (except first road in setup)
        """
        # Edge must be valid
        if not self.is_valid_edge(edge):
            return False
        
        # Edge must be empty
        if edge in self.roads:
            return False
        
        # During setup first road, no connection required
        if is_setup:
            # Just need to connect to the settlement just placed
            v1, v2 = edge.get_vertices()
            if (self.settlements.get(v1) == player_id or 
                self.settlements.get(v2) == player_id):
                return True
            return False
        
        # Must connect to existing road or settlement
        v1, v2 = edge.get_vertices()
        
        # Check if either end has player's settlement/city
        if (self.settlements.get(v1) == player_id or 
            self.cities.get(v1) == player_id or
            self.settlements.get(v2) == player_id or 
            self.cities.get(v2) == player_id):
            return True
        
        # Check if connected to player's road
        for adj_edge in edge.get_adjacent_edges():
            if self.roads.get(adj_edge) == player_id:
                # Make sure the connection point doesn't have opponent's settlement
                connection_vertices = set(edge.get_vertices()) & set(adj_edge.get_vertices())
                for v in connection_vertices:
                    other_settlement = self.settlements.get(v)
                    other_city = self.cities.get(v)
                    if other_settlement and other_settlement != player_id:
                        continue  # Can't connect through opponent's settlement
                    if other_city and other_city != player_id:
                        continue
                return True
        
        return False
    
    def place_settlement(self, vertex: Vertex, player_id: int, is_setup: bool = False) -> bool:
        """Place a settlement at a vertex. Returns True if successful."""
        if not self.can_place_settlement(vertex, player_id, is_setup):
            return False
        
        self.settlements[vertex] = player_id
        return True
    
    def place_city(self, vertex: Vertex, player_id: int) -> bool:
        """Upgrade a settlement to a city. Returns True if successful."""
        if not self.can_place_city(vertex, player_id):
            return False
        
        # Remove settlement, add city
        del self.settlements[vertex]
        self.cities[vertex] = player_id
        return True
    
    def place_road(self, edge: Edge, player_id: int, is_setup: bool = False) -> bool:
        """Place a road on an edge. Returns True if successful."""
        if not self.can_place_road(edge, player_id, is_setup):
            return False
        
        self.roads[edge] = player_id
        return True
    
    def is_connected_to_road_network(self, vertex: Vertex, player_id: int) -> bool:
        """Check if vertex is connected to player's road network."""
        # Check all edges touching this vertex
        for direction in range(6):
            edge = Edge(vertex.hex_coord, direction)
            edge_vertices = edge.get_vertices()
            
            if vertex in edge_vertices and self.roads.get(edge) == player_id:
                return True
        
        # Also check adjacent vertices' edges
        for adj_vertex in vertex.get_adjacent_vertices():
            for direction in range(6):
                edge = Edge(adj_vertex.hex_coord, direction)
                edge_vertices = edge.get_vertices()
                
                if vertex in edge_vertices and self.roads.get(edge) == player_id:
                    return True
        
        return False
    
    def get_longest_road(self, player_id: int) -> int:
        """
        Calculate the longest continuous road for a player.
        Uses depth-first search to find longest path.
        """
        player_roads = [edge for edge, pid in self.roads.items() if pid == player_id]
        
        if not player_roads:
            return 0
        
        # Build adjacency graph of roads
        graph: Dict[Edge, List[Edge]] = {edge: [] for edge in player_roads}
        
        for edge in player_roads:
            for adj_edge in edge.get_adjacent_edges():
                if adj_edge in player_roads:
                    # Check if connection is valid (not blocked by opponent's settlement)
                    v1, v2 = edge.get_vertices()
                    av1, av2 = adj_edge.get_vertices()
                    connection = (set([v1, v2]) & set([av1, av2])).pop()
                    
                    # Check if connection vertex has opponent's building
                    owner = self.settlements.get(connection) or self.cities.get(connection)
                    if owner is None or owner == player_id:
                        graph[edge].append(adj_edge)
        
        # DFS to find longest path
        max_length = 0
        for start_edge in player_roads:
            visited = set()
            length = self._dfs_longest_path(start_edge, graph, visited)
            max_length = max(max_length, length)
        
        return max_length
    
    def _dfs_longest_path(self, edge: Edge, graph: Dict[Edge, List[Edge]], 
                         visited: Set[Edge]) -> int:
        """DFS helper for finding longest road path."""
        visited.add(edge)
        max_length = 0
        
        for next_edge in graph[edge]:
            if next_edge not in visited:
                length = self._dfs_longest_path(next_edge, graph, visited)
                max_length = max(max_length, length)
        
        visited.remove(edge)
        return max_length + 1
    
    def get_vertex_resources(self, vertex: Vertex) -> List[str]:
        """Get the resources that a settlement/city at this vertex would produce."""
        resources = []
        for hex_coord in vertex.get_adjacent_hexes():
            tile = self.grid.get_tile(hex_coord)
            if tile and tile.is_land() and tile.resource != 'desert':
                resources.append(tile.resource)
        return resources
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'settlements': {
                f"{v.hex_coord.q},{v.hex_coord.r},{v.direction}": player_id
                for v, player_id in self.settlements.items()
            },
            'cities': {
                f"{v.hex_coord.q},{v.hex_coord.r},{v.direction}": player_id
                for v, player_id in self.cities.items()
            },
            'roads': {
                f"{e.hex_coord.q},{e.hex_coord.r},{e.direction}": player_id
                for e, player_id in self.roads.items()
            }
        }


# Testing
if __name__ == "__main__":
    print("=== Vertex and Edge System Test ===\n")
    
    from map_generator import MapGenerator
    from game_settings import GameSettings
    
    # Generate a board
    settings = GameSettings()
    generator = MapGenerator(settings)
    grid = generator.generate_map('standard_3_4_player')
    
    # Create topology
    print("--- Creating Board Topology ---")
    topology = BoardTopology(grid)
    
    print(f"Total vertices: {len(topology.vertices)}")
    print(f"Total edges: {len(topology.edges)}")
    
    # Test vertex
    print("\n--- Testing Vertex ---")
    test_vertex = Vertex(HexCoordinate(0, 0), 0)
    print(f"Test vertex: {test_vertex}")
    print(f"Is valid: {topology.is_valid_vertex(test_vertex)}")
    
    adj_hexes = test_vertex.get_adjacent_hexes()
    print(f"Adjacent hexes: {len(adj_hexes)}")
    for h in adj_hexes:
        tile = grid.get_tile(h)
        if tile:
            print(f"  {h}: {tile.resource}")
    
    adj_vertices = test_vertex.get_adjacent_vertices()
    print(f"Adjacent vertices: {len(adj_vertices)}")
    
    # Test placement
    print("\n--- Testing Settlement Placement ---")
    player_id = 1
    
    if topology.can_place_settlement(test_vertex, player_id, is_setup=True):
        topology.place_settlement(test_vertex, player_id, is_setup=True)
        print(f"✓ Placed settlement at {test_vertex}")
    
    # Try placing too close
    for adj_v in test_vertex.get_adjacent_vertices():
        if topology.can_place_settlement(adj_v, player_id, is_setup=True):
            print(f"✗ Should not allow placement at {adj_v} (too close!)")
        else:
            print(f"✓ Correctly blocked placement at {adj_v} (distance rule)")
        break
    
    # Test road placement
    print("\n--- Testing Road Placement ---")
    test_edge = Edge(HexCoordinate(0, 0), 0)
    
    if topology.can_place_road(test_edge, player_id, is_setup=True):
        topology.place_road(test_edge, player_id, is_setup=True)
        print(f"✓ Placed road at {test_edge}")
    
    # Test city upgrade
    print("\n--- Testing City Upgrade ---")
    if topology.can_place_city(test_vertex, player_id):
        topology.place_city(test_vertex, player_id)
        print(f"✓ Upgraded to city at {test_vertex}")
    
    # Test longest road
    print("\n--- Testing Longest Road ---")
    longest = topology.get_longest_road(player_id)
    print(f"Player {player_id}'s longest road: {longest} segments")
    
    # Test serialization
    print("\n--- Testing Serialization ---")
    data = topology.to_dict()
    print(f"Settlements: {len(data['settlements'])}")
    print(f"Cities: {len(data['cities'])}")
    print(f"Roads: {len(data['roads'])}")
