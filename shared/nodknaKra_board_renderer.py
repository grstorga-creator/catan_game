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
    
    def __init__(self, width: int = 1400, height: int = 900, hex_size: int = 40):
        pygame.init()
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NodKnaKra Settlers of Catan")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
    
    def hex_to_pixel(self, position: str, offset_x: int = 0, offset_y: int = 0) -> Tuple[int, int]:
        """Convert hex position (A1, B5, etc.) to pixel coordinates"""
        row_letter = position[0]
        col_num = int(position[1:])
        
        # Row letter to row index (A=0, B=1, ... G=6)
        row_idx = ord(row_letter) - ord('A')
        
        # Hexagon layout: pointy-top, horizontal spacing
        hex_width = self.hex_size * 2
        hex_height = self.hex_size * 1.732  # sqrt(3)
        
        # Center of screen
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Vertical offset (each row down)
        y = center_y + (row_idx - 3) * hex_height * 0.75
        
        # Horizontal offset (depends on row)
        # Rows stagger: A=6, B=7, C=8, D=9 (widest), E=8, F=7, G=6
        row_widths = [6, 7, 8, 9, 8, 7, 6]  # Width of each row
        row_start_offset = (9 - row_widths[row_idx]) // 2
        x = center_x + (col_num - row_start_offset - row_widths[row_idx] / 2) * hex_width / 2
        
        return int(x + offset_x), int(y + offset_y)
    
    def draw_hexagon(self, center: Tuple[int, int], color: Tuple[int, int, int], filled: bool = True):
        """Draw a regular hexagon"""
        import math
        points = []
        for i in range(6):
            angle = math.radians(i * 60)
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
        
        # Draw hex label
        label_text = self.font.render(hex_obj.position, True, self.TEXT_COLOR)
        label_rect = label_text.get_rect(center=position)
        self.screen.blit(label_text, label_rect)
        
        # Draw number token if present
        if hex_obj.number_token is not None:
            token_text = self.font.render(str(hex_obj.number_token), True, self.TEXT_COLOR)
            token_x = position[0]
            token_y = position[1] + 15
            token_rect = token_text.get_rect(center=(token_x, token_y))
            self.screen.blit(token_text, token_rect)
    
    def render_board(self, game: Game):
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
            
            # Draw instructions
            instructions = self.font.render("Press ESC to exit", True, self.TEXT_COLOR)
            self.screen.blit(instructions, (20, self.height - 30))
            
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
    
    # Show ASCII representation
    game.render_ascii()
    
    # Show visual representation
    print(f"Rendering {map_name} map with Pygame...")
    print("(Press ESC to exit)\n")
    
    renderer = HexRenderer()
    renderer.render_board(game)


if __name__ == "__main__":
    main()
