"""
Pygame Rendering System for Settlers of Catan
Handles drawing hexagonal tiles, resources, numbers, and game elements.
"""

import pygame
import math
from typing import Tuple, List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from shared.hex_grid import HexGrid, HexTile, HexCoordinate


class Colors:
    """Color palette for the game."""
    # Resources
    WOOD = (34, 139, 34)        # Forest Green
    BRICK = (178, 34, 34)       # Firebrick Red
    SHEEP = (144, 238, 144)     # Light Green
    WHEAT = (255, 215, 0)       # Gold
    ORE = (128, 128, 128)       # Gray
    DESERT = (210, 180, 140)    # Tan
    WATER = (70, 130, 180)      # Steel Blue
    
    # UI
    BACKGROUND = (240, 248, 255)  # Alice Blue
    BORDER = (0, 0, 0)            # Black
    TEXT = (0, 0, 0)              # Black
    NUMBER_BG = (245, 245, 220)   # Beige
    NUMBER_RED = (220, 20, 60)    # Crimson (for 6 and 8)
    ROBBER = (50, 50, 50)         # Dark Gray
    
    # Highlights
    HOVER = (255, 255, 255, 100)  # Semi-transparent white
    SELECTED = (255, 255, 0, 150) # Semi-transparent yellow
    
    @staticmethod
    def get_resource_color(resource: str) -> Tuple[int, int, int]:
        """Get color for a resource type."""
        color_map = {
            'wood': Colors.WOOD,
            'brick': Colors.BRICK,
            'sheep': Colors.SHEEP,
            'wheat': Colors.WHEAT,
            'ore': Colors.ORE,
            'desert': Colors.DESERT,
            'water': Colors.WATER
        }
        return color_map.get(resource, Colors.DESERT)


