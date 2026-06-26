# Game Settings Configuration

## Overview
The game settings system provides complete customization of all game rules, building costs, map configurations, and victory conditions. Settings are stored in JSON files and can be modified through code or the interactive settings editor.

## Configuration Files

### game_settings.json
Location: `config/game_settings.json`

Main configuration file containing:
- **Game Rules**: Victory points, player limits, starting resources
- **Building Costs**: Resource costs for roads, settlements, cities, and development cards
- **Building Limits**: Maximum buildings per player
- **Trading Rules**: Bank ratios, port ratios, player trading settings
- **Dice Rules**: Dice configuration and robber activation
- **Robber Rules**: Robber behavior and restrictions
- **Setup Phase**: Initial placement rules
- **Turn Structure**: What actions can be taken when
- **Variant Rules**: Expansion and house rule toggles
- **Time Limits**: Turn timer and game duration settings

### map_templates.json
Location: `config/map_templates.json`

Contains predefined map layouts:
- **standard_3_4_player**: Classic 19-hex board (3-4 players)
- **extended_5_6_player**: Larger 30-hex board (5-6 players)
- **large_7_8_player**: Extra large 37-hex board (7-8 players)
- **small_2_player**: Compact 13-hex board (2 players)
- **custom_rectangular**: Non-hexagonal layout option

## Using the Settings Editor

### Interactive Editor
Run the settings editor tool:
```bash
python tools/settings_editor.py
```

### Menu Options
1. **View Current Settings** - Display summary of all settings
2. **Change Victory Points** - Modify points needed to win
3. **Change Player Limits** - Set min/max players
4. **Modify Building Costs** - Adjust resource costs
5. **Modify Starting Resources** - Set initial player resources
6. **Change Map Template** - Select different board size
7. **Configure Trading Rules** - Adjust trade ratios
8. **Configure Turn Timer** - Enable/disable time limits
9. **Toggle Variant Rules** - Enable expansions or house rules
10. **View Building Limits** - Show max buildings per player
11. **View Map Details** - Detailed map template information
12. **Validate Settings** - Check for configuration issues
13. **Save Settings** - Save changes to disk
14. **Exit Without Saving** - Discard changes

## Programmatic Usage

### Basic Usage
```python
from shared.game_settings import GameSettings

# Load settings
settings = GameSettings()

# Get victory points needed to win
vp = settings.get_victory_points_to_win()
print(f"Victory points to win: {vp}")

# Get building cost
settlement_cost = settings.get_building_cost('settlement')
print(f"Settlement costs: {settlement_cost}")
# Output: {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1}

# Check if player trading is allowed
can_trade = settings.is_player_trading_allowed()
```

### Modifying Settings
```python
# Change victory points
settings.set_victory_points_to_win(12)

# Change starting resources
settings.set_starting_resources({
    'wood': 2,
    'brick': 1,
    'sheep': 1,
    'wheat': 1,
    'ore': 0
})

# Modify building cost
settings.set_building_cost('road', {'wood': 1, 'brick': 1})

# Save changes
settings.save_settings()
```

### Working with Map Templates
```python
# List all available maps
templates = settings.list_map_templates()
print(templates)
# ['standard_3_4_player', 'extended_5_6_player', ...]

# Get template details
template = settings.get_map_template('extended_5_6_player')
print(f"Hexes: {template['total_hexes']}")
print(f"Players: {template['recommended_players']}")

# Set current map template
settings.set_map_template('large_7_8_player')

# Get current template
current = settings.get_current_map_template()
```

## Key Settings Reference

### Victory Points
Default: 10 points to win

Can be adjusted for:
- Quick games (6-8 points)
- Standard games (10 points)
- Extended games (12-15 points)

### Building Costs (Standard)
```json
{
  "road": {"wood": 1, "brick": 1},
  "settlement": {"wood": 1, "brick": 1, "sheep": 1, "wheat": 1},
  "city": {"wheat": 2, "ore": 3},
  "development_card": {"sheep": 1, "wheat": 1, "ore": 1}
}
```

### Building Limits (Per Player)
- Roads: 15
- Settlements: 5
- Cities: 4

### Trading Ratios
- Bank (no port): 4:1
- Generic port: 3:1
- Resource-specific port: 2:1

