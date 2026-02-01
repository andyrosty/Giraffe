# 🦒 Giraffe

A tiny 2D arcade-style game built with `PyGame`.
You control a giraffe that grows its neck by eating falling leaves while avoiding rotten ones.
Survive as long as you can — the game gets harder over time!

---

## 🎮 Gameplay

- Control a **giraffe** with a movable head and body.
- Eat green leaves to grow your neck; red (rotten) leaves shrink it.
- Leaves fall faster and spawn more frequently as time passes.
- Only the giraffe’s **head** can eat leaves.
- The run ends if a green (good) leaf hits the ground.
- Score = number of good leaves eaten. A timer tracks survival time.

### Controls
- Move left/right: `A`/`D` or `←`/`→`
- Move head up/down: `W`/`S` or `↑`/`↓`
- Restart after game over: `R`
- Quit: `ESC`

---

## 🛠 Requirements
- Python 3.9+ (3.11+ recommended)
- `pygame`

Install dependencies:

```bash
pip install pygame
```

---

## ▶️ Run the Game
From the project root:

```bash
python giraffe_game.py
```

If you have multiple Python versions installed, you may need `python3`:

```bash
python3 giraffe_game.py
```

---

## ⚙️ Mechanics (under the hood)
- Difficulty ramps up over time:
  - Falling speed increases (capped)
  - Giraffe and head movement speed increase (capped)
  - Leaf spawn rate increases (capped)
- Neck growth/shrink:
  - Good leaf: +`NECK_GROW`
  - Rotten leaf: −`NECK_SHRINK`
- Game field is zoomed out to fit a max-height giraffe.

You can tweak constants like speeds, caps, and growth values near the top of `giraffe_game.py`.

---

## 🧪 Troubleshooting
- Module not found: `pygame`
  - Install with `pip install pygame`
  - Or ensure you’re using the right interpreter/virtualenv: `python -m pip install pygame`
- Window doesn’t open on macOS
  - Try running from a Terminal (not inside certain IDE consoles)
  - Ensure Python has screen permissions if prompted

---

## 📂 Project Structure
- `giraffe_game.py` — the game implementation
- `README.md` — this file

---


## 🙌 Credits
Built with ❤️ by:
Seibel Jada,
Bush Cody,
Orehowski Zakhary,
Wiley Adam,
Acheampong Andrew.


