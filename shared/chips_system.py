"""
Project: NodKnaKra Settlers of Catan
File: chips_system.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-08 - Gordon - Added file header with edit history tracking
2026-07-08 - Gordon - Created ChipsSystem class with earn, convert, trade mechanics
"""

from typing import Dict, Optional


class ChipsSystem:
    """Manages the chip economy for all players"""
    
    def __init__(self, num_players: int):
        """Initialize chips for all players"""
        self.num_players = num_players
        self.chips: Dict[int, int] = {player_id: 0 for player_id in range(num_players)}
        self.history: list = []
    
    def add_chips(self, player_id: int, amount: int, reason: str = "") -> bool:
        """Add chips to a player"""
        if player_id >= self.num_players or player_id < 0:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        if amount < 0:
            raise ValueError(f"Cannot add negative chips: {amount}")
        
        self.chips[player_id] += amount
        self.history.append({
            'action': 'earned',
            'player': player_id,
            'amount': amount,
            'reason': reason,
            'total': self.chips[player_id]
        })
        return True
    
    def remove_chips(self, player_id: int, amount: int, reason: str = "") -> bool:
        """Remove chips from a player. Returns True if successful, False if insufficient."""
        if player_id >= self.num_players or player_id < 0:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        if amount < 0:
            raise ValueError(f"Cannot remove negative chips: {amount}")
        
        if self.chips[player_id] < amount:
            return False
        
        self.chips[player_id] -= amount
        self.history.append({
            'action': 'removed',
            'player': player_id,
            'amount': amount,
            'reason': reason,
            'total': self.chips[player_id]
        })
        return True
    
    def convert_to_resource(self, player_id: int, amount: int) -> bool:
        """Convert chips to resources (1:1 ratio). Returns True if successful."""
        if player_id >= self.num_players or player_id < 0:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        if amount <= 0:
            raise ValueError(f"Cannot convert {amount} chips")
        
        if self.chips[player_id] < amount:
            return False
        
        self.chips[player_id] -= amount
        self.history.append({
            'action': 'converted',
            'player': player_id,
            'amount': amount,
            'reason': 'converted_to_resources',
            'total': self.chips[player_id]
        })
        return True
    
    def trade_chips(self, from_player: int, to_player: int, amount: int) -> bool:
        """Trade chips between players. Returns True if successful."""
        if from_player >= self.num_players or from_player < 0:
            raise ValueError(f"Invalid player ID: {from_player}")
        
        if to_player >= self.num_players or to_player < 0:
            raise ValueError(f"Invalid player ID: {to_player}")
        
        if from_player == to_player:
            raise ValueError("Cannot trade with yourself")
        
        if amount <= 0:
            raise ValueError(f"Cannot trade {amount} chips")
        
        if self.chips[from_player] < amount:
            return False
        
        self.chips[from_player] -= amount
        self.chips[to_player] += amount
        
        self.history.append({
            'action': 'traded',
            'from_player': from_player,
            'to_player': to_player,
            'amount': amount,
            'from_total': self.chips[from_player],
            'to_total': self.chips[to_player]
        })
        return True
    
    def get_chips(self, player_id: int) -> int:
        """Get chip count for a player"""
        if player_id >= self.num_players or player_id < 0:
            raise ValueError(f"Invalid player ID: {player_id}")
        return self.chips[player_id]
    
    def get_all_chips(self) -> Dict[int, int]:
        """Get chip counts for all players"""
        return self.chips.copy()
    
    def total_chips_in_play(self) -> int:
        """Get total chips that have been given out"""
        return sum(self.chips.values())
    
    def print_status(self):
        """Print current chip status for all players"""
        print("\n" + "="*50)
        print("Chips Status")
        print("="*50)
        for player_id in range(self.num_players):
            chips = self.chips[player_id]
            print(f"Player {player_id}: {chips} chips")
        print(f"\nTotal in play: {self.total_chips_in_play()}")
        print("="*50 + "\n")
    
    def print_history(self, limit: Optional[int] = None):
        """Print transaction history"""
        print("\n" + "="*50)
        print("Chips Transaction History")
        print("="*50)
        
        events = self.history if limit is None else self.history[-limit:]
        
        for i, event in enumerate(events, 1):
            if event['action'] == 'earned':
                print(f"{i}. Player {event['player']} earned {event['amount']} chips")
                print(f"   Reason: {event['reason']}")
                print(f"   Total: {event['total']}")
            
            elif event['action'] == 'removed':
                print(f"{i}. Player {event['player']} lost {event['amount']} chips")
                print(f"   Reason: {event['reason']}")
                print(f"   Total: {event['total']}")
            
            elif event['action'] == 'converted':
                print(f"{i}. Player {event['player']} converted {event['amount']} chips to resources")
                print(f"   Total: {event['total']}")
            
            elif event['action'] == 'traded':
                print(f"{i}. Player {event['from_player']} traded {event['amount']} chips to Player {event['to_player']}")
                print(f"   Player {event['from_player']} now has: {event['from_total']}")
                print(f"   Player {event['to_player']} now has: {event['to_total']}")
            print()
        
        print("="*50 + "\n")


if __name__ == "__main__":
    print("\nTesting NodKnaKra Chips System...\n")
    
    chips = ChipsSystem(4)
    print("✓ Created chips system for 4 players")
    
    print("\n1. Players earn chips from dice rolls:")
    chips.add_chips(0, 3, "Rolled 5, no settlements on 5")
    chips.add_chips(1, 2, "Rolled 8, one settlement on 8")
    chips.add_chips(2, 1, "Rolled 6, two settlements on 6")
    chips.print_status()
    
    print("2. Player 0 converts 2 chips to resources:")
    if chips.convert_to_resource(0, 2):
        print("✓ Conversion successful")
    chips.print_status()
    
    print("3. Player 1 trades 1 chip to Player 2:")
    if chips.trade_chips(1, 2, 1):
        print("✓ Trade successful")
    chips.print_status()
    
    print("4. Try to convert more chips than available:")
    if chips.convert_to_resource(0, 10):
        print("✓ Conversion successful")
    else:
        print("✗ Conversion failed (insufficient chips)")
    
    chips.print_history()
    
    print("✓ Chips system working!")
