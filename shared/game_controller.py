"""
Complete Catan Game Controller
Manages full game flow: setup, turns, resource distribution, trading, and victory.
"""

import random
from typing import Optional, List, Tuple, Dict
from enum import Enum
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from shared.game_state import GameState, GamePhase, TurnPhase
from shared.player import Player, PlayerColor
from shared.board_topology import BoardTopology, Vertex, Edge
from shared.hex_grid import HexCoordinate
from shared.map_generator import MapGenerator
from shared.game_settings import GameSettings


class SetupPhase(Enum):
    """Setup phase stages."""
    FIRST_SETTLEMENT = "first_settlement"
    FIRST_ROAD = "first_road"
    SECOND_SETTLEMENT = "second_settlement"
    SECOND_ROAD = "second_road"
    COMPLETE = "complete"


class GameController:
    """
    Complete game controller managing all game flow.
    Integrates all systems into a playable game.
    """
    
    def __init__(self, player_names: List[str], settings: GameSettings = None):
        """Initialize the game controller."""
        if settings is None:
            settings = GameSettings()
        
        self.settings = settings
        self.game_state = GameState(settings)
        
        # Setup game
        self.game_state.setup_game(player_names)
        
        # Create topology
        self.topology = BoardTopology(self.game_state.grid)
        
        # Setup phase tracking
        self.setup_phase = SetupPhase.FIRST_SETTLEMENT
        self.setup_round = 1  # Round 1 or 2
        self.setup_player_order = list(range(len(self.game_state.players)))
        self.setup_player_index = 0
        self.last_settlement_placed = None
        
        # Turn state
        self.dice_rolled = False
        self.can_build = True
        self.can_trade = True
        self.can_buy_dev_card = True
        
        # UI state
        self.message = "Game started! Beginning setup phase."
        self.pending_trades = []
        
        print(f"\n{'='*60}")
        print("SETTLERS OF CATAN - GAME START")
        print(f"{'='*60}")
        print(f"Players: {', '.join([p.name for p in self.game_state.players])}")
        print(f"Victory points to win: {self.settings.get_victory_points_to_win()}")
        print("\n>>> SETUP PHASE")
        print("Round 1: Each player places 1 settlement and 1 road")
        print("Round 2: Reverse order, place 1 settlement and 1 road")
        print(f"\n{self.get_current_player().name}'s turn to place first settlement!")
    
    def get_current_player(self) -> Player:
        """Get current player."""
        if self.game_state.game_phase == GamePhase.SETUP:
            return self.game_state.players[self.setup_player_order[self.setup_player_index]]
        return self.game_state.get_current_player()
    
    def get_setup_instructions(self) -> str:
        """Get instructions for current setup phase."""
        player = self.get_current_player()
        
        if self.setup_phase == SetupPhase.FIRST_SETTLEMENT:
            return f"{player.name}: Place your first settlement (Round {self.setup_round})"
        elif self.setup_phase == SetupPhase.FIRST_ROAD:
            return f"{player.name}: Place a road connected to your settlement"
        elif self.setup_phase == SetupPhase.SECOND_SETTLEMENT:
            return f"{player.name}: Place your second settlement (Round {self.setup_round})"
        elif self.setup_phase == SetupPhase.SECOND_ROAD:
            return f"{player.name}: Place a road connected to your settlement"
        return ""
    
    def try_place_settlement(self, vertex: Vertex) -> bool:
        """Try to place a settlement during setup or main game."""
        player = self.get_current_player()
        
        # Check if in setup phase
        is_setup = self.game_state.game_phase == GamePhase.SETUP
        
        # Check if it's settlement placement phase in setup
        if is_setup:
            if self.setup_phase not in [SetupPhase.FIRST_SETTLEMENT, SetupPhase.SECOND_SETTLEMENT]:
                self.message = "Place a road first!"
                return False
        
        # Check resources in main game
        if not is_setup:
            if not self.can_build:
                self.message = "Cannot build yet this turn!"
                return False
            
            cost = self.settings.get_building_cost('settlement')
            if not player.has_resources(cost):
                self.message = "Not enough resources!"
                return False
        
        # Try to place
        if self.topology.place_settlement(vertex, player.player_id, is_setup=is_setup):
            player.build_settlement(vertex)
            
            # Pay resources in main game
            if not is_setup:
                cost = self.settings.get_building_cost('settlement')
                player.pay_resources(cost)
            
            # During setup, remember this settlement for road placement
            if is_setup:
                self.last_settlement_placed = vertex
                self.message = f"{player.name} placed a settlement!"
                
                # Advance setup phase
                if self.setup_phase == SetupPhase.FIRST_SETTLEMENT:
                    self.setup_phase = SetupPhase.FIRST_ROAD
                elif self.setup_phase == SetupPhase.SECOND_SETTLEMENT:
                    self.setup_phase = SetupPhase.SECOND_ROAD
                    # Give resources in round 2
                    self._give_initial_resources(vertex, player)
            else:
                self.message = f"{player.name} built a settlement!"
            
            # Check victory
            self._check_victory()
            return True
        else:
            self.message = "Cannot place settlement here!"
            return False
    
    def try_place_city(self, vertex: Vertex) -> bool:
        """Try to upgrade settlement to city."""
        player = self.get_current_player()
        
        # Only in main game
        if self.game_state.game_phase == GamePhase.SETUP:
            self.message = "Cannot build cities during setup!"
            return False
        
        if not self.can_build:
            self.message = "Cannot build yet this turn!"
            return False
        
        # Check resources
        cost = self.settings.get_building_cost('city')
        if not player.has_resources(cost):
            self.message = "Not enough resources!"
            return False
        
        # Try to place
        if self.topology.place_city(vertex, player.player_id):
            player.build_city(vertex)
            player.pay_resources(cost)
            self.message = f"{player.name} upgraded to a city!"
            
            # Check longest road (cities don't affect it but good to update)
            self._update_longest_road()
            
            # Check victory
            self._check_victory()
            return True
        else:
            self.message = "Cannot upgrade to city here!"
            return False
    
    def try_place_road(self, edge: Edge) -> bool:
        """Try to place a road."""
        player = self.get_current_player()
        
        # Check if in setup phase
        is_setup = self.game_state.game_phase == GamePhase.SETUP
        
        # Check if it's road placement phase in setup
        if is_setup:
            if self.setup_phase not in [SetupPhase.FIRST_ROAD, SetupPhase.SECOND_ROAD]:
                self.message = "Place a settlement first!"
                return False
            
            # In setup, road must connect to the settlement just placed
            if self.last_settlement_placed:
                v1, v2 = edge.get_vertices()
                if self.last_settlement_placed not in [v1, v2]:
                    self.message = "Road must connect to your settlement!"
                    return False
        
        # Check resources in main game
        if not is_setup:
            if not self.can_build:
                self.message = "Cannot build yet this turn!"
                return False
            
            cost = self.settings.get_building_cost('road')
            if not player.has_resources(cost):
                self.message = "Not enough resources!"
                return False
        
        # Try to place
        if self.topology.place_road(edge, player.player_id, is_setup=is_setup):
            player.build_road(edge)
            
            # Pay resources in main game
            if not is_setup:
                cost = self.settings.get_building_cost('road')
                player.pay_resources(cost)
            
            # During setup, advance to next player/phase
            if is_setup:
                self.message = f"{player.name} placed a road!"
                self._advance_setup_phase()
            else:
                self.message = f"{player.name} built a road!"
                # Update longest road
                self._update_longest_road()
            
            return True
        else:
            self.message = "Cannot place road here!"
            return False
    
    def _give_initial_resources(self, vertex: Vertex, player: Player):
        """Give initial resources for second settlement in setup."""
        resources = self.topology.get_vertex_resources(vertex)
        for resource in resources:
            if resource != 'desert':
                player.add_resource(resource, 1)
        
        if resources:
            self.message += f" Received: {', '.join(resources)}"
    
    def _advance_setup_phase(self):
        """Advance setup phase to next step."""
        if self.setup_phase == SetupPhase.FIRST_ROAD:
            # Move to next player
            self.setup_player_index += 1
            
            if self.setup_player_index >= len(self.setup_player_order):
                # End of round 1, start round 2 in reverse
                self.setup_round = 2
                self.setup_player_order.reverse()
                self.setup_player_index = 0
                self.setup_phase = SetupPhase.SECOND_SETTLEMENT
                print("\n>>> SETUP ROUND 2 (Reverse Order)")
            else:
                self.setup_phase = SetupPhase.FIRST_SETTLEMENT
            
            self.last_settlement_placed = None
            
        elif self.setup_phase == SetupPhase.SECOND_ROAD:
            # Move to next player in reverse order
            self.setup_player_index += 1
            
            if self.setup_player_index >= len(self.setup_player_order):
                # Setup complete!
                self._end_setup_phase()
            else:
                self.setup_phase = SetupPhase.SECOND_SETTLEMENT
                self.last_settlement_placed = None
    
    def _end_setup_phase(self):
        """End setup phase and start main game."""
        self.game_state.game_phase = GamePhase.MAIN_GAME
        self.setup_phase = SetupPhase.COMPLETE
        
        # Reset to first player (from original order)
        self.game_state.current_player_index = 0
        
        print("\n" + "="*60)
        print(">>> MAIN GAME BEGINS!")
        print("="*60)
        self.message = f"{self.game_state.get_current_player().name}'s turn! Roll the dice."
        self.game_state.log_event("Setup complete, main game begins")
    
    def roll_dice(self) -> Tuple[int, int]:
        """Roll dice and distribute resources."""
        if self.game_state.game_phase == GamePhase.SETUP:
            self.message = "Cannot roll during setup!"
            return None
        
        if self.dice_rolled:
            self.message = "Already rolled this turn!"
            return None
        
        # Roll
        die1, die2 = self.game_state.roll_dice()
        total = die1 + die2
        self.dice_rolled = True
        
        if total == 7:
            # Robber!
            self.message = f"Rolled {total}! ROBBER! Players with 7+ cards must discard."
            self._handle_robber(total)
        else:
            # Distribute resources
            self._distribute_resources(total)
            self.message = f"Rolled {total}. Resources distributed!"
        
        return (die1, die2)
    
    def _handle_robber(self, dice_total: int):
        """Handle robber (7 rolled)."""
        # Check who needs to discard
        players_to_discard = self.game_state.check_discard_phase(dice_total)
        
        if players_to_discard:
            # For now, auto-discard
            for player in players_to_discard:
                player.discard_half_resources()
        
        # TODO: Player must move robber and steal
        # For now, robber stays where it is
    
    def _distribute_resources(self, dice_total: int):
        """Distribute resources based on dice roll."""
        if dice_total == 7:
            return
        
        resource_log = {}  # Track what each player receives
        
        # Find all tiles with this number
        for tile in self.game_state.grid.get_land_tiles():
            if tile.number_token == dice_total and not tile.has_robber:
                resource = tile.resource
                
                if resource == 'desert':
                    continue
                
                # Check all 6 vertices of this tile
                for direction in range(6):
                    vertex = Vertex(tile.coordinate, direction)
                    
                    # Check for settlement
                    if vertex in self.topology.settlements:
                        player_id = self.topology.settlements[vertex]
                        player = self.game_state.players[player_id]
                        player.add_resource(resource, 1)
                        
                        if player.name not in resource_log:
                            resource_log[player.name] = []
                        resource_log[player.name].append(f"1 {resource}")
                    
                    # Check for city (gets 2)
                    elif vertex in self.topology.cities:
                        player_id = self.topology.cities[vertex]
                        player = self.game_state.players[player_id]
                        player.add_resource(resource, 2)
                        
                        if player.name not in resource_log:
                            resource_log[player.name] = []
                        resource_log[player.name].append(f"2 {resource}")
        
        # Log what was distributed
        if resource_log:
            for player_name, resources in resource_log.items():
                self.game_state.log_event(f"{player_name} receives: {', '.join(resources)}")
            print(f"Resources distributed:")
            for player_name, resources in resource_log.items():
                print(f"  {player_name}: {', '.join(resources)}")
        else:
            print(f"No resources produced for roll of {dice_total}")
    
    def buy_development_card(self) -> bool:
        """Buy a development card."""
        if self.game_state.game_phase == GamePhase.SETUP:
            self.message = "Cannot buy dev cards during setup!"
            return False
        
        if not self.can_buy_dev_card:
            self.message = "Cannot buy dev cards yet this turn!"
            return False
        
        player = self.get_current_player()
        
        if self.game_state.buy_development_card(player):
            self.message = f"{player.name} bought a development card!"
            return True
        else:
            return False
    
    def trade_with_bank(self, give_resource: str, give_amount: int, get_resource: str) -> bool:
        """Execute bank trade."""
        if self.game_state.game_phase == GamePhase.SETUP:
            self.message = "Cannot trade during setup!"
            return False
        
        if not self.can_trade:
            self.message = "Cannot trade yet - roll dice first!"
            return False
        
        player = self.get_current_player()
        
        # Check if player has the resources
        if player.resources.get(give_resource, 0) < give_amount:
            self.message = f"Not enough {give_resource}!"
            return False
        
        # Get trade ratio
        ratio = player.trade_ratios.get(give_resource, 4)
        
        # Check if amount matches ratio
        if give_amount < ratio:
            self.message = f"Need at least {ratio} {give_resource} to trade"
            return False
        
        # Calculate how many resources they get
        get_amount = give_amount // ratio
        
        # Execute trade
        player.remove_resource(give_resource, give_amount)
        player.add_resource(get_resource, get_amount)
        
        self.message = f"{player.name} traded {give_amount} {give_resource} for {get_amount} {get_resource}!"
        self.game_state.log_event(self.message)
        print(self.message)
        
        return True
    
    def end_turn(self):
        """End current player's turn."""
        if self.game_state.game_phase == GamePhase.SETUP:
            self.message = "Complete setup phase first!"
            return
        
        # Check for victory
        if self._check_victory():
            return
        
        # Next player
        self.game_state.next_player()
        
        # Reset turn state
        self.dice_rolled = False
        self.can_build = False  # Can build after rolling
        self.can_trade = False  # Can trade after rolling
        self.can_buy_dev_card = False  # Can buy after rolling
        
        self.message = f"{self.game_state.get_current_player().name}'s turn! Roll the dice."
    
    def _update_longest_road(self):
        """Update longest road achievement."""
        max_length = 0
        max_player = None
        
        for player in self.game_state.players:
            length = self.topology.get_longest_road(player.player_id)
            if length >= 5 and length > max_length:
                max_length = length
                max_player = player
        
        # Update achievement
        if max_player and max_player != self.game_state.longest_road_player:
            if self.game_state.longest_road_player:
                self.game_state.longest_road_player.has_longest_road = False
            
            max_player.has_longest_road = True
            self.game_state.longest_road_player = max_player
            self.game_state.longest_road_length = max_length
            self.message += f" {max_player.name} claims Longest Road!"
    
    def _check_victory(self) -> bool:
        """Check if current player won."""
        winner = self.game_state.check_victory_condition()
        if winner:
            self.message = f"🎉 {winner.name} WINS with {winner.victory_points} victory points!"
            return True
        return False
    
    def get_game_info(self) -> Dict:
        """Get current game information for UI."""
        player = self.get_current_player()
        
        return {
            'phase': self.game_state.game_phase.value,
            'setup_phase': self.setup_phase.value if self.game_state.game_phase == GamePhase.SETUP else None,
            'current_player': player.name,
            'current_player_color': player.color.value,
            'turn_number': self.game_state.turn_number,
            'dice_rolled': self.dice_rolled,
            'can_build': self.can_build or self.game_state.game_phase == GamePhase.SETUP,
            'can_trade': self.can_trade,
            'message': self.message,
            'players': [
                {
                    'name': p.name,
                    'color': p.color.value,
                    'victory_points': p.calculate_victory_points(),
                    'resources': p.get_total_resource_count(),
                    'settlements': len(p.settlements),
                    'cities': len(p.cities),
                    'roads': len(p.roads),
                    'dev_cards': len(p.development_cards),
                    'has_longest_road': p.has_longest_road,
                    'has_largest_army': p.has_largest_army
                }
                for p in self.game_state.players
            ]
        }


# Testing
if __name__ == "__main__":
    print("=== Game Controller Test ===\n")
    
    # Create game
    controller = GameController(["Alice", "Bob", "Charlie"])
    
    print("\n--- Game Info ---")
    info = controller.get_game_info()
    print(f"Phase: {info['phase']}")
    print(f"Setup Phase: {info['setup_phase']}")
    print(f"Current Player: {info['current_player']}")
    print(f"Message: {info['message']}")
    
    print("\n--- Players ---")
    for p_info in info['players']:
        print(f"{p_info['name']}: {p_info['victory_points']} VP, "
              f"{p_info['settlements']} settlements")
