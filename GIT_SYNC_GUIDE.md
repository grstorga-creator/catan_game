# Complete Setup and Git Synchronization Guide

## 🎯 Your Goal
Set up Settlers of Catan development environment at `C:\catan_game\catan_game` and keep code in sync with me via git.

---

## 📋 STEP 1: Initial Setup (One Time)

### 1a. Extract the Package

Download `catan_game.zip` and extract to:
```
C:\catan_game\catan_game
```

### 1b. Run Setup Script

Open **Command Prompt** and run:

```bash
cd C:\catan_game\catan_game
setup_dev.bat
```

**This automatically:**
- ✅ Creates Python virtual environment
- ✅ Installs Pygame
- ✅ Initializes git repository
- ✅ Creates initial commit

**Wait for it to complete.** You should see:
```
==========================================
Setup Complete!
==========================================
```

---

## 🎮 STEP 2: Play the Game

```bash
cd C:\catan_game\catan_game
venv\Scripts\activate.bat
python play_catan.py
```

---

## 🔄 STEP 3: Git Workflow (Keeping in Sync)

### Your First Commit (after setup runs)

After `setup_dev.bat` completes:

```bash
cd C:\catan_game\catan_game
git config user.name "Your Name"
git config user.email "your.email@example.com"
git status
```

You should see the initial files ready to commit.

### Daily Development Workflow

**Every time you work:**

1. **Activate virtual environment:**
   ```bash
   cd C:\catan_game\catan_game
   venv\Scripts\activate.bat
   ```

2. **Make changes to code**
   - Edit files in `client/`, `shared/`, `config/`, etc.

3. **Check what changed:**
   ```bash
   git status
   ```

4. **See exact changes:**
   ```bash
   git diff
   ```

5. **Stage your changes:**
   ```bash
   git add .
   ```

6. **Commit with description:**
   ```bash
   git commit -m "What you changed - be descriptive!"
   ```

7. **Check your work:**
   ```bash
   git log --oneline
   ```

---

## 🔗 STEP 4: Sync With Me

We have a few options for keeping code in sync:

### Option A: Push to GitHub/GitLab (Recommended)

**First time only:**

1. Create account at https://github.com (free)
2. Create new repository (name it `catan_game`)
3. Copy the repository URL

**Then in your local folder:**

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

**From then on, after each commit:**
```bash
git push origin main
```

**To get my updates:**
```bash
git pull origin main
```

### Option B: Share via Git Bundle

When you want to share changes with me:

```bash
git bundle create my_changes.bundle main
```

Send me `my_changes.bundle` file.

I'll import it:
```bash
git bundle verify my_changes.bundle
git fetch my_changes.bundle main
```

### Option C: Share Individual Commits

For each batch of changes:

```bash
git log --oneline          # See your commits
git format-patch origin    # Create patch files
```

Send me the `.patch` files.

---

## 📝 Good Git Practices

### Commit Messages Should Be Clear

**✅ Good:**
```
git commit -m "Add player color assignment - Red, Green, Yellow, White, Blue, Purple"
git commit -m "Fix settlement alignment on hex vertices"
git commit -m "Implement bank trading system with resource validation"
```

**❌ Bad:**
```
git commit -m "fix stuff"
git commit -m "changes"
git commit -m "wip"
```

### Commit Frequently

- Make small, logical commits
- One feature or fix per commit
- Easy to track what changed

### Before Starting Work

```bash
git status                 # Make sure you're clean
git log --oneline -5       # See recent commits
```

---

## 📊 Understanding Git Status

### Clean (nothing to commit):
```
On branch main
nothing to commit, working tree clean
```
✅ You're ready to make changes

### Dirty (files changed):
```
On branch main
Changes not staged for commit:
  modified:   client/game.py
  modified:   shared/player.py
```
→ You have unsaved changes. Commit them or discard.

### Untracked (new files):
```
Untracked files:
  new_feature.py
  test_file.py
```
→ New files git doesn't know about. Stage with `git add .`

---

## 🐛 Troubleshooting

### "git command not found"
- Git isn't in PATH
- Restart Command Prompt after installing Git
- Or add it manually to PATH

### "fatal: not a git repository"
- You're not in the right directory
- Make sure you're in `C:\catan_game\catan_game`
- Run `git init` if needed (but `setup_dev.bat` does this)

### "Please tell me who you are"
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### "Your branch is ahead of 'origin/main'"
```bash
git push origin main
```

### "Merge conflict"
- Files have conflicting changes
- Edit the file and resolve conflicts
- Then: `git add .` and `git commit -m "Resolve conflicts"`

---

## 🔄 Syncing Workflow Summary

```
You Make Changes
        ↓
git add .
        ↓
git commit -m "description"
        ↓
git push origin main  (if using GitHub)
        ↓
I Pull and See Your Changes
        ↓
I Make Updates
        ↓
I Push Changes
        ↓
You Run: git pull origin main
        ↓
You Have My Updates!
```

---

## 🎯 Quick Reference Commands

```bash
# Setup (one time)
setup_dev.bat
git config user.name "Name"
git config user.email "email@example.com"

# Daily work
venv\Scripts\activate.bat
python play_catan.py

# Git workflow
git status              # See what changed
git diff                # See exact changes
git add .               # Stage all changes
git commit -m "msg"     # Commit
git log --oneline       # See commit history
git push origin main    # Push to GitHub
git pull origin main    # Get latest
```

---

## ✅ You're Ready!

1. ✅ Extract package to `C:\catan_game\catan_game`
2. ✅ Run `setup_dev.bat`
3. ✅ Play game: `python play_catan.py`
4. ✅ Make changes and commit: `git commit -m "..."`
5. ✅ Sync with me via GitHub or patches

You now have a professional development setup! 🚀
