"""
NodKnaKra Game - Loads maps, randomizes terrain, and manages board state
"""

import random
from typing import Dict, List
from nodknaKra_maps_oop import (
    MapConfiguration, HexTemplate, HexType, HarborType,
    SMALL, STANDARD, LARGE
)


# Token distribution for each map size
# Tokens for Standard map: 1-2, 2-3, 4-4, 5-5, 5-6, 5-8, 4-9, 4-10, 2-11, 1-12 = 33 tokens
TOKEN_VALUES = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

TOKEN_DISTRIBUTIONS = {
    'small': {
        'values': TOKEN_VALUES,
        'counts': [1, 2, 3, 4, 4, 4, 3, 3, 2, 1],  # 27 tokens
    },
    'standard': {
        'values': TOKEN_VALUES,
        'counts': [1, 2, 4, 5, 5, 5, 4, 4, 2, 1],  # 33 tokens
    },
    'large': {
        'values': TOKEN_VALUES,
        'counts': [2, 3, 5, 7, 7, 7, 5, 5, 3, 2],  # 46 tokens
    },
}


class GameHex:
    """An actual game hex with all properties"""
    
    def __init__(self, position: str, hex_type: HexType):
        self.position = position
        self.hex_type = hex_type
        self.number_token = None
        self.harbor = None
        self.adjacent_terrain_positions = []
    
    def __repr__(self):
        return f"Hex({self.position}, {self.hex_type.value})"


