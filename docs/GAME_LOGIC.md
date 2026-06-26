# Game Logic System

## Overview
The game logic system implements the core Settlers of Catan gameplay mechanics including player management, resource handling, turn structure, building placement, trading, and victory conditions.

## Components

### 1. Player Management (`shared/player.py`)

#### Player Class
Manages individual player state, resources, buildings, and scoring.

**Key Features:**
- Resource management (wood, brick, sheep, wheat, ore)
- Building inventory (settlements, cities, roads)
- Development card hand
- Victory point calculation
- Trading with bank
- Special achievements (longest road, largest army)

**Player Attributes:**
```python
player.resources = {
    'wood': 0,
    'brick': 0,
    'sheep': 0,
    'wheat': 0,
    'ore': 0
}

player.settlements_remaining = 5  # Max to place
player.cities_remaining = 4
player.roads_remaining = 15

player.settlements = []  # Placed positions
player.cities = []
player.roads = []

player.development_cards = []
player.knights_played = 0
player.has_longest_road = False
player.has_largest_army = False
player.victory_points = 0
```

**Resource Management:**
```python
# Add resources
player.add_resource('wood', 3)
player.add_resource('brick', 2)

# Check if player has resources
cost = {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1}
if player.has_resources(cost):
    # Pay for something
    player.pay_resources(cost)

# Get total cards
total = player.get_total_resource_count()
```

**Building:**
```python
# Check if can build
if player.can_build_settlement():
    # Build at position
    player.build_settlement(position)

# Upgrade settlement to city
if player.can_build_city():
    player.build_city(settlement_position)

# Build road
player.build_road(edge_position)
```

**Victory Points:**
```python
# Calculate victory points
vp = player.calculate_victory_points()

# Points come from:
# - Settlements: 1 point each
# - Cities: 2 points each
# - VP development cards: 1 point each
# - Longest Road: 2 points
# - Largest Army: 2 points
```

**Trading:**
```python
# Trade with bank (default 4:1 ratio)
player.trade_with_bank('wood', 4, 'ore')  # 4 wood for 1 ore

# Improved trade with port (2:1 or 3:1)
player.set_trade_ratio('wood', 2)  # Got a wood port
player.trade_with_bank('wood', 2, 'brick')  # 2 wood for 1 brick

# Check custom trade ratios
ratio = player.trade_ratios['wood']  # Default 4, or 3 with generic port, 2 with specific port
```

### 2. Game State Manager (`shared/game_state.py`)

#### GameState Class
Manages the complete game including all players, board state, turn order, and game phases.

**Game Phases:**
```python
class GamePhase(Enum):
    SETUP = "setup"           # Initial placement
    MAIN_GAME = "main_game"   # Normal gameplay
    GAME_OVER = "game_over"   # Someone won
```

**Turn Phases:**
```python
class TurnPhase(Enum):
    ROLL_DICE = "roll_dice"          # Roll for resources
    DISCARD = "discard"              # If 7 rolled with 7+ cards
    MOVE_ROBBER = "move_robber"      # If 7 rolled
    MAIN_PHASE = "main_phase"        # Trade, build, play cards
    END_TURN = "end_turn"            # Cleanup
```

**Setting Up a Game:**
```python
from shared.game_state import GameState
from shared.game_settings import GameSettings

# Create game
settings = GameSettings()
game = GameState(settings)

# Setup with players
player_names = ["Alice", "Bob", "Charlie", "Diana"]
game.setup_game(player_names, map_template='standard_3_4_player')

# Game is now ready to play
```

**Turn Structure:**
```python
# 1. Roll dice
die1, die2 = game.roll_dice()
total = die1 + die2

# 2. If rolled 7, handle robber
if total == 7:
    # Players with 7+ cards discard half
    players_to_discard = game.check_discard_phase(7)
    for player in players_to_discard:
        discarded = player.discard_half_resources()
    
    # Current player moves robber
    game.move_robber(new_hex_position)
    
    # Optionally steal from adjacent player
    game.steal_resource(target_player)
else:
    # Distribute resources based on dice roll
    game.distribute_resources(total)

# 3. Main phase - player can:
#    - Trade with bank
#    - Trade with other players
#    - Build settlements, cities, roads
#    - Buy development cards
#    - Play development cards

# 4. Check for victory
winner = game.check_victory_condition()
if winner:
    print(f"{winner.name} wins!")

# 5. End turn
game.next_player()
```

**Dice Rolling:**
```python
# Roll 2d6
die1, die2 = game.roll_dice()
total = die1 + die2

# Access last roll
last_roll = game.last_dice_roll  # (die1, die2)
```

