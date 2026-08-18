"""
NodKnaKra Game - Loads maps, randomizes terrain, and manages board state
"""

import random
from typing import Dict, List, Optional, TYPE_CHECKING
from nodknaKra_maps_oop import (
    MapConfiguration, HexTemplate, HexType, HarborType,
    SMALL, STANDARD, LARGE
)

if TYPE_CHECKING:
    from nodknaKra_vertices_edges import Vertex, Edge


# Token distribution for each map size
# Tokens for Standard map: 1-2, 2-3, 4-4, 5-5, 5-6, 5-8, 4-9, 4-10, 2-11, 1-12 = 33 tokens
TOKEN_VALUES = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

TOKEN_DISTRIBUTIONS = {
    'small': {
        'values': TOKEN_VALUES,
        'counts': [1, 2, 3, 4, 4, 4, 3, 3, 2, 1],  # 27 tokens
    },
    'standard': {
        'values': TOKEN_VALUES,
        'counts': [1, 2, 4, 5, 5, 5, 4, 4, 2, 1],  # 33 tokens
    },
    'large': {
        'values': TOKEN_VALUES,
        'counts': [2, 3, 5, 7, 7, 7, 5, 5, 3, 2],  # 46 tokens
    },
}

# Harbor types
HARBOR_SPECIFICS = [
    HarborType.WOOD_2_1,
    HarborType.BRICK_2_1,
    HarborType.SHEEP_2_1,
    HarborType.SHEEP_2_1,  # Two sheep ports
    HarborType.WHEAT_2_1,
    HarborType.ORE_2_1,
]

HARBOR_GENERIC = [
    HarborType.GENERIC_3_1,
    HarborType.GENERIC_3_1,
    HarborType.GENERIC_3_1,
    HarborType.GENERIC_3_1,
    HarborType.GENERIC_3_1,
    HarborType.GENERIC_3_1,
]


class GameHex:
    """An actual game hex with all properties including vertex/edge references"""
    
    def __init__(self, position: str, hex_type: HexType):
        self.position = position
        self.hex_type = hex_type
        self.number_token = None
        self.harbor = None
        self.port_vertices = None  # 2 vertices that form the port (if this is a harbor hex)
        self.adjacent_terrain_positions = []
        
        # Vertex references (6 per hex, shared with neighbors)
        self.vertex_top = None
        self.vertex_top_right = None
        self.vertex_bottom_right = None
        self.vertex_bottom = None
        self.vertex_bottom_left = None
        self.vertex_top_left = None
        
        # Edge references (6 per hex, shared with neighbors)
        self.edge_top_right = None    # Between TOP and TOP_RIGHT
        self.edge_right = None         # Between TOP_RIGHT and BOTTOM_RIGHT
        self.edge_bottom_right = None  # Between BOTTOM_RIGHT and BOTTOM
        self.edge_bottom_left = None   # Between BOTTOM and BOTTOM_LEFT
        self.edge_left = None          # Between BOTTOM_LEFT and TOP_LEFT
        self.edge_top_left = None      # Between TOP_LEFT and TOP
    
    def get_vertices(self) -> list:
        """Get all vertices of this hex in clockwise order from top"""
        return [
            self.vertex_top,
            self.vertex_top_right,
            self.vertex_bottom_right,
            self.vertex_bottom,
            self.vertex_bottom_left,
            self.vertex_top_left,
        ]
    
    def get_edges(self) -> list:
        """Get all edges of this hex in clockwise order"""
        return [
            self.edge_top_right,
            self.edge_right,
            self.edge_bottom_right,
            self.edge_bottom_left,
            self.edge_left,
            self.edge_top_left,
        ]
    
    def __repr__(self):
        return f"Hex({self.position}, {self.hex_type.value})"


