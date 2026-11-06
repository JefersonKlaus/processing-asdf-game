## processing-asdf-game
### What is this project:
Project developed as an activity at Feevale University in the field of Computer Graphics.

![Game](./docs/demo.png)
![Game](./docs/demo2.png)
![Game](./docs/demo3.png)

### How to play
The start page (home screen) shows the title **ASDF HERO** and the **5 best
results**. At the bottom of the screen (easy to reach with the thumb) there
are two big colored buttons: the **hand** button (purple) and, below it, the
**Iniciar ASDF Hero** button (green) that starts a game. The game over page
has the same buttons (the green one is **Falhar novamente**). Choose the hand
with the purple button:

| Hand | Keys (one for each lane, from left to right) |
| --- | --- |
| Left (default) | `A` `S` `D` `F` |
| Right | `J` `K` `L` `Ç` (on US keyboards the `Ç` key is `;`, it works too) |

The examples below use the left hand keys.

**Phone / tablet:** below the action bar there are 4 touch buttons, one for
each lane, with the color of the lane and its key. A touch on a button works
like its key, and a key pressed on the keyboard shows the press effect on its
button (like the action bar). The letters hide behind the buttons. On a
phone the game **fills the whole screen** (no black margins): it gets as wide
as the screen (the lanes get wider) and it is scaled to the height of the
screen. On a computer the game keeps its size (282 x 800) and is only made
smaller when the window is smaller.

Letters (`A`, `S`, `D`, `F`) fall down four lanes. Press the matching key while
the letter touches the white action bar to score a point (from the moment the
circle touches the bar until it fully leaves it). Several letters
fall one after the other. The game starts slow and gets harder in two steps:
1. **faster letters**: the speed grows with each point until the max speed
   (240 px/s) at **51 points**;
2. **more letters**: then the speed stays the same and the letters get closer
   (1 px for each point) until there is **always one letter in the action
   bar** (at 121 points), plus the special letters (gold).

After 25 points the letters no longer match their lane. Every letter is a
circle in the color of its lane (**blue, red, purple, green**: no yellow, so
a normal letter never looks like the gold one) with a small **glow** around
it; the special letters (gold, silver) have a bigger glow, so they stand out.

**Gold letter (from 40 points):** after a random number of letters (between 5
and 10), a surprise gold letter falls **1.5 times as fast** as the others, on its
own, between the normal letters. It must be pressed like any other letter
(missing it ends the game) and gives `GOLD_POINTS` points (1 by default). It can pass a normal letter, so
sometimes there are two letters in the action bar. One key press hits **all
the letters of that key** in the action bar: when the gold letter and the
normal letter have the same char, **one press hits both** and gives the points
of both (1 + `GOLD_POINTS`).

**Silver letter (from 50 points):** after a random number of letters (between
5 and 10), two letters change their chars, with an early warning:
1. the chosen letter is **already silver when it appears** at the top of the
   screen, and the next letter turns **silver** as soon as it exists too (so
   you know early that they will change);
2. when the first one is **one letter (62 px) from the action bar**, the two
   letters swap their chars. Example: `A` (close to the bar) and `F` (the next
   one) -> the first letter shows `F` and the next shows `A`.

You must press the new chars. Only the chars change, the letters stay in their
lanes. The gold letter never turns silver (it does not go through this).

When you press `A`, `S`, `D` or `F` the action bar gets 2 px bigger on each
side for a moment and blinks:
- **light yellow**: right press (the letter of that key is in the action bar);
- **light red**: wrong press, the game is over (the red stays during the slow
  motion, so you can see why the game ended).

The game is over when:
- a letter leaves the action bar without being pressed, or
- you press `A`, `S`, `D` or `F` at the wrong moment: the letter of that key
  is not in the action bar (too early, too late, or another letter is there).

The game over page shows your points and, below them, the **5 best results**
(position, name, date, time and points).

**Congratulations page (new best result):** when your points enter the 5 best
results, the game shows the **NADA MAL! / Novo recorde!** page (the title in
bold, like **GAME OVER** and **ASDF HERO**; **NOT BAD! /
New record!** in English) instead of the
game over page, with your points and a **Seu nome** field (on a phone the
keyboard opens). Then:
- **Salvar** (or Enter) saves the result with the typed name (up to 10
  characters; an empty name is anonymous);
- **Salvar como anônimo** saves the result without a name: the best results
  show **Anônimo** (**Anonymous** in English).

After saving, the game over page shows the best results with your result in
**bold**. A result that does not enter the 5 best results goes straight to
the game over page and is not saved. A game with **0 points** never enters the
best results (even when there are free places). To enter a full list you need
**more** points than the 5th result (the same points keep the oldest result).

**Colors (standard):** the buttons and the game over always use the colors of
the lanes, with the same meaning:

| Color | Used for |
| --- | --- |
| **Green** | Start a game (**Iniciar ASDF Hero** / **Falhar novamente**) and **Salvar** |
| **Purple** | Change the hand |
| **Blue** | **Salvar como anônimo** |
| **Red** | The **GAME OVER** text (bold) |

The buttons have the design of the touch buttons (the letter buttons): corners
a little rounded (`BUTTON_RADIUS` = `TOUCH_BUTTON_RADIUS`, 10 px) and bold
white text. They are 240 x 52 px with
12 px between them: bigger than the 48 dp touch target of the mobile
guidelines (Material Design; Apple: 44 pt). A pressed button gets darker.

