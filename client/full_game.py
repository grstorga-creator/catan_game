"""
Complete Settlers of Catan Game
Full playable game with all features: setup, turns, resources, trading, victory.
"""

import pygame
import sys
from pathlib import Path
from typing import Optional, Tuple, List

sys.path.append(str(Path(__file__).parent.parent))

from client.renderer import HexRenderer, Colors, Camera
from shared.game_controller import GameController, SetupPhase
from shared.game_state import GamePhase
from shared.board_topology import Vertex, Edge
from shared.hex_grid import HexCoordinate
from shared.player import PlayerColor


class ResourceDisplay:
    """Display for showing resource cards."""
    
    RESOURCE_COLORS = {
        'wood': (34, 139, 34),
        'brick': (178, 34, 34),
        'sheep': (144, 238, 144),
        'wheat': (255, 215, 0),
        'ore': (128, 128, 128)
    }
    
    @staticmethod
    def draw(surface: pygame.Surface, player, x: int, y: int, font):
        """Draw resource cards for a player."""
        card_width = 60
        card_height = 80
        spacing = 5
        
        resources = ['wood', 'brick', 'sheep', 'wheat', 'ore']
        total_width = len(resources) * (card_width + spacing)
        
        for i, resource in enumerate(resources):
            count = player.resources.get(resource, 0)
            color = ResourceDisplay.RESOURCE_COLORS[resource]
            
            card_x = x + i * (card_width + spacing)
            
            # Draw card
            card_rect = pygame.Rect(card_x, y, card_width, card_height)
            pygame.draw.rect(surface, color, card_rect)
            pygame.draw.rect(surface, Colors.BORDER, card_rect, 2)
            
            # Draw resource name
            name_text = font.render(resource[:4].upper(), True, (255, 255, 255))
            name_x = card_x + (card_width - name_text.get_width()) // 2
            surface.blit(name_text, (name_x, y + 5))
            
            # Draw count
            count_text = font.render(str(count), True, (255, 255, 255))
            count_x = card_x + (card_width - count_text.get_width()) // 2
            surface.blit(count_text, (count_x, y + card_height - 30))


class DiceDisplay:
    """Display for dice."""
    
    @staticmethod
    def draw(surface: pygame.Surface, die1: int, die2: int, x: int, y: int):
        """Draw two dice."""
        die_size = 50
        spacing = 10
        
        # Die 1
        DiceDisplay.draw_die(surface, die1, x, y, die_size)
        # Die 2
        DiceDisplay.draw_die(surface, die2, x + die_size + spacing, y, die_size)
    
    @staticmethod
    def draw_die(surface: pygame.Surface, value: int, x: int, y: int, size: int):
        """Draw a single die."""
        # Die background
        die_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(surface, (255, 255, 255), die_rect, border_radius=5)
        pygame.draw.rect(surface, Colors.BORDER, die_rect, 2, border_radius=5)
        
        # Dot positions for each value
        dot_radius = size // 10
        center_x = x + size // 2
        center_y = y + size // 2
        offset = size // 4
        
        dot_color = (0, 0, 0)
        
        # Draw dots based on value
        if value == 1:
            pygame.draw.circle(surface, dot_color, (center_x, center_y), dot_radius)
        elif value == 2:
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y + offset), dot_radius)
        elif value == 3:
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x, center_y), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y + offset), dot_radius)
        elif value == 4:
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y + offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y + offset), dot_radius)
        elif value == 5:
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x, center_y), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y + offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y + offset), dot_radius)
        elif value == 6:
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y - offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x - offset, center_y + offset), dot_radius)
            pygame.draw.circle(surface, dot_color, (center_x + offset, center_y + offset), dot_radius)


