"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_game.py
EDIT HISTORY (most recent first):
2026-08-18 - Claude - FINAL FIX: Added vertex deduplication pass to merge vertices within 2px (fixes floating-point rounding from trig); ensures perfect adjacency
2026-08-18 - Claude - CRITICAL MATH FIX: Replace hardcoded 0.866 approximation with trigonometric vertex calculation using cos/sin for perfect rounding
2026-08-18 - Claude - FIX: Port assignment now handles corner hexes with no coastal edges (fallback to coastal vertices)
2026-08-18 - Claude - CRITICAL FIX: hex_size now parameter to finalize_hex_graph() and _build_hex_graph(); eliminates hardcoded hex_size=30 mismatch
2026-08-18 - Claude - Added PlacementPhaseState class for two-player turn tracking (rounds/players/piece order)
2026-08-17 - Claude - Added _assign_port_vertices_to_harbors() method, moved port assignment to after hex-graph build
2026-08-17 - Claude - Added port_vertices attribute to GameHex, _assign_port_vertices() and _edge_touches_land() methods
2026-08-17 - Claude - Initial game logic with maps, terrain randomization, token distribution, harbor assignment
"""

import random
import math
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


class PlacementPhaseState:
    """Track state during placement phase (first two rounds)"""
    
    def __init__(self):
        self.current_round = 1  # Round 1 or 2
        self.current_player = 1  # Player 1 or 2
        self.building_piece_placed = False  # Settlement or City placed this turn
        self.road_placed = False  # Road placed this turn
        self.first_piece_type = None  # "Settlement" or "City"
        
        # Play order
        self.round1_order = [1, 2]  # Player 1 goes first in Round 1
        self.round2_order = [2, 1]  # Player 2 goes first in Round 2 (reverse)
    
    def get_required_piece(self) -> str:
        """Get what piece this player must place first"""
        if self.current_round == 1:
            return "Settlement"  # Round 1 always starts with Settlement
        else:
            return "City"  # Round 2 always starts with City
    
    def get_second_piece(self) -> str:
        """Get what piece this player must place second"""
        first = self.get_required_piece()
        return "City" if first == "Settlement" else "Settlement"
    
    def advance_turn(self) -> bool:
        """Move to next player's turn. Returns False if placement phase complete."""
        order = self.round1_order if self.current_round == 1 else self.round2_order
        current_idx = order.index(self.current_player)
        
        if current_idx == len(order) - 1:
            # End of this round
            if self.current_round == 1:
                # Move to Round 2
                self.current_round = 2
                self.current_player = self.round2_order[0]
            else:
                # Placement phase complete
                return False
        else:
            # Next player this round
            self.current_player = order[current_idx + 1]
        
        # Reset turn flags
        self.building_piece_placed = False
        self.road_placed = False
        self.first_piece_type = None
        return True


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
    
    def finalize_hex_graph(self, hex_to_pixel_func, hex_size: int = 42):
        """Build hex-graph using renderer's hex_to_pixel function
        
        Args:
            hex_to_pixel_func: Function to convert hex position to pixel coordinates
            hex_size: The hex radius size (must match renderer's hex_size)
        """
        self.hex_to_pixel_func = hex_to_pixel_func
        self.hex_size = hex_size  # Store for later use
        
        # Calculate hex positions using renderer's method
        for hex_pos in self.hexes.keys():
            self.hex_to_pixel[hex_pos] = hex_to_pixel_func(hex_pos)
        
        # Now build the vertex/edge graph
        self._build_hex_graph(hex_size)
        
        # Assign port vertices to harbor hexes (now that hex-graph exists)
        self._assign_port_vertices_to_harbors()
    
    def _load_map(self):
        """Load hexes from map configuration"""
        for template in self.map_config.hexes:
            game_hex = GameHex(template.position, template.hex_type)
            game_hex.adjacent_terrain_positions = template.adjacent_terrain_positions
            self.hexes[template.position] = game_hex
    

    def _build_hex_graph(self, hex_size: int = 42):
        """Build vertices and edges using pre-calculated hex positions
        
        Args:
            hex_size: The hex radius size (must match renderer's hex_size)
        """
        from nodknaKra_vertices_edges import Vertex, Edge
        
        print(f"[DEBUG HG] Building hex-graph with geometric vertex positions (hex_size={hex_size})...")
        
        # Create all vertices with geometric positions using trigonometry (pointy-top hexagons)
        vertex_count = 0
        for hex_pos, (hex_x, hex_y) in self.hex_to_pixel.items():
            game_hex = self.hexes[hex_pos]
            
            # For pointy-top hexagon, vertices are at 60° increments starting at 270° (top)
            # Angles: 270°(top), 330°(top-right), 30°(bottom-right), 90°(bottom), 150°(bottom-left), 210°(top-left)
            vertex_names = ['top', 'top_right', 'bottom_right', 'bottom', 'bottom_left', 'top_left']
            vertex_positions = {}
            
            for i, vertex_name in enumerate(vertex_names):
                # Calculate angle for this vertex
                angle_deg = 270 + i * 60  # 270, 330, 30, 90, 150, 210 (wraps at 360)
                angle_rad = math.radians(angle_deg)
                
                # Calculate vertex position using trigonometry, then round to integer
                vx = int(round(hex_x + hex_size * math.cos(angle_rad)))
                vy = int(round(hex_y + hex_size * math.sin(angle_rad)))
                vertex_key = f"{vx},{vy}"
                
                # Check if this vertex already exists (shared with neighbor)
                if vertex_key not in self.vertices:
                    vertex = Vertex(
                        vertex_id=vertex_key,
                        pixel_x=vx,
                        pixel_y=vy
                    )
                    self.vertices[vertex_key] = vertex
                    vertex_count += 1
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
        
        print(f"[DEBUG HG] Created {len(self.vertices)} total vertices ({vertex_count} new)")
        
        # DEDUPLICATION PASS: Merge vertices that are within 2 pixels of each other
        # This fixes floating-point rounding errors from trigonometric calculations
        print(f"[DEBUG HG] Starting vertex deduplication (tolerance: 2 pixels)...")
        self._merge_nearby_vertices(tolerance=2)
        
        # Create edges between adjacent vertices
        edge_count = 0
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
                        edge_count += 1
                        if hex_pos in ['B2', 'C2']:  # Debug sample hexes
                            print(f"[DEBUG HG EDGE] {hex_pos}: created edge {edge_key}")
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
        
        print(f"[DEBUG HG] Created {len(self.edges)} total edges ({edge_count} new)")
        print(f"[DEBUG HG] FINAL AFTER DEDUP: {len(self.vertices)} vertices and {len(self.edges)} edges")
        
        # Validate that vertices are properly connected
        self._validate_hex_graph_connections()
    
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
    
    def _validate_hex_graph_connections(self):
        """Validate that adjacent vertices are connected by edges"""
        print(f"\n[DEBUG HG VALIDATION] Checking vertex connectivity...")
        
        # CRITICAL CHECK: Make sure all edges point to vertices that still exist
        print(f"[DEBUG HG VALIDATION] Checking edge/vertex consistency...")
        invalid_edges = 0
        for edge_id, edge in self.edges.items():
            if not edge.vertex1 or not edge.vertex2:
                print(f"[ERROR] Edge {edge_id} has None vertex!")
                invalid_edges += 1
            elif edge.vertex1.vertex_id not in self.vertices:
                print(f"[ERROR] Edge {edge_id}: vertex1 {edge.vertex1.vertex_id} not in vertices dict!")
                invalid_edges += 1
            elif edge.vertex2.vertex_id not in self.vertices:
                print(f"[ERROR] Edge {edge_id}: vertex2 {edge.vertex2.vertex_id} not in vertices dict!")
                invalid_edges += 1
        
        if invalid_edges > 0:
            print(f"[ERROR] Found {invalid_edges} invalid edges!")
        else:
            print(f"[OK] All {len(self.edges)} edges point to valid vertices")
        
        # Check a few specific vertices to see if they're connected
        test_vertices = list(self.vertices.items())[:10]  # Sample first 10 vertices
        
        for vertex_id, vertex in test_vertices:
            # Find all edges containing this vertex
            connected_vertices = set()
            for edge_id, edge in self.edges.items():
                if edge.vertex1 and edge.vertex1.vertex_id == vertex_id:
                    connected_vertices.add(edge.vertex2.vertex_id)
                elif edge.vertex2 and edge.vertex2.vertex_id == vertex_id:
                    connected_vertices.add(edge.vertex1.vertex_id)
            
            print(f"[DEBUG HG VAL] Vertex {vertex_id}: connected to {len(connected_vertices)} vertices: {connected_vertices}")
            
            # For vertices with hexes, print which hexes they touch
            if hasattr(vertex, 'hex_positions'):
                print(f"[DEBUG HG VAL]   Touches hexes: {vertex.hex_positions}")
    
    def _merge_nearby_vertices(self, tolerance: int = 2):
        """
        Merge vertices that are within tolerance pixels of each other.
        This fixes floating-point rounding errors from trigonometric calculations.
        Adjacent hexes may calculate vertices at slightly different coordinates.
        """
        print(f"[DEBUG MERGE] Deduplicating vertices with tolerance={tolerance}px...")
        
        vertices_list = list(self.vertices.items())
        merged_count = 0
        skip_indices = set()  # Indices of vertices already merged
        
        # For each vertex, check if any other vertex is within tolerance
        for i, (vid1, v1) in enumerate(vertices_list):
            if i in skip_indices:
                continue
            
            # Find all vertices within tolerance of this one
            nearby_indices = [i]
            for j in range(i + 1, len(vertices_list)):
                if j in skip_indices:
                    continue
                
                vid2, v2 = vertices_list[j]
                dx = v1.pixel_x - v2.pixel_x
                dy = v1.pixel_y - v2.pixel_y
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance <= tolerance:
                    nearby_indices.append(j)
            
            # If we found duplicates, merge them
            if len(nearby_indices) > 1:
                # Use the first vertex as the canonical one
                canonical_vid = vertices_list[nearby_indices[0]][0]
                canonical_vertex = self.vertices[canonical_vid]
                
                # Merge all duplicates into the canonical vertex
                for idx in nearby_indices[1:]:
                    dup_vid, dup_vertex = vertices_list[idx]
                    
                    # Merge hex positions
                    if hasattr(canonical_vertex, 'hex_positions'):
                        canonical_vertex.hex_positions.update(dup_vertex.hex_positions)
                    
                    # Update all edges pointing to the duplicate to point to canonical
                    for edge_id, edge in list(self.edges.items()):
                        if edge.vertex1 and edge.vertex1.vertex_id == dup_vid:
                            edge.vertex1 = canonical_vertex
                        if edge.vertex2 and edge.vertex2.vertex_id == dup_vid:
                            edge.vertex2 = canonical_vertex
                    
                    # Update all hex references
                    for hex_obj in self.hexes.values():
                        if hex_obj.vertex_top and hex_obj.vertex_top.vertex_id == dup_vid:
                            hex_obj.vertex_top = canonical_vertex
                        if hex_obj.vertex_top_right and hex_obj.vertex_top_right.vertex_id == dup_vid:
                            hex_obj.vertex_top_right = canonical_vertex
                        if hex_obj.vertex_bottom_right and hex_obj.vertex_bottom_right.vertex_id == dup_vid:
                            hex_obj.vertex_bottom_right = canonical_vertex
                        if hex_obj.vertex_bottom and hex_obj.vertex_bottom.vertex_id == dup_vid:
                            hex_obj.vertex_bottom = canonical_vertex
                        if hex_obj.vertex_bottom_left and hex_obj.vertex_bottom_left.vertex_id == dup_vid:
                            hex_obj.vertex_bottom_left = canonical_vertex
                        if hex_obj.vertex_top_left and hex_obj.vertex_top_left.vertex_id == dup_vid:
                            hex_obj.vertex_top_left = canonical_vertex
                    
                    # Remove the duplicate vertex
                    del self.vertices[dup_vid]
                    skip_indices.add(idx)
                    merged_count += 1
                    print(f"[DEBUG MERGE] Merged {dup_vid} into {canonical_vid}")
        
        print(f"[DEBUG MERGE] Deduplication complete: merged {merged_count} vertices")
        print(f"[DEBUG MERGE] Final vertex count: {len(self.vertices)}")
    
    def _assign_port_vertices_to_harbors(self):
        """Assign port vertices to all harbor hexes"""
        print(f"[DEBUG PORT INIT] Starting port assignment for {len([h for h in self.get_water_hexes() if h.harbor])} harbor hexes")
        for water_hex in self.get_water_hexes():
            if water_hex.harbor:
                self._assign_port_vertices(water_hex)
                if water_hex.port_vertices:
                    print(f"[DEBUG PORT SUCCESS] Harbor hex {water_hex.position} ({water_hex.harbor.value}): vertices {water_hex.port_vertices}")
                else:
                    print(f"[DEBUG PORT FAILED] Harbor hex {water_hex.position} ({water_hex.harbor.value}): NO VERTICES ASSIGNED")
    
    def _assign_port_vertices(self, water_hex: GameHex):
        """
        Assign 2 port vertices to a harbor hex.
        Port vertices are endpoints of an edge that borders both water and land.
        For corner hexes with no coastal edges, pick 2 random coastal vertices.
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
        
        if coastal_edges:
            # Normal case: pick a coastal edge
            port_edge = random.choice(coastal_edges)
            try:
                vertices_str = port_edge.edge_id.split('-')
                vertex_1_id = vertices_str[0]
                vertex_2_id = vertices_str[1]
                water_hex.port_vertices = (vertex_1_id, vertex_2_id)
                print(f"[DEBUG PORT] Harbor hex {water_hex.position} assigned port edge {port_edge.edge_id} with vertices {vertex_1_id}, {vertex_2_id}")
            except Exception as e:
                print(f"[WARNING] Error parsing port edge {port_edge.edge_id}: {e}")
        else:
            # Corner case: no coastal edges. Find coastal vertices instead.
            print(f"[DEBUG PORT] Harbor hex {water_hex.position} has no coastal edges, finding coastal vertices...")
            coastal_vertices = []
            
            # Get all vertices of this water hex
            for edge in hex_edges:
                if edge.vertex1 and self._vertex_touches_land(edge.vertex1):
                    coastal_vertices.append(edge.vertex1)
                if edge.vertex2 and self._vertex_touches_land(edge.vertex2):
                    coastal_vertices.append(edge.vertex2)
            
            # Remove duplicates
            coastal_vertices = list(set(coastal_vertices))
            
            if len(coastal_vertices) >= 2:
                # Pick 2 random coastal vertices
                selected = random.sample(coastal_vertices, min(2, len(coastal_vertices)))
                vertex_1_id = f"{selected[0].pixel_x},{selected[0].pixel_y}"
                vertex_2_id = f"{selected[1].pixel_x},{selected[1].pixel_y}"
                water_hex.port_vertices = (vertex_1_id, vertex_2_id)
                print(f"[DEBUG PORT] Harbor hex {water_hex.position} assigned coastal vertices {vertex_1_id}, {vertex_2_id}")
            else:
                print(f"[WARNING] Harbor hex {water_hex.position} has no coastal vertices either")
    
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
    
    def _vertex_touches_land(self, vertex) -> bool:
        """Check if a vertex is adjacent to at least one land hex"""
        # Find all hexes that share this vertex
        for hex_obj in self.hexes.values():
            hex_vertices = hex_obj.get_vertices()
            for hex_vertex in hex_vertices:
                if hex_vertex and hex_vertex.pixel_x == vertex.pixel_x and hex_vertex.pixel_y == vertex.pixel_y:
                    # Found a hex that contains this vertex
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
