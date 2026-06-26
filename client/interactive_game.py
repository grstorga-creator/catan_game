"""
Interactive Catan Game with Building Placement
Full game viewer with clickable vertices and edges for building.
"""

import pygame
import sys
from pathlib import Path
from typing import Optional, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from client.renderer import HexRenderer, Colors, Camera
from shared.hex_grid import HexGrid, HexCoordinate
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings
from shared.board_topology import BoardTopology, Vertex, Edge
from shared.player import Player, PlayerColor


class InteractiveGameViewer:
    """Interactive game viewer with building placement."""
    
    def __init__(self, width: int = 1400, height: int = 900):
        """Initialize the interactive game viewer."""
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Settlers of Catan - Interactive Builder")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize renderer and camera
        self.renderer = HexRenderer(hex_size=60)
        self.renderer.init_fonts()
        self.camera = Camera(width, height)
        
        # Game components
        self.settings = GameSettings()
        self.generator = None
        self.grid = None
        self.topology = None
        
        # Test players for building
        self.players = [
            Player(0, "Red", PlayerColor.RED),
            Player(1, "Blue", PlayerColor.BLUE),
            Player(2, "White", PlayerColor.WHITE),
            Player(3, "Orange", PlayerColor.ORANGE)
        ]
        self.current_player_index = 0
        
        # Give players resources for testing
        for player in self.players:
            for resource in ['wood', 'brick', 'sheep', 'wheat', 'ore']:
                player.add_resource(resource, 10)
        
        # UI state
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.show_help = True
        
        # Building mode
        self.build_mode = None  # 'settlement', 'city', 'road', or None
        self.hovered_vertex = None
        self.hovered_edge = None
        
        # Generate initial map
        self.generate_new_map('standard_3_4_player')
    
    def generate_new_map(self, template_name: str = None):
        """Generate a new random map."""
        if template_name:
            self.settings.set_map_template(template_name)
        
        self.generator = MapGenerator(self.settings)
        self.grid = self.generator.generate_map(randomize=True)
        self.topology = BoardTopology(self.grid)
        self.camera.center_on_board(self.renderer, self.grid)
        
        print(f"\n{'='*60}")
        self.generator.print_map_summary()
        print(f"Vertices: {len(self.topology.vertices)}")
        print(f"Edges: {len(self.topology.edges)}")
    
    def get_current_player(self) -> Player:
        """Get current player."""
        return self.players[self.current_player_index]
    
    def next_player(self):
        """Switch to next player."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(f"\n>>> Now playing: {self.get_current_player().name}")
    
    def get_player_color_rgb(self, player: Player) -> Tuple[int, int, int]:
        """Get RGB color for player."""
        color_map = {
            PlayerColor.RED: (200, 50, 50),
            PlayerColor.BLUE: (50, 100, 200),
            PlayerColor.WHITE: (240, 240, 240),
            PlayerColor.ORANGE: (255, 140, 0),
            PlayerColor.GREEN: (50, 180, 50),
            PlayerColor.BROWN: (139, 90, 43),
            PlayerColor.PURPLE: (160, 50, 200),
            PlayerColor.YELLOW: (255, 215, 0)
        }
        return color_map.get(player.color, (128, 128, 128))
    
    def find_closest_vertex(self, screen_x: int, screen_y: int, max_distance: int = 30) -> Optional[Vertex]:
        """Find the closest vertex to screen coordinates."""
        world_x, world_y = self.camera.screen_to_world(screen_x, screen_y)
        
        closest_vertex = None
        closest_distance = max_distance
        
        for vertex in self.topology.vertices:
            vx, vy = self.renderer.get_vertex_pixel_position(vertex, 0, 0)
            distance = ((vx - world_x) ** 2 + (vy - world_y) ** 2) ** 0.5
            
            if distance < closest_distance:
                closest_distance = distance
                closest_vertex = vertex
        
        return closest_vertex
    
    def find_closest_edge(self, screen_x: int, screen_y: int, max_distance: int = 25) -> Optional[Edge]:
        """Find the closest edge to screen coordinates."""
        world_x, world_y = self.camera.screen_to_world(screen_x, screen_y)
        
        closest_edge = None
        closest_distance = max_distance
        
        for edge in self.topology.edges:
            pos1, pos2 = self.renderer.get_edge_pixel_position(edge, 0, 0)
            
            # Calculate distance from point to line segment
            distance = self._point_to_line_distance(world_x, world_y, pos1, pos2)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_edge = edge
        
        return closest_edge
    
    def _point_to_line_distance(self, px: float, py: float, 
                                p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Calculate distance from point to line segment."""
        x1, y1 = p1
        x2, y2 = p2
        
        # Line segment length squared
        length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        if length_sq == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        # Parameter t of closest point on line segment
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / length_sq))
        
        # Closest point on line segment
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Distance to closest point
        return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keypress(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
            
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)
        
        return True
    
    def handle_keypress(self, key):
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE or key == pygame.K_q:
            pygame.quit()
            sys.exit()
        
        elif key == pygame.K_h:
            self.show_help = not self.show_help
        
        elif key == pygame.K_SPACE or key == pygame.K_r:
            self.generate_new_map()
        
        elif key == pygame.K_c:
            self.camera.center_on_board(self.renderer, self.grid)
        
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.camera.zoom_in()
        
        elif key == pygame.K_MINUS:
            self.camera.zoom_out()
        
        # Building modes
        elif key == pygame.K_s:
            self.build_mode = 'settlement' if self.build_mode != 'settlement' else None
            print(f"Build mode: {self.build_mode}")
        
        elif key == pygame.K_c:
            self.build_mode = 'city' if self.build_mode != 'city' else None
            print(f"Build mode: {self.build_mode}")
        
        elif key == pygame.K_r:
            self.build_mode = 'road' if self.build_mode != 'road' else None
            print(f"Build mode: {self.build_mode}")
        
        elif key == pygame.K_n:
            self.next_player()
        
        # Map templates
        elif key == pygame.K_1:
            self.generate_new_map('standard_3_4_player')
        elif key == pygame.K_2:
            self.generate_new_map('extended_5_6_player')
        elif key == pygame.K_3:
            self.generate_new_map('large_7_8_player')
        elif key == pygame.K_4:
            self.generate_new_map('small_2_player')
        
        # Arrow keys for panning
        elif key == pygame.K_LEFT:
            self.camera.pan(50, 0)
        elif key == pygame.K_RIGHT:
            self.camera.pan(-50, 0)
        elif key == pygame.K_UP:
            self.camera.pan(0, 50)
        elif key == pygame.K_DOWN:
            self.camera.pan(0, -50)
    
    def handle_mouse_down(self, event):
        """Handle mouse button press."""
        if event.button == 1:  # Left click
            if self.build_mode == 'settlement' and self.hovered_vertex:
                self.try_build_settlement(self.hovered_vertex)
            elif self.build_mode == 'city' and self.hovered_vertex:
                self.try_build_city(self.hovered_vertex)
            elif self.build_mode == 'road' and self.hovered_edge:
                self.try_build_road(self.hovered_edge)
            else:
                # Start dragging
                self.dragging = True
                self.last_mouse_pos = event.pos
        
        elif event.button == 3:  # Right click - cancel mode
            self.build_mode = None
            print("Build mode: None")
        
        elif event.button == 4:  # Scroll up
            self.camera.zoom_in(0.1)
        
        elif event.button == 5:  # Scroll down
            self.camera.zoom_out(0.1)
    
    def handle_mouse_up(self, event):
        """Handle mouse button release."""
        if event.button == 1:
            self.dragging = False
    
    def handle_mouse_motion(self, event):
        """Handle mouse movement."""
        if self.dragging:
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]
            self.camera.pan(dx, dy)
            self.last_mouse_pos = event.pos
        
        # Update hovered positions
        if self.build_mode in ['settlement', 'city']:
            self.hovered_vertex = self.find_closest_vertex(event.pos[0], event.pos[1])
            self.hovered_edge = None
        elif self.build_mode == 'road':
            self.hovered_edge = self.find_closest_edge(event.pos[0], event.pos[1])
            self.hovered_vertex = None
        else:
            self.hovered_vertex = None
            self.hovered_edge = None
    
    def try_build_settlement(self, vertex: Vertex):
        """Try to build a settlement at vertex."""
        player = self.get_current_player()
        
        # For demo, use setup mode (no road connection required)
        if self.topology.place_settlement(vertex, player.player_id, is_setup=True):
            player.build_settlement(vertex)
            print(f"✓ {player.name} built settlement at {vertex}")
        else:
            print(f"✗ Cannot build settlement at {vertex}")
    
    def try_build_city(self, vertex: Vertex):
        """Try to upgrade to city at vertex."""
        player = self.get_current_player()
        
        if self.topology.place_city(vertex, player.player_id):
            player.build_city(vertex)
            print(f"✓ {player.name} upgraded to city at {vertex}")
        else:
            print(f"✗ Cannot build city at {vertex}")
    
    def try_build_road(self, edge: Edge):
        """Try to build a road at edge."""
        player = self.get_current_player()
        
        # For demo, use setup mode
        if self.topology.place_road(edge, player.player_id, is_setup=True):
            player.build_road(edge)
            print(f"✓ {player.name} built road at {edge}")
        else:
            print(f"✗ Cannot build road at {edge}")
    
    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw the board
        self.renderer.draw_grid(
            self.screen,
            self.grid,
            self.camera.x,
            self.camera.y,
            None,
            None
        )
        
        # Draw buildings
        self.draw_buildings()
        
        # Draw hover highlight
        if self.hovered_vertex and self.build_mode in ['settlement', 'city']:
            self.draw_vertex_hover()
        elif self.hovered_edge and self.build_mode == 'road':
            self.draw_edge_hover()
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_buildings(self):
        """Draw all placed buildings."""
        # Draw roads first (under settlements/cities)
        for edge, player_id in self.topology.roads.items():
            player = self.players[player_id]
            color = self.get_player_color_rgb(player)
            pos1, pos2 = self.renderer.get_edge_pixel_position(edge, self.camera.x, self.camera.y)
            self.renderer.draw_road(self.screen, pos1, pos2, color)
        
        # Draw settlements
        for vertex, player_id in self.topology.settlements.items():
            player = self.players[player_id]
            color = self.get_player_color_rgb(player)
            x, y = self.renderer.get_vertex_pixel_position(vertex, self.camera.x, self.camera.y)
            self.renderer.draw_settlement(self.screen, x, y, color)
        
        # Draw cities
        for vertex, player_id in self.topology.cities.items():
            player = self.players[player_id]
            color = self.get_player_color_rgb(player)
            x, y = self.renderer.get_vertex_pixel_position(vertex, self.camera.x, self.camera.y)
            self.renderer.draw_city(self.screen, x, y, color)
    
    def draw_vertex_hover(self):
        """Draw highlight for hovered vertex."""
        if self.hovered_vertex:
            x, y = self.renderer.get_vertex_pixel_position(
                self.hovered_vertex, self.camera.x, self.camera.y)
            
            # Check if placement is valid
            player = self.get_current_player()
            if self.build_mode == 'settlement':
                can_place = self.topology.can_place_settlement(
                    self.hovered_vertex, player.player_id, is_setup=True)
            else:  # city
                can_place = self.topology.can_place_city(
                    self.hovered_vertex, player.player_id)
            
            color = (100, 255, 100) if can_place else (255, 100, 100)
            self.renderer.draw_vertex_highlight(self.screen, x, y, color)
    
    def draw_edge_hover(self):
        """Draw highlight for hovered edge."""
        if self.hovered_edge:
            pos1, pos2 = self.renderer.get_edge_pixel_position(
                self.hovered_edge, self.camera.x, self.camera.y)
            
            # Check if placement is valid
            player = self.get_current_player()
            can_place = self.topology.can_place_road(
                self.hovered_edge, player.player_id, is_setup=True)
            
            color = (100, 255, 100) if can_place else (255, 100, 100)
            self.renderer.draw_edge_highlight(self.screen, pos1, pos2, color)
    
    def draw_ui(self):
        """Draw UI elements."""
        self.draw_player_info()
        self.draw_build_mode_indicator()
        
        if self.show_help:
            self.draw_help()
    
    def draw_player_info(self):
        """Draw current player info."""
        player = self.get_current_player()
        color = self.get_player_color_rgb(player)
        
        y_offset = 10
        x_offset = 10
        
        lines = [
            f"Player: {player.name}",
            f"Settlements: {len(player.settlements)}/5",
            f"Cities: {len(player.cities)}/4",
            f"Roads: {len(player.roads)}/15",
            f"Victory Points: {player.calculate_victory_points()}",
        ]
        
        for i, line in enumerate(lines):
            text_color = color if i == 0 else Colors.TEXT
            self.draw_text(line, x_offset, y_offset + i * 25, text_color, bg=True)
    
    def draw_build_mode_indicator(self):
        """Draw current build mode."""
        if self.build_mode:
            text = f"BUILD MODE: {self.build_mode.upper()}"
            x = self.width // 2 - 100
            y = 10
            self.draw_text(text, x, y, (255, 200, 0), font='large', bg=True)
    
    def draw_help(self):
        """Draw help text."""
        help_lines = [
            "Controls:",
            "S: Settlement mode",
            "C: City mode",
            "R: Road mode",
            "N: Next player",
            "Click: Place building",
            "Right-click: Cancel",
            "Drag: Pan camera",
            "Scroll: Zoom",
            "H: Toggle help",
            "Q: Quit"
        ]
        
        y_offset = self.height - (len(help_lines) * 22 + 10)
        x_offset = 10
        
        for i, line in enumerate(help_lines):
            self.draw_text(line, x_offset, y_offset + i * 22, Colors.TEXT, 
                         font='small', bg=True)
    
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int],
                 font: str = 'small', bg: bool = False):
        """Draw text with optional background."""
        font_obj = self.renderer.font_large if font == 'large' else self.renderer.font_small
        text_surface = font_obj.render(text, True, color)
        
        if bg:
            padding = 5
            bg_rect = pygame.Rect(
                x - padding,
                y - padding,
                text_surface.get_width() + padding * 2,
                text_surface.get_height() + padding * 2
            )
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 200))
            self.screen.blit(bg_surface, bg_rect)
        
        self.screen.blit(text_surface, (x, y))
    
    def run(self):
        """Main game loop."""
        print("\n" + "="*60)
        print("Settlers of Catan - Interactive Builder")
        print("="*60)
        print("\nControls:")
        print("  S - Settlement build mode")
        print("  C - City build mode")
        print("  R - Road build mode")
        print("  N - Switch player")
        print("  Click to place building")
        print("  Right-click to cancel mode")
        print("  H - Toggle help")
        print("  Q - Quit")
        print(f"\nStarting player: {self.get_current_player().name}")
        
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()


def main():
    """Entry point."""
    viewer = InteractiveGameViewer()
    viewer.run()


if __name__ == "__main__":
    main()
