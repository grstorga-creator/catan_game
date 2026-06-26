# Development Cards System

## Overview
The development cards system is fully customizable through JSON configuration files. You can define custom cards with various effects, modify existing cards, or use the standard Settlers of Catan card set.

## Configuration File
Location: `config/dev_cards.json`

### Card Definition Structure
```json
{
  "card_types": {
    "card_id": {
      "name": "Display Name",
      "description": "Card description shown to players",
      "count": 5,
      "effect_type": "effect_name",
      "is_victory_point": false,
      "victory_points": 0,
      "play_immediately": false,
      "parameters": {
        "param1": "value1",
        "param2": 123
      }
    }
  }
}
```

### Field Descriptions

- **card_id**: Unique identifier for the card type (e.g., "knight", "custom_trader")
- **name**: The display name shown to players
- **description**: Text describing what the card does
- **count**: How many of this card type are in the deck
- **effect_type**: The type of effect this card has (used by game logic)
- **is_victory_point**: Whether this card gives victory points
- **victory_points**: Number of victory points (if is_victory_point is true)
- **play_immediately**: Whether card must be played as soon as it's drawn
- **parameters**: Custom parameters for the card's effect

## Standard Effect Types

### Built-in Effects
- **knight**: Move the robber and steal from a player
- **victory_point**: Hidden victory point card
- **build_roads**: Place free roads
- **gain_resources**: Gain resources from the bank
- **monopoly**: Take all of one resource type from other players

### Custom Effects
You can create custom effect types and implement their logic in the game code. The parameters dictionary allows you to pass any data needed for your custom effect.

## Using the Card Editor

### Interactive Editor
Run the card editor tool:
```bash
python tools/card_editor.py
```

This provides a menu-driven interface to:
- List all current cards
- Add new cards
- Edit existing cards
- Delete cards
- Save changes

### Example: Adding a Custom Card

1. Run the card editor
2. Select "Add new card"
3. Enter the details:
   ```
   Card ID: custom_gift
   Card Name: Gift
   Card Description: Give 2 resources of your choice to another player
   Count: 3
   Effect Type: custom_gift
   Is victory point?: n
   Play immediately?: n
   
   Parameters:
     Parameter name: resources_to_give
     Value type: int
     Value: 2
     
     Parameter name: player_choice_recipient
     Value type: bool
     Value: true
   ```
4. Save and exit

## Example Custom Cards

### Trading Card
```json
"custom_trader": {
  "name": "Master Trader",
  "description": "Make one 2:1 trade with the bank for any resource",
  "count": 3,
  "effect_type": "custom_trade",
  "is_victory_point": false,
  "play_immediately": false,
  "parameters": {
    "trade_ratio": 2,
    "player_choice": true
  }
}
```

### Bonus Points Card
```json
"custom_bonus": {
  "name": "Great Achievement",
  "description": "2 Victory Points! Keep hidden until needed.",
  "count": 2,
  "effect_type": "victory_point",
  "is_victory_point": true,
  "victory_points": 2,
  "play_immediately": false,
  "parameters": {}
}
```

### Disaster Card
```json
"custom_flood": {
  "name": "Flood",
  "description": "All players with settlements on water tiles lose 1 resource",
  "count": 1,
  "effect_type": "custom_flood",
  "is_victory_point": false,
  "play_immediately": true,
  "parameters": {
    "affects_water_tiles": true,
    "resources_lost": 1
  }
}
```

## Programmatic Usage

### Loading the Deck
```python
from shared.dev_cards import DevelopmentCardDeck

# Load with default config
deck = DevelopmentCardDeck()

# Or specify custom config path
deck = DevelopmentCardDeck('custom_config/my_cards.json')
```

### Drawing Cards
```python
card = deck.draw_card()
if card:
    print(f"Drew: {card.name}")
    print(f"Effect: {card.effect_type}")
    print(f"Parameters: {card.parameters}")
```

### Checking Card Info
```python
# Get info about a card type
knight_info = deck.get_card_info('knight')
print(f"Knights in original deck: {knight_info['count']}")

# Check remaining cards
print(f"Cards left: {deck.cards_remaining()}")

# List all card types
for card_name in deck.list_all_card_types():
    print(card_name)
```

### Discard and Reshuffle
```python
# Add card to discard pile
deck.discard_card(card)

# The deck automatically reshuffles discard pile when empty
# if shuffle_on_empty is true in config
```

## Tips for Custom Cards

1. **Use descriptive card_ids**: Make them easy to reference in code
2. **Keep descriptions clear**: Players need to understand what cards do
3. **Balance card counts**: Too many powerful cards can break gameplay
4. **Test parameters**: Make sure your custom logic can handle the parameters
5. **Document custom effects**: If creating new effect types, document them for other developers

## Deck Settings

In `dev_cards.json`, you can also configure:

```json
"deck_settings": {
  "total_cards": 28,
  "shuffle_on_empty": true,
  "notes": "Custom notes about this deck configuration"
}
```

- **total_cards**: Automatically calculated from card counts
- **shuffle_on_empty**: Whether to reshuffle discard pile when deck is empty
- **notes**: Optional notes about this configuration

## Next Steps

Now that cards are configured, they can be:
- Purchased by players (costs 1 ore, 1 wheat, 1 sheep)
- Drawn randomly from the deck
- Played during a player's turn
- Integrated with the network game protocol

The card effects will be implemented in the game logic layer, which will reference the effect_type and parameters to determine what happens when each card is played.
