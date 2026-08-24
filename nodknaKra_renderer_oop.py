"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_renderer_oop.py
EDIT HISTORY (most recent first):
2026-08-18 - Claude - FEATURE: Added longest road calculation (contiguous roads per player, blocked by opponent settlements/cities) with sidebar display
2026-08-18 - Claude - FIX: Road placement now allows roads from any valid endpoint (skip blocked opponent endpoints, check if valid endpoint connects)
2026-08-18 - Claude - FIX: Road placement now blocks roads that pass through opponent settlements/cities (both endpoints checked)
2026-08-18 - Claude - FINAL FIX: Adjacency check now uses actual edge.vertex1/vertex2 objects instead of parsing edge_id strings; ensures correctness after vertex deduplication
2026-08-18 - Claude - FIX: Settlement adjacency corrected to block only distance 0-1, allow distance 2+ (proper Catan rule: one empty vertex between settlements)
2026-08-18 - Claude - FIX: Adjacency check refactored to use edge objects for graph traversal (scalable to any map size/hex_size)
2026-08-18 - Claude - CRITICAL FIX: Pass hex_size to hex-graph building; added vertex click debug output for coordinate matching
2026-08-18 - Claude - Increased hex_size from 30 to 42 (+40%); added token_font (24pt) for hex labels; vertices/edges auto-scale
2026-08-18 - Claude - Increased window to 1400x900; enlarged all fonts (+40%); spelled out full piece names
2026-08-18 - Claude - Compacted sidebar (moved below top panel, 2-row layouts); increased button sizes
2026-08-18 - Claude - Added PlayerInfo class and draw_player_info_panel() for 4-player stat display at top
2026-08-17 - Claude - Added draw_ports() method with colored port circles; added HarborType import
2026-08-17 - Claude - Updated draw_card_hand() to display card images over colored backgrounds with letter codes on top
2026-08-17 - Claude - Added road validation: connectivity to settlements/cities/roads, land hex touching, water hex rejection
2026-08-17 - Claude - Added settlement adjacency validation - settlements cannot be placed next to each other
2026-08-17 - Claude - Added black outlines to roads for visibility; draws cities/settlements last (on top)
2026-08-16 - Claude - CardHand class created with resource card display at bottom of screen
2026-08-16 - Claude - Initial renderer with board drawing, hex-graph visualization, placement palette
"""

import pygame
import sys
import math
import random
from typing import Dict, Tuple, Optional, List
from nodknaKra_game import Game, GameHex
from nodknaKra_maps_oop import HexType, HarborType


class PlayerInfo:
    """Track player stats for display"""
    
    def __init__(self, player_num: int, login_name: str = None):
        self.player_num = player_num
        self.login_name = login_name if login_name else f"Player {player_num}"
        self.victory_points = 0
        self.hand_size = 0  # Number of resource cards
        self.settlements_left = 5
        self.roads_left = 15
        self.cities_left = 4
        self.soldier_cards = 0  # Displayed
        self.development_cards = 0  # Face-down


class CardHand:
    """Manages player's resource cards"""
    
    RESOURCE_TYPES = ["wood", "brick", "sheep", "ore", "wheat"]
    RESOURCE_LABELS = {
        "wood": "W",
        "brick": "B",
        "sheep": "S",
        "ore": "R",
        "wheat": "WH"
    }
    RESOURCE_COLORS = {
        "wood": (200, 230, 201),      # Light green
        "brick": (255, 204, 188),     # Light orange
        "sheep": (255, 249, 196),     # Light yellow
        "ore": (207, 216, 220),       # Light blue-gray
        "wheat": (255, 224, 178),     # Light tan
    }
    
    # Image paths for resource cards
    RESOURCE_IMAGES = {
        "wood": "wood_card_40x55.jpg",
        "brick": "brick_card_40x55.jpg",
        "sheep": "sheep_card_40x55.jpg",
        "ore": "ore_card_40x55.jpg",
        "wheat": "wheat_card_40x55.jpg",
    }
    
    def __init__(self):
        self.cards: List[str] = []  # List of resource strings
        self.images: Dict[str, pygame.Surface] = {}  # Cached card images
    
    def add_card(self, resource: str):
        """Add a card to hand"""
        if resource in self.RESOURCE_TYPES:
            self.cards.append(resource)
    
    def add_random_cards(self, count: int):
        """Add random cards to hand (for testing)"""
        self.cards.clear()
        for _ in range(count):
            self.cards.append(random.choice(self.RESOURCE_TYPES))
    
    def get_counts(self) -> Dict[str, int]:
        """Get count of each resource type"""
        counts = {r: 0 for r in self.RESOURCE_TYPES}
        for card in self.cards:
            if card in counts:
                counts[card] += 1
        return counts
    
    def clear(self):
        """Clear all cards"""
        self.cards.clear()


