"""
NodKnaKra Development Cards System
Handles all 74 custom development cards with cancellation mechanics.
"""

import json
import random
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
import os


class CardType(Enum):
    """Card type categories"""
    ALCHEMY = "alchemy"
    VICTORY_POINT = "victory_point"
    SOLDIER = "soldier"
    BUILDING = "building"
    RESOURCE = "resource"
    ATTACK = "attack"
    DEFENSE = "defense"
    DISASTER = "disaster"
    SPECIAL = "special"
    PRODUCTION = "production"
    ROBBER = "robber"


@dataclass
class Card:
    """Represents a single development card"""
    
    id: str
    name: str
    card_type: CardType
    description: str
    victory_points: int
    can_cancel: List[str]  # Card IDs this can cancel
    keep_card: bool  # True if card stays after play
    playable_after_reveal: bool
    counts_toward_largest_army: bool = False
    affects_all_players: bool = False
    delayed_effect: bool = False
    discard_after_use: bool = False
    cost_to_play: Optional[Dict[str, int]] = None
    
    def __repr__(self):
        return f"{self.name} ({self.card_type.value})"
    
    def to_dict(self) -> dict:
        """Convert card to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.card_type.value,
            'description': self.description,
            'victory_points': self.victory_points,
            'can_cancel': self.can_cancel,
            'keep_card': self.keep_card,
            'playable_after_reveal': self.playable_after_reveal,
            'counts_toward_largest_army': self.counts_toward_largest_army,
            'affects_all_players': self.affects_all_players,
            'delayed_effect': self.delayed_effect,
            'discard_after_use': self.discard_after_use,
            'cost_to_play': self.cost_to_play
        }
    
    def can_be_cancelled_by(self, other_card_id: str) -> bool:
        """Check if this card can be cancelled by another card"""
        return other_card_id in self.can_cancel
    
    def is_soldier_type(self) -> bool:
        """Check if this is a soldier-type card"""
        soldier_ids = ['knight', 'soldier', 'chip_soldier', 'card_robber']
        return self.id in soldier_ids


class CardDeck:
    """Manages the NodKnaKra development card deck"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the card deck from JSON config"""
        self.cards: Dict[str, Card] = {}  # card_id -> Card
        self.deck_pile: List[Card] = []   # Draw pile
        self.discard_pile: List[Card] = [] # Discard pile
        self.card_counts: Dict[str, int] = {}  # Track count of each card type
        
        if config_path is None:
            # Try to find config in standard location
            config_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'config',
                'nodknaKra_cards.json'
            )
        
        self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load card configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            for card_data in config['cards']:
                # Create Card object from JSON data
                card = Card(
                    id=card_data['id'],
                    name=card_data['name'],
                    card_type=CardType(card_data['type']),
                    description=card_data['description'],
                    victory_points=card_data.get('victory_points', 0),
                    can_cancel=card_data.get('can_cancel', []),
                    keep_card=card_data.get('keep_card', False),
                    playable_after_reveal=card_data.get('playable_after_reveal', True),
                    counts_toward_largest_army=card_data.get('counts_toward_largest_army', False),
                    affects_all_players=card_data.get('affects_all_players', False),
                    delayed_effect=card_data.get('delayed_effect', False),
                    discard_after_use=card_data.get('discard_after_use', False),
                    cost_to_play=card_data.get('cost_to_play')
                )
                
                self.cards[card.id] = card
                
                # Add to deck pile (count times)
                count = card_data.get('count', 1)
                self.card_counts[card.id] = count
                for _ in range(count):
                    self.deck_pile.append(card)
            
            print(f"✓ Loaded {len(self.cards)} card types ({len(self.deck_pile)} total cards)")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Card config not found at: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in card config: {config_path}")
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.deck_pile)
    
    def draw(self) -> Optional[Card]:
        """Draw a card from the deck"""
        if not self.deck_pile:
            # Reshuffle discard pile if deck is empty
            if self.discard_pile:
                self.deck_pile = self.discard_pile.copy()
                self.discard_pile = []
                self.shuffle()
            else:
                return None  # No cards available
        
        return self.deck_pile.pop(0)
    
    def discard(self, card: Card):
        """Discard a card to the discard pile"""
        self.discard_pile.append(card)
    
    def draw_multiple(self, count: int) -> List[Card]:
        """Draw multiple cards"""
        cards = []
        for _ in range(count):
            card = self.draw()
            if card:
                cards.append(card)
        return cards
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """Get a card template by ID"""
        return self.cards.get(card_id)
    
    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        """Get all unique cards of a specific type"""
        return [card for card in self.cards.values() if card.card_type == card_type]
    
    def get_soldier_cards(self) -> List[Card]:
        """Get all soldier-type cards"""
        return [card for card in self.cards.values() if card.is_soldier_type()]
    
    def deck_size(self) -> int:
        """Get number of cards in draw pile"""
        return len(self.deck_pile)
    
    def discard_size(self) -> int:
        """Get number of cards in discard pile"""
        return len(self.discard_pile)
    
    def total_cards(self) -> int:
        """Get total card count"""
        return self.deck_size() + self.discard_size()
    
    def print_summary(self):
        """Print a summary of all cards"""
        print("\n" + "="*60)
        print("NodKnaKra Development Card Deck Summary")
        print("="*60)
        print(f"Total unique card types: {len(self.cards)}")
        print(f"Total cards in deck: {len(self.deck_pile)}")
        print(f"Cards in discard: {len(self.discard_pile)}\n")
        
        # Group by type
        by_type = {}
        for card in self.cards.values():
            card_type = card.card_type.value
            if card_type not in by_type:
                by_type[card_type] = []
            by_type[card_type].append(card)
        
        for card_type in sorted(by_type.keys()):
            cards = by_type[card_type]
            print(f"{card_type.upper()} ({len(cards)} types):")
            for card in cards:
                count = self.card_counts.get(card.id, 1)
                vp = f" ({card.victory_points} VP)" if card.victory_points > 0 else ""
                print(f"  • {card.name} x{count}{vp}")
            print()
        
        print("="*60 + "\n")


# Test/Demo functionality
if __name__ == "__main__":
    print("\nTesting NodKnaKra Card System...\n")
    
    try:
        # Create deck
        deck = CardDeck()
        
        # Print summary
        deck.print_summary()
        
        # Test drawing
        print("Drawing 5 cards:")
        for i in range(5):
            card = deck.draw()
            if card:
                print(f"  {i+1}. {card.name}")
        
        print(f"\nDeck size: {deck.deck_size()}")
        print(f"Cards left to draw: {deck.total_cards()}\n")
        
        # Test card lookup
        print("Soldier cards available:")
        soldiers = deck.get_soldier_cards()
        for soldier in soldiers:
            print(f"  • {soldier.name}")
        
        print("\n✓ Card system working!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
