"""
Development Card Editor - CLI tool for managing custom development cards
"""

import json
from pathlib import Path


class CardEditor:
    """Interactive editor for development cards configuration."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'dev_cards.json'
        
        self.config_path = config_path
        self.config = None
        self.load_config()
    
    def load_config(self):
        """Load the current configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found. Creating new one at {self.config_path}")
            self.config = {
                "card_types": {},
                "deck_settings": {
                    "total_cards": 0,
                    "shuffle_on_empty": True,
                    "notes": ""
                }
            }
    
    def save_config(self):
        """Save the configuration back to file."""
        # Update total card count
        total = sum(card['count'] for card in self.config['card_types'].values())
        self.config['deck_settings']['total_cards'] = total
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"\n✓ Configuration saved to {self.config_path}")
    
    def list_cards(self):
        """Display all current cards."""
        print("\n=== Current Development Cards ===\n")
        
        if not self.config['card_types']:
            print("No cards defined yet.")
            return
        
        for card_id, card in self.config['card_types'].items():
            print(f"ID: {card_id}")
            print(f"  Name: {card['name']}")
            print(f"  Description: {card['description']}")
            print(f"  Count: {card['count']}")
            print(f"  Effect: {card['effect_type']}")
            if card['is_victory_point']:
                print(f"  Victory Points: {card['victory_points']}")
            print()
    
    def add_card(self):
        """Add a new card type."""
        print("\n=== Add New Development Card ===\n")
        
        card_id = input("Card ID (e.g., 'custom_trader'): ").strip()
        
        if card_id in self.config['card_types']:
            overwrite = input(f"Card '{card_id}' already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                print("Cancelled.")
                return
        
        name = input("Card Name: ").strip()
        description = input("Card Description: ").strip()
        count = int(input("Number of cards in deck: "))
        effect_type = input("Effect Type (e.g., 'knight', 'gain_resources', 'custom_effect'): ").strip()
        
        is_victory = input("Is this a victory point card? (y/n): ").lower() == 'y'
        victory_points = 0
        if is_victory:
            victory_points = int(input("How many victory points?: "))
        
        play_immediately = input("Must be played immediately when drawn? (y/n): ").lower() == 'y'
        
        # Get parameters
        print("\nParameters (press Enter with empty key to finish):")
        parameters = {}
        while True:
            key = input("  Parameter name: ").strip()
            if not key:
                break
            
            value_type = input(f"  Value type for '{key}' (str/int/bool): ").strip().lower()
            value_str = input(f"  Value for '{key}': ").strip()
            
            if value_type == 'int':
                value = int(value_str)
            elif value_type == 'bool':
                value = value_str.lower() in ['true', 'yes', 'y', '1']
            else:
                value = value_str
            
            parameters[key] = value
        
        # Create the card
        card_data = {
            "name": name,
            "description": description,
            "count": count,
            "effect_type": effect_type,
            "is_victory_point": is_victory,
            "play_immediately": play_immediately,
            "parameters": parameters
        }
        
        if is_victory:
            card_data["victory_points"] = victory_points
        
        self.config['card_types'][card_id] = card_data
        
        print(f"\n✓ Card '{name}' added successfully!")
        print("\nCard definition:")
        print(json.dumps({card_id: card_data}, indent=2))
    
    def edit_card(self):
        """Edit an existing card."""
        print("\n=== Edit Development Card ===\n")
        
        if not self.config['card_types']:
            print("No cards to edit.")
            return
        
        card_id = input("Enter card ID to edit: ").strip()
        
        if card_id not in self.config['card_types']:
            print(f"Card '{card_id}' not found.")
            return
        
        card = self.config['card_types'][card_id]
        
        print(f"\nEditing: {card['name']}")
        print("(Press Enter to keep current value)\n")
        
        name = input(f"Name [{card['name']}]: ").strip()
        if name:
            card['name'] = name
        
        desc = input(f"Description [{card['description']}]: ").strip()
        if desc:
            card['description'] = desc
        
        count = input(f"Count [{card['count']}]: ").strip()
        if count:
            card['count'] = int(count)
        
        print("\n✓ Card updated successfully!")
    
    def delete_card(self):
        """Delete a card type."""
        print("\n=== Delete Development Card ===\n")
        
        if not self.config['card_types']:
            print("No cards to delete.")
            return
        
        card_id = input("Enter card ID to delete: ").strip()
        
        if card_id not in self.config['card_types']:
            print(f"Card '{card_id}' not found.")
            return
        
        card_name = self.config['card_types'][card_id]['name']
        confirm = input(f"Delete '{card_name}'? (y/n): ")
        
        if confirm.lower() == 'y':
            del self.config['card_types'][card_id]
            print(f"✓ Card '{card_name}' deleted.")
        else:
            print("Cancelled.")
    
    def run(self):
        """Run the interactive editor."""
        while True:
            print("\n" + "="*50)
            print("Development Card Editor")
            print("="*50)
            print("1. List all cards")
            print("2. Add new card")
            print("3. Edit card")
            print("4. Delete card")
            print("5. Save and exit")
            print("6. Exit without saving")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.list_cards()
            elif choice == '2':
                self.add_card()
            elif choice == '3':
                self.edit_card()
            elif choice == '4':
                self.delete_card()
            elif choice == '5':
                self.save_config()
                break
            elif choice == '6':
                print("Exiting without saving.")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    editor = CardEditor()
    editor.run()