### Map Sizes
| Template | Players | Hexes | Rings |
|----------|---------|-------|-------|
| Small | 2 | 13 | 2 |
| Standard | 3-4 | 19 | 2 |
| Extended | 5-6 | 30 | 3 |
| Large | 7-8 | 37 | 4 |

## Custom Game Variants

### Example: Generous Start
Players begin with extra resources:
```python
settings.set_starting_resources({
    'wood': 2,
    'brick': 2,
    'sheep': 2,
    'wheat': 2,
    'ore': 1
})
```

### Example: Quick Game
Lower victory point target:
```python
settings.set_victory_points_to_win(7)
```

### Example: Expensive Cities
Make cities harder to build:
```python
settings.set_building_cost('city', {
    'wheat': 3,
    'ore': 4
})
```

### Example: Cheap Roads
Encourage road building:
```python
settings.set_building_cost('road', {
    'wood': 1,
    'brick': 0
})
```

## Validation

The settings manager includes validation to catch common issues:

```python
issues = settings.validate_settings()
if issues:
    for issue in issues:
        print(f"Warning: {issue}")
```

Checks for:
- Victory points in reasonable range
- Min players ≤ max players
- All buildings have costs defined
- Logical game rules

## Network Integration

Settings can be serialized for network transmission:

```python
# Export settings for network
settings_dict = settings.to_dict()

# Can be sent over network as JSON
import json
settings_json = json.dumps(settings_dict)
```

## Variant Rules

### Standard Expansions
- **Cities & Knights**: Advanced gameplay expansion
- **Seafarers**: Islands and ships expansion

### House Rules
- **Friendly Robber**: Robber can't block players with 2 or fewer points
- **Event Cards**: Use event cards instead of dice rolls

Enable with:
```python
settings.set_variant_rule('use_cities_and_knights_expansion', True)
settings.set_variant_rule('friendly_robber', True)
```

## Turn Structure Configuration

Control what actions are allowed when:

```json
{
  "can_trade_before_roll": false,
  "can_build_before_roll": false,
  "max_dev_cards_per_turn": 1,
  "can_play_dev_card_bought_this_turn": false
}
```

## Setup Phase Configuration

Control initial game setup:

```json
{
  "settlements_to_place": 2,
  "roads_to_place": 2,
  "second_settlement_gives_resources": true,
  "placement_order": "snake"
}
```

Placement order options:
- **"snake"**: 1,2,3,4,4,3,2,1 (standard)
- **"linear"**: 1,2,3,4,1,2,3,4

## Time Limits

Enable competitive timed play:

```python
settings.settings['time_limits']['enable_turn_timer'] = True
settings.settings['time_limits']['seconds_per_turn'] = 90
```

## Best Practices

1. **Test Changes**: Always validate settings after modifications
2. **Document Variants**: Use the notes field to describe custom rules
3. **Balance**: When changing costs, ensure all resources remain useful
4. **Player Count**: Match map size to player count for best gameplay
5. **Victory Points**: Adjust based on map size (larger maps = more points)

## Tips for Custom Games

### Fast-Paced Games
- Lower victory points (6-8)
- Cheaper building costs
- Higher starting resources
- Enable turn timer

### Strategic Games
- Higher victory points (12-15)
- Expensive cities
- Limited starting resources
- Disable player trading (bank only)

### Beginner-Friendly
- Standard victory points (10)
- Generous starting resources
- Allow trading before roll
- Disable turn timer

## Integration with Other Systems

The settings system integrates with:
- **Development Cards**: Card purchase costs
- **Map Generation**: Template selection and resource distribution
- **Network Protocol**: Settings synchronization between players
- **Game Logic**: All rule enforcement

## Troubleshooting

**Settings not saving?**
- Check file permissions in config/ directory
- Ensure valid JSON syntax
- Use settings_editor.py which validates before saving

**Map template not loading?**
- Verify template name matches exactly
- Check map_templates.json for valid structure
- Use `list_map_templates()` to see available options

**Custom rules not working?**
- Game logic must be implemented to use custom settings
- Settings only store configuration, not behavior
- Implement custom effect handlers in game code

## Next Steps

Settings are now configured and ready to integrate with:
1. Board/map generation system
2. Network multiplayer protocol
3. Game state management
4. Player actions and validation
5. UI and rendering system
