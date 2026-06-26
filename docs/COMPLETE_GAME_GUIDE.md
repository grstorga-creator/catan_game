# Complete Catan Game Guide

## 🎮 Playing the Full Game

### Starting the Game

```bash
python play_catan.py
```

You'll be prompted to enter 2-4 player names. Just type each name and press Enter. When done, press Enter with an empty name.

```
Player 1: Alice
Player 2: Bob
Player 3: Charlie
Player 4: 
```

The game will then start!

## Game Flow

### Phase 1: Setup (Initial Placement)

**Round 1** - Players take turns in order (1, 2, 3, 4):
1. Place 1 settlement
2. Place 1 road connected to that settlement

**Round 2** - Players take turns in REVERSE order (4, 3, 2, 1):
1. Place 1 settlement
2. Place 1 road connected to that settlement
3. Receive resources from the 3 hexes touching this settlement

After setup, the main game begins!

### Phase 2: Main Game

Each turn follows this structure:

1. **Roll Dice** (Press SPACE)
   - Roll 2d6
   - If 7: Robber activates
   - Otherwise: Resources distributed

2. **Main Phase** (Build, Trade, Play Cards)
   - Build settlements, cities, roads
   - Trade with bank or other players
   - Buy and play development cards
   - Can do these in any order, multiple times

3. **End Turn** (Press ENTER)
   - Check for victory
   - Next player's turn

## Controls

### Essential Controls
| Key | Action |
|-----|--------|
| **SPACE** | Roll dice (main game only) |
| **ENTER** | End your turn |
| **S** | Toggle Settlement build mode |
| **C** | Toggle City build mode |
| **R** | Toggle Road build mode |
| **Click** | Place building (when in build mode) |

### Camera Controls
| Key/Mouse | Action |
|-----------|--------|
| **Click + Drag** | Pan camera around board |
| **Scroll** | Zoom in/out |
| **Arrow Keys** | Pan camera |

### Other
| Key | Action |
|-----|--------|
| **H** | Toggle help overlay |
| **Q/ESC** | Quit game |

## Setup Phase Instructions

### Placing Your First Settlement
1. On your turn, the message will say "Place your first settlement"
2. Press **S** to enter settlement mode
3. Move mouse over the board - corners (vertices) will highlight
4. **Green circle** = valid placement
5. **Red circle** = invalid (too close to another settlement)
6. Click on a green circle to place your settlement

### Placing Your First Road
1. After placing settlement, message says "Place a road"
2. Press **R** to enter road mode
3. Move mouse over edges connecting to your settlement
4. **Green line** = valid (connects to your settlement)
5. **Red line** = invalid
6. Click on a green line to place your road

### Second Round - Reverse Order
The process repeats in reverse order, and when you place your second settlement, you'll automatically receive one of each resource from the surrounding hexes!

## Main Game Instructions

### Rolling Dice
1. Press **SPACE** to roll
2. Watch the dice appear in the UI panel
3. If you rolled 7, the robber activates
4. Otherwise, resources are automatically distributed

### Getting Resources
- When a number is rolled, **all** tiles with that number produce
- If you have a settlement on a corner of that tile → get 1 resource
- If you have a city on a corner of that tile → get 2 resources
- Resources automatically added to your hand (shown in UI)

### Building Settlements
**Cost:** 1 wood, 1 brick, 1 sheep, 1 wheat

1. Make sure you have the resources
2. Press **S** for settlement mode
3. Click on a valid vertex (green circle)
4. Resources automatically deducted
5. Settlement appears on board
6. You gain 1 victory point!

**Rules:**
- Must be at least 2 edges away from any other settlement
- Must be connected to your road network

### Building Cities
**Cost:** 2 wheat, 3 ore

1. Make sure you have the resources
2. Press **C** for city mode
3. Click on one of YOUR settlements (green circle)
4. Resources automatically deducted
5. Settlement upgrades to city
6. You gain 1 more victory point (2 total from this spot)!

**Benefits:**
- Produces 2 resources instead of 1 when that hex produces

### Building Roads
**Cost:** 1 wood, 1 brick

1. Make sure you have the resources
2. Press **R** for road mode
3. Click on a valid edge (green line)
4. Resources automatically deducted
5. Road appears on board

**Rules:**
- Must connect to your existing roads or settlements

### Trading with the Bank
**Default Rate:** 4:1 (trade 4 of same resource for 1 of any other)

*Trading UI coming soon - currently use this workaround:*
- Keep track of trades yourself
- Manually adjust resources (honor system)

**Port Bonuses** (if you have settlement on a port):
- Generic Port: 3:1 (trade 3 for 1)
- Specific Port: 2:1 (trade 2 of that resource for 1 of any)

### Buying Development Cards
**Cost:** 1 sheep, 1 wheat, 1 ore

*Dev card buying UI coming soon*

### Winning the Game
First player to reach 10 victory points wins!

**Victory Points Come From:**
- Each settlement = 1 VP
- Each city = 2 VP
- Longest Road (5+ roads) = 2 VP
- Largest Army (3+ knights) = 2 VP
- Victory Point development cards = 1 VP each

## Understanding the UI

### Right Panel Layout

**Top Section - Current Player:**
- Player name in their color
- Current phase/instructions
- Game messages

**Dice Display:**
- Shows last roll
- Two dice with dots
- Total shown below

**Resources Section:**
- 5 colored cards (wood, brick, sheep, wheat, ore)
- Number on each card = how many you have
- Visually see your hand at a glance

**Buildings Section:**
- Settlements: X/5 (Y left)
- Cities: X/4 (Y left)
- Roads: X/15 (Y left)
- Victory Points: Current total

