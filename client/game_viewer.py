"""
Settlers of Catan - Interactive Game Viewer
Visual display of generated boards with Pygame.
"""

import pygame
import sys
from pathlib import Path
from typing import Tuple

sys.path.append(str(Path(__file__).parent.parent))

from client.renderer import HexRenderer, Colors, Camera
from shared.hex_grid import HexGrid, HexCoordinate
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings


class GameViewer:
    """Main game viewer application."""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """Initialize the game viewer."""
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Settlers of Catan - Board Viewer")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize renderer and camera
        self.renderer = HexRenderer(hex_size=60)
        self.renderer.init_fonts()
        self.camera = Camera(width, height)
        
        # Game state
        self.settings = GameSettings()
        self.generator = None
        self.grid = None
        self.hovered_hex = None
        self.selected_hex = None
        
        # UI state
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.show_help = True
        
        # Generate initial map
        self.generate_new_map('standard_3_4_player')
    
    def generate_new_map(self, template_name: str = None):
        """Generate a new random map."""
        if template_name:
            self.settings.set_map_template(template_name)
        
        self.generator = MapGenerator(self.settings)
        self.grid = self.generator.generate_map(randomize=True)
        self.camera.center_on_board(self.renderer, self.grid)
        
        print(f"\n{'='*60}")
        self.generator.print_map_summary()
    
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
            # Generate new map with same template
            self.generate_new_map()
        
        elif key == pygame.K_c:
            # Center camera on board
            self.camera.center_on_board(self.renderer, self.grid)
        
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.camera.zoom_in()
        
        elif key == pygame.K_MINUS:
            self.camera.zoom_out()
        
        # Map template selection
        elif key == pygame.K_1:
            self.generate_new_map('standard_3_4_player')
        elif key == pygame.K_2:
            self.generate_new_map('extended_5_6_player')
        elif key == pygame.K_3:
            self.generate_new_map('large_7_8_player')
        elif key == pygame.K_4:
            self.generate_new_map('small_2_player')
        elif key == pygame.K_5:
            self.generate_new_map('custom_rectangular')
        
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
            # Start dragging
            self.dragging = True
            self.last_mouse_pos = event.pos
            
            # Also select the hex if clicking on one
            if self.hovered_hex:
                if self.selected_hex == self.hovered_hex:
                    self.selected_hex = None  # Deselect
                else:
                    self.selected_hex = self.hovered_hex
                    self.print_hex_info(self.selected_hex)
        
        elif event.button == 4:  # Scroll up
            self.camera.zoom_in(0.1)
        
        elif event.button == 5:  # Scroll down
            self.camera.zoom_out(0.1)
    
    def handle_mouse_up(self, event):
        """Handle mouse button release."""
        if event.button == 1:  # Left click
            self.dragging = False
    
    def handle_mouse_motion(self, event):
        """Handle mouse movement."""
        if self.dragging:
            # Pan the camera
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]
            self.camera.pan(dx, dy)
            self.last_mouse_pos = event.pos
        
        # Update hovered hex
        world_x, world_y = self.camera.screen_to_world(event.pos[0], event.pos[1])
        hovered_coord = self.renderer.pixel_to_hex(world_x, world_y)
        
        # Check if this coordinate has a tile
        if self.grid.get_tile(hovered_coord):
            self.hovered_hex = hovered_coord
        else:
            self.hovered_hex = None
    
    def print_hex_info(self, coord: HexCoordinate):
        """Print information about a hex tile."""
        tile = self.grid.get_tile(coord)
        if not tile:
            return
        
        print(f"\n--- Hex Info: ({coord.q}, {coord.r}) ---")
        print(f"Resource: {tile.resource.capitalize()}")
        if tile.number_token:
            print(f"Number: {tile.number_token}")
            print(f"Production Probability: {tile.get_production_probability():.3f}")
            print(f"Pip Value: {tile.get_resource_value()}")
        if tile.has_robber:
            print("⚠ Robber Present")
        if tile.port:
            print(f"Port: {tile.port}")
        
        neighbors = self.grid.get_neighbors(coord)
        print(f"Neighbors: {len(neighbors)}")
        for neighbor in neighbors:
            neighbor_str = f"  {neighbor.resource}"
            if neighbor.number_token:
                neighbor_str += f" #{neighbor.number_token}"
            print(neighbor_str)
    
    def draw(self):
        """Draw everything to the screen."""
        # Clear screen
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw the board
        self.renderer.draw_grid(
            self.screen,
            self.grid,
            self.camera.x,
            self.camera.y,
            self.hovered_hex,
            self.selected_hex
        )
        
        # Draw UI
        self.draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI elements (text, help, etc.)."""
        # Draw statistics in top-left
        self.draw_statistics()
        
        # Draw help in bottom-left if enabled
        if self.show_help:
            self.draw_help()
        
        # Draw hovered hex info in top-right
        if self.hovered_hex:
            self.draw_hex_tooltip()
    
    def draw_statistics(self):
        """Draw board statistics."""
        stats = self.generator.get_map_statistics()
        template = self.settings.get_current_map_template()
        
        y_offset = 10
        x_offset = 10
        line_height = 25
        
        lines = [
            f"Map: {template['name'] if template else 'Unknown'}",
            f"Tiles: {stats['total_tiles']}",
            f"Land: {stats['land_tiles']}",
            f"Ports: {stats['ports_placed']}",
            f"Pip Value: {stats['total_pip_value']}",
        ]
        
        if stats['high_number_violations'] > 0:
            lines.append(f"⚠ 6/8 Adjacent: {stats['high_number_violations']}")
        
        for i, line in enumerate(lines):
            self.draw_text(line, x_offset, y_offset + i * line_height, Colors.TEXT, bg=True)
    
    def draw_help(self):
        """Draw help text."""
        help_lines = [
            "Controls:",
            "Click+Drag: Pan camera",
            "Scroll: Zoom in/out",
            "Click Hex: Select/info",
            "SPACE/R: New map",
            "1-5: Select template",
            "C: Center camera",
            "H: Toggle help",
            "Q/ESC: Quit"
        ]
        
        y_offset = self.height - (len(help_lines) * 22 + 10)
        x_offset = 10
        
        for i, line in enumerate(help_lines):
            self.draw_text(line, x_offset, y_offset + i * 22, Colors.TEXT, 
                         font='small', bg=True)
    
    def draw_hex_tooltip(self):
        """Draw information about the hovered hex."""
        tile = self.grid.get_tile(self.hovered_hex)
        if not tile:
            return
        
        lines = [
            f"Pos: ({tile.coordinate.q}, {tile.coordinate.r})",
            f"Resource: {tile.resource.capitalize()}"
        ]
        
        if tile.number_token:
            lines.append(f"Number: {tile.number_token}")
            prob = tile.get_production_probability()
            lines.append(f"Prob: {prob:.1%}")
        
        if tile.has_robber:
            lines.append("⚠ Robber")
        
        if tile.port:
            port_text = "3:1" if 'generic' in tile.port else "2:1"
            lines.append(f"Port: {port_text}")
        
        # Draw in top-right
        x_offset = self.width - 200
        y_offset = 10
        
        for i, line in enumerate(lines):
            self.draw_text(line, x_offset, y_offset + i * 22, Colors.TEXT,
                         font='small', bg=True)
    
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int],
                 font: str = 'small', bg: bool = False):
        """Draw text with optional background."""
        font_obj = self.renderer.font_small if font == 'small' else self.renderer.font_large
        text_surface = font_obj.render(text, True, color)
        
        if bg:
            # Draw semi-transparent background
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
        print("Settlers of Catan - Visual Board Viewer")
        print("="*60)
        print("\nControls:")
        print("  Click and drag to pan")
        print("  Mouse wheel to zoom")
        print("  Click hex to see details")
        print("  SPACE or R to generate new map")
        print("  1-5 to select different map templates")
        print("  H to toggle help overlay")
        print("  Q or ESC to quit")
        print("\nStarting viewer...")
        
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Draw
            self.draw()
            
            # Cap framerate
            self.clock.tick(self.fps)
        
        pygame.quit()


def main():
    """Entry point."""
    viewer = GameViewer()
    viewer.run()


if __name__ == "__main__":
    main()
