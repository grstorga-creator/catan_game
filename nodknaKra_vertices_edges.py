"""
NodKnaKra Vertices and Edges - Coordinate system for settlements, cities, and roads
Handles variable map sizes and perimeter edge cases
"""

from dataclasses import dataclass, field
from typing import Set, Tuple, List, Optional, Dict
from enum import Enum


class VertexPosition(Enum):
    """Vertex position relative to a hex center (pointy-top orientation)"""
    TOP = "top"           # 0° - top point
    TOP_RIGHT = "tr"      # 60° - top-right
    BOTTOM_RIGHT = "br"   # 120° - bottom-right
    BOTTOM = "bottom"     # 180° - bottom point
    BOTTOM_LEFT = "bl"    # 240° - bottom-left
    TOP_LEFT = "tl"       # 300° - top-left


class EdgePosition(Enum):
    """Edge position relative to a hex center"""
    TOP_RIGHT = "tr"      # Between TOP and TOP_RIGHT
    RIGHT = "right"       # Between TOP_RIGHT and BOTTOM_RIGHT
    BOTTOM_RIGHT = "br"   # Between BOTTOM_RIGHT and BOTTOM
    BOTTOM_LEFT = "bl"    # Between BOTTOM and BOTTOM_LEFT
    LEFT = "left"         # Between BOTTOM_LEFT and TOP_LEFT
    TOP_LEFT = "tl"       # Between TOP_LEFT and TOP


@dataclass
class Vertex:
    """A vertex (intersection point) where 2-3 hexes meet"""
    vertex_id: str
    pixel_x: int
    pixel_y: int
    hex_positions: Set[str] = field(default_factory=set)  # Set of hex positions touching this vertex
    settlement_owner: Optional[int] = None
    is_city: bool = False
    
    def __hash__(self):
        return hash(self.vertex_id)
    
    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.vertex_id == other.vertex_id
        return False
    
    def __repr__(self):
        return f"Vertex({self.vertex_id} @ {self.pixel_x},{self.pixel_y})"


@dataclass
class Edge:
    """An edge (border between hexes) where roads are placed"""
    edge_id: str
    vertex1: Optional['Vertex'] = None
    vertex2: Optional['Vertex'] = None
    hex_positions: Set[str] = field(default_factory=set)  # 1 or 2 hexes (1 if ocean edge)
    road_owner: Optional[int] = None
    
    def __hash__(self):
        return hash(self.edge_id)
    
    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.edge_id == other.edge_id
        return False
    
    def __repr__(self):
        return f"Edge({self.edge_id})"


