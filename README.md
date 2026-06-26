# Settlers of Catan - Complete Game

A fully playable implementation of Settlers of Catan in Python with Pygame.

## 🚀 Quick Start

### First Time (3 minutes)

```bash
cd C:\catan_game\catan_game
setup_dev.bat
```

### Every Time You Play

```bash
cd C:\catan_game\catan_game
venv\Scripts\activate.bat
python play_catan.py
```

## 🎯 Features

✅ Complete setup phase (proper turn order)
✅ Full main game with all Catan rules
✅ Dice rolling with visual display
✅ Automatic resource distribution
✅ Building placement with validation
✅ Bank trading system
✅ Victory point tracking
✅ Bright vibrant player colors
✅ Perfect hex alignment
✅ Git-enabled for syncing

## 📁 Project Structure

```
catan_game/
├── client/              # Game UI and rendering
├── shared/              # Game logic and state
├── config/              # Game configuration (JSON)
├── docs/                # Documentation
├── tools/               # Development tools
├── setup_dev.bat        # Windows setup script
├── setup_dev.ps1        # PowerShell setup script
├── play_catan.py        # Main game launcher
├── requirements.txt     # Python dependencies
└── venv/                # Virtual environment (created by setup)
```

## 🕹️ Game Controls

**Building:**
- S = Settlement mode
- C = City mode
- R = Road mode
- Click = Place building

**Game Flow:**
- SPACE = Roll dice
- ENTER = End turn
- T = Trade with bank

**Camera:**
- Drag = Pan board
- Scroll = Zoom

## 📖 Documentation

- **README.md** (this file) - Overview
- **GIT_SYNC_GUIDE.md** - How to use git and sync with developers
- **QUICK_REFERENCE.md** - Quick command reference
- See `docs/` folder for detailed guides

## 🔄 Git & Synchronization

This project uses git to keep code in sync.

**Configure git first time:**
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

**Commit your changes:**
```bash
git add .
git commit -m "Description of your changes"
```

**See detailed instructions in GIT_SYNC_GUIDE.md**

## 🛠️ Development

- Python 3.12+
- Pygame 2.6.1
- Git 2.52.0+

## 👥 Contributing

When you make changes:

1. Test the game: `python play_catan.py`
2. Commit frequently: `git commit -m "..."`
3. Sync with team via git push

## 📝 Game Rules Implemented

- ✅ Settlement placement with distance rules
- ✅ City upgrades and production
- ✅ Road building with connectivity
- ✅ Resource production from hex rolls
- ✅ Bank trading (4:1, 3:1 ports, 2:1 ports)
- ✅ Development cards
- ✅ Robber mechanics
- ✅ Longest road bonus
- ✅ Largest army bonus
- ✅ Victory point tracking (10 to win)

## 🎊 Ready to Play!

Extract, run setup, and enjoy! 🎲