**Resource Distribution:**
```python
# Automatically distributes resources to players with buildings
# adjacent to hexes with the rolled number
game.distribute_resources(dice_total)

# If 7 is rolled, no resources are distributed
```

**Robber Mechanics:**
```python
# Move robber to new hex
game.move_robber(new_hex_coordinate)

# Check if can steal from a player
if game.can_steal_from(target_player):
    stolen_resource = game.steal_resource(target_player)
    print(f"Stole {stolen_resource}!")

# Robber blocks resource production on that hex
```

**Development Cards:**
```python
# Buy a development card
if game.buy_development_card(player):
    print("Bought dev card!")
    print(f"Cards remaining: {game.dev_card_deck.cards_remaining()}")

# Play a development card
if player.play_dev_card(card):
    # Handle card effect
    if card.effect_type == 'knight':
        # Move robber, update largest army
        game.check_largest_army()
```

**Trading:**
```python
# Trade with bank
game.trade_with_bank(player, 'wood', 4, 'ore')

# Trade between players
give_resources = {'wood': 2, 'brick': 1}
receive_resources = {'sheep': 2, 'wheat': 1}
game.trade_with_player(player1, give_resources, player2, receive_resources)
```

**Special Achievements:**
```python
# Check longest road
game.check_longest_road()
if player.has_longest_road:
    print(f"{player.name} has longest road!")

# Check largest army
game.check_largest_army()
if player.has_largest_army:
    print(f"{player.name} has largest army!")
```

**Victory Checking:**
```python
# Check if anyone won
winner = game.check_victory_condition()
if winner:
    print(f"{winner.name} wins with {winner.victory_points} VP!")
    print(f"Game Phase: {game.game_phase}")  # GAME_OVER
```

**Game Information:**
```python
# Get current player
current = game.get_current_player()

# Get game summary
summary = game.get_game_summary()
print(f"Turn: {summary['turn_number']}")
print(f"Current player: {summary['current_player']}")
for p in summary['players']:
    print(f"{p['name']}: {p['victory_points']} VP")

# Access game log
for event in game.game_log[-10:]:
    print(event)
```

## Building Costs

From `game_settings.json`:

```json
{
  "road": {"wood": 1, "brick": 1},
  "settlement": {"wood": 1, "brick": 1, "sheep": 1, "wheat": 1},
  "city": {"wheat": 2, "ore": 3},
  "development_card": {"sheep": 1, "wheat": 1, "ore": 1}
}
```

Access in code:
```python
cost = game.settings.get_building_cost('settlement')
if player.has_resources(cost):
    player.pay_resources(cost)
```

## Trading Rules

### Bank Trading
- **Default ratio**: 4:1 (trade 4 of same resource for 1 of any other)
- **Generic port**: 3:1 (trade 3 of same resource for 1 of any other)
- **Specific port**: 2:1 (trade 2 of specific resource for 1 of any other)

```python
# Check player's trade ratios
print(player.trade_ratios)
# {'wood': 4, 'brick': 4, 'sheep': 4, 'wheat': 4, 'ore': 4}

# Player gets a wood port
player.set_trade_ratio('wood', 2)

# Now can trade 2 wood for anything
player.trade_with_bank('wood', 2, 'ore')
```

### Player Trading
- Free-form trading between players
- No restrictions on ratios
- Both players must agree

```python
# Alice offers 2 wood + 1 brick for Bob's 3 sheep
alice_gives = {'wood': 2, 'brick': 1}
bob_gives = {'sheep': 3}
game.trade_with_player(alice, alice_gives, bob, bob_gives)
```

## Victory Conditions

### Points Sources
1. **Settlements**: 1 VP each (max 5)
2. **Cities**: 2 VP each (max 4) = 8 VP
3. **Longest Road**: 2 VP (need 5+ connected roads)
4. **Largest Army**: 2 VP (need 3+ knights played)
5. **VP Development Cards**: 1 VP each (5 in standard deck)

**Maximum possible**: 5 + 8 + 2 + 2 + 5 = 22 VP

### Winning
Default: First to **10 VP** wins
Configurable via settings:
```python
settings.set_victory_points_to_win(12)  # Longer game
```

## Game Flow Example

