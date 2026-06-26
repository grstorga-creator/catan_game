"""
Player Management for Settlers of Catan
Handles individual player state, resources, buildings, and victory points.
"""

from typing import Dict, List, Optional
from enum import Enum


class PlayerColor(Enum):
    """Player colors."""
    RED = "red"
    BLUE = "blue"
    WHITE = "white"
    ORANGE = "orange"
    GREEN = "green"
    BROWN = "brown"
    PURPLE = "purple"
    YELLOW = "yellow"


class Player:
    """Represents a player in the game."""
    
    def __init__(self, player_id: int, name: str, color: PlayerColor):
        """
        Initialize a player.
        
        Args:
            player_id: Unique player identifier
            name: Player name
            color: Player color
        """
        self.player_id = player_id
        self.name = name
        self.color = color
        
        # Resources
        self.resources = {
            'wood': 0,
            'brick': 0,
            'sheep': 0,
            'wheat': 0,
            'ore': 0
        }
        
        # Buildings (remaining to place)
        self.settlements_remaining = 5
        self.cities_remaining = 4
        self.roads_remaining = 15
        
        # Placed buildings (coordinates)
        self.settlements = []  # List of vertex positions
        self.cities = []       # List of vertex positions
        self.roads = []        # List of edge positions
        
        # Development cards
        self.development_cards = []
        self.played_dev_cards_this_turn = []
        
        # Special cards
        self.has_longest_road = False
        self.has_largest_army = False
        self.knights_played = 0
        
        # Victory points
        self.victory_points = 0
        
        # Trade ratios (default 4:1, can be improved with ports)
        self.trade_ratios = {
            'wood': 4,
            'brick': 4,
            'sheep': 4,
            'wheat': 4,
            'ore': 4
        }
    
    def add_resource(self, resource: str, amount: int = 1):
        """Add resources to player's hand."""
        if resource in self.resources:
            self.resources[resource] += amount
    
    def remove_resource(self, resource: str, amount: int = 1) -> bool:
        """
        Remove resources from player's hand.
        Returns True if successful, False if not enough resources.
        """
        if resource not in self.resources:
            return False
        
        if self.resources[resource] >= amount:
            self.resources[resource] -= amount
            return True
        return False
    
    def has_resources(self, cost: Dict[str, int]) -> bool:
        """Check if player has the required resources."""
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True
    
    def pay_resources(self, cost: Dict[str, int]) -> bool:
        """
        Pay resources for something (building, dev card, etc.).
        Returns True if successful, False if not enough resources.
        """
        if not self.has_resources(cost):
            return False
        
        for resource, amount in cost.items():
            self.remove_resource(resource, amount)
        return True
    
    def get_total_resource_count(self) -> int:
        """Get total number of resource cards."""
        return sum(self.resources.values())
    
    def get_total_dev_card_count(self) -> int:
        """Get total number of development cards."""
        return len(self.development_cards)
    
    def calculate_victory_points(self) -> int:
        """
        Calculate total victory points.
        
        Victory points come from:
        - Settlements: 1 point each
        - Cities: 2 points each
        - Development cards with victory points
        - Longest road: 2 points
        - Largest army: 2 points
        """
        points = 0
        
        # Buildings
        points += len(self.settlements) * 1
        points += len(self.cities) * 2
        
        # Development cards with victory points
        for card in self.development_cards:
            if card.is_victory_point:
                points += card.victory_points
        
        # Special achievements
        if self.has_longest_road:
            points += 2
        if self.has_largest_army:
            points += 2
        
        self.victory_points = points
        return points
    
    def can_build_settlement(self) -> bool:
        """Check if player can build a settlement."""
        return self.settlements_remaining > 0
    
    def can_build_city(self) -> bool:
        """Check if player can build a city."""
        return self.cities_remaining > 0 and len(self.settlements) > 0
    
    def can_build_road(self) -> bool:
        """Check if player can build a road."""
        return self.roads_remaining > 0
    
    def build_settlement(self, position) -> bool:
        """
        Build a settlement at position.
        Returns True if successful.
        """
        if not self.can_build_settlement():
            return False
        
        self.settlements.append(position)
        self.settlements_remaining -= 1
        return True
    
    def build_city(self, position) -> bool:
        """
        Upgrade a settlement to a city.
        Returns True if successful.
        """
        if not self.can_build_city():
            return False
        
        if position not in self.settlements:
            return False
        
        # Remove settlement, add city
        self.settlements.remove(position)
        self.cities.append(position)
        self.settlements_remaining += 1  # Get settlement back
        self.cities_remaining -= 1
        return True
    
    def build_road(self, position) -> bool:
        """
        Build a road at position.
        Returns True if successful.
        """
        if not self.can_build_road():
            return False
        
        self.roads.append(position)
        self.roads_remaining -= 1
        return True
    
    def add_dev_card(self, card):
        """Add a development card to hand."""
        self.development_cards.append(card)
    
    def play_dev_card(self, card) -> bool:
        """
        Play a development card.
        Returns True if successful.
        """
        if card not in self.development_cards:
            return False
        
        # Can't play dev card bought this turn (unless it's a victory point card)
        if not card.is_victory_point and card in self.played_dev_cards_this_turn:
            return False
        
        # Victory point cards are kept in hand
        if not card.is_victory_point:
            self.development_cards.remove(card)
        
        # Track knights for largest army
        if card.effect_type == 'knight':
            self.knights_played += 1
        
        return True
    
    def set_trade_ratio(self, resource: str, ratio: int):
        """Set trade ratio for a resource (from ports)."""
        if resource in self.trade_ratios:
            self.trade_ratios[resource] = min(self.trade_ratios[resource], ratio)
    
    def can_trade_with_bank(self, give_resource: str, give_amount: int) -> bool:
        """Check if player can trade with bank."""
        ratio = self.trade_ratios.get(give_resource, 4)
        
        # Need at least ratio amount to trade
        if give_amount < ratio:
            return False
        
        # Must have the resources
        return self.resources.get(give_resource, 0) >= give_amount
    
    def trade_with_bank(self, give_resource: str, give_amount: int, 
                       get_resource: str) -> bool:
        """
        Trade resources with the bank.
        Returns True if successful.
        """
        ratio = self.trade_ratios.get(give_resource, 4)
        
        # Calculate how many resources we get
        get_amount = give_amount // ratio
        
        if get_amount == 0:
            return False
        
        if not self.can_trade_with_bank(give_resource, give_amount):
            return False
        
        # Execute trade
        self.remove_resource(give_resource, give_amount)
        self.add_resource(get_resource, get_amount)
        return True
    
    def discard_half_resources(self) -> Dict[str, int]:
        """
        Discard half of resources (when robber rolled with 7+ cards).
        Returns dict of discarded resources.
        """
        total = self.get_total_resource_count()
        to_discard = total // 2
        
        discarded = {}
        
        # Simple strategy: discard proportionally
        for resource in ['wood', 'brick', 'sheep', 'wheat', 'ore']:
            if to_discard == 0:
                break
            
            amount = self.resources[resource]
            if amount > 0:
                discard = min(amount, to_discard)
                self.remove_resource(resource, discard)
                discarded[resource] = discard
                to_discard -= discard
        
        return discarded
    
    def get_road_length(self, roads_graph) -> int:
        """
        Calculate longest road length for this player.
        Uses graph traversal to find longest path.
        """
        # This is a placeholder - actual implementation needs graph algorithms
        # Will be implemented when we add board connectivity
        return len(self.roads)
    
    def __repr__(self):
        return f"Player({self.name}, {self.color.value}, VP={self.victory_points})"
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for serialization."""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'color': self.color.value,
            'resources': self.resources.copy(),
            'settlements_remaining': self.settlements_remaining,
            'cities_remaining': self.cities_remaining,
            'roads_remaining': self.roads_remaining,
            'settlements': self.settlements.copy(),
            'cities': self.cities.copy(),
            'roads': self.roads.copy(),
            'development_cards': len(self.development_cards),
            'has_longest_road': self.has_longest_road,
            'has_largest_army': self.has_largest_army,
            'knights_played': self.knights_played,
            'victory_points': self.victory_points,
            'trade_ratios': self.trade_ratios.copy()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Player':
        """Create player from dictionary."""
        color = PlayerColor(data['color'])
        player = Player(data['player_id'], data['name'], color)
        
        player.resources = data['resources']
        player.settlements_remaining = data['settlements_remaining']
        player.cities_remaining = data['cities_remaining']
        player.roads_remaining = data['roads_remaining']
        player.settlements = data['settlements']
        player.cities = data['cities']
        player.roads = data['roads']
        player.has_longest_road = data['has_longest_road']
        player.has_largest_army = data['has_largest_army']
        player.knights_played = data['knights_played']
        player.victory_points = data['victory_points']
        player.trade_ratios = data['trade_ratios']
        
        return player


# Testing
if __name__ == "__main__":
    print("=== Player Management Test ===\n")
    
    # Create a player
    player = Player(1, "Alice", PlayerColor.RED)
    print(f"Created: {player}")
    
    # Add resources
    print("\n--- Adding Resources ---")
    player.add_resource('wood', 3)
    player.add_resource('brick', 2)
    player.add_resource('sheep', 1)
    print(f"Resources: {player.resources}")
    print(f"Total cards: {player.get_total_resource_count()}")
    
    # Test building costs
    print("\n--- Testing Building ---")
    settlement_cost = {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1}
    print(f"Can afford settlement? {player.has_resources(settlement_cost)}")
    
    player.add_resource('wheat', 1)
    print(f"After adding wheat, can afford? {player.has_resources(settlement_cost)}")
    
    if player.pay_resources(settlement_cost):
        print("Paid for settlement!")
        print(f"Resources after: {player.resources}")
    
    # Test building
    print("\n--- Building Structures ---")
    print(f"Settlements remaining: {player.settlements_remaining}")
    player.build_settlement((0, 0))
    print(f"Built settlement at (0, 0)")
    print(f"Settlements remaining: {player.settlements_remaining}")
    print(f"Settlements placed: {player.settlements}")
    
    # Test victory points
    print("\n--- Victory Points ---")
    player.build_settlement((1, 1))
    player.build_city((0, 0))
    vp = player.calculate_victory_points()
    print(f"Total victory points: {vp}")
    print(f"  Settlements: {len(player.settlements)}")
    print(f"  Cities: {len(player.cities)}")
    
    # Test trading
    print("\n--- Trading ---")
    player.add_resource('wood', 10)
    print(f"Wood: {player.resources['wood']}")
    print(f"Default trade ratio for wood: {player.trade_ratios['wood']}")
    
    if player.trade_with_bank('wood', 4, 'ore'):
        print("Traded 4 wood for 1 ore!")
        print(f"Wood: {player.resources['wood']}, Ore: {player.resources['ore']}")
    
    # Test port
    print("\n--- Port Trading ---")
    player.set_trade_ratio('wood', 2)  # Got a wood port
    print(f"New trade ratio for wood: {player.trade_ratios['wood']}")
    
    if player.trade_with_bank('wood', 2, 'brick'):
        print("Traded 2 wood for 1 brick (with port)!")
        print(f"Wood: {player.resources['wood']}, Brick: {player.resources['brick']}")
    
    # Test serialization
    print("\n--- Serialization ---")
    data = player.to_dict()
    print(f"Serialized player has {len(data)} fields")
    
    player2 = Player.from_dict(data)
    print(f"Restored: {player2}")
    print(f"Resources match: {player2.resources == player.resources}")