class HexRenderer:
    """Renders hexagonal tiles and game board."""
    
    def __init__(self, hex_size: int = 50):
        """
        Initialize the hex renderer.
        
        Args:
            hex_size: Radius from center to corner of hex (in pixels)
        """
        self.hex_size = hex_size
        
        # Calculate hex dimensions
        self.hex_width = hex_size * 2
        self.hex_height = int(hex_size * math.sqrt(3))
        
        # Font for numbers and text (will be initialized in pygame)
        self.font_large = None
        self.font_small = None
        self.font_tiny = None
    
    def init_fonts(self):
        """Initialize pygame fonts."""
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 16)
    
    def hex_to_pixel(self, coord: HexCoordinate) -> Tuple[int, int]:
        """
        Convert hex coordinate to pixel position (center of hex).
        Uses flat-top hexagon orientation.
        """
        x = self.hex_size * (3/2 * coord.q)
        y = self.hex_size * (math.sqrt(3)/2 * coord.q + math.sqrt(3) * coord.r)
        return (int(x), int(y))
    
    def pixel_to_hex(self, x: int, y: int) -> HexCoordinate:
        """Convert pixel position to hex coordinate."""
        q = (2/3 * x) / self.hex_size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / self.hex_size
        return HexCoordinate.round_hex(q, r)
    
    def get_hex_corners(self, center_x: int, center_y: int) -> List[Tuple[int, int]]:
        """
        Get the 6 corner points of a hexagon.
        Returns list of (x, y) tuples for flat-top orientation.
        Corners are at angles: 0°, 60°, 120°, 180°, 240°, 300°
        """
        corners = []
        for i in range(6):
            angle_deg = 60 * i  # 0, 60, 120, 180, 240, 300
            angle_rad = math.radians(angle_deg)
            x = center_x + self.hex_size * math.cos(angle_rad)
            y = center_y + self.hex_size * math.sin(angle_rad)
            corners.append((int(x), int(y)))
        return corners
    
    def draw_hexagon(self, surface: pygame.Surface, center_x: int, center_y: int,
                    color: Tuple[int, int, int], border_color: Tuple[int, int, int] = Colors.BORDER,
                    border_width: int = 2):
        """Draw a hexagon at the given center position."""
        corners = self.get_hex_corners(center_x, center_y)
        
        # Draw filled hexagon
        pygame.draw.polygon(surface, color, corners)
        
        # Draw border
        if border_width > 0:
            pygame.draw.polygon(surface, border_color, corners, border_width)
    
    def draw_tile(self, surface: pygame.Surface, tile: HexTile, offset_x: int = 0, offset_y: int = 0,
                 highlight: Optional[str] = None):
        """
        Draw a complete hex tile with resource, number, and special markers.
        
        Args:
            surface: Pygame surface to draw on
            tile: HexTile to render
            offset_x, offset_y: Screen offset for camera/panning
            highlight: 'hover' or 'selected' for highlighting
        """
        # Get pixel position
        pixel_x, pixel_y = self.hex_to_pixel(tile.coordinate)
        screen_x = pixel_x + offset_x
        screen_y = pixel_y + offset_y
        
        # Get resource color
        color = Colors.get_resource_color(tile.resource)
        
        # Draw base hexagon
        self.draw_hexagon(surface, screen_x, screen_y, color)
        
        # Draw highlight if needed
        if highlight:
            highlight_color = Colors.HOVER if highlight == 'hover' else Colors.SELECTED
            self.draw_hex_highlight(surface, screen_x, screen_y, highlight_color)
        
        # Draw number token
        if tile.number_token is not None:
            self.draw_number_token(surface, screen_x, screen_y, tile.number_token)
        
        # Draw robber
        if tile.has_robber:
            self.draw_robber(surface, screen_x, screen_y)
        
        # Draw port indicator
        if tile.port:
            self.draw_port_indicator(surface, screen_x, screen_y, tile.port)
    
    def draw_number_token(self, surface: pygame.Surface, x: int, y: int, number: int):
        """Draw a number token in the center of a hex."""
        # Draw circle background
        circle_radius = int(self.hex_size * 0.4)
        pygame.draw.circle(surface, Colors.NUMBER_BG, (x, y), circle_radius)
        pygame.draw.circle(surface, Colors.BORDER, (x, y), circle_radius, 2)
        
        # Choose text color (red for 6 and 8)
        text_color = Colors.NUMBER_RED if number in [6, 8] else Colors.TEXT
        
        # Draw number
        text = self.font_large.render(str(number), True, text_color)
        text_rect = text.get_rect(center=(x, y - 5))
        surface.blit(text, text_rect)
        
        # Draw pips (dots) below number
        pip_count = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
                    8: 5, 9: 4, 10: 3, 11: 2, 12: 1}.get(number, 0)
        
        pip_y = y + 12
        pip_spacing = 4
        pip_start_x = x - (pip_count - 1) * pip_spacing // 2
        
        for i in range(pip_count):
            pip_x = pip_start_x + i * pip_spacing
            pygame.draw.circle(surface, text_color, (pip_x, pip_y), 2)
    
    def draw_robber(self, surface: pygame.Surface, x: int, y: int):
        """Draw a robber marker on a tile."""
        # Draw simple circle for robber
        robber_radius = int(self.hex_size * 0.2)
        pygame.draw.circle(surface, Colors.ROBBER, (x, y + int(self.hex_size * 0.4)), robber_radius)
        pygame.draw.circle(surface, Colors.BORDER, (x, y + int(self.hex_size * 0.4)), robber_radius, 2)
        
        # Draw "R" text
        text = self.font_small.render("R", True, Colors.NUMBER_BG)
        text_rect = text.get_rect(center=(x, y + int(self.hex_size * 0.4)))
        surface.blit(text, text_rect)
    
    def draw_port_indicator(self, surface: pygame.Surface, x: int, y: int, port_type: str):
        """Draw a port indicator near the tile."""
        # Determine port text
        if 'generic' in port_type:
            port_text = "3:1"
        else:
            port_text = "2:1"
        
        # Draw small indicator
        indicator_y = y - int(self.hex_size * 0.7)
        text = self.font_tiny.render(port_text, True, Colors.TEXT)
        
        # Background rectangle
        padding = 2
        bg_rect = pygame.Rect(
            x - text.get_width() // 2 - padding,
            indicator_y - text.get_height() // 2 - padding,
            text.get_width() + padding * 2,
            text.get_height() + padding * 2
        )
        pygame.draw.rect(surface, Colors.NUMBER_BG, bg_rect)
        pygame.draw.rect(surface, Colors.BORDER, bg_rect, 1)
        
        # Text
        text_rect = text.get_rect(center=(x, indicator_y))
        surface.blit(text, text_rect)
    
    def draw_hex_highlight(self, surface: pygame.Surface, x: int, y: int,
                          color: Tuple[int, int, int, int]):
        """Draw a semi-transparent highlight over a hex."""
        # Create a surface with alpha channel
        highlight_surface = pygame.Surface((self.hex_width, self.hex_height), pygame.SRCALPHA)
        
        # Draw hexagon on the surface
        corners = self.get_hex_corners(self.hex_width // 2, self.hex_height // 2)
        pygame.draw.polygon(highlight_surface, color, corners)
        
        # Blit to main surface
        surface.blit(highlight_surface, (x - self.hex_width // 2, y - self.hex_height // 2))
    
    def get_vertex_pixel_position(self, vertex, offset_x: int = 0, offset_y: int = 0) -> Tuple[int, int]:
        """
        Get the pixel position of a vertex (corner of hex).
        
        Args:
            vertex: Vertex object with hex_coord and direction (0-5)
            offset_x, offset_y: Camera offset
            
        Returns:
            (x, y) pixel coordinates
            
        Note: Vertex directions match hex corner angles:
            Direction 0 = 0° (right)
            Direction 1 = 60° (bottom-right)
            Direction 2 = 120° (bottom-left)
            Direction 3 = 180° (left)
            Direction 4 = 240° (top-left)
            Direction 5 = 300° (top-right)
        """
        # Get hex center
        hex_x, hex_y = self.hex_to_pixel(vertex.hex_coord)
        
        # Calculate angle - MUST match get_hex_corners exactly
        angle_deg = 60 * vertex.direction  # 0, 60, 120, 180, 240, 300
        angle_rad = math.radians(angle_deg)
        
        # Calculate vertex position - SAME formula as get_hex_corners
        vertex_x = hex_x + self.hex_size * math.cos(angle_rad) + offset_x
        vertex_y = hex_y + self.hex_size * math.sin(angle_rad) + offset_y
        
        return (int(vertex_x), int(vertex_y))
    
    def get_edge_pixel_position(self, edge, offset_x: int = 0, offset_y: int = 0) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the pixel positions of an edge's two endpoints.
        
        Args:
            edge: Edge object
            offset_x, offset_y: Camera offset
            
        Returns:
            ((x1, y1), (x2, y2)) pixel coordinates of the two vertices
        """
        v1, v2 = edge.get_vertices()
        pos1 = self.get_vertex_pixel_position(v1, offset_x, offset_y)
        pos2 = self.get_vertex_pixel_position(v2, offset_x, offset_y)
        return (pos1, pos2)
    
    def draw_settlement(self, surface: pygame.Surface, x: int, y: int, 
                       player_color: Tuple[int, int, int], size: int = None):
        """
        Draw a settlement (house shape) at a vertex.
        
        Args:
            surface: Pygame surface to draw on
            x, y: Pixel position
            player_color: RGB color tuple
            size: Size of settlement (default based on hex_size)
        """
        if size is None:
            size = int(self.hex_size * 0.3)
        
        # House shape: triangle roof + rectangle base
        half = size // 2
        
        # Base (rectangle)
        base_rect = pygame.Rect(x - half, y - half // 2, size, size)
        pygame.draw.rect(surface, player_color, base_rect)
        pygame.draw.rect(surface, Colors.BORDER, base_rect, 2)
        
        # Roof (triangle)
        roof_points = [
            (x, y - size),           # Top point
            (x - half, y - half // 2),  # Bottom left
            (x + half, y - half // 2)   # Bottom right
        ]
        pygame.draw.polygon(surface, player_color, roof_points)
        pygame.draw.polygon(surface, Colors.BORDER, roof_points, 2)
    
    def draw_city(self, surface: pygame.Surface, x: int, y: int,
                 player_color: Tuple[int, int, int], size: int = None):
        """
        Draw a city (larger building) at a vertex.
        
        Args:
            surface: Pygame surface to draw on
            x, y: Pixel position
            player_color: RGB color tuple
            size: Size of city (default based on hex_size)
        """
        if size is None:
            size = int(self.hex_size * 0.4)
        
        # City is two buildings side by side
        half = size // 2
        quarter = size // 4
        
        # Left tower (taller)
        left_rect = pygame.Rect(x - half, y - size, quarter + 2, size + quarter)
        pygame.draw.rect(surface, player_color, left_rect)
        pygame.draw.rect(surface, Colors.BORDER, left_rect, 2)
        
        # Right tower (shorter)
        right_rect = pygame.Rect(x - quarter + 2, y - size // 2, quarter + 2, size // 2 + quarter)
        pygame.draw.rect(surface, player_color, right_rect)
        pygame.draw.rect(surface, Colors.BORDER, right_rect, 2)
        
        # Battlement on left tower
        batt_size = 3
        for i in range(2):
            batt_x = x - half + i * (quarter // 2)
            pygame.draw.rect(surface, Colors.BORDER, 
                           pygame.Rect(batt_x, y - size - batt_size, 4, batt_size))
    
    def draw_road(self, surface: pygame.Surface, pos1: Tuple[int, int], 
                 pos2: Tuple[int, int], player_color: Tuple[int, int, int], 
                 width: int = None):
        """
        Draw a road (thick line) between two vertices.
        
        Args:
            surface: Pygame surface to draw on
            pos1: (x, y) pixel position of first vertex
            pos2: (x, y) pixel position of second vertex
            player_color: RGB color tuple
            width: Width of road line (default based on hex_size)
        """
        if width is None:
            width = max(4, int(self.hex_size * 0.1))
        
        # Draw thick line
        pygame.draw.line(surface, player_color, pos1, pos2, width)
        # Draw border
        pygame.draw.line(surface, Colors.BORDER, pos1, pos2, width + 2)
        pygame.draw.line(surface, player_color, pos1, pos2, width)
    
    def draw_vertex_highlight(self, surface: pygame.Surface, x: int, y: int,
                            color: Tuple[int, int, int] = None, radius: int = None):
        """Draw a circle to highlight a vertex position."""
        if color is None:
            color = (255, 255, 100)
        if radius is None:
            radius = int(self.hex_size * 0.15)
        
        pygame.draw.circle(surface, color, (x, y), radius, 3)
    
    def draw_edge_highlight(self, surface: pygame.Surface, pos1: Tuple[int, int],
                          pos2: Tuple[int, int], color: Tuple[int, int, int] = None,
                          width: int = None):
        """Draw a thick line to highlight an edge position."""
        if color is None:
            color = (255, 255, 100)
        if width is None:
            width = max(6, int(self.hex_size * 0.12))
        
        pygame.draw.line(surface, color, pos1, pos2, width)
    
    def draw_grid(self, surface: pygame.Surface, grid: HexGrid, 
                 offset_x: int = 0, offset_y: int = 0,
                 hovered_coord: Optional[HexCoordinate] = None,
                 selected_coord: Optional[HexCoordinate] = None):
        """
        Draw the entire game board.
        
        Args:
            surface: Pygame surface to draw on
            grid: HexGrid containing all tiles
            offset_x, offset_y: Camera offset
            hovered_coord: Coordinate being hovered by mouse
            selected_coord: Coordinate that's selected
        """
        # Draw all tiles
        for tile in grid.get_all_tiles():
            highlight = None
            if hovered_coord and tile.coordinate == hovered_coord:
                highlight = 'hover'
            elif selected_coord and tile.coordinate == selected_coord:
                highlight = 'selected'
            
            self.draw_tile(surface, tile, offset_x, offset_y, highlight)
    
    def calculate_board_bounds(self, grid: HexGrid) -> Tuple[int, int, int, int]:
        """
        Calculate the pixel bounds of the board.
        Returns (min_x, max_x, min_y, max_y)
        """
        if not grid.tiles:
            return (0, 0, 0, 0)
        
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for tile in grid.get_all_tiles():
            x, y = self.hex_to_pixel(tile.coordinate)
            min_x = min(min_x, x - self.hex_size)
            max_x = max(max_x, x + self.hex_size)
            min_y = min(min_y, y - self.hex_size)
            max_y = max(max_y, y + self.hex_size)
        
        return (int(min_x), int(max_x), int(min_y), int(max_y))


class Camera:
    """Handles camera positioning and movement."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.zoom = 1.0
    
    def pan(self, dx: int, dy: int):
        """Pan the camera by the given delta."""
        self.x += dx
        self.y += dy
    
    def zoom_in(self, amount: float = 0.1):
        """Zoom in."""
        self.zoom = min(2.0, self.zoom + amount)
    
    def zoom_out(self, amount: float = 0.1):
        """Zoom out."""
        self.zoom = max(0.5, self.zoom - amount)
    
    def center_on_board(self, renderer: HexRenderer, grid: HexGrid):
        """Center the camera on the board."""
        min_x, max_x, min_y, max_y = renderer.calculate_board_bounds(grid)
        board_center_x = (min_x + max_x) // 2
        board_center_y = (min_y + max_y) // 2
        
        self.x = self.screen_width // 2 - board_center_x
        self.y = self.screen_height // 2 - board_center_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates."""
        world_x = int((screen_x - self.x) / self.zoom)
        world_y = int((screen_y - self.y) / self.zoom)
        return (world_x, world_y)
    
    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int(world_x * self.zoom + self.x)
        screen_y = int(world_y * self.zoom + self.y)
        return (screen_x, screen_y)


# Testing
if __name__ == "__main__":
    print("HexRenderer module - use game_viewer.py to run the visual demo")