**All Players Section:**
- Everyone's VP count
- 🛣️ = Has Longest Road
- ⚔️ = Has Largest Army

**Controls Section:**
- Quick reference for keyboard shortcuts

## Visual Feedback

### Building Placement
- **Green highlight** = Valid placement, click to build
- **Red highlight** = Invalid, can't place here
- **No highlight** = Exit build mode (right-click)

### Resources
- Colored cards visually show your hand
- Easy to see what you have at a glance

### Buildings on Board
- **Settlements** = House shape (triangle roof, square base)
- **Cities** = Two towers (taller buildings)
- **Roads** = Thick colored lines
- Each player has unique color

## Advanced Strategies

### Setup Phase
- **Second settlement** is crucial - pick a spot with good numbers and variety
- Consider blocking opponents from good spots
- Think about future expansion paths

### Early Game
- Focus on resource diversity
- Build roads to best spots before opponents
- Aim for settlements on 6 and 8 (most common rolls)

### Mid Game
- Upgrade to cities for double production
- Start working toward Longest Road or Largest Army
- Consider port locations for better trading

### Late Game
- Calculate VP carefully - know how many you need
- Block opponents from reaching 10 VP
- Development cards can provide surprise VP

## Robber Rules

### When 7 is Rolled:
1. **Discard Phase** (automatic)
   - Any player with 8+ cards discards half (rounded down)
   - Happens automatically

2. **Move Robber** (manual - coming soon)
   - Current player moves robber to a new hex
   - That hex doesn't produce until robber moves
   - Can steal 1 random card from player with building on that hex

*Full robber UI coming in next update*

## Tips for New Players

1. **Diversify** - Get all 5 resource types early
2. **Numbers matter** - 6 and 8 are best (most common), 2 and 12 are worst (rarest)
3. **Roads are cheap** - Build them early to secure spots
4. **Don't hoard** - Spend resources before rolling 7
5. **Watch opponents** - Block their expansion when possible
6. **Ports are powerful** - A 2:1 port is very valuable
7. **Cities win games** - Double production is game-changing

## Common Mistakes to Avoid

1. ❌ Ignoring ore/wheat early - You need them for cities
2. ❌ Building too many roads - Settlements give VP, roads don't
3. ❌ Placing settlements too close together - Spread out for more resources
4. ❌ Forgetting victory points from cards - They count!
5. ❌ Not trading - Trading is essential to progress

## Game Variants (Configurable)

You can edit `config/game_settings.json` to customize:

- **Victory points to win** (default: 10)
- **Building costs** (change resource requirements)
- **Starting resources** (give players a boost)
- **Max cards before discard** (default: 7)
- **Trade ratios** (make trading easier/harder)

## Troubleshooting

### Can't Place Building
- Check the highlight color:
  - **Green** = valid, click to place
  - **Red** = invalid, see message in UI for reason
- Common issues:
  - Not enough resources
  - Too close to another settlement (distance rule)
  - Not connected to your roads
  - Haven't rolled dice yet this turn

### Can't Roll Dice
- Are you in setup phase? (No rolling during setup)
- Have you already rolled this turn? (Can only roll once)
- Press SPACE to roll

### Don't See My Buildings
- Make sure you're looking at the right part of the board
- Pan camera by dragging with mouse
- Zoom in with scroll wheel
- Buildings appear immediately after placing

### Game Seems Stuck
- Check the message in UI panel
- It tells you exactly what to do next
- During setup: Place settlement, then road
- During main game: Roll dice first, then build/trade

## What's Included

✅ **Complete Setup Phase**
- Initial placement with proper turn order
- Reverse order for second round
- Automatic resource distribution

✅ **Full Game Loop**
- Dice rolling with visual dice
- Automatic resource distribution
- Building placement with validation
- Turn management

✅ **Resource System**
- Visual resource cards
- Automatic deduction when building
- Proper production based on dice rolls

✅ **Victory Conditions**
- Automatic VP calculation
- Winner detection
- Longest Road tracking

✅ **Visual Feedback**
- Green/red placement indicators
- Real-time building rendering
- Clear UI with all information

## Coming Soon

The game is fully playable! These features are planned for future updates:

- ⏳ Trading UI (currently use honor system)
- ⏳ Interactive robber movement
- ⏳ Development card UI
- ⏳ Player-to-player trade interface
- ⏳ Animated dice rolls
- ⏳ Victory screen
- ⏳ Sound effects
- ⏳ Network multiplayer

## Quick Reference Card

```
╔══════════════════════════════════════════╗
║  SETTLERS OF CATAN - QUICK REFERENCE    ║
╠══════════════════════════════════════════╣
║ BUILDING COSTS                          ║
║  Settlement ... Wood, Brick, Sheep, Wheat║
║  City ......... 2 Wheat, 3 Ore          ║
║  Road ......... Wood, Brick             ║
║  Dev Card ..... Sheep, Wheat, Ore       ║
║                                         ║
║ VICTORY POINTS                          ║
║  Settlement ... 1 VP                    ║
║  City ......... 2 VP                    ║
║  Longest Road . 2 VP (5+ roads)         ║
║  Largest Army . 2 VP (3+ knights)       ║
║  VP Cards ..... 1 VP each               ║
║                                         ║
║ CONTROLS                                ║
║  SPACE ........ Roll dice               ║
║  ENTER ........ End turn                ║
║  S ............ Settlement mode         ║
║  C ............ City mode               ║
║  R ............ Road mode               ║
║  Click ........ Place building          ║
║  Drag ......... Pan camera              ║
║  Scroll ....... Zoom                    ║
╚══════════════════════════════════════════╝
```

Enjoy your game of Settlers of Catan! 🎲🏘️