class PlacementPalette:
    """Manages piece placement state and UI"""
    
    PIECE_TYPES = ["Settlement", "City", "Road"]
    PLAYER_COLORS = {
        1: (255, 0, 0),      # Red
        2: (0, 0, 255),      # Blue
        3: (255, 255, 0),    # Yellow
        4: (0, 255, 0),      # Green
    }
    
    def __init__(self):
        self.selected_piece = "Settlement"  # Default piece
        self.selected_player = 1             # Default to Player 1
        
        # Placed pieces: vertex_id -> player, edge_id -> player
        self.settlements: Dict[str, int] = {}  # vertex_id -> player
        self.cities: Dict[str, int] = {}       # vertex_id -> player
        self.roads: Dict[str, int] = {}        # edge_id -> player
        
        # UI button rectangles (for sidebar)
        self.piece_buttons: Dict[str, pygame.Rect] = {}
        self.player_buttons: Dict[int, pygame.Rect] = {}
        self.action_buttons: Dict[str, pygame.Rect] = {}
        
        self.hover_vertex: Optional[str] = None  # For preview
        self.hover_edge: Optional[str] = None
    
    def get_piece_count(self, player: int) -> Dict[str, int]:
        """Return piece counts for a player"""
        settlements = sum(1 for p in self.settlements.values() if p == player)
        cities = sum(1 for p in self.cities.values() if p == player)
        roads = sum(1 for p in self.roads.values() if p == player)
        return {"settlements": settlements, "cities": cities, "roads": roads}
    
    def place_piece(self, vertex_id: str, piece_type: str, player: int, board: 'Game' = None) -> bool:
        """Place a piece on a vertex. Returns True if successful."""
        if piece_type == "Settlement":
            if vertex_id not in self.settlements and vertex_id not in self.cities:
                # Check that no adjacent vertices have settlements or cities
                if board and self._has_adjacent_settlement_or_city(vertex_id, board):
                    print(f"[DEBUG SETTLEMENT] Cannot place settlement at {vertex_id} - adjacent vertex has settlement/city")
                    return False
                
                self.settlements[vertex_id] = player
                print(f"[DEBUG SETTLEMENT] Placed settlement at {vertex_id} for player {player}")
                return True
        elif piece_type == "City":
            # Can upgrade existing settlement OR place directly on empty vertex (for testing)
            if vertex_id in self.settlements and self.settlements[vertex_id] == player:
                # Upgrade settlement to city
                del self.settlements[vertex_id]
                self.cities[vertex_id] = player
                print(f"[DEBUG CITY] Upgraded settlement to city at {vertex_id} for player {player}")
                return True
            elif vertex_id not in self.settlements and vertex_id not in self.cities:
                # Place city directly (for testing)
                # Check that no adjacent vertices have settlements or cities
                if board and self._has_adjacent_settlement_or_city(vertex_id, board):
                    print(f"[DEBUG CITY] Cannot place city at {vertex_id} - adjacent vertex has settlement/city")
                    return False
                
                self.cities[vertex_id] = player
                print(f"[DEBUG CITY] Placed city at {vertex_id} for player {player}")
                return True
        return False
    
    def _has_adjacent_settlement_or_city(self, vertex_id: str, board: 'Game') -> bool:
        """
        Check if any vertex within 1 edge has a settlement or city.
        In Catan, there must be at least ONE EMPTY VERTEX between settlements.
        This means settlements must be 2+ edges apart.
        
        Blocked vertices:
        - Distance 0: The vertex itself
        - Distance 1: Direct neighbors (adjacent vertices via one edge)
        Allowed: Distance 2+ (neighbors of neighbors)
        
        Uses actual edge objects (not parsing edge_id strings) to ensure accuracy after vertex deduplication.
        """
        blocked_vertices = set([vertex_id])  # The vertex itself is blocked
        
        # Find direct neighbors (1 edge away) - use actual edge objects
        direct_neighbors = set()
        for edge in board.edges.values():
            if not edge.vertex1 or not edge.vertex2:
                continue
            
            v1_id = edge.vertex1.vertex_id
            v2_id = edge.vertex2.vertex_id
            
            # If this edge connects to our vertex, add the other vertex
            if v1_id == vertex_id:
                direct_neighbors.add(v2_id)
            elif v2_id == vertex_id:
                direct_neighbors.add(v1_id)
        
        blocked_vertices.update(direct_neighbors)
        
        # Check if any blocked vertex has a settlement or city
        for blocked_vertex in blocked_vertices:
            if blocked_vertex in self.settlements or blocked_vertex in self.cities:
                print(f"[ADJ REJECT] {vertex_id} too close to {blocked_vertex} (has settlement/city)")
                return True
        
        return False
        return False
    
    def calculate_longest_road(self, player: int, board: 'Game') -> int:
        """
        Calculate the longest contiguous road for a player.
        A contiguous road is a single unbranched path - no branches allowed.
        A chain ends when hitting an opponent's settlement/city or when the road branches.
        
        Args:
            player: Player number (1-4)
            board: Game board
        
        Returns:
            Length of the longest unbranched road (number of connected road segments)
        """
        if not self.roads:
            print(f"[ROAD DEBUG] No roads at all")
            return 0
        
        # Get all roads owned by this player
        player_roads = {edge_id: edge for edge_id, edge in board.edges.items() 
                       if edge_id in self.roads and self.roads[edge_id] == player}
        
        if not player_roads:
            print(f"[ROAD DEBUG P{player}] No roads for this player. Total roads: {len(self.roads)}")
            for edge_id, owner in self.roads.items():
                print(f"[ROAD DEBUG] Edge {edge_id} owned by P{owner}")
            return 0
        
        print(f"[ROAD DEBUG P{player}] Found {len(player_roads)} roads for this player")
        for edge_id in player_roads.keys():
            print(f"[ROAD DEBUG P{player}] Road: {edge_id}")
        
        longest_length = 0
        longest_start = None
        
        # For each road, try it as a starting point and find longest unbranched path from it
        for start_edge_id in player_roads.keys():
            # Try extending in both directions from this road
            length = self._longest_unbranched_path(start_edge_id, player, board, set(), None)
            print(f"[ROAD DEBUG P{player}] Starting from {start_edge_id}: length = {length}")
            if length > longest_length:
                longest_length = length
                longest_start = start_edge_id
        
        print(f"[ROAD DEBUG P{player}] LONGEST ROAD: {longest_length} roads (starting from {longest_start})")
        return longest_length
    
    def _longest_unbranched_path(self, edge_id: str, player: int, board: 'Game', 
                                 visited_edges: set, prev_vertex_id: str = None) -> int:
        """
        Find the longest unbranched path from a starting edge.
        At each vertex, there can be at most 2 roads (one incoming, one outgoing).
        If there are more, the path branches and we stop.
        
        Args:
            edge_id: Current edge being traversed
            player: Player number
            board: Game board
            visited_edges: Set of edges already in this path
            prev_vertex_id: The vertex we came FROM (to avoid going backwards)
        """
        if edge_id in visited_edges:
            print(f"[ROAD PATH] Edge {edge_id} already visited")
            return 0
        
        visited_edges.add(edge_id)
        print(f"[ROAD PATH] Traversing edge {edge_id} (visited: {len(visited_edges)})")
        
        if edge_id not in board.edges:
            print(f"[ROAD PATH] Edge {edge_id} not in board.edges!")
            return 0
        
        edge = board.edges[edge_id]
        if not edge.vertex1 or not edge.vertex2:
            print(f"[ROAD PATH] Edge {edge_id} has missing vertices")
            return 0
        
        current_length = 1  # Count this road
        
        # Determine which end of the edge to extend from
        # If prev_vertex_id is None, we can go from either end
        # Otherwise, we came from prev_vertex_id, so go to the OTHER vertex
        
        if prev_vertex_id is None:
            print(f"[ROAD PATH] Starting point {edge_id}: trying both ends")
            # Starting point - try extending from both ends, pick longest
            max_length = 0
            for next_vertex in [edge.vertex1, edge.vertex2]:
                next_vertex_id = next_vertex.vertex_id
                print(f"[ROAD PATH]   Trying end {next_vertex_id}")
                length = self._extend_from_vertex(next_vertex_id, player, board, visited_edges.copy(), edge_id)
                if length > max_length:
                    max_length = length
            print(f"[ROAD PATH] Edge {edge_id}: max extension = {max_length}, total = {current_length + max_length}")
            return current_length + max_length
        else:
            # We're in the middle of a path - continue to the OTHER end
            if edge.vertex1.vertex_id == prev_vertex_id:
                next_vertex_id = edge.vertex2.vertex_id
            else:
                next_vertex_id = edge.vertex1.vertex_id
            
            print(f"[ROAD PATH] Continuing from {prev_vertex_id} through {edge_id} to {next_vertex_id}")
            extension = self._extend_from_vertex(next_vertex_id, player, board, visited_edges, edge_id)
            print(f"[ROAD PATH] Edge {edge_id}: extension = {extension}, total = {current_length + extension}")
            return current_length + extension
    
    def _extend_from_vertex(self, vertex_id: str, player: int, board: 'Game',
                           visited_edges: set, coming_from_edge_id: str) -> int:
        """
        Try to extend the path from a vertex.
        The path can only continue if there's exactly ONE unvisited connected road.
        If there are 0 or 2+ unvisited roads, the path ends (either terminus or branch).
        """
        # Check if this vertex is blocked by opponent settlement/city
        if vertex_id in self.settlements and self.settlements[vertex_id] != player:
            print(f"[ROAD EXT] Vertex {vertex_id}: blocked by opponent settlement")
            return 0  # Path ends at opponent's settlement
        if vertex_id in self.cities and self.cities[vertex_id] != player:
            print(f"[ROAD EXT] Vertex {vertex_id}: blocked by opponent city")
            return 0  # Path ends at opponent's city
        
        # Find unvisited connected roads from this vertex
        connected_roads = []
        for edge_id, edge in board.edges.items():
            if edge_id in visited_edges:
                continue  # Already part of path
            if edge_id not in self.roads or self.roads[edge_id] != player:
                continue  # Not a player's road
            
            # Check if this edge connects to our vertex
            if edge.vertex1 and edge.vertex1.vertex_id == vertex_id:
                connected_roads.append(edge_id)
            elif edge.vertex2 and edge.vertex2.vertex_id == vertex_id:
                connected_roads.append(edge_id)
        
        print(f"[ROAD EXT] Vertex {vertex_id}: found {len(connected_roads)} unvisited connected roads: {connected_roads}")
        
        # Path can only continue if there's EXACTLY ONE unvisited connected road
        if len(connected_roads) == 0:
            print(f"[ROAD EXT] Vertex {vertex_id}: dead end (0 roads)")
            return 0  # Dead end
        elif len(connected_roads) == 1:
            # Continue on the only connected road
            next_edge_id = connected_roads[0]
            print(f"[ROAD EXT] Vertex {vertex_id}: continuing to {next_edge_id}")
            # Don't add to visited here - let _longest_unbranched_path do it
            return self._longest_unbranched_path(next_edge_id, player, board, visited_edges, vertex_id)
        else:
            # len(connected_roads) >= 2 - this is a branch point!
            print(f"[ROAD EXT] Vertex {vertex_id}: BRANCH POINT ({len(connected_roads)} roads) - stopping")
            return 0  # Path branches here, can't continue
        """Calculate minimum edge distance between two vertices"""
        if v1_id == v2_id:
            return 0
        
        # Simple BFS to find shortest path
        visited = {v1_id}
        queue = [(v1_id, 0)]
        
        while queue:
            current, distance = queue.pop(0)
            if current == v2_id:
                return distance
            
            # Find neighbors
            for edge_id in self.board.edges.keys() if hasattr(self, 'board') else []:
                try:
                    vertices_str = edge_id.split('-')
                    v1, v2 = vertices_str[0], vertices_str[1]
                except:
                    continue
                
                neighbor = None
                if v1 == current:
                    neighbor = v2
                elif v2 == current:
                    neighbor = v1
                
                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        
        return float('inf')
    
    def is_valid_road_placement(self, edge_id: str, player: int, board: 'Game') -> bool:
        """
        Check if a road can be placed on this edge.
        Valid if:
        - Edge is empty AND
        - Edge touches at least one land hex (not water) AND
        - At least ONE endpoint is NOT blocked by opponent piece AND
        - That valid endpoint connects to player's settlement/city/road
        """
        if edge_id in self.roads:
            print(f"[DEBUG ROAD] Edge {edge_id} already has a road")
            return False  # Edge already has a road
        
        if edge_id not in board.edges:
            print(f"[DEBUG ROAD] Edge {edge_id} not in board.edges")
            return False  # Invalid edge
        
        # Check if edge touches at least one land hex (not water)
        if not self._edge_touches_land(edge_id, board):
            print(f"[DEBUG ROAD] Edge {edge_id} only touches water")
            return False  # Edge is between two water hexes
        
        # Extract vertex IDs from edge_id (format: "x1,y1-x2,y2")
        try:
            vertices_str = edge_id.split('-')
            vertex_id_1 = vertices_str[0]  # "x1,y1"
            vertex_id_2 = vertices_str[1]  # "x2,y2"
            print(f"[DEBUG ROAD] Edge {edge_id} has vertices: {vertex_id_1}, {vertex_id_2}")
        except Exception as e:
            print(f"[DEBUG ROAD] Error parsing edge {edge_id}: {e}")
            return False
        
        # Check which endpoints are BLOCKED by opponent pieces
        blocked_endpoints = set()
        for vertex_id in [vertex_id_1, vertex_id_2]:
            if vertex_id in self.settlements:
                settlement_owner = self.settlements[vertex_id]
                if settlement_owner != player:
                    print(f"[DEBUG ROAD] Vertex {vertex_id} has opponent settlement (player {settlement_owner}) - BLOCKED")
                    blocked_endpoints.add(vertex_id)
            
            if vertex_id in self.cities:
                city_owner = self.cities[vertex_id]
                if city_owner != player:
                    print(f"[DEBUG ROAD] Vertex {vertex_id} has opponent city (player {city_owner}) - BLOCKED")
                    blocked_endpoints.add(vertex_id)
        
        # Check valid (non-blocked) endpoints for connections
        print(f"[DEBUG ROAD] Settlements: {self.settlements}, Cities: {self.cities}")
        print(f"[DEBUG ROAD] Player {player} checking endpoints. Blocked: {blocked_endpoints}")
        
        for vertex_id in [vertex_id_1, vertex_id_2]:
            if vertex_id in blocked_endpoints:
                print(f"[DEBUG ROAD] Skipping blocked endpoint {vertex_id}")
                continue  # Skip blocked endpoints
            
            print(f"[DEBUG ROAD] Checking valid endpoint {vertex_id} for player {player}")
            
            # Check if vertex has a settlement or city of same player
            if vertex_id in self.settlements and self.settlements[vertex_id] == player:
                print(f"[DEBUG ROAD] Found own settlement at {vertex_id} - VALID!")
                return True
            
            if vertex_id in self.cities and self.cities[vertex_id] == player:
                print(f"[DEBUG ROAD] Found own city at {vertex_id} - VALID!")
                return True
            
            # Check if vertex connects to a road of same player
            if self._is_connected_to_road(vertex_id, player, board, edge_id):
                print(f"[DEBUG ROAD] Vertex {vertex_id} connects to own road - VALID!")
                return True
        
        print(f"[DEBUG ROAD] No valid endpoints found for edge {edge_id}")
        return False
    
    def _edge_touches_land(self, edge_id: str, board: 'Game') -> bool:
        """Check if an edge touches at least one land hex (not water)"""
        if edge_id not in board.edges:
            return False
        
        # Find all hexes that contain this edge
        for hex_obj in board.hexes.values():
            # Check if this edge is one of the hex's edges
            hex_edges = [
                hex_obj.edge_top_right,
                hex_obj.edge_right,
                hex_obj.edge_bottom_right,
                hex_obj.edge_bottom_left,
                hex_obj.edge_left,
                hex_obj.edge_top_left,
            ]
            
            for hex_edge in hex_edges:
                if hex_edge and hex_edge.edge_id == edge_id:  # ← Compare edge_id strings!
                    # Found a hex that contains this edge
                    # Check if it's not water
                    if hex_obj.hex_type != HexType.WATER:
                        print(f"[DEBUG LAND] Edge {edge_id} touches land hex {hex_obj.position} ({hex_obj.hex_type})")
                        return True  # Found at least one land hex
        
        print(f"[DEBUG LAND] Edge {edge_id} only touches water")
        return False  # Only water hexes (or no hexes)
    
    def _is_connected_to_road(self, vertex_id: str, player: int, board: 'Game', exclude_edge_id: str = None, visited_edges: set = None) -> bool:
        """
        Recursively check if a vertex connects to a road of the same player.
        Uses BFS-like search to find connected roads.
        """
        if visited_edges is None:
            visited_edges = set()
        
        # Find all edges connected to this vertex
        edges_at_vertex = []
        for edge_id in board.edges.keys():
            if edge_id == exclude_edge_id:
                continue
            if edge_id in visited_edges:
                continue
            
            # Extract vertex IDs from edge_id (format: "x1,y1-x2,y2")
            try:
                vertices_str = edge_id.split('-')
                v1_id = vertices_str[0]  # "x1,y1"
                v2_id = vertices_str[1]  # "x2,y2"
            except:
                continue
            
            if v1_id == vertex_id or v2_id == vertex_id:
                edges_at_vertex.append(edge_id)
        
        # Check each edge at this vertex
        for edge_id in edges_at_vertex:
            if edge_id in self.roads and self.roads[edge_id] == player:
                return True  # Found a connected road of same player
            
            visited_edges.add(edge_id)
        
        # For each road found, recursively check the other vertex
        for edge_id in edges_at_vertex:
            if edge_id in self.roads and self.roads[edge_id] == player:
                # Extract the other vertex
                try:
                    vertices_str = edge_id.split('-')
                    v1_id = vertices_str[0]
                    v2_id = vertices_str[1]
                except:
                    continue
                
                other_vertex_id = v2_id if v1_id == vertex_id else v1_id
                
                # Check if other vertex has a settlement/city
                if other_vertex_id in self.settlements and self.settlements[other_vertex_id] == player:
                    return True
                if other_vertex_id in self.cities and self.cities[other_vertex_id] == player:
                    return True
                
                # Recursively check from other vertex
                if self._is_connected_to_road(other_vertex_id, player, board, exclude_edge_id, visited_edges):
                    return True
        
        return False
    
    def place_road(self, edge_id: str, player: int, board: 'Game' = None) -> bool:
        """Place a road on an edge. Returns True if successful."""
        # Validate road placement if board is provided
        if board:
            if not self.is_valid_road_placement(edge_id, player, board):
                return False
        
        if edge_id not in self.roads:
            self.roads[edge_id] = player
            return True
        return False
    
    def remove_piece(self, vertex_id: str) -> bool:
        """Remove a piece from a vertex. Returns True if removed."""
        if vertex_id in self.settlements:
            del self.settlements[vertex_id]
            return True
        elif vertex_id in self.cities:
            del self.cities[vertex_id]
            return True
        return False
    
    def remove_road(self, edge_id: str) -> bool:
        """Remove a road from an edge. Returns True if removed."""
        if edge_id in self.roads:
            del self.roads[edge_id]
            return True
        return False
    
    def clear_all(self):
        """Clear all placed pieces"""
        self.settlements.clear()
        self.cities.clear()
        self.roads.clear()


