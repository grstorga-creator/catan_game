# Quick Reference

## Activate Virtual Environment

```bash
cd C:\catan_game\catan_game
venv\Scripts\activate.bat
```

You should see `(venv)` in your prompt.

## Run the Game

```bash
python play_catan.py
```

## Git Commands

```bash
# Check status
git status

# See what changed
git diff

# Stage changes
git add .

# Commit
git commit -m "Your message"

# View history
git log --oneline

# Push to GitHub (if configured)
git push origin main

# Pull latest
git pull origin main
```

## Configure Git (First Time)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Deactivate Environment

```bash
deactivate
```

## Install New Dependencies

```bash
pip install package_name
```

## Game Controls

- S = Settlement, C = City, R = Road
- SPACE = Roll, ENTER = End turn, T = Trade
- Drag = Pan, Scroll = Zoom, Click = Place

## Troubleshooting

**Python not found?**
- Install Python 3.12+
- Ensure it's in PATH

**Pygame error?**
- `pip install pygame --upgrade`

**Git not found?**
- Install from https://git-scm.com/download/win
- Restart Command Prompt

---

For more details, see GIT_SYNC_GUIDE.md
