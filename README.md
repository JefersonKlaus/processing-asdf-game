## processing-asdf-game
### What is this project:
Project developed as an activity at Feevale University in the field of Computer Graphics.

![Game](./docs/demo.png)
![Game](./docs/demo2.png)
![Game](./docs/demo3.png)

### How to play
Letters (`A`, `S`, `D`, `F`) fall down four lanes. Press the matching key while
the letter touches the white action bar to score a point (from the moment the
circle touches the bar until it fully leaves it). Several letters
fall one after the other. The game starts slow; the more points you have, the
faster the letters fall and the closer they get to each other. After 25 points
the letters no longer match their lane.

**Gold letter (from 50 points):** after a random number of letters (between 5
and 10), a surprise gold letter falls **twice as fast** as the others, on its
own, between the normal letters. It must be pressed like any other letter
(one point; missing it ends the game). It can pass a normal letter, so
sometimes there are two letters in the action bar: each key press hits one
letter (the lowest one with that char).

When you press `A`, `S`, `D` or `F` the action bar gives a small and short
vibration and blinks:
- **light yellow**: right press (the letter of that key is in the action bar);
- **light red**: wrong press, the game is over (the red stays during the slow
  motion, so you can see why the game ended).

The game is over when:
- a letter leaves the action bar without being pressed, or
- you press `A`, `S`, `D` or `F` at the wrong moment: the letter of that key
  is not in the action bar (too early, too late, or another letter is there).

Pressing the same letter again while it is still in the action bar is ignored.
Other keys (arrows, space, other letters...) and keys on the start / game over
pages are ignored too.

---

## Project structure
```
processing-asdf-game/
├── pyproject.toml               # project, dependencies, pytest / coverage / Flet settings
├── README.md
├── docs/                        # screenshots used by this README
├── src/
│   ├── main.py                  # entry point: starts the Flet web server
│   ├── assets/                  # Flet assets (background image)
│   └── asdf_hero/
│       ├── config.py            # ALL game settings (sizes, speeds, level, timings)
│       ├── app.py               # Flet app: game loop (input -> update -> render)
│       ├── game/                # game rules, no Flet
│       │   ├── states.py        #   GamePage, LetterStatus, Highlight (enums)
│       │   ├── game.py          #   Game: pages, points, letters, game over
│       │   ├── letter.py        #   Letter: movement and status
│       │   ├── action_bar.py    #   ActionBar: hit area and highlight
│       │   ├── button.py        #   Button: clickable area
│       │   └── level.py         #   speed / distance by points
│       └── ui/                  # Flet views, no game rules
│           ├── theme.py         #   colors, font sizes and texts
│           ├── game_view.py     #   GameView: the whole screen
│           ├── letter_view.py
│           ├── action_bar_view.py
│           ├── background_view.py
│           └── button_view.py
└── tests/                       # same structure as the package
    ├── conftest.py
    ├── game/                    # rules (and the architecture rule)
    ├── ui/                      # views
    ├── test_app.py
    └── test_main.py
```

### How it works
- **Game loop** (`asdf_hero/app.py`): 60 times per second, `GameApp.frame()`
  does the classic game loop: **input** (queued keys / clicks) →
  **update** (`Game.update()`) → **render** (`GameView.render()`). Then
  `page.update()` sends only the changes to the browser (nothing is sent
  when nothing changes).
- **Rules** (`asdf_hero/game`): plain Python, no Flet. `Game` keeps the state
  (page, points, letters, level) and the input methods (`key_pressed`,
  `mouse_pressed`, `mouse_released`).
- **Views** (`asdf_hero/ui`): each view owns Flet controls and `render()`
  copies the state of the game to them (position, colors, visibility, texts).
- Each browser tab gets its own `GameApp`, `Game` and `GameView`. The loop
  pauses while the tab is hidden or disconnected and stops when the session
  is closed.

---

## Setting up and running the game (Flet, in the browser)
Requirements: **Python 3.10+**.

### 1. Create a virtual environment
From inside the `processing-asdf-game` folder:

Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (Git Bash):
```bash
py -3 -m venv .venv
source .venv/Scripts/activate
```

### 2. Install
```bash
pip install -e ".[dev]"
```
This installs the game (`asdf_hero` package), Flet and the test tools
(`pytest`, `pytest-cov`). All the dependencies are in `pyproject.toml`.

### 3. Start the game
```bash
python src/main.py
```
The browser opens at <http://127.0.0.1:8550>. Click **Iniciar ASDF Hero** and
play with the `A`, `S`, `D`, `F` keys. Stop the server with `Ctrl+C`.

| Environment variable | Default | What it does |
| --- | --- | --- |
| `FLET_SERVER_PORT` | `8550` | Port of the web server |
| `FLET_SERVER_IP` | `127.0.0.1` | IP the server listens on (`0.0.0.0` to play from other devices on the network) |

Example: `FLET_SERVER_IP=0.0.0.0 FLET_SERVER_PORT=8080 python src/main.py`

### Tuning the game
All the numbers of the game are in `src/asdf_hero/config.py`, and the colors
and texts are in `src/asdf_hero/ui/theme.py`.

The game level depends on the points. It goes from the initial level (0
points) to the max level (100 points):

