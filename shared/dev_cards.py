"""
Development Card System for Settlers of Catan
Loads card definitions from config and manages the card deck.
"""

import json
import random
from typing import Dict, List, Optional
from pathlib import Path


class DevelopmentCard:
    """Represents a single development card."""
    
    def __init__(self, card_type: str, card_data: Dict):
        self.card_type = card_type
        self.name = card_data['name']
        self.description = card_data['description']
        self.effect_type = card_data['effect_type']
        self.is_victory_point = card_data['is_victory_point']
        self.play_immediately = card_data['play_immediately']
        self.parameters = card_data['parameters']
        self.victory_points = card_data.get('victory_points', 0)
        
    def __repr__(self):
        return f"DevelopmentCard({self.name})"
    
    def to_dict(self):
        """Convert card to dictionary for network transmission."""
        return {
            'card_type': self.card_type,
            'name': self.name,
            'description': self.description,
            'effect_type': self.effect_type,
            'is_victory_point': self.is_victory_point,
            'victory_points': self.victory_points,
            'parameters': self.parameters
        }


class DevelopmentCardDeck:
    """Manages the development card deck."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'dev_cards.json'
        
        self.config_path = config_path
        self.card_definitions = {}
        self.deck: List[DevelopmentCard] = []
        self.discard_pile: List[DevelopmentCard] = []
        self.shuffle_on_empty = True
        
        self.load_config()
        self.initialize_deck()
    
    def load_config(self):
        """Load card definitions from JSON config file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            self.card_definitions = config['card_types']
            self.shuffle_on_empty = config['deck_settings'].get('shuffle_on_empty', True)
            
            print(f"Loaded {len(self.card_definitions)} card types from config")
            
        except FileNotFoundError:
            print(f"Error: Config file not found at {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            raise
    
    def initialize_deck(self):
        """Create the deck based on card definitions."""
        self.deck = []
        
        for card_type, card_data in self.card_definitions.items():
            count = card_data.get('count', 0)
            for _ in range(count):
                card = DevelopmentCard(card_type, card_data)
                self.deck.append(card)
        
        self.shuffle()
        print(f"Initialized deck with {len(self.deck)} cards")
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.deck)
    
    def draw_card(self) -> Optional[DevelopmentCard]:
        """Draw a card from the deck."""
        if not self.deck:
            if self.shuffle_on_empty and self.discard_pile:
                print("Deck empty. Shuffling discard pile back into deck.")
                self.deck = self.discard_pile
                self.discard_pile = []
                self.shuffle()
            else:
                print("No cards left to draw.")
                return None
        
        return self.deck.pop()
    
    def discard_card(self, card: DevelopmentCard):
        """Add a card to the discard pile."""
        self.discard_pile.append(card)
    
    def cards_remaining(self) -> int:
        """Return number of cards left in deck."""
        return len(self.deck)
    
    def get_card_info(self, card_type: str) -> Optional[Dict]:
        """Get information about a specific card type."""
        return self.card_definitions.get(card_type)
    
    def list_all_card_types(self) -> List[str]:
        """Return list of all card type names."""
        return [data['name'] for data in self.card_definitions.values()]
    
    def reset_deck(self):
        """Reset the deck to initial state."""
        self.discard_pile = []
        self.initialize_deck()


# Example usage and testing
if __name__ == "__main__":
    print("=== Development Card System Test ===\n")
    
    # Initialize the deck
    deck = DevelopmentCardDeck()
    
    # Show all available card types
    print("\nAvailable card types:")
    for card_name in deck.list_all_card_types():
        print(f"  - {card_name}")
    
    # Draw some cards
    print(f"\n--- Drawing 5 cards ---")
    print(f"Cards in deck: {deck.cards_remaining()}")
    
    drawn_cards = []
    for i in range(5):
        card = deck.draw_card()
        if card:
            drawn_cards.append(card)
            print(f"{i+1}. {card.name}: {card.description}")
    
    print(f"\nCards remaining in deck: {deck.cards_remaining()}")
    
    # Test card information
    print("\n--- Knight Card Details ---")
    knight_info = deck.get_card_info('knight')
    if knight_info:
        print(f"Name: {knight_info['name']}")
        print(f"Count in deck: {knight_info['count']}")
        print(f"Effect type: {knight_info['effect_type']}")
        print(f"Parameters: {knight_info['parameters']}")
    
    # Test discarding and reshuffling
    print("\n--- Testing discard pile ---")
    for card in drawn_cards:
        deck.discard_card(card)
    print(f"Cards in discard pile: {len(deck.discard_pile)}")
    
    # Draw all remaining cards to trigger reshuffle
    print("\n--- Drawing all cards to test reshuffle ---")
    cards_drawn = 0
    while deck.cards_remaining() > 0:
        card = deck.draw_card()
        if card:
            cards_drawn += 1
    
    print(f"Drew {cards_drawn} cards until deck was empty")
    
    # This should trigger reshuffle from discard pile
    next_card = deck.draw_card()
    if next_card:
        print(f"After reshuffle, drew: {next_card.name}")
        print(f"Cards now in deck: {deck.cards_remaining()}")