class HexRenderer:
    """Renders hexagons and game state with Pygame"""
    
    # Colors
    COLORS = {
        HexType.WATER: (100, 150, 200),      # Light blue
        HexType.WOOD: (34, 139, 34),         # Forest green
        HexType.BRICK: (205, 92, 92),        # Brick red
        HexType.SHEEP: (240, 230, 200),      # Wheat/beige
        HexType.WHEAT: (255, 215, 0),        # Gold
        HexType.ORE: (128, 128, 128),        # Gray
        HexType.DESERT: (255, 222, 89),      # Sandy yellow
    }
    
    BORDER_COLOR = (0, 0, 0)
    TEXT_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (200, 200, 200)
    
    def __init__(self, width: int = 1400, height: int = 900, hex_size: int = 42, sidebar_width: int = 200):
        pygame.init()
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.sidebar_width = sidebar_width
        self.board_x_start = sidebar_width  # Board starts after sidebar
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NodKnaKra Settlers of Catan - Placement Tool")
        self.clock = pygame.time.Clock()
        
        # Larger, more readable fonts
        self.font = pygame.font.Font(None, 20)           # Was 14
        self.small_font = pygame.font.Font(None, 16)     # Was 12
        self.card_font = pygame.font.Font(None, 13)      # Was 10
        self.title_font = pygame.font.Font(None, 36)     # Was 28
        self.token_font = pygame.font.Font(None, 24)     # For hex labels (scales with larger hexes)
        
        # Placement palette
        self.palette = PlacementPalette()
        
        # Card hand for testing
        self.card_hand = CardHand()
        self.card_hand.add_random_cards(12)  # Start with 12 random cards
        
        # Player info (4 players max)
        self.player_info = [
            PlayerInfo(1, "Gordon"),
            PlayerInfo(2, "Claude"),
            PlayerInfo(3, "Frank"),
            PlayerInfo(4, "Wayne"),
        ]
        self.current_player = 1  # Player 1 starts
        
        # Load card images
        self.load_card_images()
    
    def load_card_images(self):
        """Load card images from files"""
        for resource, image_file in CardHand.RESOURCE_IMAGES.items():
            try:
                img = pygame.image.load(image_file)
                self.card_hand.images[resource] = img
                print(f"[DEBUG] Loaded card image for {resource}: {image_file}")
            except pygame.error as e:
                print(f"[WARNING] Could not load {resource} card image ({image_file}): {e}")
                self.card_hand.images[resource] = None
    
    def find_vertex_at_position(self, board, mouse_x: int, mouse_y: int, threshold: int = 10) -> Optional[str]:
        """Find vertex near mouse position. Returns vertex_id or None."""
        if not board.vertices:
            print(f"[DEBUG] No vertices in board!")
            return None
        
        closest_vertex = None
        closest_distance = threshold
        
        # Debug: show first 5 vertices and their coordinates
        vertex_list = list(board.vertices.items())
        if len(vertex_list) > 0:
            print(f"[DEBUG] Sample vertices (first 3):")
            for vid, v in vertex_list[:3]:
                print(f"  {vid}: pixel_x={v.pixel_x}, pixel_y={v.pixel_y}")
        
        print(f"[DEBUG] Mouse click at: ({mouse_x}, {mouse_y})")
        
        for vertex_id, vertex in board.vertices.items():
            dx = vertex.pixel_x - mouse_x
            dy = vertex.pixel_y - mouse_y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < closest_distance:
                closest_distance = distance
                closest_vertex = vertex_id
        
        if closest_vertex:
            v = board.vertices[closest_vertex]
            print(f"[DEBUG] FOUND vertex {closest_vertex} at pixel ({v.pixel_x}, {v.pixel_y}), distance {closest_distance:.1f}")
        else:
            print(f"[DEBUG] NO vertex found within threshold {threshold}. Closest was {closest_distance:.1f} away")
        
        return closest_vertex
    
    def find_edge_at_position(self, board, mouse_x: int, mouse_y: int, threshold: int = 8) -> Optional[str]:
        """Find edge near mouse position. Returns edge_id or None."""
        for edge_id, edge in board.edges.items():
            if not edge.vertex1 or not edge.vertex2:
                continue
            
            # Distance from point to line segment
            x1, y1 = edge.vertex1.pixel_x, edge.vertex1.pixel_y
            x2, y2 = edge.vertex2.pixel_x, edge.vertex2.pixel_y
            
            # Calculate distance from point to line
            dx = x2 - x1
            dy = y2 - y1
            length_sq = dx*dx + dy*dy
            
            if length_sq == 0:
                distance = math.sqrt((mouse_x - x1)**2 + (mouse_y - y1)**2)
            else:
                t = max(0, min(1, ((mouse_x - x1)*dx + (mouse_y - y1)*dy) / length_sq))
                closest_x = x1 + t * dx
                closest_y = y1 + t * dy
                distance = math.sqrt((mouse_x - closest_x)**2 + (mouse_y - closest_y)**2)
            
            if distance < threshold:
                return edge_id
        
        return None
    
    def hex_to_pixel(self, position: str, offset_x: int = 0, offset_y: int = 0) -> Tuple[int, int]:
        """Convert hex position (A1, B5, etc.) to pixel coordinates - pointy-top orientation"""
        row_letter = position[0]
        col_num = int(position[1:])
        
        # Row letter to row index (A=0, B=1, ... G=6)
        row_idx = ord(row_letter) - ord('A')
        
        # Pointy-top hex spacing (edges should touch perfectly)
        # For pointy-top hexes: horizontal spacing = hex_size * sqrt(3), vertical = hex_size * 1.5
        hex_width = self.hex_size * 1.732   # sqrt(3) horizontal spacing
        hex_height = self.hex_size * 1.5    # vertical spacing
        
        # Center of screen
        center_x = self.width // 2
        center_y = self.height // 2 + 20
        
        # Row widths: A=7, B=8, C=9, D=10 (center), E=9, F=8, G=7
        row_widths = [7, 8, 9, 10, 9, 8, 7]
        row_width = row_widths[row_idx]
        
        # Vertical position
        y = center_y + (row_idx - 3) * hex_height
        
        # Horizontal position - center each row under the widest (row D)
        # col_num is 1-indexed, so subtract 1 for 0-indexed
        x = center_x + (col_num - 1 - row_width / 2 + 0.5) * hex_width
        
        return int(x + offset_x), int(y + offset_y)
    
    def draw_hexagon(self, center: Tuple[int, int], color: Tuple[int, int, int], filled: bool = True):
        """Draw a pointy-top hexagon (point at top)"""
        import math
        points = []
        for i in range(6):
            # Pointy-top: start at 30 degrees, rotate 60 degrees each vertex
            angle = math.radians(30 + i * 60)
            x = center[0] + self.hex_size * math.cos(angle)
            y = center[1] + self.hex_size * math.sin(angle)
            points.append((x, y))
        
        if filled:
            pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, self.BORDER_COLOR, points, 2)
    
    def draw_hex(self, hex_obj: GameHex, position: Tuple[int, int]):
        """Draw a single game hex"""
        # Draw hexagon background
        color = self.COLORS.get(hex_obj.hex_type, (200, 200, 200))
        self.draw_hexagon(position, color)
        
        # For terrain hexes: draw number token
        if hex_obj.hex_type not in [HexType.WATER, HexType.DESERT]:
            if hex_obj.number_token is not None:
                # Draw white circle for token background
                pygame.draw.circle(self.screen, (255, 255, 255), position, self.hex_size // 2 - 5)
                pygame.draw.circle(self.screen, (0, 0, 0), position, self.hex_size // 2 - 5, 2)
                
                # 6 and 8 tokens are red (most frequently rolled)
                token_color = (255, 0, 0) if hex_obj.number_token in [6, 8] else (0, 0, 0)
                
                # Draw token number
                token_text = self.token_font.render(str(hex_obj.number_token), True, token_color)
                token_rect = token_text.get_rect(center=position)
                self.screen.blit(token_text, token_rect)
        
        # For water hexes: draw harbor if present
        if hex_obj.hex_type == HexType.WATER and hex_obj.harbor is not None:
            harbor_val = hex_obj.harbor.value
            
            if "3:1" in harbor_val:
                # Generic 3:1 - single line
                harbor_text = self.token_font.render("3-1", True, (255, 255, 255))
                harbor_rect = harbor_text.get_rect(center=position)
                self.screen.blit(harbor_text, harbor_rect)
            elif "2:1" in harbor_val:
                # Specific 2:1 - two lines
                # Extract resource name (e.g., "Wheat" from "Wheat 2:1")
                resource = harbor_val.split()[0]
                
                # Draw resource name on top
                resource_text = self.token_font.render(resource, True, (255, 255, 255))
                resource_rect = resource_text.get_rect(center=(position[0], position[1] - 8))
                self.screen.blit(resource_text, resource_rect)
                
                # Draw 2-1 on bottom
                ratio_text = self.token_font.render("2-1", True, (255, 255, 255))
                ratio_rect = ratio_text.get_rect(center=(position[0], position[1] + 8))
                self.screen.blit(ratio_text, ratio_rect)
    
    def draw_sidebar(self, palette: PlacementPalette):
        """Draw the left sidebar with controls - compact layout"""
        # Sidebar background (starts at y=90 to avoid top panel)
        pygame.draw.rect(self.screen, (240, 240, 240), (0, 90, self.sidebar_width, self.height - 90))
        pygame.draw.line(self.screen, (200, 200, 200), (self.sidebar_width, 90), (self.sidebar_width, self.height), 1)
        
        y_pos = 100
        
        # Title (smaller)
        title = self.small_font.render("Placement", True, (0, 0, 0))
        self.screen.blit(title, (8, y_pos))
        y_pos += 16
        
        # Piece selector - 2 rows of buttons (compact)
        label = self.small_font.render("Piece:", True, (80, 80, 80))
        self.screen.blit(label, (8, y_pos))
        y_pos += 13
        
        palette.piece_buttons.clear()
        button_width = (self.sidebar_width - 24) // 2  # 2 buttons per row
        
        for idx, piece_type in enumerate(palette.PIECE_TYPES):
            row = idx // 2  # Row 0 or 1
            col = idx % 2   # Column 0 or 1
            
            x = 8 + col * (button_width + 4)
            rect = pygame.Rect(x, y_pos + row * 28, button_width, 26)
            palette.piece_buttons[piece_type] = rect
            
            # Highlight selected
            if piece_type == palette.selected_piece:
                pygame.draw.rect(self.screen, (70, 140, 220), rect)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(self.screen, (220, 220, 220), rect)
                pygame.draw.rect(self.screen, (180, 180, 180), rect, 1)
                text_color = (0, 0, 0)
            
            text = self.small_font.render(piece_type, True, text_color)  # Full name: Settlement, City, Road
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        y_pos += 60  # Increased spacing for larger buttons
        
        # Player selector - 2 rows of 2 buttons (compact)
        label = self.small_font.render("Player:", True, (80, 80, 80))
        self.screen.blit(label, (8, y_pos))
        y_pos += 13
        
        palette.player_buttons.clear()
        button_width = (self.sidebar_width - 24) // 2
        
        for player in range(1, 5):
            row = (player - 1) // 2
            col = (player - 1) % 2
            
            x = 8 + col * (button_width + 4)
            rect = pygame.Rect(x, y_pos + row * 28, button_width, 26)
            palette.player_buttons[player] = rect
            
            color = palette.PLAYER_COLORS[player]
            
            # Highlight selected
            if player == palette.selected_player:
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
                text_color = (0, 0, 0) if player == 3 else (255, 255, 255)
            else:
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (180, 180, 180), rect, 1)
                text_color = (0, 0, 0) if player == 3 else (255, 255, 255)
            
            text = self.card_font.render(f"P{player}", True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        y_pos += 60  # Increased spacing for larger buttons
        
        # Current selection display (compact)
        label = self.small_font.render("Current:", True, (80, 80, 80))
        self.screen.blit(label, (8, y_pos))
        y_pos += 13
        
        current_box = pygame.Rect(8, y_pos, self.sidebar_width - 16, 35)
        pygame.draw.rect(self.screen, (230, 240, 250), current_box)
        pygame.draw.rect(self.screen, (150, 180, 220), current_box, 1)
        
        piece_text = self.card_font.render(palette.selected_piece, True, (30, 80, 150))
        self.screen.blit(piece_text, (14, y_pos + 3))
        
        player_text = self.card_font.render(f"Player {palette.selected_player}", True, (30, 80, 150))
        self.screen.blit(player_text, (14, y_pos + 15))
        
        y_pos += 40
        
        # Action buttons (compact)
        palette.action_buttons.clear()
        
        undo_rect = pygame.Rect(8, y_pos, (self.sidebar_width - 20) // 2, 20)
        palette.action_buttons["undo"] = undo_rect
        pygame.draw.rect(self.screen, (220, 220, 220), undo_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), undo_rect, 1)
        text = self.card_font.render("Undo", True, (0, 0, 0))
        text_rect = text.get_rect(center=undo_rect.center)
        self.screen.blit(text, text_rect)
        
        clear_rect = pygame.Rect(8 + (self.sidebar_width - 20) // 2 + 4, y_pos, (self.sidebar_width - 20) // 2, 20)
        palette.action_buttons["clear"] = clear_rect
        pygame.draw.rect(self.screen, (220, 220, 220), clear_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), clear_rect, 1)
        text = self.card_font.render("Clear", True, (0, 0, 0))
        text_rect = text.get_rect(center=clear_rect.center)
        self.screen.blit(text, text_rect)
        
        y_pos += 45
        
        # Piece count
        label = self.small_font.render("Piece count:", True, (80, 80, 80))
        self.screen.blit(label, (8, y_pos))
        y_pos += 15
        
        for player in range(1, 5):
            counts = palette.get_piece_count(player)
            count_text = f"P{player}: {counts['settlements']}S {counts['cities']}C {counts['roads']}R"
            text = self.small_font.render(count_text, True, (80, 80, 80))
            self.screen.blit(text, (8, y_pos))
            y_pos += 14
        
        # Longest road display
        y_pos += 5  # Add spacing
        label = self.small_font.render("Longest road:", True, (80, 80, 80))
        self.screen.blit(label, (8, y_pos))
        y_pos += 15
        
        for player in range(1, 5):
            longest = palette.calculate_longest_road(player, self.board)
            road_text = f"P{player}: {longest} roads"
            text = self.small_font.render(road_text, True, (80, 80, 80))
            self.screen.blit(text, (8, y_pos))
            y_pos += 14
    
    def draw_ports(self, board: 'Game'):
        """Draw port indicators at harbor vertices"""
        PORT_RADIUS = 8
        PORT_COLORS = {
            HarborType.WOOD_2_1: (34, 139, 34),        # Green
            HarborType.BRICK_2_1: (205, 92, 92),       # Red/brown
            HarborType.SHEEP_2_1: (240, 230, 200),     # Tan
            HarborType.ORE_2_1: (128, 128, 128),       # Gray
            HarborType.WHEAT_2_1: (255, 215, 0),       # Gold
            HarborType.GENERIC_3_1: (150, 150, 150),   # Dark gray
        }
        
        # Draw ports for all harbor hexes
        for water_hex in board.get_water_hexes():
            if water_hex.harbor and water_hex.port_vertices:
                color = PORT_COLORS.get(water_hex.harbor, (100, 100, 100))
                
                # Get vertex positions
                for vertex_id in water_hex.port_vertices:
                    try:
                        coords = vertex_id.split(',')
                        vertex_x = int(coords[0])
                        vertex_y = int(coords[1])
                        
                        # Draw port circle at vertex
                        pygame.draw.circle(self.screen, color, (vertex_x, vertex_y), PORT_RADIUS)
                        pygame.draw.circle(self.screen, (0, 0, 0), (vertex_x, vertex_y), PORT_RADIUS, 2)  # Black outline
                    except:
                        pass
    
    def draw_placed_pieces(self, palette: PlacementPalette):
        """Draw all placed settlements, cities, and roads on board"""
        # Draw roads first with black outline so they're visible but under pieces
        for edge_id, player in palette.roads.items():
            edge = self.board.edges.get(edge_id)
            
            if edge and edge.vertex1 and edge.vertex2:
                p1 = (edge.vertex1.pixel_x, edge.vertex1.pixel_y)
                p2 = (edge.vertex2.pixel_x, edge.vertex2.pixel_y)
                color = palette.PLAYER_COLORS[player]
                # Draw road with black outline
                pygame.draw.line(self.screen, (0, 0, 0), p1, p2, 8)  # Black outline (8px)
                pygame.draw.line(self.screen, color, p1, p2, 6)      # Colored center (6px)
        
        # Draw settlements (15x15 squares, 50% bigger)
        for vertex_id, player in palette.settlements.items():
            vertex = self.board.vertices.get(vertex_id)
            if vertex:
                color = palette.PLAYER_COLORS[player]
                # 15x15 square, centered on vertex
                rect = pygame.Rect(int(vertex.pixel_x - 7.5), int(vertex.pixel_y - 7.5), 15, 15)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
        
        # Draw cities LAST so they appear on top of roads and settlements
        for vertex_id, player in palette.cities.items():
            vertex = self.board.vertices.get(vertex_id)
            if vertex:
                color = palette.PLAYER_COLORS[player]
                x, y = vertex.pixel_x, vertex.pixel_y
                
                # Draw crown with 3 spires
                # Base (filled rectangle at bottom)
                base_rect = pygame.Rect(x - 9, y + 2, 18, 8)
                pygame.draw.rect(self.screen, color, base_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), base_rect, 2)
                
                # Left spire (triangle)
                left_spire = [(x - 8, y + 2), (x - 5, y - 8), (x - 2, y + 2)]
                pygame.draw.polygon(self.screen, color, left_spire)
                pygame.draw.polygon(self.screen, (0, 0, 0), left_spire, 1)
                
                # Center spire (tallest)
                center_spire = [(x - 2, y + 2), (x, y - 12), (x + 2, y + 2)]
                pygame.draw.polygon(self.screen, color, center_spire)
                pygame.draw.polygon(self.screen, (0, 0, 0), center_spire, 1)
                
                # Right spire (triangle)
                right_spire = [(x + 2, y + 2), (x + 5, y - 8), (x + 8, y + 2)]
                pygame.draw.polygon(self.screen, color, right_spire)
                pygame.draw.polygon(self.screen, (0, 0, 0), right_spire, 1)
    
    def draw_player_info_panel(self):
        """Draw player information at top of screen (4 players)"""
        try:
            panel_height = 90
            player_width = self.width // 4
            panel_bg_color = (220, 220, 220)
            
            # Draw panel background
            pygame.draw.rect(self.screen, panel_bg_color, (0, 0, self.width, panel_height))
            pygame.draw.line(self.screen, (100, 100, 100), (0, panel_height), (self.width, panel_height), 2)
            
            # Draw each player info
            for i, player in enumerate(self.player_info):
                x = i * player_width
                y = 5
                
                # Highlight current player
                if player.player_num == self.current_player:
                    pygame.draw.rect(self.screen, (255, 255, 100), (x, 0, player_width, panel_height), 3)
                
                # Player name
                name_text = self.small_font.render(f"P{player.player_num}: {player.login_name}", True, (0, 0, 0))
                self.screen.blit(name_text, (x + 5, y))
                
                # VP score
                vp_text = self.small_font.render(f"VP: {player.victory_points}", True, (0, 0, 0))
                self.screen.blit(vp_text, (x + 5, y + 14))
                
                # Hand size
                hand_text = self.small_font.render(f"Hand: {player.hand_size}", True, (0, 0, 0))
                self.screen.blit(hand_text, (x + 5, y + 28))
                
                # Pieces left: S/R/C
                pieces_text = self.small_font.render(f"S:{player.settlements_left} R:{player.roads_left} C:{player.cities_left}", True, (0, 0, 0))
                self.screen.blit(pieces_text, (x + 5, y + 42))
                
                # Dev cards
                dev_text = self.small_font.render(f"Dev: {player.development_cards} Sol: {player.soldier_cards}", True, (0, 0, 0))
                self.screen.blit(dev_text, (x + 5, y + 56))
        except Exception as e:
            print(f"[ERROR] Failed to draw player info panel: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_card_hand(self, card_hand: CardHand):
        """Draw player's card hand at bottom of screen with resource images over colored backgrounds"""
        # Card display area: x=sidebar_width+10, y=bottom
        start_x = self.sidebar_width + 10
        start_y = self.height - 120  # Bottom of screen with padding
        card_width = 50
        card_height = 70
        gap = 12
        
        # Draw label
        label = self.small_font.render("Hand:", True, (80, 80, 80))
        self.screen.blit(label, (start_x, start_y - 25))
        
        # Draw cards in single row
        for i, resource in enumerate(card_hand.cards):
            x = start_x + i * (card_width + gap)
            y = start_y
            
            # Card background color (resource color)
            color = CardHand.RESOURCE_COLORS.get(resource, (200, 200, 200))
            
            # Draw colored card background
            rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (80, 80, 80), rect, 1)
            
            # Draw card image centered on colored background
            if resource in card_hand.images and card_hand.images[resource]:
                img = card_hand.images[resource]
                # Center image on card
                img_x = x + (card_width - img.get_width()) // 2
                img_y = y + (card_height - img.get_height()) // 2
                self.screen.blit(img, (img_x, img_y))
        
        # Draw letter codes LAST so they appear on top of images
        for i, resource in enumerate(card_hand.cards):
            x = start_x + i * (card_width + gap)
            y = start_y
            
            label_text = CardHand.RESOURCE_LABELS.get(resource, "?")
            label_surface = self.card_font.render(label_text, True, (0, 0, 0))
            self.screen.blit(label_surface, (x + 4, y + 4))
        
        # Draw resource counts below cards
        counts = card_hand.get_counts()
        count_y = start_y + card_height + 10
        count_texts = []
        for resource in CardHand.RESOURCE_TYPES:
            count = counts.get(resource, 0)
            label = CardHand.RESOURCE_LABELS.get(resource, "?")
            count_texts.append(f"{label}:{count}")
        
        count_str = " | ".join(count_texts)
        count_surface = self.small_font.render(count_str, True, (80, 80, 80))
        self.screen.blit(count_surface, (start_x, count_y))
    
    def draw_vertices(self, board, game: Game):
        """Draw settlements and cities on vertices (skip empty vertex indicators)"""
        if not board.vertices:
            return
        
        for vertex_id, vertex in board.vertices.items():
            pixel_x = vertex.pixel_x
            pixel_y = vertex.pixel_y
            
            # Only draw if vertex has a settlement or city
            if vertex.settlement_owner is not None:
                # Colors for players
                player_colors = [
                    (255, 0, 0),      # Player 1 - Red
                    (0, 0, 255),      # Player 2 - Blue
                    (255, 255, 0),    # Player 3 - Yellow
                    (0, 255, 0),      # Player 4 - Green
                ]
                color = player_colors[vertex.settlement_owner - 1] if vertex.settlement_owner <= 4 else (128, 128, 128)
                
                # Draw city (circle with crown) or settlement (square with bold black outline)
                if vertex.is_city:
                    # City: 7px radius circle with white border and crown symbol
                    pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), 7)
                    pygame.draw.circle(self.screen, (255, 255, 255), (pixel_x, pixel_y), 7, 2)
                else:
                    # Settlement: 10x10 square with 2px bold black outline
                    # Draw filled square with player color
                    rect = pygame.Rect(pixel_x - 5, pixel_y - 5, 10, 10)
                    pygame.draw.rect(self.screen, color, rect)
                    # Draw bold black outline (2px)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
    
    def draw_edges(self, board, game: Game):
        """Draw all edges on the board using board's hex-graph"""
        if not board.edges:
            return
        
        edge_color = (150, 150, 150)  # Light gray
        edge_width = 1  # Empty edges are thin (1px)
        
        drawn_edges = set()
        
        for edge_id, edge in board.edges.items():
            if edge_id in drawn_edges:
                continue
            drawn_edges.add(edge_id)
            
            if not edge.vertex1 or not edge.vertex2:
                continue
            
            # Get pixel positions from vertices
            p1 = (edge.vertex1.pixel_x, edge.vertex1.pixel_y)
            p2 = (edge.vertex2.pixel_x, edge.vertex2.pixel_y)
            
            # Determine color based on road owner
            road_color = edge_color
            road_width = edge_width
            
            if edge.road_owner is not None:
                player_colors = [
                    (255, 0, 0),      # Player 1 - Red
                    (0, 0, 255),      # Player 2 - Blue
                    (255, 255, 0),    # Player 3 - Yellow
                    (0, 255, 0),      # Player 4 - Green
                ]
                road_color = player_colors[edge.road_owner - 1] if edge.road_owner <= 4 else (128, 128, 128)
                road_width = 6  # 6px thick roads
            
            pygame.draw.line(self.screen, road_color, p1, p2, road_width)
    
    def render_board(self, game: Game, ve_system=None):
        """Render the complete board with placement palette"""
        running = True
        self.board = game.board  # Store reference for drawing placed pieces
        undo_stack = []  # For undo functionality
        
        print(f"[DEBUG] Board initialized with {len(game.board.vertices)} vertices and {len(game.board.edges)} edges")
        print(f"[DEBUG] Renderer hex_size: {self.hex_size}, Sidebar width: {self.sidebar_width}, Board starts at x={self.sidebar_width}")
        
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        # Deal new random cards (for testing)
                        self.card_hand.add_random_cards(12)
                        print("[DEBUG] Dealt new 12 cards")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Left click
                    if event.button == 1:
                        # Check if clicked on sidebar buttons
                        clicked = False
                        
                        # Piece type buttons
                        for piece_type, rect in self.palette.piece_buttons.items():
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.palette.selected_piece = piece_type
                                clicked = True
                                break
                        
                        # Player buttons
                        if not clicked:
                            for player, rect in self.palette.player_buttons.items():
                                if rect.collidepoint(mouse_x, mouse_y):
                                    self.palette.selected_player = player
                                    clicked = True
                                    break
                        
                        # Action buttons
                        if not clicked:
                            for action, rect in self.palette.action_buttons.items():
                                if rect.collidepoint(mouse_x, mouse_y):
                                    if action == "undo" and undo_stack:
                                        action_type, action_data = undo_stack.pop()
                                        if action_type == "settlement":
                                            self.palette.remove_piece(action_data)
                                        elif action_type == "city":
                                            vertex_id = action_data
                                            self.palette.cities.pop(vertex_id, None)
                                            self.palette.settlements[vertex_id] = self.palette.selected_player
                                        elif action_type == "road":
                                            self.palette.remove_road(action_data)
                                    elif action == "clear":
                                        undo_stack.clear()
                                        self.palette.clear_all()
                                    clicked = True
                                    break
                        
                        # Board clicks (place pieces)
                        if not clicked and mouse_x > self.sidebar_width:
                            if self.palette.selected_piece == "Road":
                                edge_id = self.find_edge_at_position(game.board, mouse_x, mouse_y)
                                print(f"[DEBUG] Clicked on board, looking for road at ({mouse_x}, {mouse_y}), found edge: {edge_id}")
                                if edge_id:
                                    if self.palette.place_road(edge_id, self.palette.selected_player, game.board):
                                        print(f"[DEBUG] Placed road on edge {edge_id} for player {self.palette.selected_player}")
                                        undo_stack.append(("road", edge_id))
                                    else:
                                        print(f"[DEBUG] Road placement INVALID - not connected to settlement/city/road for player {self.palette.selected_player}")
                            else:
                                vertex_id = self.find_vertex_at_position(game.board, mouse_x, mouse_y)
                                print(f"[DEBUG] Clicked on board, looking for vertex at ({mouse_x}, {mouse_y}), found: {vertex_id}")
                                if vertex_id:
                                    if self.palette.selected_piece == "Settlement":
                                        if self.palette.place_piece(vertex_id, "Settlement", self.palette.selected_player, game.board):
                                            print(f"[DEBUG] Placed settlement at {vertex_id} for player {self.palette.selected_player}")
                                            undo_stack.append(("settlement", vertex_id))
                                        else:
                                            print(f"[DEBUG] Settlement placement INVALID at {vertex_id}")
                                    elif self.palette.selected_piece == "City":
                                        if self.palette.place_piece(vertex_id, "City", self.palette.selected_player, game.board):
                                            print(f"[DEBUG] Placed city at {vertex_id} for player {self.palette.selected_player}")
                                            undo_stack.append(("city", vertex_id))
                                        else:
                                            print(f"[DEBUG] City placement INVALID at {vertex_id}")
                    
                    # Right click - remove piece
                    elif event.button == 3:
                        if mouse_x > self.sidebar_width:
                            # Try to remove settlement/city
                            vertex_id = self.find_vertex_at_position(game.board, mouse_x, mouse_y, threshold=12)
                            print(f"[DEBUG] Right-click at ({mouse_x}, {mouse_y}), vertex: {vertex_id}")
                            if vertex_id:
                                self.palette.remove_piece(vertex_id)
                                print(f"[DEBUG] Removed piece at {vertex_id}")
                            else:
                                # Try to remove road
                                edge_id = self.find_edge_at_position(game.board, mouse_x, mouse_y, threshold=10)
                                print(f"[DEBUG] No vertex, looking for edge: {edge_id}")
                                if edge_id:
                                    self.palette.remove_road(edge_id)
                                    print(f"[DEBUG] Removed road at {edge_id}")
            
            # Clear screen
            self.screen.fill((245, 245, 240))
            
            # Draw board area (below panel, which is 90px tall)
            pygame.draw.rect(self.screen, (250, 250, 248), (self.sidebar_width, 90, self.width - self.sidebar_width, self.height - 90))
            
            # Draw title (below player info panel)
            title = self.title_font.render(f"{game.map_name.upper()} Map (Placement Tool)", True, self.TEXT_COLOR)
            title_rect = title.get_rect(topleft=(self.sidebar_width + 15, 100))
            self.screen.blit(title, title_rect)
            
            # Draw all hexes
            board_data = game.get_board_data()
            for position, hex_obj in board_data['hexes'].items():
                pixel_pos = self.hex_to_pixel(position)
                self.draw_hex(hex_obj, pixel_pos)
            
            # Draw edges (unowned) before everything
            self.draw_edges(game.board, game)
            
            # Draw vertices (empty only)
            self.draw_vertices(game.board, game)
            
            # Draw ports
            self.draw_ports(game.board)
            
            # Draw placed pieces (roads, settlements, cities) on top
            self.draw_placed_pieces(self.palette)
            
            # Draw sidebar UI
            self.draw_sidebar(self.palette)
            
            # Draw card hand at top of board
            self.draw_card_hand(self.card_hand)
            
            # Instructions
            instructions = self.small_font.render("Right-click to remove | ESC to exit", True, (100, 100, 100))
            self.screen.blit(instructions, (self.sidebar_width + 15, self.height - 25))
            
            # Draw player info panel LAST so it appears on top
            self.draw_player_info_panel()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Main entry point"""
    import sys
    
    # Allow map selection from command line
    map_name = sys.argv[1] if len(sys.argv) > 1 else 'standard'
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    
    print(f"\nLoading {map_name.upper()} map (seed={seed})...")
    game = Game(map_name=map_name, seed=seed)
    
    # Create renderer first
    renderer = HexRenderer()
    
    # Now build hex-graph using renderer's hex_to_pixel method
    print("Building hex-graph using renderer coordinates...")
    game.board.finalize_hex_graph(renderer.hex_to_pixel, hex_size=renderer.hex_size)
    
    # Show ASCII representation
    game.render_ascii()
    
    # Show visual representation with vertices and edges
    print(f"Rendering {map_name} map with vertices, edges, and harbors...")
    print(f"Hex-graph: {len(game.board.vertices)} vertices, {len(game.board.edges)} edges")
    print("(Press ESC to exit)\n")
    
    renderer.render_board(game)


if __name__ == "__main__":
    main()
