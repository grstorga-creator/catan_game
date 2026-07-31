"""
NodKnaKra Renderer - Pygame-based visual board renderer for OOP game
"""

import pygame
import sys
from typing import Dict, Tuple
from nodknaKra_game import Game, GameHex
from nodknaKra_maps_oop import HexType


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
    
    def __init__(self, width: int = 800, height: int = 700, hex_size: int = 30):
        pygame.init()
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NodKnaKra Settlers of Catan")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 28)
    
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
                token_text = self.font.render(str(hex_obj.number_token), True, token_color)
                token_rect = token_text.get_rect(center=position)
                self.screen.blit(token_text, token_rect)
        
        # For water hexes: draw harbor if present
        if hex_obj.hex_type == HexType.WATER and hex_obj.harbor is not None:
            harbor_val = hex_obj.harbor.value
            
            if "3:1" in harbor_val:
                # Generic 3:1 - single line
                harbor_text = self.font.render("3-1", True, (255, 255, 255))
                harbor_rect = harbor_text.get_rect(center=position)
                self.screen.blit(harbor_text, harbor_rect)
            elif "2:1" in harbor_val:
                # Specific 2:1 - two lines
                # Extract resource name (e.g., "Wheat" from "Wheat 2:1")
                resource = harbor_val.split()[0]
                
                # Draw resource name on top
                resource_text = self.font.render(resource, True, (255, 255, 255))
                resource_rect = resource_text.get_rect(center=(position[0], position[1] - 8))
                self.screen.blit(resource_text, resource_rect)
                
                # Draw 2-1 on bottom
                ratio_text = self.font.render("2-1", True, (255, 255, 255))
                ratio_rect = ratio_text.get_rect(center=(position[0], position[1] + 8))
                self.screen.blit(ratio_text, ratio_rect)
    
    def draw_vertices(self, ve_system, game: Game):
        """Draw all vertices on the board"""
        if not ve_system:
            return
        
        # Draw vertices as small dots
        vertex_radius = 4
        vertex_color = (100, 100, 100)  # Dark gray
        
        for vertex_id, vertex in ve_system.vertices.items():
            # Calculate vertex position from hex positions
            pixel_x = 0
            pixel_y = 0
            
            for hex_pos in vertex.hex_positions:
                hex_pixel = self.hex_to_pixel(hex_pos)
                pixel_x += hex_pixel[0]
                pixel_y += hex_pixel[1]
            
            # Average the positions
            pixel_x //= len(vertex.hex_positions)
            pixel_y //= len(vertex.hex_positions)
            
            # Draw settlement/city if present
            if vertex.settlement_owner is not None:
                # Colors for players
                player_colors = [
                    (255, 0, 0),      # Player 1 - Red
                    (0, 0, 255),      # Player 2 - Blue
                    (255, 255, 0),    # Player 3 - Yellow
                    (0, 255, 0),      # Player 4 - Green
                ]
                color = player_colors[vertex.settlement_owner - 1] if vertex.settlement_owner <= 4 else (128, 128, 128)
                
                # Draw city (filled circle) or settlement (outline circle)
                if vertex.is_city:
                    pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), vertex_radius + 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), (pixel_x, pixel_y), vertex_radius + 2, 2)
                else:
                    pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), vertex_radius)
                    pygame.draw.circle(self.screen, (255, 255, 255), (pixel_x, pixel_y), vertex_radius, 2)
            else:
                # Empty vertex - small gray dot
                pygame.draw.circle(self.screen, vertex_color, (pixel_x, pixel_y), vertex_radius)
                pygame.draw.circle(self.screen, (50, 50, 50), (pixel_x, pixel_y), vertex_radius, 1)
    
    def draw_edges(self, ve_system, game: Game):
        """Draw all edges on the board"""
        if not ve_system:
            return
        
        edge_color = (150, 150, 150)  # Light gray
        edge_width = 1
        
        # Pre-calculate all vertex positions
        vertex_positions = {}
        for vertex_id, vertex in ve_system.vertices.items():
            pixel_x = 0
            pixel_y = 0
            
            for hex_pos in vertex.hex_positions:
                hex_pixel = self.hex_to_pixel(hex_pos)
                pixel_x += hex_pixel[0]
                pixel_y += hex_pixel[1]
            
            pixel_x //= len(vertex.hex_positions)
            pixel_y //= len(vertex.hex_positions)
            vertex_positions[vertex_id] = (pixel_x, pixel_y)
        
        # Draw edges based on vertex adjacency
        drawn_edges = set()
        
        for vertex_id, vertex in ve_system.vertices.items():
            # Get adjacent vertices for this vertex
            adjacent_vertices = ve_system.get_adjacent_vertices(vertex_id)
            
            for adj_vertex_id in adjacent_vertices:
                # Create a canonical edge ID to avoid duplicates
                edge_pair = tuple(sorted([vertex_id, adj_vertex_id]))
                if edge_pair in drawn_edges:
                    continue
                drawn_edges.add(edge_pair)
                
                # Get pixel positions
                p1 = vertex_positions.get(vertex_id)
                p2 = vertex_positions.get(adj_vertex_id)
                
                if p1 and p2:
                    # Check if there's a road on this edge
                    road_color = edge_color
                    road_width = edge_width
                    
                    # Find the edge object for this vertex pair (if exists)
                    for edge_id, edge in ve_system.edges.items():
                        if edge.road_owner is not None:
                            player_colors = [
                                (255, 0, 0),      # Player 1 - Red
                                (0, 0, 255),      # Player 2 - Blue
                                (255, 255, 0),    # Player 3 - Yellow
                                (0, 255, 0),      # Player 4 - Green
                            ]
                            road_color = player_colors[edge.road_owner - 1] if edge.road_owner <= 4 else (128, 128, 128)
                            road_width = 3
                            break
                    
                    pygame.draw.line(self.screen, road_color, p1, p2, road_width)
    
    def render_board(self, game: Game, ve_system=None):
        """Render the complete board"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Clear screen
            self.screen.fill(self.BACKGROUND_COLOR)
            
            # Draw title
            title = self.title_font.render(f"{game.map_name.upper()} Map", True, self.TEXT_COLOR)
            title_rect = title.get_rect(center=(self.width // 2, 20))
            self.screen.blit(title, title_rect)
            
            # Draw all hexes
            board_data = game.get_board_data()
            for position, hex_obj in board_data['hexes'].items():
                pixel_pos = self.hex_to_pixel(position)
                self.draw_hex(hex_obj, pixel_pos)
            
            # Draw edges before vertices so they appear underneath
            if ve_system:
                self.draw_edges(ve_system, game)
            
            # Draw vertices
            if ve_system:
                self.draw_vertices(ve_system, game)
            
            # Draw legend
            legend_x = 20
            legend_y = 60
            legend_items = [
                ("W", HexType.WOOD, "Wood"),
                ("B", HexType.BRICK, "Brick"),
                ("S", HexType.SHEEP, "Sheep"),
                ("T", HexType.WHEAT, "Wheat"),
                ("O", HexType.ORE, "Ore"),
                ("D", HexType.DESERT, "Desert"),
                ("~", HexType.WATER, "Water"),
            ]
            
            for i, (abbr, hex_type, name) in enumerate(legend_items):
                color = self.COLORS[hex_type]
                y = legend_y + i * 30
                
                # Draw small hex
                pygame.draw.circle(self.screen, color, (legend_x + 10, y), 8)
                pygame.draw.circle(self.screen, self.BORDER_COLOR, (legend_x + 10, y), 8, 2)
                
                # Draw label
                label = self.font.render(f"  {name}", True, self.TEXT_COLOR)
                self.screen.blit(label, (legend_x + 25, y - 12))
            
            # Harbor legend
            harbor_legend_y = legend_y + len(legend_items) * 30 + 15
            harbor_label = self.font.render("Harbors:", True, self.TEXT_COLOR)
            self.screen.blit(harbor_label, (legend_x, harbor_legend_y))
            
            harbor_items = [
                "2:1 Specific (W,B,S,T,O)",
                "3:1 Generic",
            ]
            for i, harbor_text in enumerate(harbor_items):
                label = self.font.render(harbor_text, True, self.TEXT_COLOR)
                self.screen.blit(label, (legend_x + 10, harbor_legend_y + 25 + i * 20))
            
            # Vertex/Edge legend
            ve_legend_y = harbor_legend_y + 100
            ve_label = self.font.render("Placement:", True, self.TEXT_COLOR)
            self.screen.blit(ve_label, (legend_x, ve_legend_y))
            
            placement_items = [
                ("●", (100, 100, 100), "Empty vertex"),
                ("●", (255, 0, 0), "P1 Settlement"),
                ("●", (0, 0, 255), "P2 Settlement"),
                ("─", (150, 150, 150), "Road"),
            ]
            for i, (symbol, color, name) in enumerate(placement_items):
                if symbol == "─":
                    pygame.draw.line(self.screen, color, (legend_x + 10, ve_legend_y + 25 + i * 20), 
                                   (legend_x + 30, ve_legend_y + 25 + i * 20), 2)
                else:
                    pygame.draw.circle(self.screen, color, (legend_x + 15, ve_legend_y + 25 + i * 20), 4)
                label = self.font.render(f"  {name}", True, self.TEXT_COLOR)
                self.screen.blit(label, (legend_x + 40, ve_legend_y + 15 + i * 20))
            
            # Draw instructions
            instructions = self.font.render("Press ESC to exit", True, self.TEXT_COLOR)
            self.screen.blit(instructions, (20, self.height - 30))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Main entry point"""
    import sys
    from nodknaKra_vertices_edges import VertexEdgeSystem
    
    # Allow map selection from command line
    map_name = sys.argv[1] if len(sys.argv) > 1 else 'standard'
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    
    print(f"\nLoading {map_name.upper()} map (seed={seed})...")
    game = Game(map_name=map_name, seed=seed)
    
    # Show ASCII representation
    game.render_ascii()
    
    # Initialize vertex/edge system
    print("Building vertex/edge placement system...")
    ve_system = VertexEdgeSystem(game.board)
    
    # Show visual representation with vertices and edges
    print(f"Rendering {map_name} map with vertices, edges, and harbors...")
    print("(Press ESC to exit)\n")
    
    renderer = HexRenderer()
    renderer.render_board(game, ve_system)


if __name__ == "__main__":
    main()
