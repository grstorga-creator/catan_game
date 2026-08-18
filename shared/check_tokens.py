import sys
sys.path.insert(0, './shared')

from nodknaKra_board import NodKnaKraBoard

board = NodKnaKraBoard(seed=42)
print(f'Available numbers count: {len(board.available_numbers)}')
print(f'Available numbers: {board.available_numbers}')
print(f'Total hexes: {board.total_hexes}')
print(f'Tokens needed: {board.total_hexes - 1}')
