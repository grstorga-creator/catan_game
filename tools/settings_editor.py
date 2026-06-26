"""
Game Settings Editor - Interactive CLI tool for modifying game settings
"""

import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.game_settings import GameSettings


class SettingsEditor:
    """Interactive editor for game settings."""
    
    def __init__(self):
        self.settings = GameSettings()
    
    def main_menu(self):
        """Display main menu."""
        while True:
            print("\n" + "="*60)
            print("GAME SETTINGS EDITOR")
            print("="*60)
            print("1.  View Current Settings")
            print("2.  Change Victory Points to Win")
            print("3.  Change Player Count Limits")
            print("4.  Modify Building Costs")
            print("5.  Modify Starting Resources")
            print("6.  Change Map Template")
            print("7.  Configure Trading Rules")
            print("8.  Configure Turn Timer")
            print("9.  Toggle Variant Rules")
            print("10. View Building Limits")
            print("11. View Map Template Details")
            print("12. Validate Settings")
            print("13. Save Settings")
            print("14. Exit Without Saving")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.view_settings()
            elif choice == '2':
                self.change_victory_points()
            elif choice == '3':
                self.change_player_limits()
            elif choice == '4':
                self.modify_building_costs()
            elif choice == '5':
                self.modify_starting_resources()
            elif choice == '6':
                self.change_map_template()
            elif choice == '7':
                self.configure_trading()
            elif choice == '8':
                self.configure_turn_timer()
            elif choice == '9':
                self.toggle_variants()
            elif choice == '10':
                self.view_building_limits()
            elif choice == '11':
                self.view_map_details()
            elif choice == '12':
                self.validate_settings()
            elif choice == '13':
                self.save_and_exit()
                break
            elif choice == '14':
                print("Exiting without saving.")
                break
            else:
                print("Invalid option.")
    
    def view_settings(self):
        """Display current settings summary."""
        print("\n" + self.settings.get_summary())
        input("\nPress Enter to continue...")
    
    def change_victory_points(self):
        """Change victory points needed to win."""
        print("\n--- Change Victory Points to Win ---")
        current = self.settings.get_victory_points_to_win()
        print(f"Current: {current}")
        
        try:
            new_vp = int(input("New victory points (3-20): "))
            self.settings.set_victory_points_to_win(new_vp)
            print(f"✓ Victory points set to {new_vp}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def change_player_limits(self):
        """Change min/max player counts."""
        print("\n--- Change Player Count Limits ---")
        print(f"Current: {self.settings.get_min_players()}-{self.settings.get_max_players()} players")
        
        try:
            min_players = int(input("Minimum players (2-8): "))
            max_players = int(input("Maximum players (2-8): "))
            
            if min_players > max_players:
                print("Error: Min cannot be greater than max")
                return
            
            self.settings.settings['game_rules']['min_players'] = min_players
            self.settings.settings['game_rules']['max_players'] = max_players
            print(f"✓ Player limits set to {min_players}-{max_players}")
        except ValueError:
            print("Error: Invalid input")
    
    def modify_building_costs(self):
        """Modify building costs."""
        print("\n--- Modify Building Costs ---")
        buildings = ['road', 'settlement', 'city', 'development_card']
        
        for i, building in enumerate(buildings, 1):
            cost = self.settings.get_building_cost(building)
            cost_str = ', '.join([f"{v} {k}" for k, v in cost.items()])
            print(f"{i}. {building.replace('_', ' ').title()}: {cost_str}")
        
        choice = input("\nSelect building to modify (1-4, or Enter to cancel): ").strip()
        if not choice:
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(buildings):
                self.edit_building_cost(buildings[idx])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    def edit_building_cost(self, building: str):
        """Edit cost for a specific building."""
        print(f"\n--- Edit {building.replace('_', ' ').title()} Cost ---")
        current = self.settings.get_building_cost(building)
        print(f"Current cost: {current}")
        
        new_cost = {}
        resources = ['wood', 'brick', 'sheep', 'wheat', 'ore']
        
        print("\nEnter new costs (0 to remove resource):")
        for resource in resources:
            current_amount = current.get(resource, 0)
            inp = input(f"  {resource.capitalize()} [{current_amount}]: ").strip()
            if inp:
                amount = int(inp)
                if amount > 0:
                    new_cost[resource] = amount
            elif current_amount > 0:
                new_cost[resource] = current_amount
        
        self.settings.set_building_cost(building, new_cost)
        print(f"✓ {building.replace('_', ' ').title()} cost updated")
    
    def modify_starting_resources(self):
        """Modify starting resources for players."""
        print("\n--- Modify Starting Resources ---")
        current = self.settings.get_starting_resources()
        
        print("Current starting resources:")
        for resource, amount in current.items():
            print(f"  {resource.capitalize()}: {amount}")
        
        print("\nEnter new amounts (press Enter to keep current):")
        new_resources = {}
        for resource, current_amount in current.items():
            inp = input(f"  {resource.capitalize()} [{current_amount}]: ").strip()
            new_resources[resource] = int(inp) if inp else current_amount
        
        self.settings.set_starting_resources(new_resources)
        print("✓ Starting resources updated")
    
    def change_map_template(self):
        """Change the map template."""
        print("\n--- Select Map Template ---")
        templates = self.settings.list_map_templates()
        
        for i, template_name in enumerate(templates, 1):
            template = self.settings.get_map_template(template_name)
            print(f"{i}. {template['name']}")
            print(f"   Players: {template['recommended_players']}, Hexes: {template['total_hexes']}")
        
        choice = input("\nSelect template (1-{}, or Enter to cancel): ".format(len(templates))).strip()
        if not choice:
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template_name = templates[idx]
                self.settings.set_map_template(template_name)
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    def configure_trading(self):
        """Configure trading rules."""
        print("\n--- Configure Trading Rules ---")
        print(f"1. Default trade ratio: {self.settings.get_default_trade_ratio()}:1")
        print(f"2. Player trading: {'Enabled' if self.settings.is_player_trading_allowed() else 'Disabled'}")
        
        choice = input("\nWhat to modify? (1-2, or Enter to cancel): ").strip()
        
        if choice == '1':
            new_ratio = int(input("New default trade ratio (2-5): "))
            self.settings.settings['trading_rules']['default_trade_ratio'] = new_ratio
            print(f"✓ Default trade ratio set to {new_ratio}:1")
        elif choice == '2':
            toggle = input("Enable player trading? (y/n): ").lower() == 'y'
            self.settings.settings['trading_rules']['allow_player_trading'] = toggle
            print(f"✓ Player trading {'enabled' if toggle else 'disabled'}")
    
    def configure_turn_timer(self):
        """Configure turn timer settings."""
        print("\n--- Configure Turn Timer ---")
        time_limits = self.settings.get_time_limits()
        print(f"Turn timer: {'Enabled' if time_limits['enable_turn_timer'] else 'Disabled'}")
        print(f"Seconds per turn: {time_limits['seconds_per_turn']}")
        
        enable = input("\nEnable turn timer? (y/n): ").lower() == 'y'
        self.settings.settings['time_limits']['enable_turn_timer'] = enable
        
        if enable:
            seconds = int(input("Seconds per turn (30-300): "))
            self.settings.settings['time_limits']['seconds_per_turn'] = seconds
        
        print("✓ Turn timer settings updated")
    
    def toggle_variants(self):
        """Toggle variant rules."""
        print("\n--- Toggle Variant Rules ---")
        variants = self.settings.get_variant_rules()
        
        for i, (rule, enabled) in enumerate(variants.items(), 1):
            if rule != 'custom_rule_description':
                status = "ON" if enabled else "OFF"
                print(f"{i}. {rule.replace('_', ' ').title()}: {status}")
        
        choice = input("\nSelect rule to toggle (or Enter to cancel): ").strip()
        if not choice:
            return
        
        try:
            idx = int(choice) - 1
            rule_names = [k for k in variants.keys() if k != 'custom_rule_description']
            if 0 <= idx < len(rule_names):
                rule = rule_names[idx]
                current = variants[rule]
                self.settings.set_variant_rule(rule, not current)
                print(f"✓ {rule.replace('_', ' ').title()} {'enabled' if not current else 'disabled'}")
        except ValueError:
            print("Invalid input")
    
    def view_building_limits(self):
        """Display building limits."""
        print("\n--- Building Limits Per Player ---")
        for building_type in ['roads', 'settlements', 'cities']:
            limit = self.settings.get_building_limit(building_type)
            print(f"{building_type.capitalize()}: {limit}")
        input("\nPress Enter to continue...")
    
    def view_map_details(self):
        """View detailed map template information."""
        print("\n--- Map Template Details ---")
        templates = self.settings.list_map_templates()
        
        for i, template_name in enumerate(templates, 1):
            print(f"{i}. {template_name}")
        
        choice = input("\nSelect template to view (1-{}, or Enter to cancel): ".format(len(templates))).strip()
        if not choice:
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template = self.settings.get_map_template(templates[idx])
                print(f"\n{template['name']}")
                print(f"Description: {template['description']}")
                print(f"Recommended Players: {template['recommended_players']}")
                print(f"Total Hexes: {template['total_hexes']}")
                print(f"Layout: {template['board_layout']}")
                print("\nResource Distribution:")
                for resource, count in template['hex_distribution'].items():
                    print(f"  {resource.capitalize()}: {count}")
                print("\nPorts:")
                for port_type, count in template['ports'].items():
                    print(f"  {port_type.replace('_', ' ').title()}: {count}")
        except (ValueError, IndexError):
            print("Invalid input")
        
        input("\nPress Enter to continue...")
    
    def validate_settings(self):
        """Validate current settings."""
        print("\n--- Validating Settings ---")
        issues = self.settings.validate_settings()
        
        if issues:
            print("\n⚠ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ All settings are valid!")
        
        input("\nPress Enter to continue...")
    
    def save_and_exit(self):
        """Save settings and exit."""
        confirm = input("\nSave changes? (y/n): ")
        if confirm.lower() == 'y':
            self.settings.save_settings()
            print("✓ Settings saved successfully!")
        else:
            print("Changes discarded.")


if __name__ == "__main__":
    editor = SettingsEditor()
    editor.main_menu()