### Complete Turn Example
```python
# Setup
game = GameState()
game.setup_game(["Alice", "Bob", "Charlie"])

# Turn 1: Alice's turn
print(f"Turn {game.turn_number}: {game.get_current_player().name}")

# Roll dice
die1, die2 = game.roll_dice()
total = die1 + die2

if total == 7:
    # Robber!
    # 1. Players discard
    for player in game.check_discard_phase(7):
        player.discard_half_resources()
    
    # 2. Move robber
    game.move_robber(new_position)
    
    # 3. Optionally steal
    if game.can_steal_from(target):
        game.steal_resource(target)
else:
    # Normal resource production
    game.distribute_resources(total)

# Main phase
current = game.get_current_player()

# Trade with bank
if current.has_resources({'wood': 4}):
    game.trade_with_bank(current, 'wood', 4, 'brick')

# Build something
settlement_cost = game.settings.get_building_cost('settlement')
if current.has_resources(settlement_cost):
    current.pay_resources(settlement_cost)
    current.build_settlement(position)

# Buy dev card
if current.has_resources({'sheep': 1, 'wheat': 1, 'ore': 1}):
    game.buy_development_card(current)

# Check for winner
winner = game.check_victory_condition()
if winner:
    print(f"{winner.name} wins!")
else:
    # Next turn
    game.next_player()
```

## Integration with Other Systems

### With Settings
```python
# Game uses settings for:
victory_points = settings.get_victory_points_to_win()
building_costs = settings.get_all_building_costs()
max_cards = settings.get_max_cards_before_discard()
```

### With Map Generator
```python
# Game generates board
game.grid = game.map_generator.generate_map('standard_3_4_player')

# Access tiles
tile = game.grid.get_tile(coordinate)
```

### With Dev Cards
```python
# Game manages dev card deck
card = game.dev_card_deck.draw_card()
player.add_dev_card(card)
```

### With Renderer (Future)
```python
# Renderer will show:
# - Player colors
# - Building placements
# - Resource cards
# - Current player indicator
# - Victory points
```

## Serialization

### Save Game State
```python
# Export to dictionary
state_dict = game.to_dict()

# Save to file
import json
with open('savegame.json', 'w') as f:
    json.dump(state_dict, f)
```

### Load Game State
```python
# Load from file
with open('savegame.json', 'r') as f:
    state_dict = json.load(f)

# Restore game
# (Full restoration not yet implemented - coming soon)
```

## Current Limitations

### Not Yet Implemented
1. **Vertex/Edge System**: Building placement validation needs board topology
2. **Resource Distribution**: Needs to know which buildings are adjacent to which hexes
3. **Longest Road Calculation**: Needs graph traversal of road network
4. **Setup Phase**: Initial placement order (1-2-3-4-4-3-2-1 pattern)
5. **Maritime Trade UI**: Visual port selection
6. **Development Card Effects**: Full implementation of all card types

### Coming Soon
These features will be added when we implement building placement:
- Valid settlement positions (vertices)
- Valid road positions (edges)
- Road connectivity checking
- Settlement spacing rules (distance rule)
- Harbor adjacency detection
- Longest road graph traversal

## Testing

```bash
# Test player system
python shared/player.py

# Test game state
python shared/game_state.py
```

## Usage Examples

### Simple Game Loop
```python
from shared.game_state import GameState

game = GameState()
game.setup_game(["Alice", "Bob", "Charlie", "Diana"])

while game.game_phase != GamePhase.GAME_OVER:
    player = game.get_current_player()
    print(f"\n{player.name}'s turn")
    
    # Roll
    d1, d2 = game.roll_dice()
    total = d1 + d2
    
    # Handle 7
    if total == 7:
        # Discard, move robber, steal
        pass
    else:
        game.distribute_resources(total)
    
    # Main phase (simplified)
    # ... player actions ...
    
    # Check win
    winner = game.check_victory_condition()
    if winner:
        break
    
    game.next_player()
```

### Custom Victory Points
```python
settings = GameSettings()
settings.set_victory_points_to_win(15)  # Longer game

game = GameState(settings)
```

### Track Statistics
```python
# After each turn
summary = game.get_game_summary()

for p_info in summary['players']:
    print(f"{p_info['name']}: {p_info['victory_points']} VP, "
          f"{p_info['resources']} resources")
```

## Next Steps

To complete the game logic, we need to add:
1. **Vertex/Edge System**: Board topology for building placement
2. **Placement Validation**: Rules for where buildings can go
3. **Setup Phase**: Initial settlement/road placement
4. **Full Resource Distribution**: Connect buildings to hexes
5. **Development Card Effects**: Implement all card abilities
6. **AI Players** (optional): Computer opponents

The core game logic is now in place and ready to be connected to the visual renderer and building placement system!
