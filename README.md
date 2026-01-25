# 🦒 Giraffe

**Giraffe** is a 2D arcade-style game built with **PyGame**.  
You control a giraffe that grows its neck by eating falling leaves.  
The longer you survive, the faster and harder the game becomes.

---

## 🎮 Gameplay

- The player controls a **giraffe**.
- The giraffe **starts small** and grows its neck by eating falling **good leaves**.
- **Rotten leaves** shrink the giraffe’s neck.
- Leaves fall from the top of the screen at increasing speed.
- The number of falling leaves increases over time.
- The giraffe:
  - Moves **left and right** (body).
  - Moves its **head up and down**.
- Only the **head** can eat leaves.
- A **timer** shows how long you've survived.
- **Game over** occurs when a **good leaf hits the ground**.
- The goal: **survive as long as possible**.

---

## ⚙️ Game Mechanics

- Gradually increasing difficulty:
  - Falling speed increases.
  - Giraffe movement speed increases.
  - Leaf spawn rate increases.
- Neck growth and shrinkage:
  - Good leaves → grow neck.
  - Rotten leaves → shrink neck.
- Fixed limits:
  - Maximum giraffe height.
  - Maximum movement speed.
- The camera is **zoomed out** from the start to accommodate a fully grown giraffe.

---

## 🛠 Tech Stack

- **Python**
- **PyGame**

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+ recommended
- PyGame installed (will be automatically installed by the run script if needed)

### Installation

1. Clone this repository
2. Navigate to the project directory

### Running the Game

You can run the game using the provided run script:

```bash
# On Windows
python run.py

# On Linux/macOS (after making the script executable)
./run.py
```

Or install pygame manually and run the main file directly:

```bash
pip install pygame
python main.py
```

### Controls

- **Left/Right Arrow Keys**: Move the giraffe's body left and right
- **Up/Down Arrow Keys**: Move the giraffe's head up and down
- **ESC**: Quit the game (after game over)
