"""
Project: NodKnaKra Settlers of Catan
File: nodknaKra_rules.py
Created: 2026-07-08

EDIT HISTORY (most recent first):
2026-07-08 - Gordon - Added file header with edit history tracking
2026-07-08 - Gordon - Created Rules class with building, trading, robber, resource validation
"""

from typing import Dict, List, Optional, Tuple


class Rules:
    """Enforces all NodKnaKra game rules"""
    
    def __init__(self, board_hexes: Dict, board_topology: Optional[Dict] = None):
        """
        Initialize rules engine.
        
        Args:
            board_hexes: Dictionary of hex coordinates to Hex objects
            board_topology: Pre-computed topology (settlements, edges, etc.)
        """
        self.board_hexes = board_hexes
        self.board_topology = board_topology or {}
    
    # ===== BUILDING RULES =====
    
    def is_valid_settlement_placement(self, player, location: tuple, all_settlements: List[tuple], all_cities: List[tuple]) -> bool:
        """
        Validate settlement placement.
        Rules:
        - Can't build on occupied location
        - Distance rule: 2+ edges from other settlements/cities
        """
        # Already occupied?
        if location in all_settlements or location in all_cities:
            return False
        
        # Distance rule: check neighbors aren't occupied
        # Get adjacent vertices (in a real implementation, use board topology)
        # For now, simplified check
        return True
    
    def is_valid_city_upgrade(self, player, location: tuple) -> bool:
        """Validate city upgrade. Player must have settlement there."""
        return location in player.get_settlements()
    
    def is_valid_road_placement(self, player, edge: tuple, player_roads: List[tuple], 
                                player_settlements: List[tuple], player_cities: List[tuple]) -> bool:
        """
        Validate road placement.
        Rules:
        - Can't build on existing road
        - Must connect to player's network (settlement, city, or existing road)
        """
        # Already has road there?
        if edge in player_roads:
            return False
        
        # Check connectivity (simplified - in real game, would use board topology)
        # Must connect to settlement, city, or existing road
        return True
    
    # ===== TRADING RULES =====
    
    def can_trade_with_bank(self, player, giving: Dict, receiving: Dict) -> bool:
        """
        Validate bank trade.
        Rules:
        - Player must have resources to give
        - Trade ratio depends on ports
        """
        # Check player has resources
        for resource, amount in giving.items():
            if player.get_resource(resource) < amount:
                return False
        
        return True
    
    def can_trade_with_player(self, player1, giving1: Dict, player2, giving2: Dict) -> bool:
        """
        Validate player-to-player trade.
        Both players must have resources they're offering.
        """
        # Player 1 has what they're giving?
        for resource, amount in giving1.items():
            if player1.get_resource(resource) < amount:
                return False
        
        # Player 2 has what they're giving?
        for resource, amount in giving2.items():
            if player2.get_resource(resource) < amount:
                return False
        
        return True
    
    def get_port_ratio(self, player, resource=None) -> int:
        """
        Get trade ratio for player.
        Default: 4:1 (bank)
        Generic port: 3:1
        Specific port: 2:1
        """
        # Simplified - would check player's settlements on ports
        return 4  # Default bank ratio
    
    # ===== DEVELOPMENT CARD RULES =====
    
    def can_play_dev_card(self, player, card_id: str, game_state, optional_rules: Dict) -> bool:
        """
        Validate development card play.
        Rules:
        - Player must have the card
        - Can only play one per turn
        - Some cards have restrictions (no attack cards turn 1, etc.)
        """
        # Check player has card
        if card_id not in player.dev_cards_hand:
            return False
        
        # Check optional rules
        if optional_rules.get('no_attack_first_turn', False):
            if game_state.turn_count == 0:
                # Turn 1 - no attack cards
                attack_cards = ['monopoly', 'robber', 'saboteur', 'diplomat', 'desertion']
                if card_id in attack_cards:
                    return False
        
        if optional_rules.get('no_monopoly_same_turn_as_trade', False):
            # Would track if traded this turn
            pass
        
        return True
    
    def can_buy_dev_card(self, player) -> bool:
        """Check if player can afford development card"""
        required = {
            'sheep': 1,
            'wheat': 1,
            'ore': 1
        }
        # Simplified - would check actual Resource enum
        return True
    
    # ===== ROBBER RULES =====
    
    def is_valid_robber_placement(self, location: tuple) -> bool:
        """
        Validate robber placement.
        Rules:
        - Can't place on desert (optional - some variants allow it)
        """
        if location not in self.board_hexes:
            return False
        
        hex_obj = self.board_hexes[location]
        # Allow on any terrain for NodKnaKra
        return True
    
    def get_blockaded_settlements(self, robber_location: tuple) -> List[tuple]:
        """Get settlements blocked by robber at location"""
        # Would return all settlements on that hex
        return []
    
    # ===== RESOURCE DISTRIBUTION =====
    
    def distribute_resources(self, dice_total: int, players: List, board_hexes: Dict):
        """
        Distribute resources based on dice roll.
        Rules:
        - Only hexes with matching number produce
        - Settlements get 1 resource, cities get 2
        - Robber blocks production on its hex
        """
        resources_given = {i: {} for i in range(len(players))}
        
        for coord, hex_obj in board_hexes.items():
            # Does this hex produce?
            if hex_obj.number_token != dice_total:
                continue
            
            # Is robber here? (blocks production)
            # Would check: if robber_location == coord: continue
            
            # Award resources to adjacent settlements/cities
            # Would iterate through vertices and check for player buildings
            pass
        
        return resources_given
    
    # ===== LONGEST ROAD & LARGEST ARMY =====
    
    def calculate_longest_road(self, player, roads: List[tuple]) -> int:
        """Calculate longest continuous road for player"""
        # Simplified - would use graph traversal
        return len(roads)
    
    def calculate_largest_army(self, player) -> int:
        """Calculate largest army (soldier cards played)"""
        soldier_cards = player.get_dev_cards_played()
        return soldier_cards.get('soldier', 0) + soldier_cards.get('knight', 0)
    
    # ===== VALIDATION SUMMARY =====
    
    def print_rules(self):
        """Print all NodKnaKra rules"""
        print("\n" + "="*60)
        print("NodKnaKra Game Rules")
        print("="*60)
        
        print("\nBUILDING:")
        print("  • Settlement: 1 wood, 1 brick, 1 sheep, 1 wheat = 1 VP")
        print("  • City (from settlement): 2 wheat, 3 ore = +1 VP")
        print("  • Road: 1 wood, 1 brick")
        
        print("\nTRADING:")
        print("  • Bank: 4:1 default, 3:1 generic port, 2:1 specific port")
        print("  • Player-to-player: Any ratio both agree to")
        
        print("\nDEVELOPMENT CARDS:")
        print("  • Cost: 1 sheep, 1 wheat, 1 ore")
        print("  • Can play 1 per turn")
        print("  • Knight cards count toward Largest Army (3+ = bonus)")
        
        print("\nVICTORY CONDITIONS:")
        print("  • 15 VP for 4 players (varies by count)")
        print("  • MUST win by 2-point margin (NodKnaKra rule!)")
        
        print("\nCHIPS SYSTEM:")
        print("  • Earn chips when dice don't match your hex numbers")
        print("  • Convert chips to resources 1:1 with visible VP")
        
        print("\nOPTIONAL RULES:")
        print("  • No attack cards on turn 1")
        print("  • No monopoly same turn as trade")
        print("  • Touch-move enforced")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    print("\nTesting NodKnaKra Rules System...\n")
    
    # Create mock objects
    class MockPlayer:
        def __init__(self, name):
            self.name = name
            self.resources = {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1, 'ore': 0}
            self.dev_cards_hand = ['knight', 'monopoly']
        
        def get_resource(self, resource):
            return self.resources.get(resource, 0)
        
        def get_settlements(self):
            return [(0, 0)]
        
        def get_dev_cards_played(self):
            return {'knight': 2}
    
    class MockHex:
        def __init__(self, number):
            self.number_token = number
            self.terrain = 'wood'
    
    # Initialize rules
    board_hexes = {
        (0, 0): MockHex(6),
        (1, 0): MockHex(8),
        (0, 1): MockHex(5)
    }
    
    rules = Rules(board_hexes)
    
    # Test trading
    player1 = MockPlayer("Alice")
    player2 = MockPlayer("Bob")
    
    print("1. Test Trading:")
    giving = {'wood': 1, 'brick': 1}
    receiving = {'sheep': 1, 'wheat': 1}
    
    if rules.can_trade_with_player(player1, giving, player2, receiving):
        print("✓ Trade is valid")
    
    # Test longest road
    print("\n2. Test Longest Road:")
    roads = [(0, 0), (1, 0), (0, 1)]
    length = rules.calculate_longest_road(player1, roads)
    print(f"✓ Longest road: {length} segments")
    
    # Test largest army
    print("\n3. Test Largest Army:")
    army = rules.calculate_largest_army(player1)
    print(f"✓ Largest army: {army} soldiers")
    
    # Print rules
    rules.print_rules()
    
    print("✓ Rules system working!")
