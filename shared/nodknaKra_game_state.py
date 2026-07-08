"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_game_state.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-08 - Gordon - Added file header with edit history tracking
2026-07-08 - Gordon - Created GameState class with phases, turns, victory conditions, 2-point margin rule
"""

from enum import Enum
from typing import List, Optional, Dict, Tuple
import random


class GamePhase(Enum):
    """Game phase states"""
    SETUP_PHASE_1 = "setup_phase_1"      # First round of placement
    SETUP_PHASE_2 = "setup_phase_2"      # Second round (reverse order)
    MAIN_GAME = "main_game"               # Main game play
    GAME_OVER = "game_over"


class GameState:
    """Manages overall game state, turns, and victory conditions"""
    
    def __init__(self, num_players: int, victory_points_to_win: Dict[int, int], victory_margin: int = 2):
        """
        Initialize game state.
        
        Args:
            num_players: Number of players (2-6)
            victory_points_to_win: Dict mapping player count to VP needed
            victory_margin: Win by this many points (NodKnaKra default: 2)
        """
        if num_players < 2 or num_players > 6:
            raise ValueError("Game must have 2-6 players")
        
        self.num_players = num_players
        self.victory_points_to_win = victory_points_to_win.get(num_players, 10)
        self.victory_margin = victory_margin
        
        # Game flow
        self.phase = GamePhase.SETUP_PHASE_1
        self.current_player_idx = 0
        self.turn_count = 0
        
        # Players (will be set by controller)
        self.players: List = []
        
        # Dice
        self.last_dice_roll = (0, 0)
        self.dice_total = 0
        
        # Robber
        self.robber_location: Optional[tuple] = None
        
        # Game history
        self.move_history: List = []
    
    def set_players(self, players: List):
        """Set the list of players"""
        if len(players) != self.num_players:
            raise ValueError(f"Expected {self.num_players} players")
        self.players = players
    
    def get_current_player(self):
        """Get the current player"""
        if not self.players:
            return None
        return self.players[self.current_player_idx]
    
    def get_current_player_idx(self) -> int:
        """Get current player index"""
        return self.current_player_idx
    
    # ===== TURN MANAGEMENT =====
    
    def next_turn(self):
        """Move to next turn"""
        if self.phase == GamePhase.SETUP_PHASE_1:
            # Setup phase 1: normal order
            self.current_player_idx += 1
            if self.current_player_idx >= self.num_players:
                # Move to setup phase 2
                self.phase = GamePhase.SETUP_PHASE_2
                self.current_player_idx = self.num_players - 1
        
        elif self.phase == GamePhase.SETUP_PHASE_2:
            # Setup phase 2: reverse order
            self.current_player_idx -= 1
            if self.current_player_idx < 0:
                # Move to main game
                self.phase = GamePhase.MAIN_GAME
                self.current_player_idx = 0
                self.turn_count = 0
        
        elif self.phase == GamePhase.MAIN_GAME:
            # Main game: normal order
            self.current_player_idx += 1
            if self.current_player_idx >= self.num_players:
                self.current_player_idx = 0
            self.turn_count += 1
    
    def get_phase(self) -> GamePhase:
        """Get current game phase"""
        return self.phase
    
    def get_turn_count(self) -> int:
        """Get total turns in main game"""
        return self.turn_count
    
    # ===== DICE ROLLING =====
    
    def roll_dice(self) -> Tuple[int, int]:
        """Roll two dice. Returns (die1, die2)"""
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.last_dice_roll = (die1, die2)
        self.dice_total = die1 + die2
        return (die1, die2)
    
    def get_last_roll(self) -> Tuple[int, int]:
        """Get last dice roll"""
        return self.last_dice_roll
    
    def get_dice_total(self) -> int:
        """Get total of last dice roll"""
        return self.dice_total
    
    # ===== ROBBER MANAGEMENT =====
    
    def set_robber_location(self, location: tuple):
        """Set robber location (hex coordinate)"""
        self.robber_location = location
    
    def get_robber_location(self) -> Optional[tuple]:
        """Get robber location"""
        return self.robber_location
    
    # ===== VICTORY CONDITIONS =====
    
    def check_winner(self) -> Optional[int]:
        """
        Check if there's a winner.
        Returns player_id if someone won, None otherwise.
        NodKnaKra: Must win by 2-point margin!
        """
        if self.phase != GamePhase.MAIN_GAME:
            return None  # Can't win in setup
        
        # Find highest VP player
        max_vp = -1
        leader_idx = -1
        
        for i, player in enumerate(self.players):
            vp = player.get_total_vp()
            if vp > max_vp:
                max_vp = vp
                leader_idx = i
        
        # Must have enough total VP and lead by margin
        if max_vp >= self.victory_points_to_win:
            # Check margin
            second_highest = -1
            for i, player in enumerate(self.players):
                if i != leader_idx:
                    vp = player.get_total_vp()
                    if vp > second_highest:
                        second_highest = vp
            
            # Win if lead by victory_margin
            if (max_vp - second_highest) >= self.victory_margin:
                return leader_idx
        
        return None
    
    def get_leader(self) -> Tuple[Optional[int], int]:
        """Get leader player index and their VP. Returns (player_idx, vp)"""
        if not self.players:
            return (None, 0)
        
        max_vp = -1
        leader_idx = -1
        
        for i, player in enumerate(self.players):
            vp = player.get_total_vp()
            if vp > max_vp:
                max_vp = vp
                leader_idx = i
        
        return (leader_idx, max_vp)
    
    def get_leaderboard(self) -> List[Tuple[int, str, int]]:
        """Get leaderboard. Returns list of (player_idx, name, total_vp) sorted by VP"""
        leaderboard = []
        for i, player in enumerate(self.players):
            leaderboard.append((i, player.name, player.get_total_vp()))
        
        leaderboard.sort(key=lambda x: x[2], reverse=True)
        return leaderboard
    
    # ===== GAME SUMMARY =====
    
    def print_status(self):
        """Print current game state"""
        print("\n" + "="*60)
        print("GAME STATUS")
        print("="*60)
        
        print(f"\nPhase: {self.phase.value}")
        print(f"Current Player: {self.get_current_player().name}")
        print(f"Turn Count: {self.turn_count}")
        
        print(f"\nLast Dice Roll: {self.last_dice_roll} = {self.dice_total}")
        
        if self.robber_location:
            print(f"Robber at: {self.robber_location}")
        
        print(f"\nVictory Condition: {self.victory_points_to_win} VP (win by {self.victory_margin})")
        
        print("\nLeaderboard:")
        leaderboard = self.get_leaderboard()
        for rank, (idx, name, vp) in enumerate(leaderboard, 1):
            print(f"  {rank}. {name}: {vp} VP")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    print("\nTesting NodKnaKra Game State...\n")
    
    # Create mock players
    class MockPlayer:
        def __init__(self, player_id, name):
            self.player_id = player_id
            self.name = name
            self._vp = 0
        
        def get_total_vp(self):
            return self._vp
    
    # Create game state for 4 players
    victory_points = {2: 10, 3: 17, 4: 15, 5: 12, 6: 10}
    game = GameState(4, victory_points, victory_margin=2)
    
    # Create mock players
    players = [
        MockPlayer(0, "Alice"),
        MockPlayer(1, "Bob"),
        MockPlayer(2, "Carol"),
        MockPlayer(3, "Dave")
    ]
    game.set_players(players)
    
    print("✓ Created game with 4 players")
    print(f"Victory condition: {game.victory_points_to_win} VP (win by {game.victory_margin})")
    
    # Test setup phase
    print("\n1. Test Setup Phase 1:")
    print(f"Phase: {game.phase.value}, Current player: {game.get_current_player().name}")
    game.next_turn()
    print(f"After next_turn(): Current player: {game.get_current_player().name}")
    
    # Skip to main game
    print("\n2. Skip to Main Game:")
    while game.phase != game.phase.__class__.MAIN_GAME:
        game.next_turn()
    print(f"Phase: {game.phase.value}, Turn: {game.turn_count}")
    
    # Test dice rolling
    print("\n3. Test Dice Rolling:")
    roll = game.roll_dice()
    print(f"Rolled: {roll[0]} + {roll[1]} = {game.get_dice_total()}")
    
    # Test robber
    print("\n4. Test Robber:")
    game.set_robber_location((0, 0))
    print(f"Robber at: {game.get_robber_location()}")
    
    # Test victory condition (without margin)
    print("\n5. Test Victory Condition:")
    players[0]._vp = 15  # Alice gets 15 VP
    players[1]._vp = 13  # Bob gets 13 VP
    print(f"Alice: {players[0].get_total_vp()} VP")
    print(f"Bob: {players[1].get_total_vp()} VP")
    print(f"Margin: {players[0].get_total_vp() - players[1].get_total_vp()}")
    
    winner = game.check_winner()
    if winner is not None:
        print(f"✓ Winner: {players[winner].name}!")
    else:
        print("No winner yet (need 2-point margin)")
    
    # Print status
    game.print_status()
    
    print("✓ Game state system working!")
