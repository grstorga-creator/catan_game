"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_player.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-08 - Gordon - Added file header with edit history tracking
2026-07-08 - Gordon - Created Player class with resources, chips, VP, cards, buildings
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class Resource(Enum):
    """Resource types"""
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"


@dataclass
class Building:
    """Represents a building placement"""
    building_type: str  # 'settlement', 'city', 'road'
    location: tuple  # (q, r) for hex, or ((q1,r1), (q2,r2)) for edge
    
    def __repr__(self):
        return f"{self.building_type} at {self.location}"


class Player:
    """Represents a single player in the game"""
    
    def __init__(self, player_id: int, name: str, color: str):
        """Initialize a player"""
        self.player_id = player_id
        self.name = name
        self.color = color
        
        # Resources (5 types)
        self.resources: Dict[Resource, int] = {
            Resource.WOOD: 0,
            Resource.BRICK: 0,
            Resource.SHEEP: 0,
            Resource.WHEAT: 0,
            Resource.ORE: 0
        }
        
        # Chips
        self.chips: int = 0
        
        # Victory Points
        self.visible_vp: int = 0  # From settlements, cities, development cards
        self.hidden_vp: int = 0   # From face-down dev cards
        
        # Development Cards
        self.dev_cards_hand: List[str] = []  # Card IDs in hand
        self.dev_cards_played: Dict[str, int] = {}  # Card ID -> count of played cards
        self.dev_cards_facedown: Dict[str, int] = {}  # Card ID -> count of face-down cards
        
        # Buildings
        self.settlements: List[tuple] = []  # List of (q, r) coordinates
        self.cities: List[tuple] = []       # List of (q, r) coordinates
        self.roads: List[tuple] = []        # List of edge coordinates ((q1,r1), (q2,r2))
        
        # Game state
        self.longest_road_length: int = 0
        self.largest_army_count: int = 0
        self.has_longest_road: bool = False
        self.has_largest_army: bool = False
    
    # ===== RESOURCE MANAGEMENT =====
    
    def add_resource(self, resource: Resource, amount: int) -> bool:
        """Add a resource. Returns True if successful."""
        if amount < 0:
            return False
        self.resources[resource] += amount
        return True
    
    def remove_resource(self, resource: Resource, amount: int) -> bool:
        """Remove a resource. Returns False if insufficient."""
        if amount < 0 or self.resources[resource] < amount:
            return False
        self.resources[resource] -= amount
        return True
    
    def get_resource(self, resource: Resource) -> int:
        """Get amount of a specific resource"""
        return self.resources[resource]
    
    def get_total_resources(self) -> int:
        """Get total number of resource cards"""
        return sum(self.resources.values())
    
    def has_resources(self, required: Dict[Resource, int]) -> bool:
        """Check if player has required resources"""
        for resource, amount in required.items():
            if self.resources[resource] < amount:
                return False
        return True
    
    def pay_resources(self, required: Dict[Resource, int]) -> bool:
        """Remove resources for a cost. Returns False if insufficient."""
        if not self.has_resources(required):
            return False
        
        for resource, amount in required.items():
            self.resources[resource] -= amount
        return True
    
    def print_resources(self):
        """Print resource inventory"""
        print(f"\n{self.name}'s Resources:")
        for resource in Resource:
            print(f"  {resource.value.upper()}: {self.resources[resource]}")
    
    # ===== CHIPS MANAGEMENT =====
    
    def add_chips(self, amount: int) -> bool:
        """Add chips to player"""
        if amount < 0:
            return False
        self.chips += amount
        return True
    
    def remove_chips(self, amount: int) -> bool:
        """Remove chips from player. Returns False if insufficient."""
        if amount < 0 or self.chips < amount:
            return False
        self.chips -= amount
        return True
    
    def get_chips(self) -> int:
        """Get chip count"""
        return self.chips
    
    # ===== VICTORY POINTS =====
    
    def add_visible_vp(self, amount: int) -> bool:
        """Add visible victory points"""
        if amount < 0:
            return False
        self.visible_vp += amount
        return True
    
    def remove_visible_vp(self, amount: int) -> bool:
        """Remove visible victory points"""
        if amount < 0 or self.visible_vp < amount:
            return False
        self.visible_vp -= amount
        return True
    
    def add_hidden_vp(self, amount: int) -> bool:
        """Add hidden VP (from face-down dev cards)"""
        if amount < 0:
            return False
        self.hidden_vp += amount
        return True
    
    def get_visible_vp(self) -> int:
        """Get visible VP"""
        return self.visible_vp
    
    def get_hidden_vp(self) -> int:
        """Get hidden VP"""
        return self.hidden_vp
    
    def get_total_vp(self) -> int:
        """Get total VP (visible + hidden)"""
        return self.visible_vp + self.hidden_vp
    
    # ===== DEVELOPMENT CARDS =====
    
    def add_dev_card(self, card_id: str):
        """Add a development card to hand"""
        self.dev_cards_hand.append(card_id)
    
    def remove_dev_card(self, card_id: str) -> bool:
        """Remove a dev card from hand. Returns False if not found."""
        if card_id in self.dev_cards_hand:
            self.dev_cards_hand.remove(card_id)
            return True
        return False
    
    def play_dev_card(self, card_id: str) -> bool:
        """Play a dev card (move from hand to played). Returns False if not in hand."""
        if not self.remove_dev_card(card_id):
            return False
        
        if card_id not in self.dev_cards_played:
            self.dev_cards_played[card_id] = 0
        self.dev_cards_played[card_id] += 1
        return True
    
    def facedown_dev_card(self, card_id: str) -> bool:
        """Place a dev card face-down (move from hand). Returns False if not in hand."""
        if not self.remove_dev_card(card_id):
            return False
        
        if card_id not in self.dev_cards_facedown:
            self.dev_cards_facedown[card_id] = 0
        self.dev_cards_facedown[card_id] += 1
        return True
    
    def get_dev_cards_in_hand(self) -> int:
        """Get count of dev cards in hand"""
        return len(self.dev_cards_hand)
    
    def get_dev_cards_played(self) -> Dict[str, int]:
        """Get all played dev cards"""
        return self.dev_cards_played.copy()
    
    def get_dev_cards_facedown(self) -> Dict[str, int]:
        """Get all face-down dev cards"""
        return self.dev_cards_facedown.copy()
    
    # ===== BUILDINGS =====
    
    def build_settlement(self, location: tuple) -> bool:
        """Build a settlement. Returns False if already at location."""
        if location in self.settlements or location in self.cities:
            return False
        self.settlements.append(location)
        self.add_visible_vp(1)
        return True
    
    def upgrade_to_city(self, location: tuple) -> bool:
        """Upgrade settlement to city. Returns False if no settlement there."""
        if location not in self.settlements:
            return False
        self.settlements.remove(location)
        self.cities.append(location)
        self.add_visible_vp(1)  # +1 more VP (was 1, now 2)
        return True
    
    def build_road(self, edge: tuple) -> bool:
        """Build a road. Returns False if already at location."""
        if edge in self.roads:
            return False
        self.roads.append(edge)
        return True
    
    def get_settlements(self) -> List[tuple]:
        """Get all settlement locations"""
        return self.settlements.copy()
    
    def get_cities(self) -> List[tuple]:
        """Get all city locations"""
        return self.cities.copy()
    
    def get_roads(self) -> List[tuple]:
        """Get all road locations"""
        return self.roads.copy()
    
    def get_settlement_count(self) -> int:
        """Get number of settlements"""
        return len(self.settlements)
    
    def get_city_count(self) -> int:
        """Get number of cities"""
        return len(self.cities)
    
    def get_road_count(self) -> int:
        """Get number of roads"""
        return len(self.roads)
    
    # ===== SPECIAL ACHIEVEMENTS =====
    
    def set_longest_road(self, has_it: bool, length: int = 0):
        """Set longest road status"""
        self.has_longest_road = has_it
        self.longest_road_length = length
    
    def set_largest_army(self, has_it: bool, count: int = 0):
        """Set largest army status"""
        self.has_largest_army = has_it
        self.largest_army_count = count
    
    # ===== SUMMARY =====
    
    def print_status(self):
        """Print player status"""
        print("\n" + "="*50)
        print(f"Player {self.player_id}: {self.name} ({self.color})")
        print("="*50)
        
        print(f"\nVictory Points: {self.get_total_vp()}")
        print(f"  Visible: {self.visible_vp}, Hidden: {self.hidden_vp}")
        
        print(f"\nResources: {self.get_total_resources()}")
        for resource in Resource:
            print(f"  {resource.value.upper()}: {self.resources[resource]}")
        
        print(f"\nChips: {self.chips}")
        
        print(f"\nBuildings:")
        print(f"  Settlements: {len(self.settlements)}")
        print(f"  Cities: {len(self.cities)}")
        print(f"  Roads: {len(self.roads)}")
        
        print(f"\nDevelopment Cards: {self.get_dev_cards_in_hand()} in hand")
        
        if self.has_longest_road:
            print(f"  Longest Road: YES ({self.longest_road_length} roads)")
        if self.has_largest_army:
            print(f"  Largest Army: YES ({self.largest_army_count} soldiers)")
        
        print("="*50 + "\n")


