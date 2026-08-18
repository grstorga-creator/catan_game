"""
Test script to generate all 7 NodKnaKra board sizes and verify symmetry
"""
import sys
sys.path.insert(0, './shared')

from nodknaKra_board import NodKnaKraBoard

def test_all_sizes():
    print("\n" + "="*80)
    print("NodKnaKra Board Generator - All 7 Symmetric Sizes")
    print("="*80 + "\n")
    
    sizes = NodKnaKraBoard.BOARD_SIZES
    
    summary = []
    
    for size_name in ['ultra_small', 'micro', 'small', 'standard', 'large', 'xlarge', 'ultra_large']:
        print(f"\n{'-'*80}")
        print(f"Generating {size_name.upper()} board...")
        print(f"{'-'*80}")
        
        board = NodKnaKraBoard(row_pattern=sizes[size_name], seed=42)
        hexes = board.generate()
        all_hexes = board.get_all_hexes()
        
        land_count = len(board.hexes)
        water_count = len(board.water_hexes)
        total_count = len(all_hexes)
        row_pattern = board.row_pattern
        
        print(f"\n[OK] {size_name.upper()} board generated!")
        print(f"  Row pattern:    {row_pattern}")
        print(f"  Land hexes:     {land_count:3d}")
        print(f"  Water hexes:    {water_count:3d}")
        print(f"  Total hexes:    {total_count:3d}")
        
        # Count ports
        generic_count = sum(1 for h in board.water_hexes.values() if h.port and h.port.value == 'generic')
        specific_count = sum(1 for h in board.water_hexes.values() if h.port and h.port.value != 'generic')
        plain_water = water_count - generic_count - specific_count
        
        print(f"  Generic 3:1:    {generic_count:3d}")
        print(f"  Specific 2:1:   {specific_count:3d}")
        print(f"  Plain water:    {plain_water:3d}")
        
        summary.append({
            'name': size_name,
            'rows': row_pattern,
            'land': land_count,
            'water': water_count,
            'total': total_count
        })
    
    # Print summary table
    print(f"\n\n{'='*80}")
    print("SUMMARY TABLE - All 7 Board Sizes")
    print(f"{'='*80}\n")
    print(f"{'Size':<15} {'Rows':<20} {'Land':<8} {'Water':<8} {'Total':<8}")
    print(f"{'-'*80}")
    
    for s in summary:
        rows_str = str(s['rows'])
        print(f"{s['name']:<15} {rows_str:<20} {s['land']:<8} {s['water']:<8} {s['total']:<8}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    test_all_sizes()