class VertexEdgeSystem:
    """Manages all vertices and edges on the board"""
    
    def __init__(self, board):
        """Initialize vertex/edge system from a board"""
        self.board = board
        self.map_config = board.map_config
        self.vertices: Dict[str, Vertex] = {}
        self.edges: Dict[str, Edge] = {}
        self.vertex_adjacency: Dict[str, Set[str]] = {}
        self.vertex_edges: Dict[str, Set[str]] = {}
        
        # Build row width lookup
        self.row_widths = self._get_row_widths()
        
        print(f"[DEBUG] Row widths: {self.row_widths}")
        
        self._build_vertices()
        self._build_edges()
        self._calculate_adjacency()
    
    def _get_row_widths(self) -> Dict[str, int]:
        """Get the width of each row from board hexes"""
        row_widths = {}
        
        for hex_pos in self.board.hexes.keys():
            row_letter = hex_pos[0]
            col_num = int(hex_pos[1:])
            
            if row_letter not in row_widths:
                row_widths[row_letter] = col_num
            else:
                row_widths[row_letter] = max(row_widths[row_letter], col_num)
        
        return row_widths
    
    def _get_hex_neighbors(self, hex_pos: str) -> List[str]:
        """Get the 6 neighboring hex positions for a hex (or fewer if on edge)"""
        row_letter = hex_pos[0]
        col_num = int(hex_pos[1:])
        
        # Convert row letter to index (A=0, B=1, ..., G=6)
        row_idx = ord(row_letter) - ord('A')
        
        neighbors = []
        
        # Same row neighbors (always exist if hex exists)
        # Left neighbor
        if col_num > 1:
            neighbors.append(f"{row_letter}{col_num - 1}")
        # Right neighbor
        if col_num < self.row_widths[row_letter]:
            neighbors.append(f"{row_letter}{col_num + 1}")
        
        # Upper row neighbors
        if row_idx > 0:
            upper_row_letter = chr(ord('A') + row_idx - 1)
            upper_row_width = self.row_widths.get(upper_row_letter, 0)
            current_row_width = self.row_widths[row_letter]
            
            if upper_row_width > current_row_width:
                # Upper row is wider (expanding up)
                upper_left = col_num
                upper_right = col_num + 1
            elif upper_row_width < current_row_width:
                # Upper row is narrower (contracting up)
                upper_left = col_num - 1
                upper_right = col_num
            else:
                # Same width
                upper_left = col_num - 1
                upper_right = col_num
            
            if upper_left > 0:
                neighbors.append(f"{upper_row_letter}{upper_left}")
            if upper_right <= upper_row_width:
                neighbors.append(f"{upper_row_letter}{upper_right}")
        
        # Lower row neighbors
        if row_idx < 6:  # Assuming 7 rows (A-G)
            lower_row_letter = chr(ord('A') + row_idx + 1)
            lower_row_width = self.row_widths.get(lower_row_letter, 0)
            current_row_width = self.row_widths[row_letter]
            
            if lower_row_width > current_row_width:
                # Lower row is wider (expanding down)
                lower_left = col_num
                lower_right = col_num + 1
            elif lower_row_width < current_row_width:
                # Lower row is narrower (contracting down)
                lower_left = col_num - 1
                lower_right = col_num
            else:
                # Same width
                lower_left = col_num - 1
                lower_right = col_num
            
            if lower_left > 0:
                neighbors.append(f"{lower_row_letter}{lower_left}")
            if lower_right <= lower_row_width:
                neighbors.append(f"{lower_row_letter}{lower_right}")
        
        return neighbors
    
    def _build_vertices(self):
        """Build all vertices from hex neighbors"""
        print(f"[DEBUG] Building vertices...")
        
        vertex_set = {}  # hex_set_tuple -> vertex_id
        
        for hex_pos in self.board.hexes.keys():
            neighbors = self._get_hex_neighbors(hex_pos)
            
            # Create vertices by combining this hex with each pair of adjacent neighbors
            for i in range(len(neighbors)):
                neighbor1 = neighbors[i]
                neighbor2 = neighbors[(i + 1) % len(neighbors)]
                
                # Create a vertex from three hexes (sorted for unique ID)
                hex_set = tuple(sorted([hex_pos, neighbor1, neighbor2]))
                
                if hex_set not in vertex_set:
                    vertex_id = "|".join(hex_set)
                    vertex_set[hex_set] = vertex_id
        
        # Create Vertex objects
        for hex_set, vertex_id in vertex_set.items():
            vertex = Vertex(vertex_id=vertex_id, hex_positions=set(hex_set))
            self.vertices[vertex_id] = vertex
        
        print(f"[DEBUG] Created {len(self.vertices)} vertices")
    
    def _build_edges(self):
        """Build all edges from adjacent hexes"""
        print(f"[DEBUG] Building edges...")
        
        edge_set = set()
        
        for hex_pos in self.board.hexes.keys():
            neighbors = self._get_hex_neighbors(hex_pos)
            
            for neighbor in neighbors:
                # Create edge ID (sorted so consistent regardless of direction)
                edge_id = "|".join(sorted([hex_pos, neighbor]))
                edge_set.add(edge_id)
        
        # Create Edge objects
        for edge_id in edge_set:
            hex_list = edge_id.split("|")
            edge = Edge(edge_id=edge_id, hex_positions=set(hex_list))
            self.edges[edge_id] = edge
        
        print(f"[DEBUG] Created {len(self.edges)} edges")
    
    def _calculate_adjacency(self):
        """Calculate which vertices are adjacent to each vertex"""
        print(f"[DEBUG] Calculating vertex adjacency...")
        
        # Initialize adjacency sets
        for vertex_id in self.vertices.keys():
            self.vertex_adjacency[vertex_id] = set()
            self.vertex_edges[vertex_id] = set()
        
        # Two vertices are adjacent if they share an edge
        for edge_id, edge in self.edges.items():
            # Find all vertices that touch this edge
            vertices_on_edge = []
            for vertex_id, vertex in self.vertices.items():
                # A vertex touches an edge if it's formed by those two hexes
                hex_set = set(vertex.hex_positions)
                edge_hexes = edge.hex_positions
                
                # Vertex touches this edge if it contains both hexes of the edge
                if edge_hexes.issubset(hex_set):
                    vertices_on_edge.append(vertex_id)
            
            # Record edges for vertices on this edge
            for v_id in vertices_on_edge:
                self.vertex_edges[v_id].add(edge_id)
            
            # The vertices on this edge are adjacent to each other
            # (usually 2, but perimeter edges may have only 1)
            if len(vertices_on_edge) >= 2:
                v1, v2 = vertices_on_edge[0], vertices_on_edge[1]
                self.vertex_adjacency[v1].add(v2)
                self.vertex_adjacency[v2].add(v1)
        
        print(f"[DEBUG] Vertex adjacency calculated")
    
    def get_vertex(self, vertex_id: str) -> Optional[Vertex]:
        """Get a vertex by ID"""
        return self.vertices.get(vertex_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID"""
        return self.edges.get(edge_id)
    
    def get_all_vertices(self) -> List[Vertex]:
        """Get all vertices"""
        return list(self.vertices.values())
    
    def get_all_edges(self) -> List[Edge]:
        """Get all edges"""
        return list(self.edges.values())
    
    def get_adjacent_vertices(self, vertex_id: str) -> Set[str]:
        """Get vertex IDs adjacent to a given vertex (within 1 edge)"""
        return self.vertex_adjacency.get(vertex_id, set())
    
    def get_incident_edges(self, vertex_id: str) -> Set[str]:
        """Get edge IDs connected to a given vertex"""
        return self.vertex_edges.get(vertex_id, set())
    
    def can_place_settlement(self, vertex_id: str, player_id: int) -> bool:
        """Check if a settlement can be placed at a vertex"""
        vertex = self.get_vertex(vertex_id)
        if not vertex:
            return False
        
        # Vertex must be empty
        if vertex.settlement_owner is not None:
            return False
        
        # No settlements within 2 vertices (1 edge away)
        adjacent = self.get_adjacent_vertices(vertex_id)
        for adj_v_id in adjacent:
            adj_vertex = self.get_vertex(adj_v_id)
            if adj_vertex and adj_vertex.settlement_owner is not None:
                return False
        
        return True
    
    def can_place_road(self, edge_id: str, player_id: int) -> bool:
        """Check if a road can be placed on an edge"""
        edge = self.get_edge(edge_id)
        if not edge:
            return False
        
        # Edge must be empty
        if edge.road_owner is not None:
            return False
        
        # TODO: Must be connected to player's settlement/city or road
        return True
    
    def place_settlement(self, vertex_id: str, player_id: int) -> bool:
        """Place a settlement at a vertex"""
        if not self.can_place_settlement(vertex_id, player_id):
            return False
        
        vertex = self.get_vertex(vertex_id)
        vertex.settlement_owner = player_id
        vertex.is_city = False
        return True
    
    def place_city(self, vertex_id: str, player_id: int) -> bool:
        """Upgrade a settlement to a city"""
        vertex = self.get_vertex(vertex_id)
        if not vertex or vertex.settlement_owner != player_id:
            return False
        
        vertex.is_city = True
        return True
    
    def place_road(self, edge_id: str, player_id: int) -> bool:
        """Place a road on an edge"""
        if not self.can_place_road(edge_id, player_id):
            return False
        
        edge = self.get_edge(edge_id)
        edge.road_owner = player_id
        return True


if __name__ == "__main__":
    print("Vertex and Edge system loaded")
