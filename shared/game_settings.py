"""
Game Settings Manager for Settlers of Catan
Handles loading and managing game configuration including rules, costs, and map settings.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class GameSettings:
    """Manages game settings and configuration."""
    
    def __init__(self, settings_path: str = None, map_templates_path: str = None):
        if settings_path is None:
            settings_path = Path(__file__).parent.parent / 'config' / 'game_settings.json'
        if map_templates_path is None:
            map_templates_path = Path(__file__).parent.parent / 'config' / 'map_templates.json'
        
        self.settings_path = settings_path
        self.map_templates_path = map_templates_path
        
        self.settings = {}
        self.map_templates = {}
        self.current_map_template = None
        
        self.load_settings()
        self.load_map_templates()
    
    def load_settings(self):
        """Load game settings from JSON file."""
        try:
            with open(self.settings_path, 'r') as f:
                self.settings = json.load(f)
            print(f"✓ Loaded game settings from {self.settings_path}")
        except FileNotFoundError:
            print(f"Error: Settings file not found at {self.settings_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in settings file: {e}")
            raise
    
    def load_map_templates(self):
        """Load map templates from JSON file."""
        try:
            with open(self.map_templates_path, 'r') as f:
                data = json.load(f)
                self.map_templates = data['map_templates']
            print(f"✓ Loaded {len(self.map_templates)} map templates")
        except FileNotFoundError:
            print(f"Error: Map templates file not found at {self.map_templates_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in map templates file: {e}")
            raise
    
    def save_settings(self):
        """Save current settings back to file."""
        with open(self.settings_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
        print(f"✓ Settings saved to {self.settings_path}")
    
    # Game Rules Getters
    def get_victory_points_to_win(self) -> int:
        """Get the number of victory points needed to win."""
        return self.settings['game_rules']['victory_points_to_win']
    
    def set_victory_points_to_win(self, points: int):
        """Set the number of victory points needed to win."""
        if points < 1:
            raise ValueError("Victory points must be at least 1")
        self.settings['game_rules']['victory_points_to_win'] = points
    
    def get_max_players(self) -> int:
        """Get maximum number of players."""
        return self.settings['game_rules']['max_players']
    
    def get_min_players(self) -> int:
        """Get minimum number of players."""
        return self.settings['game_rules']['min_players']
    
    def get_starting_resources(self) -> Dict[str, int]:
        """Get starting resources for each player."""
        return self.settings['game_rules']['starting_resources'].copy()
    
    def set_starting_resources(self, resources: Dict[str, int]):
        """Set starting resources for each player."""
        self.settings['game_rules']['starting_resources'] = resources
    
    # Building Costs
    def get_building_cost(self, building_type: str) -> Dict[str, int]:
        """Get the resource cost for a building type."""
        return self.settings['building_costs'].get(building_type, {}).copy()
    
    def set_building_cost(self, building_type: str, cost: Dict[str, int]):
        """Set the resource cost for a building type."""
        self.settings['building_costs'][building_type] = cost
    
    def get_all_building_costs(self) -> Dict[str, Dict[str, int]]:
        """Get all building costs."""
        return self.settings['building_costs'].copy()
    
    # Building Limits
    def get_building_limit(self, building_type: str) -> int:
        """Get the maximum number of a building type per player."""
        limit_key = f"{building_type}_per_player"
        return self.settings['building_limits'].get(limit_key, 0)
    
    # Trading Rules
    def get_default_trade_ratio(self) -> int:
        """Get the default trade ratio with the bank (4:1 standard)."""
        return self.settings['trading_rules']['default_trade_ratio']
    
    def get_port_trade_ratio(self, port_type: str) -> int:
        """Get the trade ratio for a specific port type."""
        return self.settings['trading_rules']['port_trade_ratios'].get(port_type, 4)
    
    def is_player_trading_allowed(self) -> bool:
        """Check if player-to-player trading is allowed."""
        return self.settings['trading_rules']['allow_player_trading']
    
    # Dice Rules
    def get_dice_config(self) -> Dict[str, int]:
        """Get dice configuration."""
        return self.settings['dice_rules'].copy()
    
    def get_robber_activation_number(self) -> int:
        """Get the dice roll that activates the robber."""
        return self.settings['dice_rules']['robber_activation_number']
    
    def get_max_cards_before_discard(self) -> int:
        """Get max cards a player can hold when robber is rolled."""
        return self.settings['dice_rules']['max_cards_before_discard']
    
    # Robber Rules
    def get_robber_rules(self) -> Dict[str, Any]:
        """Get all robber rules."""
        return self.settings['robber_rules'].copy()
    
    # Setup Phase
    def get_setup_phase_config(self) -> Dict[str, Any]:
        """Get setup phase configuration."""
        return self.settings['setup_phase'].copy()
    
    # Turn Structure
    def get_turn_structure(self) -> Dict[str, Any]:
        """Get turn structure rules."""
        return self.settings['turn_structure'].copy()
    
    def can_play_dev_card_bought_this_turn(self) -> bool:
        """Check if dev cards can be played the same turn they're bought."""
        return self.settings['turn_structure']['can_play_dev_card_bought_this_turn']
    
    # Map Templates
    def get_map_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific map template by name."""
        return self.map_templates.get(template_name)
    
    def list_map_templates(self) -> List[str]:
        """List all available map template names."""
        return list(self.map_templates.keys())
    
    def set_map_template(self, template_name: str) -> bool:
        """Set the current map template."""
        if template_name in self.map_templates:
            self.current_map_template = template_name
            # Update map settings in main settings
            template = self.map_templates[template_name]
            self.settings['map_settings']['map_size'] = template_name
            self.settings['map_settings']['hex_distribution'] = template['hex_distribution']
            self.settings['map_settings']['number_token_distribution'] = template['number_tokens']
            self.settings['map_settings']['ports'] = template['ports']
            print(f"✓ Map template set to: {template['name']}")
            return True
        else:
            print(f"Error: Map template '{template_name}' not found")
            return False
    
    def get_current_map_template(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected map template."""
        if self.current_map_template:
            return self.map_templates[self.current_map_template]
        return None
    
    # Variant Rules
    def get_variant_rules(self) -> Dict[str, Any]:
        """Get variant/expansion rules."""
        return self.settings['variant_rules'].copy()
    
    def set_variant_rule(self, rule_name: str, enabled: bool):
        """Enable or disable a variant rule."""
        if rule_name in self.settings['variant_rules']:
            self.settings['variant_rules'][rule_name] = enabled
    
    # Time Limits
    def get_time_limits(self) -> Dict[str, Any]:
        """Get time limit configuration."""
        return self.settings['time_limits'].copy()
    
    def is_turn_timer_enabled(self) -> bool:
        """Check if turn timer is enabled."""
        return self.settings['time_limits']['enable_turn_timer']
    
    # Utility Methods
    def validate_settings(self) -> List[str]:
        """Validate current settings and return list of any issues."""
        issues = []
        
        # Check victory points
        vp = self.get_victory_points_to_win()
        if vp < 3:
            issues.append(f"Victory points ({vp}) seems too low")
        if vp > 20:
            issues.append(f"Victory points ({vp}) seems very high")
        
        # Check player counts
        if self.get_min_players() > self.get_max_players():
            issues.append("Min players is greater than max players")
        
        # Check building costs
        for building, cost in self.get_all_building_costs().items():
            if not cost:
                issues.append(f"Building '{building}' has no resource cost")
        
        return issues
    
    def get_summary(self) -> str:
        """Get a human-readable summary of current settings."""
        summary = []
        summary.append("=== Game Settings Summary ===")
        summary.append(f"Victory Points to Win: {self.get_victory_points_to_win()}")
        summary.append(f"Players: {self.get_min_players()}-{self.get_max_players()}")
        summary.append(f"Map: {self.settings['map_settings']['map_size']}")
        summary.append(f"Player Trading: {'Enabled' if self.is_player_trading_allowed() else 'Disabled'}")
        summary.append(f"Turn Timer: {'Enabled' if self.is_turn_timer_enabled() else 'Disabled'}")
        
        if self.current_map_template:
            template = self.get_current_map_template()
            summary.append(f"\nCurrent Map Template: {template['name']}")
            summary.append(f"  Recommended Players: {template['recommended_players']}")
            summary.append(f"  Total Hexes: {template['total_hexes']}")
        
        return '\n'.join(summary)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all settings as a dictionary for network transmission."""
        return {
            'settings': self.settings,
            'current_map_template': self.current_map_template
        }


# Example usage and testing
if __name__ == "__main__":
    print("=== Game Settings Manager Test ===\n")
    
    # Initialize settings
    settings = GameSettings()
    
    # Display summary
    print(settings.get_summary())
    
    # Test various getters
    print("\n--- Building Costs ---")
    for building in ['road', 'settlement', 'city', 'development_card']:
        cost = settings.get_building_cost(building)
        cost_str = ', '.join([f"{v} {k}" for k, v in cost.items()])
        print(f"{building.capitalize()}: {cost_str}")
    
    # Test building limits
    print("\n--- Building Limits Per Player ---")
    for building_type in ['roads', 'settlements', 'cities']:
        limit = settings.get_building_limit(building_type)
        print(f"{building_type.capitalize()}: {limit}")
    
    # Test map templates
    print("\n--- Available Map Templates ---")
    for template_name in settings.list_map_templates():
        template = settings.get_map_template(template_name)
        print(f"  {template['name']}")
        print(f"    Players: {template['recommended_players']}")
        print(f"    Hexes: {template['total_hexes']}")
    
    # Test changing settings
    print("\n--- Testing Setting Modifications ---")
    print(f"Current VP to win: {settings.get_victory_points_to_win()}")
    settings.set_victory_points_to_win(12)
    print(f"New VP to win: {settings.get_victory_points_to_win()}")
    
    # Test map template selection
    print("\n--- Testing Map Template Selection ---")
    settings.set_map_template('extended_5_6_player')
    current = settings.get_current_map_template()
    if current:
        print(f"Selected: {current['name']}")
        print(f"Total hexes: {current['total_hexes']}")
    
    # Validate settings
    print("\n--- Settings Validation ---")
    issues = settings.validate_settings()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All settings valid!")
    
    # Test dice configuration
    print("\n--- Dice Configuration ---")
    dice_config = settings.get_dice_config()
    print(f"Dice count: {dice_config['dice_count']}")
    print(f"Dice sides: {dice_config['dice_sides']}")
    print(f"Robber activates on: {settings.get_robber_activation_number()}")
    print(f"Max cards before discard: {settings.get_max_cards_before_discard()}")