The best results are saved in a **SQLite database**, so they are kept when the
game or the server is closed (see [Best results database](#best-results-database)).
On the web server they are shared by all the browser tabs.

**Language:** the game uses the language of the phone (or of the browser):
**Portuguese** when it is Portuguese (`pt`, `pt-BR`, `pt-PT`), **English**
when it is English, and English for the other languages. The texts are in
`src/asdf_hero/ui/texts.py` (see [Languages](#languages)).

Pressing the same letter again while it is still in the action bar is ignored.
Other keys (arrows, space, other letters...) and keys on the start / game over
pages are ignored too.

---

## Project structure
```
processing-asdf-game/
├── pyproject.toml               # project, dependencies, pytest / coverage / Flet / ruff settings
├── requirements-dev.txt         # all the packages to run, test, lint and build
├── README.md
├── .github/
│   └── workflows/
│       └── ci.yml               # CI: ruff check + pytest on every commit (see "Continuous integration")
├── docs/                        # screenshots used by this README
├── src/
│   ├── main.py                  # entry point: starts the Flet web server
│   ├── assets/                  # Flet assets (background image)
│   └── asdf_hero/
│       ├── config.py            # ALL game settings (sizes, speeds, level, timings)
│       ├── app.py               # Flet app: game loop (input -> update -> render)
│       ├── storage.py           # SqliteResultStore: the best results in a SQLite file
│       ├── logs.py              # setup_logging(): logs on the console and in a file
│       ├── performance.py       # PerformanceMonitor: frame times, slow game reports
│       ├── game/                # game rules, no Flet
│       │   ├── challenges/      #   surprises after some points
│       │   │   ├── base.py      #     Challenge (hooks) + ChallengeSchedule (5-10 letters)
│       │   │   ├── gold.py      #     gold letter (faster)
│       │   │   └── silver.py    #     silver letters: silver from the start, swap near the bar
│       │   ├── states.py        #   GamePage, Hand, LetterStatus, Highlight (enums)
│       │   ├── game.py          #   Game: pages, points, letters, game over
│       │   ├── letter.py        #   Letter: movement and status
│       │   ├── action_bar.py    #   ActionBar: hit area and highlight
│       │   ├── button.py        #   Button: clickable area
│       │   ├── scoreboard.py    #   Scoreboard: the 5 best results, ResultStore (interface)
│       │   └── level.py         #   speed / distance by points
│       └── ui/                  # Flet views, no game rules
│           ├── theme.py         #   colors, font sizes and positions
│           ├── texts.py         #   the texts in Portuguese and English
│           ├── game_view.py     #   GameView: the whole screen
│           ├── letter_view.py
│           ├── action_bar_view.py
│           ├── background_view.py
│           ├── button_view.py
│           ├── scoreboard_view.py   #   the 5 best results
│           ├── congratulations_view.py   #   new best result: name field, save buttons
│           ├── touch_buttons_view.py   #   the 4 touch buttons (phone)
│           └── press_effect.py  #   press effect (action bar and touch buttons)
└── tests/                       # one responsibility per file (see "Tests")
    ├── conftest.py              # shared fixtures
    ├── helpers.py               # shared helpers (perfect player, frames...)
    ├── game/                    # rules
    ├── ui/                      # views
    └── app/                     # Flet app and entry point
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
  On the congratulations page each change of the name field is queued like a
  key and applied by the loop (`Game.type_name`); the save buttons are game
  buttons (`Game.save_name` / `Game.save_anonymous`).
- **Screen** (`GameApp`): on a phone (`page.platform` is Android / iOS) the
  game width follows the shape of the screen (`game_width()`, between
  `WIDTH` and `MAX_WIDTH`) and the game is scaled to fill it; the lanes,
  letters and touch buttons use `Game.lane_lines` / `Game.lane_centers`.
- **Storage** (`asdf_hero/storage.py`): `Scoreboard` only knows the
  `ResultStore` interface (`load()` / `save()`); the app gives it a
  `SqliteResultStore`, the tests a `MemoryResultStore` (the default).
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
pip install -r requirements-dev.txt
```
This installs everything to **run**, **test**, **lint** and **build** the game:

| Package | For |
| --- | --- |
| `flet` | The game (and the mobile app) |
| `flet-web` (`flet[web]`) | The web server: `python src/main.py` |
| `flet-cli` (`flet[cli]`) | The `flet` command: `flet build`, `flet debug` |
| `pytest`, `pytest-cov` | The tests and the coverage |
| `ruff` | The code style and common bugs: `ruff check .` (see [Lint (ruff)](#lint-ruff)) |

The mobile build also needs tools that are not Python packages (Flutter,
Java, Android SDK / Xcode): see [Build a mobile app](#build-a-mobile-app-android--ios).

The same packages are in `pyproject.toml`, as extras, if you prefer to install
the project as a package:

| Install | What you get |
| --- | --- |
| `pip install -e ".[dev,build]"` | The same as `requirements-dev.txt` |
| `pip install -e ".[dev]"` | Play in the browser + run the tests |
| `pip install -e ".[web]"` | Only play in the browser |
| `pip install -e ".[build]"` | The `flet` command, to build the mobile app |

`tests/test_requirements.py` checks that `requirements-dev.txt` and
`pyproject.toml` have the same packages: change both when you add a package.

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

### Play on a phone
1. Start the server so other devices on the network can open it:
   `FLET_SERVER_IP=0.0.0.0 python src/main.py`
   (Windows PowerShell: `$env:FLET_SERVER_IP="0.0.0.0"; python src/main.py`).
2. Find the IP of the computer (`ipconfig` on Windows, `ip addr` on Linux,
   `ipconfig getifaddr en0` on macOS).
3. On the phone (same Wi-Fi), open `http://<computer IP>:8550` and play with
   the touch buttons. The firewall of the computer must allow the port 8550.

### Tuning the game
All the numbers of the game are in `src/asdf_hero/config.py`, the colors,
font sizes and positions are in `src/asdf_hero/ui/theme.py`, and the texts
are in `src/asdf_hero/ui/texts.py`.

The game level depends on the points. It goes from the initial level (0
points) to the max level in two steps: first the letters get faster (until
the **max speed at 51 points**), then there are more letters (they get
closer until the min distance at 121 points, where the next letter touches
the action bar when the last one leaves it: always one letter in the bar):

| Setting | Constant (`config.py`) | Value | Effect |
| --- | --- | --- | --- |
| Initial speed | `INIT_SPEED` | `3` px per frame (180 px/s) | Speed at the start of a game |
| Max speed | `MAX_SPEED` | `4` px per frame (240 px/s) | Fastest speed |
| Max speed points | `MAX_SPEED_FROM_POINTS` | `51` | Points to reach the max speed; the speed grows evenly from 0 points until here (~0.02 px per frame for each point). The letters only get closer after it |
| Initial distance | `INIT_DISTANCE` | `150` px | Space between letters until the max speed |
| Min distance | `MIN_DISTANCE` | `ACTION_BAR_HEIGHT` (80 px) | Smallest space between letters: center to center = 142 px = the hit area, so there is always one letter in the action bar |
| Distance step | `DISTANCE_STEP_BY_POINT` | `1` px per point | After the max speed: bigger = more letters sooner (min distance at 121 points) |
| Highlight | `HIGHLIGHT_FRAMES` | `12` frames (0.2 s) | How long the action bar blinks |
| Action bar | `ACTION_BAR_TOP` / `ACTION_BAR_HEIGHT` | `600` / `80` px | A letter can be pressed while its circle touches the bar (hit area of 142 px) |
| Slow motion | `SLOW_MOTION_STEPS` / `SLOW_MOTION_STEP_FRAMES` | `13` / `12` | Game over transition (~2.8 s) |
| Gold letter | `GOLD_FROM_POINTS` | `40` | Points to start the gold letters |
| Gold frequency | `GOLD_EVERY_MIN_LETTERS` / `GOLD_EVERY_MAX_LETTERS` | `5` / `10` | Random number of normal letters before each gold letter |
| Gold speed | `GOLD_SPEED_FACTOR` | `1.5` | Gold speed = game speed x this (341 px/s at 40 points, 360 px/s at the max speed) |
| Gold points | `GOLD_POINTS` | `1` | Points for a gold letter (more points also make the game faster) |
| Silver letter | `SILVER_FROM_POINTS` | `50` | Points to start the silver letters |
| Silver frequency | `SILVER_EVERY_MIN_LETTERS` / `SILVER_EVERY_MAX_LETTERS` | `5` / `10` | Random number of normal letters before each silver challenge |
| Silver swap | `SILVER_SWAP_DISTANCE` | `LETTER_SIZE` (62 px) | The letters are silver from the start and swap when the circle is this far from the action bar (at the max speed: at least 1 s of warning, then 0.85 s until the letter leaves the bar) |
| Silver points | `SILVER_POINTS` | `1` | Points for a silver letter |
| Best results | `SCOREBOARD_SIZE` | `5` | Number of best results on the start and game over pages (and in the database) |
| Min points | `MIN_BEST_RESULT_POINTS` | `1` | A game needs at least these points to enter the best results (0 points: never) |
| Buttons | `BUTTON_WIDTH` / `BUTTON_HEIGHT` / `BUTTON_GAP` | `240` / `52` / `12` px | Size of the buttons and space between them (touch targets of at least 48 px) |
| Buttons position | `BUTTONS_BOTTOM_MARGIN` | `40` px | Space below the start button (the buttons are at the bottom of the screen) |
| Name | `NAME_MAX_LENGTH` | `10` | Max length of the name (an empty name is anonymous) |
| Language | `LANGUAGE` / `DEFAULT_LANGUAGE` | `None` / `"en"` | `None`: the language of the device; `"pt"` / `"en"`: always this one. `DEFAULT_LANGUAGE`: for devices in other languages |
| Congratulations buttons | `CONGRATULATIONS_BUTTONS_TOP` | `350` px | y of **Salvar** (**Salvar como anônimo** is below it) |
| Phone width | `MAX_WIDTH` | `600` px | Max width of the game on phones / tablets (the game is never narrower than `WIDTH`) |
| Database | `DATABASE_FILE` | `asdf_hero.db` | SQLite file of the best results |
| Logs | `LOG_LEVEL` / `LOG_FILE` / `LOG_FILE_MAX_BYTES` | `INFO` / `asdf_hero.log` / 1 MB | See [Logs](#logs-why-the-game-gets-slow) |
| Performance logs | `PERFORMANCE_REPORT_SECONDS` / `MIN_GOOD_FPS` / `FREEZE_MS` / `PAUSE_SECONDS` / `SLOW_STORAGE_MS` | `10` / `54` / `100` / `1.0` / `50` | One report every 10 s; a warning below 54 fps, with a 100 ms freeze, or a database slower than 50 ms |
| Touch buttons | `TOUCH_BUTTONS_TOP` / `TOUCH_BUTTON_HEIGHT` / `TOUCH_BUTTON_MARGIN` | `690` / `68` / `2` px | Position and size of the touch buttons (60 x 68 px) |
| Keys | `LEFT_HAND_KEYS` / `RIGHT_HAND_KEYS` | `ASDF` / `JKLÇ` | Keys of each hand (one for each lane) |
| Key names | `KEY_ALIASES` | `{";": "Ç"}` | Other names of the same key |

In `ui/theme.py`: the press effect of the action bar and of the touch buttons
is `PRESS_EFFECT_GROW` (2 px bigger on each side) for `PRESS_EFFECT_FRAMES`
frames (8 = 0.13 s),
the normal letters have a small glow (`LANE_GLOW_BLUR`, `LANE_GLOW_SPREAD`,
`LANE_GLOW_ALPHA`) in the color of their lane (`LANE_GLOW_COLORS`), the
special letters a big one (`GLOW_BLUR`, `GLOW_SPREAD`), the colors of the
challenges are
`GOLD_COLOR` / `GOLD_GLOW_COLOR` and `SILVER_COLOR` / `SILVER_GLOW_COLOR`; the
best results use
`SCOREBOARD_COLUMNS` (width of position, name, date, time and points), the
buttons use `START_BUTTON_COLOR` (green lane) / `HAND_BUTTON_COLOR` (purple
lane) / `ANONYMOUS_BUTTON_COLOR` (blue lane), `BUTTON_RADIUS` (the radius of
the touch buttons), `BUTTON_FONT_SIZE` /
`HAND_BUTTON_FONT_SIZE` and `darker()` (pressed), and the congratulations page uses the `CONGRATULATIONS_*` sizes and positions and
`NAME_FIELD_*` (name field). The touch buttons use
`TOUCH_BUTTON_FONT_SIZE`, `TOUCH_BUTTON_RADIUS` and
`TOUCH_BUTTON_PRESSED_OPACITY` (the button is lighter during the press
effect).

To add a new challenge: create a `Challenge` subclass in
`game/challenges/` (with a `ChallengeSchedule`), and add it to
`Game.challenges`.

The normal letters move at the game speed, so they never overlap. The gold
letter avoids the lanes of the letters that are still coming, so it does not
fall on top of them.
`FPS` (60) also changes the speed, because the speed is in pixels per frame.

With these values, a perfect player sees:

| Time | Points | Speed | New letter every |
| --- | --- | --- | --- |
| 0 s | 0 | 180 px/s | 1.2 s |
| 30 s | ~25 | 209 px/s | 1.0 s |
| 60 s | ~59 (max speed) | 240 px/s | 0.85 s |
| 90 s | ~103 | 240 px/s | 0.67 s |
| 120 s | ~159 (max level) | 240 px/s | 0.59 s |

The max speed is kept moderate on purpose: the game gets harder with more
letters, not with faster letters. A new game always starts at the initial
level. At the max level there is always exactly one normal letter in the
action bar (only the gold letter can be there too), and a new letter starts
exactly `distance` after the last one.
`tests/game/test_design_rules.py` and `tests/game/test_level.py` check these
rules, so update them if the design changes.

### Languages
All the texts of the screen are in `src/asdf_hero/ui/texts.py`: one `Texts`
for each language (`PORTUGUESE`, `ENGLISH`), with the buttons, the pages, the
name of an anonymous result and the date format (`dd/mm/yyyy` in Portuguese,
`mm/dd/yyyy` in English).

When a page opens, `main()` asks Flet for the languages of the device
(`page.get_device_info()`: the phone in the app, the browser on the web) and
uses the first one (`texts_for()`). If the device does not answer in 3 seconds
the game starts in `DEFAULT_LANGUAGE`. To always use one language, set
`LANGUAGE = "pt"` (or `"en"`) in `config.py`. The language is chosen when the
game opens: after changing the language of the phone, close and open the game.

To add a language: create a `Texts` in `texts.py` (copy `ENGLISH` and
translate it) and add it to `LANGUAGES`. `tests/ui/test_texts.py` checks that
every text is filled and that the `{}` are the same in each language.

### Logs (why the game gets slow)
The game writes logs to the **console** and to the file **`asdf_hero.log`**
in the data folder (next to the database):

| How the game runs | Where to see the logs |
| --- | --- |
| `python src/main.py` (web server) | The terminal, and `~/.asdf_hero/asdf_hero.log` (Windows: `%USERPROFILE%\.asdf_hero\asdf_hero.log`) |
| `flet run` | The terminal, and `.flet/storage/data/asdf_hero.log` in the project |
| Android app | With a USB cable: `flet debug android` shows the output of the app in the terminal. In a debug build the file can be read with `adb shell run-as com.example.asdf_hero find . -name asdf_hero.log` and then `adb shell run-as com.example.asdf_hero cat <that path>` |

The first line of the log shows the level and the path of the file. The file
has at most 1 MB (`LOG_FILE_MAX_BYTES`); then it starts again and the old one
is kept as `asdf_hero.log.1`, so the logs never fill the phone.

**Level:** `LOG_LEVEL = "INFO"` in `config.py` (change it to `"DEBUG"` for
more details, also in the app). On the computer the environment variable wins:
`ASDF_HERO_LOG_LEVEL=DEBUG python src/main.py` (PowerShell:
`$env:ASDF_HERO_LOG_LEVEL="DEBUG"; python src/main.py`).

**What is logged:**

| Level | Log | When |
| --- | --- | --- |
| INFO | `Language: pt (...)` | A page opens: the language of the device |
| INFO | `Game started (N running): platform, page size, game size, scale, FPS` | A game loop starts (N: browser tabs playing on the web server) |
| INFO | `Page: RUNNING (0 points)` | The page of the game changes (start, running, congratulations, game over) |
| INFO | `Performance: 60.0 fps in 10.0 s \| frame avg ... \| slowest ... \| GC ... \| CPU ...% \| N letters` | Every 10 s of game (`PERFORMANCE_REPORT_SECONDS`) |
| WARNING | `Slow game: ...` (the same line) | The 10 s had less than 54 fps (`MIN_GOOD_FPS`) or a frame longer than 100 ms (`FREEZE_MS`) |
| INFO | `Page connected` / `disconnected` / `closed`, `Game stopped (N running)` | The tab / app connects, pauses or closes |
| WARNING | `Saved 5 best results in 80.0 ms` | The database took more than 50 ms (`SLOW_STORAGE_MS`); DEBUG when it is fast |
| DEBUG | `Page resized to ...`, `The game was paused for 12.0 s` | The page changes size (the keyboard of the phone), the game comes back from a pause |
| ERROR | `Error in the game frame` (with the traceback) | A bug in a frame (the game goes on) |

Example:
```
2026-03-05 14:30:10,124 INFO asdf_hero.performance: Performance: 60.0 fps in 10.0 s | frame avg 2.1 ms (input 0.0, update 0.3, render 0.9, send 0.9, late 1.0 ms) | slowest 9.8 ms (input 0.0, update 0.4, render 1.2, send 8.2, late 0.0 ms) | GC 3 collections, 0.9 ms, longest 0.4 ms | CPU 12% | 6 letters
2026-03-05 14:30:20,131 WARNING asdf_hero.performance: Slow game: 41.3 fps in 10.0 s | frame avg 3.0 ms (...) | slowest 180.4 ms (input 0.0, update 0.3, render 1.0, send 1.1, late 178.0 ms) | GC 9 collections, 160.2 ms, longest 150.3 ms | CPU 95% | 7 letters
```

**How to read a `Slow game` line** (look at the *slowest* frame, and at the
average). A frame has 16.7 ms at 60 FPS:

| The biggest part | What it means | What to try |
| --- | --- | --- |
| `update` | The game rules are slow | Fewer letters / challenges on the screen |
| `render` | The views are slow (Flet controls) | Fewer changes in `render()`; fewer glows / shadows |
| `send` | `page.update()`: Flet sends the changes to the screen (web: over the network) | A slow network (web server), or too many changes in each frame |
| `late` | The frame started late: something else kept Python busy | `GC` big: the garbage collector; `N running` big: many tabs on one server; `CPU` near 100%: the device is too slow or busy |
| `GC ... longest` | The garbage collector paused the game | Fewer objects created in each frame |

If all the parts are small but the fps is low, the phone / browser itself is
slow to draw (compare with `CPU`).

### Best results database
The best results are saved with `sqlite3` (part of Python: nothing to
install, and it works inside the Android / iOS app). The file is
`asdf_hero.db`, in:

| How the game runs | Folder of the database |
| --- | --- |
| Android / iOS app (`flet build`) | The private data folder of the app (`FLET_APP_STORAGE_DATA`, set by Flet). It is kept when the app is updated and deleted when the app is uninstalled (or with *Clear data* in the Android settings) |
| `flet run` | `.flet/storage/data/` in the project (git-ignored by Flet) |
| `python src/main.py` (web server) | `~/.asdf_hero/` (Windows: `%USERPROFILE%\.asdf_hero\`) |

The table `results` (`name`, `points`, `played_at`) has only the 5 best
results: after each new best result the scoreboard saves all of them at once.
To reset the best results, delete the file (or uninstall the app). If the
database cannot be read or written (disk full, no permission), the error is
logged and the game goes on with the results in memory.

---

## Build a mobile app (Android / iOS)
The same code can be built as an app that is installed on the phone. Inside
the app Python runs on the phone: no server, no network. The game uses the
touch buttons and fits the screen. Flet builds the app with
[`flet build`](https://flet.dev/docs/publish/android) (Flutter).

The project is already configured for Android in `pyproject.toml`:

| Setting | Value | What it does |
| --- | --- | --- |
| `[project] dependencies` | `flet==1.0.5` | The only package that goes into the app (the web server and the test tools stay out, so the app is small) |
| `[project] version` | `1.0.0` | Version shown on the phone |
| `[tool.flet] product` | `ASDF Hero` | Name of the app on the phone |
| `[tool.flet] org` | `com.example` | Android package: `com.example.asdf_hero` |
| `[tool.flet] build_number` | `1` | Internal version (Android `versionCode`): raise it for every new release |
| `[tool.flet.app] path` / `module` | `src` / `main` | Only `src/` goes into the app; the entry point is `src/main.py` |
| `[tool.flet.android] split_per_abi` | `false` | One APK that works on every phone (and on the emulator) |
| `[tool.flet.android.gradle_properties]` | `-Xmx4G ...` | Memory of the Android build: the Flet default (8 GB) fails on computers with 8 GB of RAM or less |

`src/main.py` does not change for the app: inside the app Flet ignores the web
server settings (`view`, host, port) and shows the game in the app window.

### What is needed
| To build | Computer | Tools |
| --- | --- | --- |
| Android (`apk`, `aab`) | Windows 10/11, macOS or Linux (64-bit), 8 GB of RAM, **~15 GB of free disk** | Python 3.10+, Git, internet. Flutter SDK (3.44.8), Java JDK 17 and Android SDK are installed by `flet build` on the first build |
| iOS (`ipa`, `ios-simulator`) | macOS only | Xcode (from the App Store); an Apple Developer account to install on a real iPhone |

### Build the Android app, step by step
Run every command from the project folder (`processing-asdf-game`, where
`pyproject.toml` is). Each step says how to check that it worked; if a step
fails, see [When a step fails](#when-a-step-fails).

**Step 1. Prepare the computer (once)**
- Install **Git** (`git --version` must work): Flutter needs it.
- **Windows only:** turn on the **Developer Mode** (Flutter needs it to
  create symbolic links): run `start ms-settings:developers` and turn on
  *Developer Mode*.
- **Windows only:** put the project in a short folder **without spaces or
  accents**, for example `C:\dev\processing-asdf-game` (Gradle and Flutter
  fail with long paths and with names like `C:\Users\João Silva\Área de Trabalho\...`).
- Have ~15 GB free on the disk of your user folder (Flutter, JDK, Android SDK
  and the Gradle cache go there).

**Step 2. Install the project in a virtual environment**
Follow [Setting up and running the game](#setting-up-and-running-the-game-flet-in-the-browser)
(steps 1 and 2). Check:
```bash
flet --version      # must show 1.0.5 (the same as flet in pyproject.toml)
pytest --no-cov -q  # all the tests pass
```

**Step 3. Check the game in the browser**
```bash
python src/main.py
```
If the game works in the browser, the code is fine: any later error is in
the build tools, not in the game.

**Step 4. Set the app identity (once)**
In `pyproject.toml`: change `org` to your own reverse domain (only needed to
publish: `com.example` is refused by the Play Store), `product` (name on the
phone) and `version`. Optional: an app icon in `src/assets/icon.png` (square
PNG, 1024 x 1024); without it, the Flet icon is used.

**Step 5. Build the APK**
```bash
flet build apk --yes -v
```
- `--yes` answers yes to the questions "install the Flutter SDK?" and
  "install the Android SDK?".
- `-v` shows what each step does (use `-vv` to see everything).
- The **first build** downloads the Flutter SDK, JDK 17, the Android SDK and
  NDK, Gradle and the Python for Android (a few GB): it can take **20 to 40
  minutes**. The next builds take a few minutes.

The build is done when the last message is a green box like
`Successfully built your .apk for Android! ... build/apk`.

To keep the whole log in a file (useful when something fails):

```bash
# Linux / macOS / Git Bash
flet build apk --yes -vv --no-rich-output 2>&1 | tee build.log
```
```powershell
# Windows PowerShell
flet build apk --yes -vv --no-rich-output 2>&1 | Tee-Object -FilePath build.log
```

**Step 6. Find the APK**
The `.apk` file is in `build/apk/` (for example `build/apk/app-release.apk`).
It works on every Android phone (arm64, arm 32 bits and the x86_64 emulator).
For a smaller APK only for modern phones: `flet build apk --yes --arch arm64-v8a`.

**Step 7. Install the APK on the phone**
- Copy the `.apk` file to the phone (cable, Google Drive, e-mail...) and open
  it. Allow "install unknown apps" for the app that opens it.
- Or with a USB cable (turn on *Developer options* > *USB debugging* on the
  phone):
  ```bash
  adb install -r build/apk/app-release.apk
  ```
  `adb` is in the Android SDK: `~/Android/sdk/platform-tools/adb`
  (Windows: `%USERPROFILE%\Android\sdk\platform-tools\adb.exe`).

**Step 8. Play**
Open **ASDF Hero** on the phone, choose the hand and play with the touch
buttons.

**For the Google Play Store** build an `.aab` instead of an `.apk`
(`flet build aab --yes`, result in `build/aab/`). It must be signed with your
key: see the `--android-signing-key-store`, `--android-signing-key-alias` and
`--android-signing-key-store-password` options and the
[Flet Android guide](https://flet.dev/docs/publish/android#signing-an-android-bundle).

### When a step fails
When the build fails, `flet build` runs `flutter doctor` and the **end** of
the output looks like this:

```
           ! Doctor found issues in 3 categories.

Error building Flet app - see the log of failed command above.
```

This message **is not the error**. It only says that `flutter doctor` found
tools that are missing on the computer, and most of them are **not needed**
for Android. Do this:

**1. Find the real error, above the doctor.** Scroll up to the first lines in
red before `Running Flutter doctor...` (or search `build.log` for `FAILURE:`,
`Error`, `Exception`, `What went wrong`). If there is not enough detail, run
the build again with `-vv` and save the log (see step 5). To hide the doctor
part, add `--skip-flutter-doctor`.

**2. Read the doctor list.** Each line starts with `[✓]` (ok), `[!]`
(warning) or `[✗]` (missing). For an Android build only these lines matter:

| Doctor line | Needed for Android? | What to do |
| --- | --- | --- |
| `Flutter` | Yes | See *Flutter SDK* in the table below |
| `Android toolchain` | **Yes** | See *Android SDK* and *licenses* in the table below |
| `Network resources` | Yes (first build) | See *download errors* in the table below |
| `Chrome - develop for the web` | No | Ignore |
| `Visual Studio - develop Windows apps` | No | Ignore |
| `Linux toolchain - develop for Linux desktop` | No | Ignore |
| `Xcode` / `CocoaPods` | No (only iOS) | Ignore |
| `Android Studio (not installed)` | No | Ignore: `flet build` installs the SDK without Android Studio |
| `Connected device` | No (only for `flet debug`) | Ignore |

So "issues in 3 categories" is often just `Chrome`, `Visual Studio` / `Linux
toolchain` and `Android Studio`: the real error is above.
To run the doctor by yourself (with all the details):

```bash
~/flutter/3.44.8/bin/flutter doctor -v                 # Linux / macOS
%USERPROFILE%\flutter\3.44.8\bin\flutter doctor -v     # Windows (cmd)
```

**3. Find the error in this table and fix it.** Then run the same build
command again (the next build continues from where it stopped).

Where the tools are (in the table, `flutter` means the Flutter installed by
Flet):

| Tool | Linux / macOS | Windows |
| --- | --- | --- |
| Flutter | `~/flutter/3.44.8/bin/flutter` | `%USERPROFILE%\flutter\3.44.8\bin\flutter.bat` |
| Android SDK (*SDK folder*) | `~/Android/sdk` (`~/Android/Sdk` or `~/Library/Android/sdk` if Android Studio installed it) | `%USERPROFILE%\Android\sdk` (`%LOCALAPPDATA%\Android\Sdk` if Android Studio installed it) |
| JDK 17 | `~/java/17.0.13+11` | `%USERPROFILE%\java\17.0.13+11` |
| Gradle cache | `~/.gradle` | `%USERPROFILE%\.gradle` |

With `-v` the log shows the SDK folder used (`Android SDK installation found at ...`).

| Step | Error in the log | Fix |
| --- | --- | --- |
| 2 | `flet: command not found` / `'flet' is not recognized` | Activate the virtual environment (`source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`) and run `pip install -r requirements-dev.txt` |
| 5 | `Flutter SDK installation is required. Re-run with --yes` / `Android SDK installation is required` | Add `--yes`: `flet build apk --yes` |
| 5 | `main.py not found in the root of Flet app directory` | Run the command from the project folder (where `pyproject.toml` is), not from `src/` |
| 5 | `URLError`, `Name or service not known`, `Could not resolve host`, `timed out`, `Connection reset` | Download failed: check the internet. Behind a proxy set `HTTPS_PROXY` / `HTTP_PROXY`. The build downloads from `storage.googleapis.com`, `github.com`, `pub.dev`, `dl.google.com`, `services.gradle.org`, `repo.maven.apache.org` and `pypi.org`: a school / company firewall must allow them (or use another network, e.g. the phone hotspot) |
| 5 | `CERTIFICATE_VERIFY_FAILED` | macOS with Python from python.org: run `Install Certificates.command` (in `/Applications/Python 3.x/`). Otherwise a proxy / antivirus is intercepting HTTPS: try another network |
| 5 | `Unable to find git in your PATH` | Install Git and open a new terminal |
| 5 | `Building with plugins requires symlink support` | Windows: turn on the Developer Mode (step 1) and open a new terminal |
| 5 | `Flutter SDK not found or invalid version` on every build, or errors inside `~/flutter/` | The Flutter download was interrupted: delete the folder `~/flutter/3.44.8` (Windows: `%USERPROFILE%\flutter\3.44.8`) and build again |
| 5 | `Android toolchain`: `cmdline-tools component is missing` or `Android license status unknown` / `You have not accepted the license agreements` | Accept the licenses (answer `y` to all): `flutter config --android-sdk <SDK folder>` then `flutter doctor --android-licenses`. If it still fails, delete the SDK folder and build again with `--yes` (Flet installs the SDK again and accepts the licenses) |
| 5 | `NDK at ... did not have a source.properties file` / `NDK is not installed` | The NDK download was interrupted: delete the folder `~/Android/sdk/ndk/<version>` shown in the message and build again |
| 5 | `Unsupported class file major version`, `Android Gradle plugin requires Java 17`, `Could not determine java version` | `JAVA_HOME` points to an old Java. Remove `JAVA_HOME` (or point it to a JDK 17) and open a new terminal: `flet build` installs JDK 17 in `~/java/` |
| 5 | `OutOfMemoryError: Java heap space` / `Metaspace` | Gradle needs more memory: in `pyproject.toml` raise `-Xmx4G` to `-Xmx6G` (or `-Xmx8G`) in `org.gradle.jvmargs`, close other programs and build again |
| 5 | `Could not reserve enough space for object heap` / `Gradle build daemon disappeared unexpectedly` | Not enough RAM: close other programs, or lower `-Xmx4G` to `-Xmx3G` in `pyproject.toml` |
| 5 | `No space left on device` / `There is not enough space on the disk` | Free disk space (~15 GB are needed on the disk of your user folder) |
| 5 | `Filename longer than 260 characters`, `path too long`, strange errors with `ç`, `ã` or spaces in the path | Windows: move the project to `C:\dev\processing-asdf-game` (step 1). If your **user name** has spaces or accents, also set short folders for the caches before building: `$env:GRADLE_USER_HOME="C:\gradle"; $env:PUB_CACHE="C:\pub-cache"` |
| 5 | `The process cannot access the file because it is being used by another process` / `Access is denied` | Windows: the antivirus or another terminal is using the files. Close other terminals / editors that use the `build` folder, and build again |
| 5 | `Could not open ... cache`, `zip END header not found`, `Could not resolve all files for configuration` | Gradle cache is broken: delete `~/.gradle/caches` and `~/.gradle/wrapper/dists` and build again |
| 5 | `Could not find a version that satisfies the requirement flet==1.0.5` | `flet --version` must be the same as `flet` in `pyproject.toml` (1.0.5): `pip install -r requirements-dev.txt` |
| 5 | `Gradle task assembleRelease failed with exit code 1` and nothing else clear | Delete the old build and build again with the full log: `flet clean` then `flet build apk --yes -vv`; look for `What went wrong:` in the log |
| 5 | Still failing after changes in `pyproject.toml` (icon, name, org...) | Old files in `build/`: run `flet clean` (deletes `build/`) and build again |
| 7 | `INSTALL_FAILED_UPDATE_INCOMPATIBLE` / "App not installed" | An older ASDF Hero signed with another key is on the phone: uninstall it (`adb uninstall com.example.asdf_hero`) and install again |
| 7 | `INSTALL_FAILED_NO_MATCHING_ABIS` | The APK was built with `--arch` for another CPU: build without `--arch` |
| 7 | `adb: no devices/emulators found` / `unauthorized` | Turn on *USB debugging*, accept the "Allow USB debugging?" question on the phone, and check with `adb devices` |
| 8 | The app opens with a blank or red error screen | Run the game on the phone in debug mode to see the Python error: `flet debug android` (phone with USB debugging on). Check that the game works in the browser (step 3) |

If the error is not in the table, search for the first red lines of the log
(without your paths) in the [Flet issues](https://github.com/flet-dev/flet/issues)
and in the [Flet Android guide](https://flet.dev/docs/publish/android).
`flet doctor` shows the Flet, Flutter and Python versions to add to a new issue.

### Test on a phone while developing
- In the phone browser (no build): see [Play on a phone](#play-on-a-phone).
- As an app, on a phone connected with USB: `flet debug android`
  (or `flet debug ios` on macOS).

### iOS (macOS only)
```bash
flet build ipa --yes          # .ipa file, in build/ipa/
flet build ios-simulator      # app for the Xcode iOS simulator
```
Installing on a real iPhone needs an Apple Developer account and signing: see
the `--ios-*` options of `flet build` and the
[Flet iOS guide](https://flet.dev/docs/publish/ios).

### Good to know
- The best results are saved on the phone, in the data folder of the app (see
  [Best results database](#best-results-database)): they are kept when the
  app is closed or updated, and deleted when it is uninstalled.
- Use the same Flet version in `pyproject.toml` and in the `flet` command
  (1.0.5). When Flet is updated, the Flutter version changes too (see
  `flet doctor`), and the paths `~/flutter/<version>` above change with it.
- `build/` and `build.log` are not committed (`.gitignore`).

---

## Tests
The tests run with [pytest](https://docs.pytest.org/) and
[pytest-cov](https://pytest-cov.readthedocs.io/) (installed by
`pip install -r requirements-dev.txt`). No browser or Flet server is needed.

```bash
pytest
```

The settings are in `pyproject.toml`: coverage runs automatically and the
run **fails if total coverage is below 90%**. Example output:

```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src/asdf_hero/__init__.py                 1      0   100%
src/asdf_hero/app.py                    141      0   100%
src/asdf_hero/config.py                  42      0   100%
...
src/asdf_hero/storage.py                 40      0   100%
...
src/asdf_hero/ui/congratulations_view.py 41      0   100%
...
src/main.py                               6      0   100%
-------------------------------------------------------------------
TOTAL                                  1234      0   100%
Required test coverage of 90.0% reached. Total coverage: 100.00%
============================= 579 passed in 11.64s ==============================
```

### Lint (ruff)
[`ruff`](https://docs.astral.sh/ruff/) (installed by `requirements-dev.txt`)
checks the code style and common bugs (no Flet, no tests: it is instant):

```bash
ruff check .
```

It must show `All checks passed!`; this is also checked by CI (see
[Continuous integration (CI)](#continuous-integration-ci)), on every commit.
`ruff check --fix .` fixes the problems it can fix by itself (review the
change before committing). The version is pinned in `requirements-dev.txt`
and in `pyproject.toml` (`[project.optional-dependencies] dev`, like `flet`),
so a newer `ruff` with new rules never breaks the build by surprise: update
the version in both places on purpose, fix what it finds, then commit.

### Useful commands
| Command | What it does |
| --- | --- |
| `pytest` | Run all tests with coverage (fails below 90%) |
| `pytest tests/game` | Run only the game rules tests (or `tests/ui`, `tests/app`) |
| `pytest -k highlight` | Run the tests whose name matches an expression |
| `pytest -v` | Show the name of each test |
| `pytest --cov-report=html` | Also build an HTML report in `htmlcov/index.html` |
| `pytest --no-cov` | Run the tests without coverage (faster) |
| `ruff check .` | Check the code style and common bugs (see [Lint (ruff)](#lint-ruff)) |

### How the tests work
Each test file has one responsibility:

| File | What it checks |
| --- | --- |
| **`tests/game/`** | **Game rules (no Flet)** |
| `test_architecture.py` | The rules, the database and the logs do not import Flet or the views |
| `test_design_rules.py` | The agreed design limits in `config.py` (speeds, gold not too fast, always one letter in the bar at the max level...) |
| `test_level.py` | Speed and distance by points (faster until 51 points, then more letters) |
| `test_action_bar.py` | Hit area of the bar and its highlight |
| `test_button.py` | Clickable area of a button |
| `test_keys.py` | Keys of each hand and key names (`;` = `Ç`) |
| `test_letter.py` | A letter: fall, status, key press |
| `test_pages.py` | Start, game over and retry; buttons at the bottom, mobile touch size; a new game is clean |
| `test_hand.py` | Hand choice (start and game over pages); hand button above the start button |
| `test_letter_flow.py` | New letters, exact spacing, movement, removal |
| `test_key_press.py` | Result of a key press: points, one press hits all the letters of the key, game over, yellow / red bar |
| `test_game_over.py` | Missed letter, the slow motion, a best result shows the congratulations page |
| `test_congratulations.py` | Congratulations page: only for a best result (not 0 points); type, save, save as anonymous, buttons, saved once |
| `test_wide_game.py` | A wider game (phones): lanes, letters, gold letters and touch buttons spread out |
| `test_scoreboard.py` | Best results: order, only the best 5, same points, who enters (never 0 points), names, stores |
| `test_challenge_base.py` | Challenge hooks and the schedule (from N points, after 5-10 letters) |
| `test_gold_schedule.py` | When and where the gold letter appears |
| `test_gold_letter.py` | Gold letter: speed, points, game over, one press with a normal letter of the same char |
| `test_silver.py` | Silver letter: when, which letters, silver from the start, swap one letter from the bar, new chars |
| `test_touch_buttons.py` | Touch buttons: one in each lane, each one is the key of its lane, keys press their button |
| `test_full_game.py` | Whole games with a perfect player |
| **`tests/ui/`** | **Flet views** |
| `test_theme.py` | Color helpers and the color standard (green start, purple hand, blue anonymous, red game over, no lane like gold, small lane glow) |
| `test_texts.py` | Portuguese / English: language of the device, default language, every text filled, same `{}` |
| `test_letter_view.py` | Circles, char, colors of each status, the glow of every letter (small for lanes, big for gold / silver) |
| `test_action_bar_view.py` | Bar color and its press effect (also during the slow motion) |
| `test_button_view.py` | A button: the touch buttons design (radius, bold white text), its color, darker when pressed |
| `test_background_view.py` | Lanes (also of a wider game) and the banner (bold: `ASDF HERO` black / `GAME OVER` red) |
| `test_game_view.py` | Layers and what each page shows (best results on the home screen, button colors, congratulations, English) |
| `test_scoreboard_view.py` | Best results: position, name (anonymous), date, time, points, last game in bold, empty, English |
| `test_congratulations_view.py` | Congratulations page: texts (bold title), buttons, a new empty name field for each best result, field events |
| `test_touch_buttons_view.py` | Touch buttons: lane colors, keys, press effect |
| `test_press_effect.py` | Press effect: 2 px bigger for some frames after each press |
| `test_game_view_letters.py` | One view for each letter (kept, removed, gold on top, hidden behind the buttons) |
| **`tests/app/`** | **Flet app** |
| `test_page_setup.py` | Page settings, events, `main()`, best results shared by all tabs |
| `test_input.py` | Keys / clicks are queued and applied by the game loop |
| `test_congratulations.py` | Congratulations page in the app: name events queued, save / anonymous, results kept after a restart and shown on the home screen, 0 points |
| `test_language.py` | Language of the device (`get_device_info`), no answer, `config.LANGUAGE`, `main()` |
| `test_game_loop.py` | Frame order (input -> update -> render), frame rate, slow frames, errors |
| `test_lifecycle.py` | Tab connect / disconnect (pause) / close (stop) |
| `test_screen_fit.py` | The game fits the page: smaller on a computer, fills the phone screen (no margins), keyboard open |
| `test_main.py` | `python src/main.py` (server settings, assets, logs in the data folder) |
| `test_performance_logs.py` | The logs of the app: time of each part of the frame, late frames, sessions, pages, language |
| **`tests/`** | **Project** |
| `test_requirements.py` | `requirements-dev.txt` has the same packages as `pyproject.toml` |
| `test_storage.py` | SQLite database: folder (app / web server), save / load, restart, errors, load / save times in the logs |
| `test_logs.py` | `setup_logging()`: console and file, max size, level (config / env), only once, no file |
| `test_performance.py` | `PerformanceMonitor`: reports (INFO / WARNING), slowest frame, late frames, pauses, garbage collector, CPU |

- **Database:** an autouse fixture (`tests/conftest.py`) points
  `FLET_APP_STORAGE_DATA` to a temporary folder, so the tests never touch the
  real database.
- **Rules without mocks:** `Game` receives the random generator (`rng`), so
  the tests choose the lanes with `scripted_rng([...])` and put letters where
  they want with the `place_letter` fixture (`tests/conftest.py`).
- **Views:** the Flet controls are plain Python objects, so the tests check
  their properties (`visible`, `top`, `bgcolor`, `content.value`...).
- **Game loop timing** is tested with a `FakeClock` (`tests/app/fakes.py`)
  that only moves when the loop sleeps or a frame takes time. Real clocks are
  different on each OS (on Windows the asyncio clock moves in steps of
  ~15.6 ms), so these tests give the same result on Windows, Linux and macOS.
- Flet controls with the same values are equal (`==`). Check if a control is
  present with `is` (identity), not with `in` / `==`. Letter controls have
  a unique `key` for this reason.

---

## Continuous integration (CI)
Every commit (`git push`) and every pull request runs
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) on GitHub Actions,
with two independent jobs (so one failing does not hide the other):

| Job | Runs | What it checks |
| --- | --- | --- |
| **Lint** | `ruff check .` | The code style and common bugs (see [Lint (ruff)](#lint-ruff)) |
| **Test** | `pytest` | All the tests, with coverage (fails below 90%, see [Tests](#tests)). On **Python 3.10 and 3.13**: the oldest and the newest supported by `[project] requires-python` in `pyproject.toml` |

A new push to the same branch (or the same pull request) cancels the CI that
was still running for the previous push: only the latest commit matters.

**Reproducing CI locally** (before pushing, or to debug a failure): both jobs
only run commands already described above, in a clean virtual environment:

```bash
python3 -m venv .venv && source .venv/bin/activate   # or py -3 -m venv .venv (Windows)
pip install -r requirements-dev.txt
ruff check .
pytest -v
```

If this passes locally exactly as above (same two commands, nothing extra
installed, nothing left over from an old run), CI passes too: the workflow
does not do anything else. Testing on **both** Python 3.10 and 3.13 locally
(`py -3.10 -m venv ...` / `py -3.13 -m venv ...`, or `uv venv --python 3.10`)
catches the rare problem that only shows on one of them before it reaches CI;
this is how a real Python-version bug in this project's own test helpers
(`tests/conftest.py`) and a leaked database connection in a test
(`tests/test_storage.py`) were found and fixed.

### When the CI build fails
1. **Open the failing job on GitHub** (Actions tab of the commit / pull
   request) and read the step that has the red ✗: its output is the same
   text `ruff check .` or `pytest -v` would print locally.
2. **Reproduce it locally** with the commands above (same job, same Python
   version: the "Test" job shows its version in the job name, for example
   *Test (Python 3.10)*). A failure that only happens in CI and not locally
   is almost always a different Python version, an old package already
   installed locally that `requirements-dev.txt` would not install fresh, or
   a leftover file from a previous run (`build/`, `.flet/`, a database left
   by a test): delete `.venv` and any of those and try again.
3. **Fix it like any local failure:**
   - `ruff check .` fails: read the rule code (for example `UP031`) and the
     suggestion; `ruff check --fix .` fixes most of them, then re-run
     `ruff check .` to confirm and review the diff before committing.
   - `pytest -v` fails: see [Tests](#tests) (`pytest -v` shows the failing
     test name; `pytest tests/game` etc. reruns only one area while fixing).
   - Fails only on Python 3.10, not on newer versions (or the other way
     around): a language / standard-library difference (as in the example
     above); install that Python version locally and test directly on it
     before pushing again.
4. **Push again.** The new commit starts a new CI run (and cancels the old
   one, per the job names above); there is nothing to restart manually on
   GitHub.
