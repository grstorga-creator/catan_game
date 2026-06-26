"""
Game State Manager for Settlers of Catan
Manages the overall game state, turns, phases, and win conditions.
"""

import random
from typing import List, Optional, Dict, Tuple
from enum import Enum
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from player import Player, PlayerColor
from game_settings import GameSettings
from map_generator import MapGenerator
from dev_cards import DevelopmentCardDeck
from hex_grid import HexCoordinate


class GamePhase(Enum):
    """Game phases."""
    SETUP = "setup"           # Initial settlement/road placement
    MAIN_GAME = "main_game"   # Normal gameplay
    GAME_OVER = "game_over"   # Someone won


class TurnPhase(Enum):
    """Phases within a player's turn."""
    ROLL_DICE = "roll_dice"              # Roll dice for resource production
    DISCARD = "discard"                  # Discard if 7 rolled with 7+ cards
    MOVE_ROBBER = "move_robber"          # Move robber if 7 rolled
    MAIN_PHASE = "main_phase"            # Trade, build, play dev cards
    END_TURN = "end_turn"                # Cleanup and pass turn


class GameState:
    """Manages the complete game state."""
    
    def __init__(self, settings: GameSettings = None):
        """Initialize game state."""
        if settings is None:
            settings = GameSettings()
        
        self.settings = settings
        
        # Game info
        self.game_id = None
        self.game_phase = GamePhase.SETUP
        self.turn_phase = TurnPhase.ROLL_DICE
        self.turn_number = 0
        
        # Players
        self.players: List[Player] = []
        self.current_player_index = 0
        
        # Board
        self.map_generator = MapGenerator(settings)
        self.grid = None
        
        # Development cards
        self.dev_card_deck = DevelopmentCardDeck()
        
        # Robber
        self.robber_position: Optional[HexCoordinate] = None
        
        # Special achievements
        self.longest_road_player: Optional[Player] = None
        self.largest_army_player: Optional[Player] = None
        self.longest_road_length = 4  # Minimum length to claim
        self.largest_army_size = 2    # Minimum knights to claim
        
        # Dice
        self.last_dice_roll: Optional[Tuple[int, int]] = None
        
        # Game log
        self.game_log: List[str] = []
    
    def setup_game(self, player_names: List[str], map_template: str = None):
        """
        Setup a new game.
        
        Args:
            player_names: List of player names
            map_template: Map template to use (None = use current setting)
        """
        # Create players with different colors
        colors = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.WHITE, 
                 PlayerColor.ORANGE, PlayerColor.GREEN, PlayerColor.BROWN]
        
        self.players = []
        for i, name in enumerate(player_names):
            color = colors[i % len(colors)]
            player = Player(i, name, color)
            
            # Give starting resources if configured
            starting_resources = self.settings.get_starting_resources()
            for resource, amount in starting_resources.items():
                player.add_resource(resource, amount)
            
            self.players.append(player)
        
        # Generate map
        self.grid = self.map_generator.generate_map(map_template, randomize=True)
        
        # Find robber starting position (desert)
        for tile in self.grid.get_all_tiles():
            if tile.has_robber:
                self.robber_position = tile.coordinate
                break
        
        # Randomize player order
        random.shuffle(self.players)
        self.current_player_index = 0
        
        # Start in setup phase
        self.game_phase = GamePhase.SETUP
        self.turn_number = 1
        
        self.log_event(f"Game started with {len(self.players)} players")
        self.log_event(f"Victory points to win: {self.settings.get_victory_points_to_win()}")
    
    def get_current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_index]
    
    def next_player(self):
        """Advance to next player."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        if self.current_player_index == 0:
            self.turn_number += 1
    
    def roll_dice(self) -> Tuple[int, int]:
        """
        Roll two dice.
        Returns tuple of (die1, die2).
        """
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.last_dice_roll = (die1, die2)
        
        total = die1 + die2
        self.log_event(f"{self.get_current_player().name} rolled {die1} + {die2} = {total}")
        
        return (die1, die2)
    
    def distribute_resources(self, dice_total: int):
        """
        Distribute resources based on dice roll.
        
        Args:
            dice_total: Sum of dice (2-12)
        """
        if dice_total == 7:
            # Robber! No resources distributed
            self.log_event("Robber activated! No resources this turn.")
            return
        
        # Find all tiles with this number
        for tile in self.grid.get_land_tiles():
            if tile.number_token == dice_total and not tile.has_robber:
                # This tile produces
                resource = tile.resource
                
                # Check which players have settlements/cities adjacent
                # (This is placeholder - needs vertex implementation)
                self.log_event(f"Tile {tile.coordinate} produced {resource}")
    
    def check_discard_phase(self, dice_total: int) -> List[Player]:
        """
        Check if players need to discard (rolled 7 with 7+ cards).
        Returns list of players who must discard.
        """
        if dice_total != 7:
            return []
        
        players_to_discard = []
        max_cards = self.settings.get_max_cards_before_discard()
        
        for player in self.players:
            if player.get_total_resource_count() > max_cards:
                players_to_discard.append(player)
                self.log_event(f"{player.name} must discard half their cards")
        
        return players_to_discard
    
    def move_robber(self, new_position: HexCoordinate) -> bool:
        """
        Move the robber to a new position.
        
        Args:
            new_position: New hex coordinate for robber
            
        Returns:
            True if move is valid
        """
        # Can't stay on same position
        if new_position == self.robber_position:
            return False
        
        # Can't move to water (if that rule is enabled)
        tile = self.grid.get_tile(new_position)
        if not tile or not tile.is_land():
            if not self.settings.get_robber_rules().get('can_place_on_water', False):
                return False
        
        # Remove robber from old position
        if self.robber_position:
            old_tile = self.grid.get_tile(self.robber_position)
            if old_tile:
                old_tile.has_robber = False
        
        # Place robber on new position
        self.robber_position = new_position
        tile.has_robber = True
        
        self.log_event(f"Robber moved to {new_position}")
        return True
    
    def can_steal_from(self, target_player: Player) -> bool:
        """Check if current player can steal from target player."""
        # Target must have resources
        if target_player.get_total_resource_count() == 0:
            return False
        
        # Target must have building adjacent to robber
        # (This is placeholder - needs vertex implementation)
        return True
    
    def steal_resource(self, target_player: Player) -> Optional[str]:
        """
        Steal a random resource from target player.
        Returns the stolen resource type, or None if failed.
        """
        if not self.can_steal_from(target_player):
            return None
        
        # Get random resource from target
        available_resources = []
        for resource, amount in target_player.resources.items():
            available_resources.extend([resource] * amount)
        
        if not available_resources:
            return None
        
        stolen_resource = random.choice(available_resources)
        
        # Transfer resource
        target_player.remove_resource(stolen_resource, 1)
        self.get_current_player().add_resource(stolen_resource, 1)
        
        self.log_event(f"{self.get_current_player().name} stole from {target_player.name}")
        return stolen_resource
    
    def buy_development_card(self, player: Player) -> bool:
        """
        Player buys a development card.
        Returns True if successful.
        """
        cost = self.settings.get_building_cost('development_card')
        
        if not player.has_resources(cost):
            self.log_event(f"{player.name} cannot afford development card")
            return False
        
        card = self.dev_card_deck.draw_card()
        if not card:
            self.log_event("No development cards left!")
            return False
        
        # Pay cost
        player.pay_resources(cost)
        
        # Add card to hand
        player.add_dev_card(card)
        
        self.log_event(f"{player.name} bought a development card")
        return True
    
    def check_longest_road(self):
        """Check and update longest road achievement."""
        for player in self.players:
            road_length = player.get_road_length(None)  # Placeholder
            
            if road_length >= self.longest_road_length:
                if road_length > self.longest_road_length or self.longest_road_player is None:
                    # New longest road holder
                    if self.longest_road_player:
                        self.longest_road_player.has_longest_road = False
                    
                    self.longest_road_player = player
                    player.has_longest_road = True
                    self.longest_road_length = road_length
                    
                    self.log_event(f"{player.name} claimed Longest Road!")
    
    def check_largest_army(self):
        """Check and update largest army achievement."""
        for player in self.players:
            if player.knights_played >= self.largest_army_size:
                if player.knights_played > self.largest_army_size or self.largest_army_player is None:
                    # New largest army holder
                    if self.largest_army_player:
                        self.largest_army_player.has_largest_army = False
                    
                    self.largest_army_player = player
                    player.has_largest_army = True
                    self.largest_army_size = player.knights_played
                    
                    self.log_event(f"{player.name} claimed Largest Army!")
    
    def check_victory_condition(self) -> Optional[Player]:
        """
        Check if any player has won.
        Returns winning player, or None if no winner yet.
        """
        victory_points_needed = self.settings.get_victory_points_to_win()
        
        for player in self.players:
            vp = player.calculate_victory_points()
            if vp >= victory_points_needed:
                self.game_phase = GamePhase.GAME_OVER
                self.log_event(f"{player.name} wins with {vp} victory points!")
                return player
        
        return None
    
    def trade_with_bank(self, player: Player, give_resource: str, 
                       give_amount: int, get_resource: str) -> bool:
        """
        Execute a bank trade.
        Returns True if successful.
        """
        if player.trade_with_bank(give_resource, give_amount, get_resource):
            ratio = player.trade_ratios[give_resource]
            get_amount = give_amount // ratio
            self.log_event(f"{player.name} traded {give_amount} {give_resource} "
                          f"for {get_amount} {get_resource}")
            return True
        return False
    
    def trade_with_player(self, player1: Player, give1: Dict[str, int],
                         player2: Player, give2: Dict[str, int]) -> bool:
        """
        Execute a player-to-player trade.
        Returns True if successful.
        """
        # Check both players have the resources
        if not player1.has_resources(give1) or not player2.has_resources(give2):
            return False
        
        # Execute trade
        for resource, amount in give1.items():
            player1.remove_resource(resource, amount)
            player2.add_resource(resource, amount)
        
        for resource, amount in give2.items():
            player2.remove_resource(resource, amount)
            player1.add_resource(resource, amount)
        
        self.log_event(f"{player1.name} traded with {player2.name}")
        return True
    
    def log_event(self, message: str):
        """Add an event to the game log."""
        log_entry = f"[Turn {self.turn_number}] {message}"
        self.game_log.append(log_entry)
        print(log_entry)
    
    def get_game_summary(self) -> Dict:
        """Get a summary of the current game state."""
        return {
            'game_phase': self.game_phase.value,
            'turn_number': self.turn_number,
            'current_player': self.get_current_player().name,
            'players': [
                {
                    'name': p.name,
                    'color': p.color.value,
                    'victory_points': p.calculate_victory_points(),
                    'resources': p.get_total_resource_count(),
                    'dev_cards': p.get_total_dev_card_count()
                }
                for p in self.players
            ],
            'dev_cards_remaining': self.dev_card_deck.cards_remaining()
        }
    
    def to_dict(self) -> Dict:
        """Serialize game state to dictionary."""
        return {
            'game_phase': self.game_phase.value,
            'turn_phase': self.turn_phase.value,
            'turn_number': self.turn_number,
            'current_player_index': self.current_player_index,
            'players': [p.to_dict() for p in self.players],
            'robber_position': self.robber_position.to_dict() if self.robber_position else None,
            'longest_road_length': self.longest_road_length,
            'largest_army_size': self.largest_army_size,
            'last_dice_roll': self.last_dice_roll,
            'game_log': self.game_log[-50:]  # Last 50 events
        }


# Testing
if __name__ == "__main__":
    print("=== Game State Manager Test ===\n")
    
    # Create game
    settings = GameSettings()
    game = GameState(settings)
    
    # Setup game
    print("--- Setting Up Game ---")
    player_names = ["Alice", "Bob", "Charlie"]
    game.setup_game(player_names, 'standard_3_4_player')
    
    print(f"Game started with {len(game.players)} players")
    for player in game.players:
        print(f"  - {player}")
    
    # Test turn
    print("\n--- Starting First Turn ---")
    current_player = game.get_current_player()
    print(f"Current player: {current_player.name}")
    
    # Roll dice
    die1, die2 = game.roll_dice()
    total = die1 + die2
    print(f"Rolled: {die1} + {die2} = {total}")
    
    # Distribute resources (placeholder)
    game.distribute_resources(total)
    
    # Test buying dev card
    print("\n--- Testing Development Cards ---")
    current_player.add_resource('sheep', 1)
    current_player.add_resource('wheat', 1)
    current_player.add_resource('ore', 1)
    
    print(f"Resources: {current_player.resources}")
    if game.buy_development_card(current_player):
        print(f"Dev cards in hand: {current_player.get_total_dev_card_count()}")
    
    # Test victory condition
    print("\n--- Testing Victory Condition ---")
    current_player.build_settlement((0, 0))
    current_player.build_settlement((1, 1))
    current_player.build_settlement((2, 2))
    current_player.build_city((0, 0))
    current_player.build_city((1, 1))
    
    vp = current_player.calculate_victory_points()
    print(f"{current_player.name} has {vp} victory points")
    
    winner = game.check_victory_condition()
    if winner:
        print(f"Winner: {winner.name}!")
    else:
        print("No winner yet")
    
    # Test game summary
    print("\n--- Game Summary ---")
    summary = game.get_game_summary()
    print(f"Turn: {summary['turn_number']}")
    print(f"Current player: {summary['current_player']}")
    print("Players:")
    for p in summary['players']:
        print(f"  {p['name']}: {p['victory_points']} VP, "
              f"{p['resources']} resources, {p['dev_cards']} dev cards")
    
    # Show game log
    print("\n--- Game Log (last 10 events) ---")
    for event in game.game_log[-10:]:
        print(event)