class Board:
    """Game board - loaded from map configuration with randomized terrain"""
    
    def __init__(self, map_config: MapConfiguration, seed: int = None):
        self.map_config = map_config
        self.hexes: Dict[str, GameHex] = {}
        
        # Hex-graph data
        self.vertices: Dict[str, 'Vertex'] = {}
        self.edges: Dict[str, 'Edge'] = {}
        self.hex_to_pixel: Dict[str, tuple] = {}
        self.hex_to_pixel_func = None  # Will be set by renderer
        
        if seed is not None:
            random.seed(seed)
        
        self._load_map()
        self._randomize_terrain()
        self._distribute_tokens()
        self._assign_harbors()  # Assign harbors (port vertices assigned later after hex-graph)
        # Hex-graph building deferred until renderer provides hex_to_pixel
    
    def finalize_hex_graph(self, hex_to_pixel_func):
        """Build hex-graph using renderer's hex_to_pixel function"""
        self.hex_to_pixel_func = hex_to_pixel_func
        
        # Calculate hex positions using renderer's method
        for hex_pos in self.hexes.keys():
            self.hex_to_pixel[hex_pos] = hex_to_pixel_func(hex_pos)
        
        # Now build the vertex/edge graph
        self._build_hex_graph()
        
        # Assign port vertices to harbor hexes (now that hex-graph exists)
        self._assign_port_vertices_to_harbors()
    
    def _load_map(self):
        """Load hexes from map configuration"""
        for template in self.map_config.hexes:
            game_hex = GameHex(template.position, template.hex_type)
            game_hex.adjacent_terrain_positions = template.adjacent_terrain_positions
            self.hexes[template.position] = game_hex
    

    def _build_hex_graph(self):
        """Build vertices and edges using pre-calculated hex positions"""
        from nodknaKra_vertices_edges import Vertex, Edge
        
        print(f"[DEBUG] Building hex-graph with geometric vertex positions...")
        
        hex_size = 30  # radius (must match renderer's hex_size)
        
        # Create all vertices with geometric positions
        for hex_pos, (hex_x, hex_y) in self.hex_to_pixel.items():
            game_hex = self.hexes[hex_pos]
            
            # Calculate 6 vertices for this hex (pointy-top orientation)
            # Using sin/cos: top at 90°, then 60° apart clockwise
            vertex_positions = {
                'top': (hex_x, hex_y - hex_size),
                'top_right': (hex_x + hex_size * 0.866, hex_y - hex_size * 0.5),
                'bottom_right': (hex_x + hex_size * 0.866, hex_y + hex_size * 0.5),
                'bottom': (hex_x, hex_y + hex_size),
                'bottom_left': (hex_x - hex_size * 0.866, hex_y + hex_size * 0.5),
                'top_left': (hex_x - hex_size * 0.866, hex_y - hex_size * 0.5),
            }
            
            # Create or link to existing vertices
            for vertex_name, (vx, vy) in vertex_positions.items():
                # Round coordinates to avoid floating point issues
                vx, vy = int(round(vx)), int(round(vy))
                vertex_key = f"{vx},{vy}"
                
                # Check if this vertex already exists (shared with neighbor)
                if vertex_key not in self.vertices:
                    vertex = Vertex(
                        vertex_id=vertex_key,
                        pixel_x=vx,
                        pixel_y=vy
                    )
                    self.vertices[vertex_key] = vertex
                else:
                    vertex = self.vertices[vertex_key]
                
                # Track which hexes touch this vertex
                vertex.hex_positions.add(hex_pos)
                
                # Link vertex to hex
                if vertex_name == 'top':
                    game_hex.vertex_top = vertex
                elif vertex_name == 'top_right':
                    game_hex.vertex_top_right = vertex
                elif vertex_name == 'bottom_right':
                    game_hex.vertex_bottom_right = vertex
                elif vertex_name == 'bottom':
                    game_hex.vertex_bottom = vertex
                elif vertex_name == 'bottom_left':
                    game_hex.vertex_bottom_left = vertex
                elif vertex_name == 'top_left':
                    game_hex.vertex_top_left = vertex
        
        # Create edges between adjacent vertices
        for hex_pos, game_hex in self.hexes.items():
            vertices = game_hex.get_vertices()
            
            # Create edges between consecutive vertices
            for i in range(6):
                v1 = vertices[i]
                v2 = vertices[(i + 1) % 6]
                
                if v1 and v2:
                    # Create edge ID from vertex coordinates
                    edge_key = f"{min(v1.vertex_id, v2.vertex_id)}-{max(v1.vertex_id, v2.vertex_id)}"
                    
                    if edge_key not in self.edges:
                        edge = Edge(edge_id=edge_key, vertex1=v1, vertex2=v2)
                        self.edges[edge_key] = edge
                    else:
                        edge = self.edges[edge_key]
                    
                    # Track which hexes touch this edge
                    edge.hex_positions.add(hex_pos)
                    
                    # Link edge to hex
                    if i == 0:
                        game_hex.edge_top_right = edge
                    elif i == 1:
                        game_hex.edge_right = edge
                    elif i == 2:
                        game_hex.edge_bottom_right = edge
                    elif i == 3:
                        game_hex.edge_bottom_left = edge
                    elif i == 4:
                        game_hex.edge_left = edge
                    elif i == 5:
                        game_hex.edge_top_left = edge
        
        print(f"[DEBUG] Created {len(self.vertices)} vertices and {len(self.edges)} edges")
    
    def _randomize_terrain(self):
        """Randomize terrain types while keeping desert at D1"""
        # Get all terrain hexes (excluding desert)
        terrain_hexes = [
            h for h in self.hexes.values() 
            if h.hex_type not in [HexType.WATER, HexType.DESERT]
        ]
        
        # Get all non-desert terrain templates to extract distribution
        terrain_templates = [
            t for t in self.map_config.hexes 
            if t.hex_type not in [HexType.WATER, HexType.DESERT]
        ]
        
        # Extract terrain types from templates (maintaining the distribution)
        terrain_types = [t.hex_type for t in terrain_templates]
        
        # Shuffle terrain types
        random.shuffle(terrain_types)
        
        # Assign shuffled terrain to hexes (excluding desert hex D1)
        terrain_hex_positions = sorted([h.position for h in terrain_hexes])
        
        for pos, terrain_type in zip(terrain_hex_positions, terrain_types):
            self.hexes[pos].hex_type = terrain_type
        
        print(f"[DEBUG] Randomized terrain for {len(terrain_types)} hexes")
    
    def _distribute_tokens(self):
        """Distribute and shuffle number tokens to terrain hexes"""
        # Get token distribution for this map
        map_key = self.map_config.name.lower()
        if map_key not in TOKEN_DISTRIBUTIONS:
            print(f"[WARNING] No token distribution for {map_key}, skipping tokens")
            return
        
        dist = TOKEN_DISTRIBUTIONS[map_key]
        token_values = dist['values']
        token_counts = dist['counts']
        
        # Build list of tokens
        tokens = []
        for value, count in zip(token_values, token_counts):
            tokens.extend([value] * count)
        
        # Shuffle tokens
        random.shuffle(tokens)
        
        # Get terrain hexes (excluding desert)
        terrain_hexes = self.get_terrain_hexes()
        terrain_positions = sorted([h.position for h in terrain_hexes])
        
        # Assign tokens to hexes
        for pos, token_value in zip(terrain_positions, tokens):
            self.hexes[pos].number_token = token_value
        
        print(f"[DEBUG] Distributed {len(tokens)} tokens to {len(terrain_positions)} terrain hexes")
        print(f"[DEBUG] Token distribution: {dict(zip(token_values, token_counts))}")
    
    def _assign_port_vertices_to_harbors(self):
        """Assign port vertices to all harbor hexes"""
        for water_hex in self.get_water_hexes():
            if water_hex.harbor:
                self._assign_port_vertices(water_hex)
                print(f"[DEBUG PORT] Harbor hex {water_hex.position} ({water_hex.harbor.value}): vertices {water_hex.port_vertices}")
    
    def _assign_port_vertices(self, water_hex: GameHex):
        """
        Assign 2 port vertices to a harbor hex.
        Port vertices are the endpoints of an edge that borders both the water hex and a land hex.
        """
        hex_edges = water_hex.get_edges()
        hex_edges = [e for e in hex_edges if e is not None]
        
        if not hex_edges:
            print(f"[WARNING] Harbor hex {water_hex.position} has no edges")
            return
        
        # Find edges that touch at least one land hex
        coastal_edges = []
        for edge in hex_edges:
            if self._edge_touches_land(edge.edge_id):
                coastal_edges.append(edge)
        
        if not coastal_edges:
            print(f"[WARNING] Harbor hex {water_hex.position} has no coastal edges")
            return
        
        # Randomly pick one coastal edge for the port
        port_edge = random.choice(coastal_edges)
        
        # The port vertices are the two endpoints of this edge
        # Extract from edge_id (format: "x1,y1-x2,y2")
        try:
            vertices_str = port_edge.edge_id.split('-')
            vertex_1_id = vertices_str[0]
            vertex_2_id = vertices_str[1]
            water_hex.port_vertices = (vertex_1_id, vertex_2_id)
            print(f"[DEBUG PORT] Harbor hex {water_hex.position} assigned port edge {port_edge.edge_id} with vertices {vertex_1_id}, {vertex_2_id}")
        except Exception as e:
            print(f"[WARNING] Error parsing port edge {port_edge.edge_id}: {e}")
    
    def _edge_touches_land(self, edge_id: str) -> bool:
        """Check if an edge touches at least one land hex"""
        if edge_id not in self.edges:
            return False
        
        # Find all hexes that contain this edge
        for hex_obj in self.hexes.values():
            hex_edges = hex_obj.get_edges()
            for hex_edge in hex_edges:
                if hex_edge and hex_edge.edge_id == edge_id:
                    # Found a hex that contains this edge
                    if hex_obj.hex_type not in [HexType.WATER, HexType.DESERT]:
                        return True  # Found at least one land hex
        
        return False  # Only water/desert hexes
    
    def _assign_harbors(self):
        """Assign harbors to water hexes in alternating pattern"""
        # Get water hexes in perimeter order
        water_hexes = self.get_water_hexes()
        perimeter_hexes = self._get_perimeter_water_hexes(water_hexes)
        
        if len(perimeter_hexes) < 8:
            print(f"[WARNING] Perimeter too small ({len(perimeter_hexes)} hexes), skipping harbors")
            return
        
        print(f"[DEBUG] Perimeter water hexes ({len(perimeter_hexes)}): {perimeter_hexes}")
        
        # Shuffle specific 2:1 harbors
        specific_harbors = HARBOR_SPECIFICS.copy()
        random.shuffle(specific_harbors)
        
        # Shuffle generic 3:1 harbors
        generic_harbors = HARBOR_GENERIC.copy()
        random.shuffle(generic_harbors)
        
        # Apply alternating pattern: 2:1, plain, 3:1, plain, repeat
        harbor_idx_specific = 0
        harbor_idx_generic = 0
        
        for i, water_hex_pos in enumerate(perimeter_hexes):
            water_hex = self.hexes[water_hex_pos]
            
            if i % 4 == 0:  # 2:1 harbor
                if harbor_idx_specific < len(specific_harbors):
                    water_hex.harbor = specific_harbors[harbor_idx_specific]
                    print(f"[DEBUG] Position {i} ({water_hex_pos}): {water_hex.harbor.value}")
                    harbor_idx_specific += 1
            elif i % 4 == 2:  # 3:1 harbor
                if harbor_idx_generic < len(generic_harbors):
                    water_hex.harbor = generic_harbors[harbor_idx_generic]
                    print(f"[DEBUG] Position {i} ({water_hex_pos}): {water_hex.harbor.value}")
                    harbor_idx_generic += 1
            else:
                print(f"[DEBUG] Position {i} ({water_hex_pos}): plain water")
        
        print(f"[DEBUG] Assigned {harbor_idx_specific} specific 2:1 harbors (of {len(specific_harbors)} available)")
        print(f"[DEBUG] Assigned {harbor_idx_generic} generic 3:1 harbors (of {len(generic_harbors)} available)")
    
    def _get_perimeter_water_hexes(self, water_hexes: List[GameHex]) -> List[str]:
        """Get water hexes in perimeter order (clockwise from top-left)"""
        # For Standard map: 
        # Row A: all 7 (top)
        # Rows B-F: just left and right edges
        # Row G: all 7 (bottom)
        
        perimeter = []
        
        # Top row (A) - left to right
        row_a = sorted([h for h in water_hexes if h.position[0] == 'A'], 
                      key=lambda h: int(h.position[1:]))
        perimeter.extend([h.position for h in row_a])
        
        # Right side - going down (B7, B8, C9, D10, E9, F8)
        # These are rightmost water hexes of each middle row
        for row_letter in ['B', 'C', 'D', 'E', 'F']:
            row_hexes = [h for h in water_hexes if h.position[0] == row_letter]
            if row_hexes:
                rightmost = max(row_hexes, key=lambda h: int(h.position[1:]))
                perimeter.append(rightmost.position)
        
        # Bottom row (G) - right to left
        row_g = sorted([h for h in water_hexes if h.position[0] == 'G'], 
                      key=lambda h: int(h.position[1:]), reverse=True)
        perimeter.extend([h.position for h in row_g])
        
        # Left side - going up (F1, E1, D2, C1, B1)
        # These are leftmost water hexes of each middle row (going up)
        for row_letter in ['F', 'E', 'D', 'C', 'B']:
            row_hexes = [h for h in water_hexes if h.position[0] == row_letter]
            if row_hexes:
                leftmost = min(row_hexes, key=lambda h: int(h.position[1:]))
                perimeter.append(leftmost.position)
        
        return perimeter
    
    def get_hex(self, position: str) -> GameHex:
        """Get hex by position"""
        return self.hexes.get(position)
    
    def get_all_hexes(self) -> Dict[str, GameHex]:
        """Get all hexes"""
        return self.hexes
    
    def get_terrain_hexes(self) -> List[GameHex]:
        """Get all terrain hexes (excluding desert and water)"""
        return [h for h in self.hexes.values() if h.hex_type not in [HexType.WATER, HexType.DESERT]]
    
    def get_water_hexes(self) -> List[GameHex]:
        """Get all water hexes"""
        return [h for h in self.hexes.values() if h.hex_type == HexType.WATER]
    
    def get_desert_hex(self) -> GameHex:
        """Get the desert hex"""
        return next((h for h in self.hexes.values() if h.hex_type == HexType.DESERT), None)
    
    def show_board(self):
        """Display the board"""
        print(f"\n{'='*70}")
        print(f"BOARD: {self.map_config.name.upper()}")
        print(f"{'='*70}")
        
        # Organize by row
        rows = {}
        for pos, hex_obj in self.hexes.items():
            row_letter = pos[0]
            if row_letter not in rows:
                rows[row_letter] = []
            rows[row_letter].append((pos, hex_obj))
        
        # Display each row with terrain and tokens
        for row_letter in sorted(rows.keys()):
            hex_list = rows[row_letter]
            # Sort by column number
            hex_list.sort(key=lambda x: int(x[0][1:]))
            
            hex_display = []
            for pos, hex_obj in hex_list:
                if hex_obj.hex_type == HexType.WATER:
                    # Water hex with optional harbor
                    if hex_obj.harbor and hex_obj.harbor.value:
                        harbor_val = hex_obj.harbor.value
                        # Shorten harbor name for display
                        if "3:1" in harbor_val:
                            harbor_str = "3:1"
                        elif "2:1" in harbor_val:
                            # Extract resource letter from "Wood 2:1", "Ore 2:1", etc.
                            parts = harbor_val.split()
                            if len(parts) >= 1:
                                resource = parts[0][0]  # First letter of resource
                                harbor_str = f"{resource}:1"
                            else:
                                harbor_str = "?:1"
                        else:
                            harbor_str = "?:?"
                        hex_display.append(f"~({harbor_str:3})")
                    else:
                        hex_display.append("~    ")
                elif hex_obj.hex_type == HexType.DESERT:
                    hex_display.append("D    ")
                else:
                    # Terrain with token
                    terrain_char = hex_obj.hex_type.value[0]
                    if hex_obj.number_token:
                        token = f"{hex_obj.number_token:2d}"
                    else:
                        token = "  "
                    hex_display.append(f"{terrain_char}{token}")
            
            print(f"Row {row_letter}: {' '.join(hex_display)}")
        
        # Summary
        print(f"\nTerrain hexes: {len(self.get_terrain_hexes())}")
        print(f"Desert hexes: 1")
        print(f"Water hexes: {len(self.get_water_hexes())}")
        print(f"Harbor hexes: {len([h for h in self.get_water_hexes() if h.harbor])}")
        print(f"Total hexes: {len(self.hexes)}\n")