class FullCatanGame:
    """Complete playable Catan game with all features."""
    
    def __init__(self, player_names: List[str], width: int = 1600, height: int = 1000):
        """Initialize the full game."""
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Settlers of Catan - Full Game")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize renderer and camera
        self.renderer = HexRenderer(hex_size=50)
        self.renderer.init_fonts()
        self.camera = Camera(width, height)
        
        # Initialize game controller
        self.controller = GameController(player_names)
        self.topology = self.controller.topology
        self.grid = self.controller.game_state.grid
        
        # Center camera
        self.camera.center_on_board(self.renderer, self.grid)
        
        # UI state
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.show_help = False
        
        # Building mode
        self.build_mode = None  # 'settlement', 'city', 'road'
        self.hovered_vertex = None
        self.hovered_edge = None
        
        # Trading mode
        self.trade_mode = False
        self.trade_give_resource = None
        self.trade_give_amount = 4
        self.trade_get_resource = None
        
        # Last dice roll
        self.last_dice_roll = None
        
        # UI regions (right panel for UI)
        self.board_width = width - 400
        self.ui_x = self.board_width + 10
        self.ui_width = 380
    
    def get_player_color_rgb(self, player) -> Tuple[int, int, int]:
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
    
    def find_closest_vertex(self, screen_x: int, screen_y: int, max_distance: int = 25) -> Optional[Vertex]:
        """Find the closest vertex to screen coordinates."""
        # Only check if in board area
        if screen_x > self.board_width:
            return None
        
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
    
    def find_closest_edge(self, screen_x: int, screen_y: int, max_distance: int = 20) -> Optional[Edge]:
        """Find the closest edge to screen coordinates."""
        # Only check if in board area
        if screen_x > self.board_width:
            return None
        
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
        
        length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if length_sq == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / length_sq))
        
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
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
        
        elif key == pygame.K_SPACE:
            # Roll dice (if not setup)
            if self.controller.game_state.game_phase != GamePhase.SETUP:
                dice = self.controller.roll_dice()
                if dice:
                    self.last_dice_roll = dice
                    # Enable building and trading after roll
                    self.controller.can_build = True
                    self.controller.can_trade = True
                    self.controller.can_buy_dev_card = True
        
        elif key == pygame.K_RETURN:
            # End turn
            self.controller.end_turn()
            self.last_dice_roll = None
            self.build_mode = None
        
        # Building modes
        elif key == pygame.K_s:
            self.build_mode = 'settlement' if self.build_mode != 'settlement' else None
            if self.build_mode:
                self.trade_mode = False
        
        elif key == pygame.K_c:
            self.build_mode = 'city' if self.build_mode != 'city' else None
            if self.build_mode:
                self.trade_mode = False
        
        elif key == pygame.K_r:
            self.build_mode = 'road' if self.build_mode != 'road' else None
            if self.build_mode:
                self.trade_mode = False
        
        elif key == pygame.K_t:
            # Toggle trade mode
            self.trade_mode = not self.trade_mode
            if self.trade_mode:
                self.build_mode = None
                print("Trade mode activated - use 1-5 to select resource to give, 6-0 for resource to get")
        
        # Trading - select resources
        elif self.trade_mode:
            resources = ['wood', 'brick', 'sheep', 'wheat', 'ore']
            
            if key == pygame.K_1:
                self.trade_give_resource = 'wood'
            elif key == pygame.K_2:
                self.trade_give_resource = 'brick'
            elif key == pygame.K_3:
                self.trade_give_resource = 'sheep'
            elif key == pygame.K_4:
                self.trade_give_resource = 'wheat'
            elif key == pygame.K_5:
                self.trade_give_resource = 'ore'
            elif key == pygame.K_6:
                self.trade_get_resource = 'wood'
            elif key == pygame.K_7:
                self.trade_get_resource = 'brick'
            elif key == pygame.K_8:
                self.trade_get_resource = 'sheep'
            elif key == pygame.K_9:
                self.trade_get_resource = 'wheat'
            elif key == pygame.K_0:
                self.trade_get_resource = 'ore'
            elif key == pygame.K_MINUS:
                self.trade_give_amount = max(1, self.trade_give_amount - 1)
            elif key == pygame.K_EQUALS or key == pygame.K_PLUS:
                self.trade_give_amount = min(10, self.trade_give_amount + 1)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                # Execute trade
                if self.trade_give_resource and self.trade_get_resource:
                    if self.controller.trade_with_bank(
                        self.trade_give_resource, 
                        self.trade_give_amount, 
                        self.trade_get_resource
                    ):
                        # Reset trade
                        self.trade_give_resource = None
                        self.trade_get_resource = None
                        self.trade_give_amount = 4
        
        # Camera
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
            # Check if clicking in board area
            if event.pos[0] < self.board_width:
                if self.build_mode == 'settlement' and self.hovered_vertex:
                    self.controller.try_place_settlement(self.hovered_vertex)
                elif self.build_mode == 'city' and self.hovered_vertex:
                    self.controller.try_place_city(self.hovered_vertex)
                elif self.build_mode == 'road' and self.hovered_edge:
                    self.controller.try_place_road(self.hovered_edge)
                else:
                    # Start dragging
                    self.dragging = True
                    self.last_mouse_pos = event.pos
            else:
                # Clicking in UI area
                self.handle_ui_click(event.pos)
        
        elif event.button == 3:  # Right click
            self.build_mode = None
        
        elif event.button == 4:  # Scroll up
            if event.pos[0] < self.board_width:
                self.camera.zoom_in(0.1)
        
        elif event.button == 5:  # Scroll down
            if event.pos[0] < self.board_width:
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
    
    def handle_ui_click(self, pos: Tuple[int, int]):
        """Handle clicks in UI area."""
        # TODO: Implement button clicks for trading, buying cards, etc.
        pass
    
    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw board (left side)
        board_surface = self.screen.subsurface(pygame.Rect(0, 0, self.board_width, self.height))
        self.renderer.draw_grid(board_surface, self.grid, self.camera.x, self.camera.y, None, None)
        
        # Draw buildings
        self.draw_buildings(board_surface)
        
        # Draw hover highlight
        if self.hovered_vertex and self.build_mode in ['settlement', 'city']:
            self.draw_vertex_hover(board_surface)
        elif self.hovered_edge and self.build_mode == 'road':
            self.draw_edge_hover(board_surface)
        
        # Draw board border
        pygame.draw.line(self.screen, Colors.BORDER, 
                        (self.board_width, 0), (self.board_width, self.height), 3)
        
        # Draw UI (right side)
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_buildings(self, surface):
        """Draw all placed buildings."""
        # Draw roads first
        for edge, player_id in self.topology.roads.items():
            player = self.controller.game_state.players[player_id]
            color = self.get_player_color_rgb(player)
            pos1, pos2 = self.renderer.get_edge_pixel_position(edge, self.camera.x, self.camera.y)
            self.renderer.draw_road(surface, pos1, pos2, color)
        
        # Draw settlements
        for vertex, player_id in self.topology.settlements.items():
            player = self.controller.game_state.players[player_id]
            color = self.get_player_color_rgb(player)
            x, y = self.renderer.get_vertex_pixel_position(vertex, self.camera.x, self.camera.y)
            self.renderer.draw_settlement(surface, x, y, color)
        
        # Draw cities
        for vertex, player_id in self.topology.cities.items():
            player = self.controller.game_state.players[player_id]
            color = self.get_player_color_rgb(player)
            x, y = self.renderer.get_vertex_pixel_position(vertex, self.camera.x, self.camera.y)
            self.renderer.draw_city(surface, x, y, color)
    
    def draw_vertex_hover(self, surface):
        """Draw highlight for hovered vertex."""
        if self.hovered_vertex:
            x, y = self.renderer.get_vertex_pixel_position(
                self.hovered_vertex, self.camera.x, self.camera.y)
            
            player = self.controller.get_current_player()
            if self.build_mode == 'settlement':
                can_place = self.topology.can_place_settlement(
                    self.hovered_vertex, player.player_id, 
                    is_setup=self.controller.game_state.game_phase == GamePhase.SETUP)
            else:
                can_place = self.topology.can_place_city(
                    self.hovered_vertex, player.player_id)
            
            color = (100, 255, 100) if can_place else (255, 100, 100)
            self.renderer.draw_vertex_highlight(surface, x, y, color)
    
    def draw_edge_hover(self, surface):
        """Draw highlight for hovered edge."""
        if self.hovered_edge:
            pos1, pos2 = self.renderer.get_edge_pixel_position(
                self.hovered_edge, self.camera.x, self.camera.y)
            
            player = self.controller.get_current_player()
            can_place = self.topology.can_place_road(
                self.hovered_edge, player.player_id,
                is_setup=self.controller.game_state.game_phase == GamePhase.SETUP)
            
            color = (100, 255, 100) if can_place else (255, 100, 100)
            self.renderer.draw_edge_highlight(surface, pos1, pos2, color)
    
    def draw_ui(self):
        """Draw all UI elements on right panel."""
        y_offset = 10
        
        # Current player and phase
        y_offset = self.draw_current_player_info(y_offset)
        y_offset += 20
        
        # Dice
        if self.last_dice_roll:
            y_offset = self.draw_dice(y_offset)
            y_offset += 20
        
        # Resources
        y_offset = self.draw_resources(y_offset)
        y_offset += 20
        
        # Buildings count
        y_offset = self.draw_building_count(y_offset)
        y_offset += 20
        
        # All players status
        y_offset = self.draw_all_players(y_offset)
        y_offset += 20
        
        # Trading interface
        if self.trade_mode:
            y_offset = self.draw_trade_interface(y_offset)
            y_offset += 20
        
        # Controls
        self.draw_controls()
    
    def draw_current_player_info(self, y: int) -> int:
        """Draw current player info."""
        player = self.controller.get_current_player()
        color = self.get_player_color_rgb(player)
        info = self.controller.get_game_info()
        
        # Player name with color
        self.draw_ui_text(f"CURRENT: {player.name}", self.ui_x, y, color, font='large')
        y += 35
        
        # Phase
        if info['phase'] == 'setup':
            phase_text = self.controller.get_setup_instructions()
            self.draw_ui_text(phase_text, self.ui_x, y, (255, 200, 0), wrap_width=self.ui_width-20)
            y += 50
        else:
            if not self.controller.dice_rolled:
                self.draw_ui_text("Press SPACE to roll dice", self.ui_x, y, (255, 200, 0))
            else:
                self.draw_ui_text("Build, trade, or press ENTER to end turn", self.ui_x, y, (100, 255, 100))
            y += 30
        
        # Message
        self.draw_ui_text(info['message'], self.ui_x, y, Colors.TEXT, wrap_width=self.ui_width-20)
        y += 40
        
        return y
    
    def draw_dice(self, y: int) -> int:
        """Draw dice."""
        self.draw_ui_text("Last Roll:", self.ui_x, y, Colors.TEXT)
        y += 25
        
        die1, die2 = self.last_dice_roll
        DiceDisplay.draw(self.screen, die1, die2, self.ui_x + 50, y)
        y += 60
        
        total = die1 + die2
        self.draw_ui_text(f"Total: {total}", self.ui_x + 50, y, Colors.TEXT, font='large')
        y += 30
        
        return y
    
    def draw_resources(self, y: int) -> int:
        """Draw resource cards."""
        player = self.controller.get_current_player()
        
        self.draw_ui_text("Resources:", self.ui_x, y, Colors.TEXT)
        y += 25
        
        ResourceDisplay.draw(self.screen, player, self.ui_x, y, self.renderer.font_small)
        y += 90
        
        return y
    
    def draw_building_count(self, y: int) -> int:
        """Draw building counts."""
        player = self.controller.get_current_player()
        
        self.draw_ui_text("Buildings:", self.ui_x, y, Colors.TEXT)
        y += 25
        
        lines = [
            f"Settlements: {len(player.settlements)}/5 ({player.settlements_remaining} left)",
            f"Cities: {len(player.cities)}/4 ({player.cities_remaining} left)",
            f"Roads: {len(player.roads)}/15 ({player.roads_remaining} left)",
            f"Victory Points: {player.calculate_victory_points()}"
        ]
        
        for line in lines:
            self.draw_ui_text(line, self.ui_x, y, Colors.TEXT, font='small')
            y += 22
        
        return y
    
    def draw_all_players(self, y: int) -> int:
        """Draw all players' status."""
        self.draw_ui_text("All Players:", self.ui_x, y, Colors.TEXT)
        y += 25
        
        for player in self.controller.game_state.players:
            color = self.get_player_color_rgb(player)
            vp = player.calculate_victory_points()
            
            # Player name and VP
            text = f"{player.name}: {vp} VP"
            if player.has_longest_road:
                text += " 🛣️"
            if player.has_largest_army:
                text += " ⚔️"
            
            self.draw_ui_text(text, self.ui_x, y, color)
            y += 20
        
        y += 10
        return y
    
    def draw_trade_interface(self, y: int) -> int:
        """Draw trading interface."""
        player = self.controller.get_current_player()
        
        self.draw_ui_text("=== BANK TRADE ===", self.ui_x, y, (255, 215, 0), font='large')
        y += 30
        
        # Give section
        self.draw_ui_text("GIVE (press 1-5):", self.ui_x, y, Colors.TEXT)
        y += 20
        
        resources = ['wood', 'brick', 'sheep', 'wheat', 'ore']
        for i, resource in enumerate(resources):
            color = ResourceDisplay.RESOURCE_COLORS[resource]
            text = f"{i+1}. {resource.upper()}"
            if self.trade_give_resource == resource:
                text = f">>> {text} x{self.trade_give_amount} <<<"
                self.draw_ui_text(text, self.ui_x, y, color, font='large')
            else:
                self.draw_ui_text(text, self.ui_x, y, color)
            y += 20
        
        # Amount controls
        self.draw_ui_text(f"+/- to change amount: {self.trade_give_amount}", 
                         self.ui_x, y, (255, 200, 0))
        y += 25
        
        # Get section
        self.draw_ui_text("GET (press 6-0):", self.ui_x, y, Colors.TEXT)
        y += 20
        
        for i, resource in enumerate(resources):
            color = ResourceDisplay.RESOURCE_COLORS[resource]
            text = f"{i+6}. {resource.upper()}"
            if self.trade_get_resource == resource:
                text = f">>> {text} <<<"
                self.draw_ui_text(text, self.ui_x, y, color, font='large')
            else:
                self.draw_ui_text(text, self.ui_x, y, color)
            y += 20
        
        # Execute
        if self.trade_give_resource and self.trade_get_resource:
            ratio = player.trade_ratios.get(self.trade_give_resource, 4)
            get_amount = self.trade_give_amount // ratio
            
            self.draw_ui_text(f"Trade {self.trade_give_amount} {self.trade_give_resource}",
                             self.ui_x, y, (100, 255, 100))
            y += 20
            self.draw_ui_text(f"for {get_amount} {self.trade_get_resource}",
                             self.ui_x, y, (100, 255, 100))
            y += 20
            self.draw_ui_text("Press SPACE to confirm", self.ui_x, y, (255, 255, 100))
            y += 25
        
        self.draw_ui_text("Press T to exit trade mode", self.ui_x, y, (200, 200, 200), font='small')
        y += 20
        
        return y
    
    def draw_controls(self):
        """Draw controls at bottom."""
        y = self.height - 220
        
        self.draw_ui_text("Controls:", self.ui_x, y, Colors.TEXT)
        y += 25
        
        controls = [
            "S - Settlement mode",
            "C - City mode",
            "R - Road mode",
            "T - Trade mode",
            "SPACE - Roll dice",
            "ENTER - End turn",
            "H - Help",
            "Drag - Pan camera",
            "Scroll - Zoom"
        ]
        
        for control in controls:
            self.draw_ui_text(control, self.ui_x, y, Colors.TEXT, font='small')
            y += 18
    
    def draw_ui_text(self, text: str, x: int, y: int, color: Tuple[int, int, int],
                    font: str = 'small', wrap_width: int = None):
        """Draw text in UI area."""
        font_obj = self.renderer.font_large if font == 'large' else self.renderer.font_small
        
        if wrap_width:
            # Simple word wrap
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = font_obj.render(test_line, True, color)
                
                if test_surface.get_width() <= wrap_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                text_surface = font_obj.render(line, True, color)
                self.screen.blit(text_surface, (x, y))
                y += text_surface.get_height() + 2
        else:
            text_surface = font_obj.render(text, True, color)
            self.screen.blit(text_surface, (x, y))
    
    def run(self):
        """Main game loop."""
        print("\n" + "="*60)
        print("SETTLERS OF CATAN - FULL GAME")
        print("="*60)
        print("\nFollow the on-screen instructions!")
        print("Press H for help at any time")
        
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()


def main():
    """Entry point."""
    print("="*60)
    print("SETTLERS OF CATAN - FULL GAME")
    print("="*60)
    print("\nEnter player names (2-4 players):")
    print("(Press Enter with empty name to finish)")
    
    player_names = []
    for i in range(4):
        name = input(f"Player {i+1}: ").strip()
        if not name:
            break
        player_names.append(name)
    
    if len(player_names) < 2:
        print("Need at least 2 players!")
        return
    
    print(f"\nStarting game with: {', '.join(player_names)}")
    print("Loading...")
    
    game = FullCatanGame(player_names)
    game.run()


if __name__ == "__main__":
    main()
