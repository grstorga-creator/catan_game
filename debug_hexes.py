import sys
sys.path.insert(0, './shared')

from nodknaKra_board import NodKnaKraBoard

board = NodKnaKraBoard(seed=42)
board.generate()

print(f'Total land hexes in board.hexes: {len(board.hexes)}')

# Count by terrain type
terrain_counts = {}
for coord, hex_obj in board.hexes.items():
    terrain = hex_obj.terrain.name
    terrain_counts[terrain] = terrain_counts.get(terrain, 0) + 1

print(f'Terrain distribution:')
for terrain, count in sorted(terrain_counts.items()):
    print(f'  {terrain}: {count}')

# Count non-desert hexes
non_desert = [h for h in board.hexes.values() if h.terrain.name != 'DESERT']
print(f'\nNon-desert hexes: {len(non_desert)}')
print(f'Desert hexes: {len([h for h in board.hexes.values() if h.terrain.name == "DESERT"])}')

# Count hexes WITH tokens
hexes_with_tokens = [h for h in board.hexes.values() if h.number_token is not None]
print(f'\nHexes with number tokens: {len(hexes_with_tokens)}')
print(f'Hexes without number tokens: {len(board.hexes) - len(hexes_with_tokens)}')