| Setting | Constant (`config.py`) | Value | Effect |
| --- | --- | --- | --- |
| Initial speed | `INIT_SPEED` | `3` px per frame (180 px/s) | Speed at the start of a game |
| Max speed | `MAX_SPEED` | `5` px per frame (300 px/s) | Fastest speed |
| Speed step | `SPEED_STEP_BY_POINT` | `0.02` px per point | Bigger = gets fast sooner |
| Initial distance | `INIT_DISTANCE` | `150` px | Space between letters at the start |
| Min distance | `MIN_DISTANCE` | `100` px | Smallest space between letters |
| Distance step | `DISTANCE_STEP_BY_POINT` | `0.5` px per point | Bigger = letters get closer sooner |
| Highlight | `HIGHLIGHT_FRAMES` | `12` frames (0.2 s) | How long the action bar blinks |
| Action bar | `ACTION_BAR_TOP` / `ACTION_BAR_HEIGHT` | `600` / `80` px | A letter can be pressed while its circle touches the bar (hit area of 142 px) |
| Slow motion | `SLOW_MOTION_STEPS` / `SLOW_MOTION_STEP_FRAMES` | `13` / `12` | Game over transition (~2.8 s) |
| Gold letter | `GOLD_FROM_POINTS` | `50` | Points to start the gold letters |
| Gold frequency | `GOLD_EVERY_MIN_LETTERS` / `GOLD_EVERY_MAX_LETTERS` | `5` / `10` | Random number of normal letters before each gold letter |
| Gold speed | `GOLD_SPEED_FACTOR` | `2.0` | Gold speed = game speed x this (480 px/s at 50 points, 600 px/s at the max level) |

The vibration of the action bar is `ACTION_BAR_SHAKE` in `ui/theme.py`: the
horizontal offset (pixels) of the bar on each frame after a key press
(`3, -3, 3, -3, 2, -2, 1, -1, 0`: 0.15 s). The gold colors are `GOLD_COLOR`
and `GOLD_GLOW_COLOR`.

The normal letters move at the game speed, so they never overlap. The gold
letter avoids the lanes of the letters that are still coming, so it does not
fall on top of them.
`FPS` (60) also changes the speed, because the speed is in pixels per frame.

With these values, a perfect player sees:

| Time | Points | Speed | New letter every |
| --- | --- | --- | --- |
| 0 s | 0 | 180 px/s | 1.2 s |
| 30 s | ~26 | 211 px/s | 0.9 s |
| 60 s | ~61 | 253 px/s | 0.7 s |
| 90 s | ~110 (max level) | 300 px/s | 0.5 s |

The max level is kept moderate on purpose, so new challenges can be added
later. A new game always starts at the initial level. There is never more than
one normal letter inside the action bar at the same time. `TestLevelDesign` in
`tests/game/test_level.py` checks these rules, so update it if the design
changes.

---

## Tests
The tests run with [pytest](https://docs.pytest.org/) and
[pytest-cov](https://pytest-cov.readthedocs.io/) (installed by
`pip install -e ".[dev]"`). No browser or Flet server is needed.

```bash
pytest
```

The settings are in `pyproject.toml`: coverage runs automatically and the
run **fails if total coverage is below 90%**. Example output:

```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src/asdf_hero/__init__.py                 1      0   100%
src/asdf_hero/app.py                     87      0   100%
src/asdf_hero/config.py                  22      0   100%
...
src/asdf_hero/ui/theme.py                23      0   100%
src/main.py                               6      0   100%
-------------------------------------------------------------------
TOTAL                                   497      0   100%
Required test coverage of 90.0% reached. Total coverage: 100.00%
============================= 299 passed in 4.97s ==============================
```

### Useful commands
| Command | What it does |
| --- | --- |
| `pytest` | Run all tests with coverage (fails below 90%) |
| `pytest tests/game` | Run only the game rules tests |
| `pytest -k highlight` | Run the tests whose name matches an expression |
| `pytest -v` | Show the name of each test |
| `pytest --cov-report=html` | Also build an HTML report in `htmlcov/index.html` |
| `pytest --no-cov` | Run the tests without coverage (faster) |

### How the tests work
| Folder / file | What it covers |
| --- | --- |
| `tests/game/` | Rules: game, letters, action bar (highlight), button, level design, states |
| `tests/game/test_gold.py` | Gold letter: when it comes, where it starts, speed, lanes, two letters in the bar |
| `tests/game/test_architecture.py` | The rules do not import Flet or the views |
| `tests/ui/` | Views: what each page shows, letters (gold), action bar colors and vibration, button, theme |
| `tests/test_app.py` | Page setup, input queue, frame order, game loop (frame rate, errors, pause / close) |
| `tests/test_main.py` | `python src/main.py` (server settings, assets) |

- **Rules without mocks:** `Game` receives the random generator (`rng`), so
  the tests choose the lanes with `scripted_rng([...])` and put letters where
  they want with the `place_letter` fixture.
- **Views:** the Flet controls are plain Python objects, so the tests check
  their properties (`visible`, `top`, `bgcolor`, `content.value`...).
- **Game loop timing** (frame rate, slow frames) is tested with a `FakeClock`
  that only moves when the loop sleeps or a frame takes time. Real clocks are
  different on each OS (on Windows the asyncio clock moves in steps of
  ~15.6 ms), so these tests give the same result on Windows, Linux and macOS.
- Flet controls with the same values are equal (`==`). Check if a control is
  present with `is` (identity), not with `in` / `==`. Letter controls have
  a unique `key` for this reason.
