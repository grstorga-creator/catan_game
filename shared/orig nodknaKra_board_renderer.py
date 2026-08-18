"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_board_renderer.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-09 - Gordon - Fixed coordinate calculation to match board generator's q range (min_q = -offset)
2026-07-08 - Gordon - Fixed offset calculation based on row width difference from center row
2026-07-08 - Gordon - Fixed row centering: shift odd rows LEFT for proper symmetrical honeycomb
2026-07-08 - Gordon - Changed to pointy-top hexagon orientation with proper interlocking spacing
2026-07-08 - Gordon - Rewrote hex_to_pixel coordinate calculation for proper honeycomb interlocking
2026-07-08 - Gordon - Fixed row centering for proper honeycomb layout
2026-07-08 - Gordon - Fixed hexagon interlocking with proper spacing formula
2026-07-08 - Gordon - Fixed coordinate-to-pixel conversion for row-based layout (6-7-8-7-6)
2026-07-08 - Gordon - Created BoardRenderer with hexagon drawing, terrain colors, number tokens
"""

import pygame
import math
from typing import Dict, Tuple, Optional, List


class BoardRenderer:
    """Renders the NodKnaKra board using Pygame"""
    
    # Terrain colors
    TERRAIN_COLORS = {
        'wood': (34, 139, 34),
        'brick': (178, 100, 60),
        'sheep': (220, 220, 180),
        'wheat': (255, 223, 100),
        'ore': (140, 140, 140),
        'desert': (210, 180, 140)
    }
    
    COLOR_BORDER = (0, 0, 0)
    COLOR_NUMBER = (0, 0, 0)
    COLOR_BACKGROUND = (240, 248, 255)
    
    def __init__(self, row_pattern: List[int] = None, width: int = 1000, height: int = 800, hex_size: int = 45):
        """Initialize renderer"""
        pygame.init()
        
        self.row_pattern = row_pattern or [6, 7, 8, 7, 6]
        self.width = width
        self.height = height
        self.hex_size = hex_size
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NodKnaKra Settlers of Catan")
        
        self.font_large = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def hex_to_pixel(self, hex_coord) -> Tuple[int, int]:
        """Convert hex coordinates to pixel coordinates (pointy-top hexagons)"""
        q = hex_coord.q
        r = hex_coord.r
        
        # Pointy-top hex spacing
        hex_width = self.hex_size * math.sqrt(3)
        row_height = self.hex_size * 2
        
        # Center of screen
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Get row info
        middle_row = len(self.row_pattern) // 2
        row_idx = r + middle_row
        if 0 <= row_idx < len(self.row_pattern):
            row_width = self.row_pattern[row_idx]
        else:
            row_width = 0
        
        # Calculate the offset that the board generator uses
        # This determines the q range for this row
        offset = abs(middle_row - row_idx)
        
        # The actual q values go from -offset to (row_width - offset - 1)
        min_q = -offset
        max_q = row_width - offset - 1
        center_q = (min_q + max_q) / 2.0
        
        # Calculate vertical position
        y = center_y + (r * row_height * 0.75)
        
        # Calculate horizontal position
        # Position relative to the center of this row's q range
        row_center = center_x - center_q * hex_width
        x = row_center + q * hex_width
        
        return (int(x), int(y))
    
    def draw_hexagon(self, center: Tuple[int, int], terrain_color: Tuple[int, int, int], border_width: int = 2):
        """Draw pointy-top hexagon (point at top)"""
        points = []
        for i in range(6):
            # Pointy-top: start at 30° to get point at top
            angle = math.pi / 3 * i + math.pi / 6
            x = center[0] + self.hex_size * math.cos(angle)
            y = center[1] + self.hex_size * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(self.screen, terrain_color, points)
        pygame.draw.polygon(self.screen, self.COLOR_BORDER, points, border_width)
    
    def draw_number_token(self, center: Tuple[int, int], number: int):
        """Draw number token"""
        if number == 0:
            return
        
        if number in [6, 8]:
            token_color = (220, 80, 80)
        else:
            token_color = (200, 200, 200)
        
        token_radius = self.hex_size // 3
        pygame.draw.circle(self.screen, token_color, center, token_radius)
        pygame.draw.circle(self.screen, self.COLOR_BORDER, center, token_radius, 2)
        
        text = self.font_small.render(str(number), True, self.COLOR_NUMBER)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
    
    def draw_board(self, board_hexes: Dict):
        """Draw the entire board"""
        self.screen.fill(self.COLOR_BACKGROUND)
        
        for coord, hex_obj in board_hexes.items():
            pixel_pos = self.hex_to_pixel(coord)
            terrain_color = self.TERRAIN_COLORS.get(hex_obj.terrain.value, (200, 200, 200))
            self.draw_hexagon(pixel_pos, terrain_color)
            if hex_obj.number_token > 0:
                self.draw_number_token(pixel_pos, hex_obj.number_token)
        
        # Draw title
        title = self.font_large.render("NodKnaKra Settlers of Catan - 34 Hex Board", True, (0, 0, 0))
        title_rect = title.get_rect(topleft=(20, 20))
        self.screen.blit(title, title_rect)
        
        self.draw_legend()
        pygame.display.flip()
    
    def draw_legend(self):
        """Draw terrain legend"""
        legend_x = self.width - 220
        legend_y = 20
        box_size = 20
        spacing = 30
        
        for i, (terrain_name, color) in enumerate(self.TERRAIN_COLORS.items()):
            y = legend_y + (i * spacing)
            pygame.draw.rect(self.screen, color, (legend_x, y, box_size, box_size))
            pygame.draw.rect(self.screen, self.COLOR_BORDER, (legend_x, y, box_size, box_size), 1)
            label = self.font_small.render(terrain_name.capitalize(), True, (0, 0, 0))
            self.screen.blit(label, (legend_x + box_size + 10, y + 2))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def run(self, board_hexes: Dict):
        """Run the renderer loop"""
        while self.running:
            self.handle_events()
            self.draw_board(board_hexes)
            self.clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    print("\nTesting NodKnaKra Board Renderer...\n")
    
    import sys
    sys.path.insert(0, '.')
    from nodknaKra_board import NodKnaKraBoard
    
    board = NodKnaKraBoard(seed=42)
    hexes = board.generate()
    
    print(f"✓ Generated board with {len(hexes)} hexes")
    print("✓ Starting Pygame renderer...")
    print("(Close window or press ESC to exit)\n")
    
    renderer = BoardRenderer(row_pattern=[6, 7, 8, 7, 6])
    renderer.run(hexes)
    
    print("✓ Renderer closed!")
