"""
Test script for Vertex/Edge system
"""

import sys
sys.path.insert(0, r'C:\catan_game\catan_game')

from nodknaKra_game import Game
from nodknaKra_vertices_edges import VertexEdgeSystem

# Create a game
print("Creating game with Standard map...")
game = Game(map_name='standard', seed=42)

print("\nInitializing Vertex/Edge system...")
ve_system = VertexEdgeSystem(game.board)

print(f"\n{'='*70}")
print(f"VERTEX/EDGE SYSTEM TEST - STANDARD MAP")
print(f"{'='*70}")

print(f"\nTotal vertices: {len(ve_system.vertices)}")
print(f"Total edges: {len(ve_system.edges)}")

# Test hex neighbors
print(f"\n{'='*70}")
print(f"HEX NEIGHBOR TESTS")
print(f"{'='*70}")

test_hexes = ['D5', 'B3', 'E8', 'F3', 'G5']

for hex_pos in test_hexes:
    neighbors = ve_system._get_hex_neighbors(hex_pos)
    print(f"\n{hex_pos} neighbors ({len(neighbors)}): {neighbors}")

# Test vertex queries
print(f"\n{'='*70}")
print(f"VERTEX TESTS")
print(f"{'='*70}")

# Find a vertex touching D5
print(f"\nVertices touching D5, B3, E8, C4:")
for hex_pos in ['D5', 'B3', 'E8', 'C4']:
    vertices_touching = [v for v in ve_system.vertices.values() if hex_pos in v.hex_positions]
    print(f"\n  {hex_pos}: {len(vertices_touching)} vertices")
    for v in vertices_touching[:3]:  # Show first 3
        print(f"    {v.vertex_id} touches hexes: {v.hex_positions}")

# Test vertex adjacency
print(f"\n{'='*70}")
print(f"VERTEX ADJACENCY TEST")
print(f"{'='*70}")

# Pick a vertex and show its adjacent vertices
if ve_system.vertices:
    sample_vertex_id = list(ve_system.vertices.keys())[0]
    sample_vertex = ve_system.vertices[sample_vertex_id]
    adjacent = ve_system.get_adjacent_vertices(sample_vertex_id)
    edges = ve_system.get_incident_edges(sample_vertex_id)
    
    print(f"\nSample vertex: {sample_vertex_id}")
    print(f"Touches hexes: {sample_vertex.hex_positions}")
    print(f"Adjacent vertices ({len(adjacent)}): {adjacent}")
    print(f"Incident edges ({len(edges)}): {edges}")

# Test settlement placement
print(f"\n{'='*70}")
print(f"PLACEMENT RULE TESTS")
print(f"{'='*70}")

# Test can_place_settlement
if ve_system.vertices:
    test_vertex_id = list(ve_system.vertices.keys())[0]
    can_place = ve_system.can_place_settlement(test_vertex_id, player_id=1)
    print(f"\nCan place settlement at {test_vertex_id}: {can_place}")
    
    # Place it
    if can_place:
        result = ve_system.place_settlement(test_vertex_id, player_id=1)
        print(f"Placed settlement: {result}")
        
        # Check adjacent vertices now
        adjacent = ve_system.get_adjacent_vertices(test_vertex_id)
        print(f"\nAdjacent vertices that now block new settlements: {adjacent}")
        
        for adj_id in list(adjacent)[:2]:
            can_place_adj = ve_system.can_place_settlement(adj_id, player_id=2)
            print(f"  Can place at {adj_id}: {can_place_adj} (blocked)")

print(f"\n{'='*70}")
print("Tests complete!")
print(f"{'='*70}\n")