class Board:
    """Game board - loaded from map configuration with randomized terrain"""
    
    def __init__(self, map_config: MapConfiguration, seed: int = None):
        self.map_config = map_config
        self.hexes: Dict[str, GameHex] = {}
        
        if seed is not None:
            random.seed(seed)
        
        self._load_map()
        self._randomize_terrain()
        self._distribute_tokens()
    
    def _load_map(self):
        """Load hexes from map configuration"""
        for template in self.map_config.hexes:
            game_hex = GameHex(template.position, template.hex_type)
            game_hex.adjacent_terrain_positions = template.adjacent_terrain_positions
            self.hexes[template.position] = game_hex
    
    def _randomize_terrain(self):
        """Randomize terrain types while keeping desert at D1"""
        # Get all terrain hexes (excluding desert)
        terrain_hexes = [
            h for h in self.hexes.values() 
            if h.hex_type not in [HexType.WATER, HexType.DESERT]
        ]
        
        # Get all non-desert terrain templates to extract distribution
        terrain_templates = [
            t for t in self.map_config.hexes 
            if t.hex_type not in [HexType.WATER, HexType.DESERT]
        ]
        
        # Extract terrain types from templates (maintaining the distribution)
        terrain_types = [t.hex_type for t in terrain_templates]
        
        # Shuffle terrain types
        random.shuffle(terrain_types)
        
        # Assign shuffled terrain to hexes (excluding desert hex D1)
        terrain_hex_positions = sorted([h.position for h in terrain_hexes])
        
        for pos, terrain_type in zip(terrain_hex_positions, terrain_types):
            self.hexes[pos].hex_type = terrain_type
        
        print(f"[DEBUG] Randomized terrain for {len(terrain_types)} hexes")
    
    def _distribute_tokens(self):
        """Distribute and shuffle number tokens to terrain hexes"""
        # Get token distribution for this map
        map_key = self.map_config.name.lower()
        if map_key not in TOKEN_DISTRIBUTIONS:
            print(f"[WARNING] No token distribution for {map_key}, skipping tokens")
            return
        
        dist = TOKEN_DISTRIBUTIONS[map_key]
        token_values = dist['values']
        token_counts = dist['counts']
        
        # Build list of tokens
        tokens = []
        for value, count in zip(token_values, token_counts):
            tokens.extend([value] * count)
        
        # Shuffle tokens
        random.shuffle(tokens)
        
        # Get terrain hexes (excluding desert)
        terrain_hexes = self.get_terrain_hexes()
        terrain_positions = sorted([h.position for h in terrain_hexes])
        
        # Assign tokens to hexes
        for pos, token_value in zip(terrain_positions, tokens):
            self.hexes[pos].number_token = token_value
        
        print(f"[DEBUG] Distributed {len(tokens)} tokens to {len(terrain_positions)} terrain hexes")
        print(f"[DEBUG] Token distribution: {dict(zip(token_values, token_counts))}")
    
    def get_hex(self, position: str) -> GameHex:
        """Get hex by position"""
        return self.hexes.get(position)
    
    def get_all_hexes(self) -> Dict[str, GameHex]:
        """Get all hexes"""
        return self.hexes
    
    def get_terrain_hexes(self) -> List[GameHex]:
        """Get all terrain hexes (excluding desert and water)"""
        return [h for h in self.hexes.values() if h.hex_type not in [HexType.WATER, HexType.DESERT]]
    
    def get_water_hexes(self) -> List[GameHex]:
        """Get all water hexes"""
        return [h for h in self.hexes.values() if h.hex_type == HexType.WATER]
    
    def get_desert_hex(self) -> GameHex:
        """Get the desert hex"""
        return next((h for h in self.hexes.values() if h.hex_type == HexType.DESERT), None)
    
    def show_board(self):
        """Display the board"""
        print(f"\n{'='*70}")
        print(f"BOARD: {self.map_config.name.upper()}")
        print(f"{'='*70}")
        
        # Organize by row
        rows = {}
        for pos, hex_obj in self.hexes.items():
            row_letter = pos[0]
            if row_letter not in rows:
                rows[row_letter] = []
            rows[row_letter].append((pos, hex_obj))
        
        # Display each row with terrain and tokens
        for row_letter in sorted(rows.keys()):
            hex_list = rows[row_letter]
            # Sort by column number
            hex_list.sort(key=lambda x: int(x[0][1:]))
            
            hex_display = []
            for pos, hex_obj in hex_list:
                if hex_obj.hex_type == HexType.WATER:
                    hex_display.append("~  ")
                elif hex_obj.hex_type == HexType.DESERT:
                    hex_display.append("D  ")
                else:
                    # Terrain with token
                    terrain_char = hex_obj.hex_type.value[0]
                    if hex_obj.number_token:
                        token = f"{hex_obj.number_token:2d}"
                    else:
                        token = "  "
                    hex_display.append(f"{terrain_char}{token}")
            
            print(f"Row {row_letter}: {' '.join(hex_display)}")
        
        # Summary
        print(f"\nTerrain hexes: {len(self.get_terrain_hexes())}")
        print(f"Desert hexes: 1")
        print(f"Water hexes: {len(self.get_water_hexes())}")
        print(f"Total hexes: {len(self.hexes)}\n")


class Game:
    """Main game class"""
    
    MAPS = {
        'small': SMALL,
        'standard': STANDARD,
        'large': LARGE,
    }
    
    def __init__(self, map_name: str = 'standard', seed: int = None):
        """Initialize game with a map"""
        if map_name not in self.MAPS:
            raise ValueError(f"Unknown map: {map_name}. Choose from {list(self.MAPS.keys())}")
        
        self.map_name = map_name
        self.map_config = self.MAPS[map_name]
        self.board = Board(self.map_config, seed=seed)
    
    def render_ascii(self):
        """Show ASCII board representation"""
        self.board.show_board()
    
    def get_board_data(self) -> Dict:
        """Get board data for rendering"""
        return {
            'map_name': self.map_name,
            'hexes': self.board.get_all_hexes(),
            'terrain_hexes': self.board.get_terrain_hexes(),
            'water_hexes': self.board.get_water_hexes(),
            'desert_hex': self.board.get_desert_hex(),
        }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NodKnaKra Game - Board Generation Test")
    print("="*70)
    
    # Test all three maps
    for map_name in ['small', 'standard', 'large']:
        game = Game(map_name=map_name, seed=42)
        game.render_ascii()
    
    print("="*70)
    print("All maps generated successfully!")
    print("="*70 + "\n")