if __name__ == "__main__":
    print("\nTesting NodKnaKra Player System...\n")
    
    # Create players
    player1 = Player(0, "Alice", "red")
    player2 = Player(1, "Bob", "blue")
    
    print("✓ Created 2 players")
    
    # Give resources
    print("\n1. Give resources:")
    player1.add_resource(Resource.WOOD, 3)
    player1.add_resource(Resource.BRICK, 2)
    player1.add_resource(Resource.WHEAT, 1)
    print("Alice received: 3 wood, 2 brick, 1 wheat")
    
    # Build settlement
    print("\n2. Build settlement:")
    if player1.build_settlement((0, 0)):
        print("✓ Alice built settlement at (0, 0)")
    player1.print_resources()
    
    # Add chips
    print("3. Add chips:")
    player1.add_chips(2)
    print(f"Alice now has {player1.get_chips()} chips")
    
    # Add dev card
    print("\n4. Add development card:")
    player1.add_dev_card("knight")
    print(f"Alice has {player1.get_dev_cards_in_hand()} dev cards")
    
    # Play dev card
    print("\n5. Play development card:")
    if player1.play_dev_card("knight"):
        print("✓ Alice played knight")
    print(f"Alice has {player1.get_dev_cards_in_hand()} in hand")
    
    # Print status
    player1.print_status()
    player2.print_status()
    
    print("✓ Player system working!")