class Game:
    """Main game class"""
    
    MAPS = {
        'small': SMALL,
        'standard': STANDARD,
        'large': LARGE,
    }
    
    def __init__(self, map_name: str = 'standard', seed: int = None):
        """Initialize game with a map"""
        if map_name not in self.MAPS:
            raise ValueError(f"Unknown map: {map_name}. Choose from {list(self.MAPS.keys())}")
        
        self.map_name = map_name
        self.map_config = self.MAPS[map_name]
        self.board = Board(self.map_config, seed=seed)
    
    def render_ascii(self):
        """Show ASCII board representation"""
        self.board.show_board()
    
    def get_board_data(self) -> Dict:
        """Get board data for rendering"""
        return {
            'map_name': self.map_name,
            'hexes': self.board.get_all_hexes(),
            'terrain_hexes': self.board.get_terrain_hexes(),
            'water_hexes': self.board.get_water_hexes(),
            'desert_hex': self.board.get_desert_hex(),
        }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NodKnaKra Game - Board Generation Test")
    print("="*70)
    
    # Test all three maps
    for map_name in ['small', 'standard', 'large']:
        game = Game(map_name=map_name, seed=42)
        game.render_ascii()
    
    print("="*70)
    print("All maps generated successfully!")
    print("="*70 + "\n")
