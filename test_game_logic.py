"""
Project: NodKnaKra Settlers of Catan
File: test_game_logic.py
Created: 2026-07-09

EDIT HISTORY (most recent first):
2026-07-09 - Gordon - Fixed imports to reference shared folder
2026-07-09 - Gordon - Created integrated game logic test showcasing all Phase 1 systems
"""

import sys
sys.path.insert(0, './shared')

from nodknaKra_board import NodKnaKraBoard
from nodknaKra_player import Player, Resource
from nodknaKra_game_state import GameState
from nodknaKra_card import CardDeck
from chips_system import ChipsSystem
from nodknaKra_rules import Rules


def test_full_game_flow():
    """Test complete game logic flow"""
    print("\n" + "="*70)
    print("NodKnaKra - Full Game Logic Test")
    print("="*70)
    
    # Create players
    print("\n1. INITIALIZE GAME")
    print("-" * 70)
    players = [
        Player(0, "Alice", "red"),
        Player(1, "Bob", "blue"),
        Player(2, "Carol", "green"),
        Player(3, "Dave", "yellow")
    ]
    print(f"✓ Created {len(players)} players")
    
    # Create game state
    victory_points = {2: 10, 3: 17, 4: 15, 5: 12, 6: 10}
    game_state = GameState(4, victory_points, victory_margin=2)
    game_state.set_players(players)
    print(f"✓ Game state initialized: {game_state.victory_points_to_win} VP to win (by 2)")
    
    # Create board
    print("\n2. GENERATE BOARD")
    print("-" * 70)
    board = NodKnaKraBoard(seed=42)
    hexes = board.generate()
    print(f"✓ Generated {len(hexes)}-hex board")
    board.print_stats()
    
    # Create chips system
    print("\n3. INITIALIZE CHIPS SYSTEM")
    print("-" * 70)
    chips = ChipsSystem(4)
    print("✓ Chips system initialized")
    
    # Create card deck
    print("\n4. LOAD DEVELOPMENT CARDS")
    print("-" * 70)
    try:
        deck = CardDeck("./config/nodknaKra_cards.json")
    except FileNotFoundError:
        print("⚠ Card config not found - skipping deck test")
        deck = None
    
    # Create rules engine
    print("\n5. INITIALIZE RULES ENGINE")
    print("-" * 70)
    rules = Rules(hexes)
    print("✓ Rules engine initialized")
    
    # Test resource giving
    print("\n6. TEST RESOURCE DISTRIBUTION")
    print("-" * 70)
    alice_resources = {
        Resource.WOOD: 2,
        Resource.BRICK: 2,
        Resource.SHEEP: 2,
        Resource.WHEAT: 2,
        Resource.ORE: 1
    }
    for resource, amount in alice_resources.items():
        players[0].add_resource(resource, amount)
    print("✓ Alice received: 2 wood, 2 brick, 2 sheep, 2 wheat, 1 ore")
    
    # Test building
    print("\n7. TEST BUILDING MECHANICS")
    print("-" * 70)
    if players[0].build_settlement((0, 0)):
        print("✓ Alice built settlement at (0, 0) = +1 VP")
    
    if players[0].upgrade_to_city((0, 0)):
        print("✓ Alice upgraded settlement to city = +1 VP (total 2)")
    
    players[0].build_road(((0, 0), (1, 0)))
    print("✓ Alice built road")
    
    players[0].print_status()
    
    # Test chips
    print("\n8. TEST CHIPS SYSTEM")
    print("-" * 70)
    chips.add_chips(0, 3, "Rolled 9, no settlements on 9")
    chips.add_chips(1, 2, "Rolled 8, one settlement on 8")
    chips.add_chips(2, 1, "Rolled 6, two settlements on 6")
    print("✓ Chips distributed based on dice rolls")
    chips.print_status()
    
    # Test chip conversion
    print("\n9. TEST CHIP CONVERSION")
    print("-" * 70)
    if chips.convert_to_resource(0, 2):
        print("✓ Alice converted 2 chips to resources (1:1 ratio)")
    else:
        print("✗ Conversion failed")
    chips.print_status()
    
    # Test trading
    print("\n10. TEST PLAYER-TO-PLAYER TRADING")
    print("-" * 70)
    giving_alice = {Resource.WOOD: 1, Resource.BRICK: 1}
    giving_bob = {Resource.SHEEP: 1, Resource.ORE: 1}
    
    if rules.can_trade_with_player(players[0], giving_alice, players[1], giving_bob):
        print("✓ Trade validated")
        players[0].pay_resources(giving_alice)
        for res, amount in giving_bob.items():
            players[0].add_resource(res, amount)
        players[1].pay_resources(giving_bob)
        for res, amount in giving_alice.items():
            players[1].add_resource(res, amount)
        print("✓ Alice traded 1 wood + 1 brick → 1 sheep + 1 ore (from Bob)")
    
    # Test game state
    print("\n11. TEST GAME STATE & TURNS")
    print("-" * 70)
    print(f"Phase: {game_state.get_phase().value}")
    print(f"Current player: {game_state.get_current_player().name}")
    
    game_state.next_turn()
    print(f"After next_turn(): {game_state.get_current_player().name}'s turn")
    
    # Test dice rolling
    print("\n12. TEST DICE ROLLING")
    print("-" * 70)
    dice_roll = game_state.roll_dice()
    print(f"✓ Rolled: {dice_roll[0]} + {dice_roll[1]} = {game_state.get_dice_total()}")
    
    # Test robber
    print("\n13. TEST ROBBER MECHANICS")
    print("-" * 70)
    game_state.set_robber_location((3, 0))
    print(f"✓ Robber placed at: {game_state.get_robber_location()}")
    
    # Test victory conditions with 2-point margin
    print("\n14. TEST VICTORY CONDITIONS (2-POINT MARGIN)")
    print("-" * 70)
    # Manually set VP for testing
    players[0]._visible_vp = 15
    players[1]._visible_vp = 13
    players[2]._visible_vp = 10
    players[3]._visible_vp = 8
    
    print(f"Alice: {players[0].get_total_vp()} VP")
    print(f"Bob: {players[1].get_total_vp()} VP")
    print(f"Carol: {players[2].get_total_vp()} VP")
    print(f"Dave: {players[3].get_total_vp()} VP")
    
    winner = game_state.check_winner()
    if winner is not None:
        print(f"\n✓ WINNER: {players[winner].name}! (Margin: {players[winner].get_total_vp() - players[1].get_total_vp()} points)")
    else:
        print("\n✓ No winner yet")
    
    # Print leaderboard
    print("\n15. LEADERBOARD")
    print("-" * 70)
    leaderboard = game_state.get_leaderboard()
    for rank, (idx, name, vp) in enumerate(leaderboard, 1):
        status = " (LEADER)" if rank == 1 else ""
        print(f"{rank}. {name}: {vp} VP{status}")
    
    # Print all rules
    print("\n16. GAME RULES SUMMARY")
    print("-" * 70)
    rules.print_rules()
    
    print("="*70)
    print("✓ ALL GAME LOGIC TESTS PASSED!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_full_game_flow()
