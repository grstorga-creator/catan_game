"""Debug script to show board hex coordinates"""
import sys
sys.path.insert(0, '.')
from nodknaKra_board import NodKnaKraBoard

board = NodKnaKraBoard(seed=42)
hexes = board.generate()

# Group by row (r coordinate)
rows = {}
for coord, hex_obj in hexes.items():
    if coord.r not in rows:
        rows[coord.r] = []
    rows[coord.r].append((coord.q, coord.r))

# Print by row
print("\nBoard Coordinates by Row:")
print("="*50)
for r in sorted(rows.keys()):
    row_coords = sorted(rows[r], key=lambda x: x[0])
    q_values = [str(q) for q, _ in row_coords]
    min_q = min([q for q, _ in row_coords])
    max_q = max([q for q, _ in row_coords])
    print(f"Row r={r:2d}: {len(row_coords):2d} hexes | q range: [{min_q:2d} to {max_q:2d}] | q values: {', '.join(q_values)}")
print("="*50)
