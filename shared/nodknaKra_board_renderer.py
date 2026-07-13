"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_board_renderer.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-10 - Gordon - Final complete renderer with pointy-top hexagons, water hexes, and proper port distribution
2026-07-09 - Gordon - Added water hexes and port indicators to renderer
2026-07-09 - Gordon - Fixed coordinate calculation to match board generator's q range
2026-07-08 - Gordon - Changed to pointy-top hexagon orientation with proper interlocking spacing
"""

import pygame
import math
from typing import Dict, Tuple, Optional, List


class BoardRenderer:
    """Renders the complete NodKnaKra board using Pygame"""
    
    # Terrain colors
    TERRAIN_COLORS = {
        'wood': (34, 139, 34),
        'brick': (178, 100, 60),
        'sheep': (220, 220, 180),
        'wheat': (255, 223, 100),
        'ore': (140, 140, 140),
        'desert': (210, 180, 140),
        'water': (100, 149, 237)  # Cornflower blue
    }
    
    # Port colors
    PORT_COLORS = {
        'generic': (255, 165, 0),    # Orange
        'wood': (34, 139, 34),       # Green
        'brick': (178, 100, 60),     # Brown
        'sheep': (220, 220, 180),    # Cream
        'wheat': (255, 223, 100),    # Gold
        'ore': (140, 140, 140)       # Gray
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
        self.font_tiny = pygame.font.Font(None, 20)  # Increased from 16 for port labels
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def hex_to_pixel(self, hex_coord) -> Tuple[int, int]:
        """Convert hex coordinates to pixel coordinates (pointy-top hexagons)"""
        q = hex_coord.q
        r = hex_coord.r
        
        hex_width = self.hex_size * math.sqrt(3)
        row_height = self.hex_size * 2
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Get row info
        middle_row = len(self.row_pattern) // 2
        row_idx = r + middle_row
        
        # Calculate vertical position
        y = center_y + (r * row_height * 0.75)
        
        # Handle special water rows (outside row_pattern)
        if r == -middle_row - 1:
            # Top water row (r=-3 for standard board)
            # 7 hexes: q from -3 to 3
            center_q = 0.0
        elif r == middle_row + 1:
            # Bottom water row (r=3 for standard board)
            # 7 hexes: q from -3 to 3 (mirrors top row)
            center_q = 0.0
        elif 0 <= row_idx < len(self.row_pattern):
            # Normal land or middle water rows
            row_width = self.row_pattern[row_idx]
            offset = abs(middle_row - row_idx)
            
            min_q = -offset
            max_q = row_width - offset - 1
            center_q = (min_q + max_q) / 2.0
        else:
            # Fallback
            center_q = 0.0
        
        # Calculate horizontal position
        row_center = center_x - center_q * hex_width
        x = row_center + q * hex_width
        
        return (int(x), int(y))
    
    def draw_hexagon(self, center: Tuple[int, int], terrain_color: Tuple[int, int, int], border_width: int = 2):
        """Draw pointy-top hexagon"""
        points = []
        for i in range(6):
            angle = math.pi / 2 + math.pi / 3 * i  # Start at 90° for pointy-top
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
    
    def draw_port_indicator(self, center: Tuple[int, int], port_type: str):
        """Draw port indicator centered on water hex"""
        # Draw large circle centered on hex
        indicator_radius = 20
        
        port_color = self.PORT_COLORS.get(port_type, (255, 255, 255))
        pygame.draw.circle(self.screen, port_color, (int(center[0]), int(center[1])), indicator_radius)
        pygame.draw.circle(self.screen, self.COLOR_BORDER, (int(center[0]), int(center[1])), indicator_radius, 2)
        
        # Draw ratio text centered
        if port_type == 'generic':
            ratio_text = "3:1"
        else:
            ratio_text = "2:1"
        
        text = self.font_small.render(ratio_text, True, (0, 0, 0))
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
    
    def draw_board(self, all_hexes: Dict):
        """Draw the entire board"""
        self.screen.fill(self.COLOR_BACKGROUND)
        
        # Separate land and water
        land_hexes = {}
        water_hexes = {}
        
        for coord, hex_obj in all_hexes.items():
            if hex_obj.terrain.value == 'water':
                water_hexes[coord] = hex_obj
            else:
                land_hexes[coord] = hex_obj
        
        # Draw water hexes first (background)
        for coord, hex_obj in water_hexes.items():
            pixel_pos = self.hex_to_pixel(coord)
            terrain_color = self.TERRAIN_COLORS.get('water', (100, 149, 237))
            self.draw_hexagon(pixel_pos, terrain_color)
            
            # Draw port indicator if hex has a port
            if hex_obj.port:
                self.draw_port_indicator(pixel_pos, hex_obj.port.value)
        
        # Draw land hexes on top
        for coord, hex_obj in land_hexes.items():
            pixel_pos = self.hex_to_pixel(coord)
            terrain_color = self.TERRAIN_COLORS.get(hex_obj.terrain.value, (200, 200, 200))
            self.draw_hexagon(pixel_pos, terrain_color)
            
            if hex_obj.number_token > 0:
                self.draw_number_token(pixel_pos, hex_obj.number_token)
        
        # Draw title
        title = self.font_large.render("NodKnaKra Settlers of Catan - Complete Board", True, (0, 0, 0))
        title_rect = title.get_rect(topleft=(20, 20))
        self.screen.blit(title, title_rect)
        
        self.draw_legend()
        pygame.display.flip()
    
    def draw_legend(self):
        """Draw terrain and port legend on the LEFT side"""
        legend_x = 20  # Left side instead of right
        legend_y = 20
        box_size = 15
        spacing = 22
        
        # Terrain legend
        terrain_label = self.font_small.render("Terrain:", True, (0, 0, 0))
        self.screen.blit(terrain_label, (legend_x, legend_y))
        
        terrain_start_y = legend_y + 25
        terrain_items = ['wood', 'brick', 'sheep', 'wheat', 'ore', 'desert', 'water']
        
        for i, terrain_name in enumerate(terrain_items):
            y = terrain_start_y + (i * spacing)
            color = self.TERRAIN_COLORS.get(terrain_name, (200, 200, 200))
            pygame.draw.rect(self.screen, color, (legend_x, y, box_size, box_size))
            pygame.draw.rect(self.screen, self.COLOR_BORDER, (legend_x, y, box_size, box_size), 1)
            label = self.font_tiny.render(terrain_name.capitalize(), True, (0, 0, 0))
            self.screen.blit(label, (legend_x + box_size + 10, y + 1))
        
        # Port legend
        port_start_y = terrain_start_y + (len(terrain_items) * spacing) + 20
        port_label = self.font_small.render("Ports:", True, (0, 0, 0))
        self.screen.blit(port_label, (legend_x, port_start_y))
        
        port_items = [('generic', '3:1'), ('wood', '2:1'), ('brick', '2:1'), 
                      ('sheep', '2:1'), ('wheat', '2:1'), ('ore', '2:1')]
        
        for i, (port_name, ratio) in enumerate(port_items):
            y = port_start_y + 25 + (i * spacing)
            color = self.PORT_COLORS.get(port_name, (255, 255, 255))
            pygame.draw.circle(self.screen, color, (legend_x + 8, y + 8), 6)
            pygame.draw.circle(self.screen, self.COLOR_BORDER, (legend_x + 8, y + 8), 6, 1)
            label = self.font_tiny.render(f"{port_name.capitalize()} {ratio}", True, (0, 0, 0))
            self.screen.blit(label, (legend_x + box_size + 10, y))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def run(self, all_hexes: Dict):
        """Run the renderer loop"""
        while self.running:
            self.handle_events()
            self.draw_board(all_hexes)
            self.clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    print("\nTesting NodKnaKra Complete Board Renderer...\n")
    
    import sys
    sys.path.insert(0, '.')
    from nodknaKra_board import NodKnaKraBoard
    
    board = NodKnaKraBoard(seed=42)
    hexes_dict = board.generate()
    all_hexes = board.get_all_hexes()
    
    print(f"✓ Generated complete board with {len(all_hexes)} total hexes")
    board.print_stats()
    
    print("✓ Starting Pygame renderer...")
    print("(Close window or press ESC to exit)\n")
    
    renderer = BoardRenderer(row_pattern=[6, 7, 8, 7, 6])
    renderer.run(all_hexes)
    
    print("✓ Renderer closed!")
