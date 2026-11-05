"""The game rules must not depend on the user interface (Flet)."""

import os
import subprocess
import sys

SRC = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src")


def imported_modules(module):
    """Import a module in a new Python and return all the loaded modules."""
    code = "import sys, %s; print('\\n'.join(sys.modules))" % module
    env = dict(os.environ, PYTHONPATH=os.path.abspath(SRC))
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
    )
    return set(result.stdout.split())


def test_game_rules_do_not_import_flet():
    modules = imported_modules("asdf_hero.game")

    assert "asdf_hero.game.game" in modules
    assert not any(name == "flet" or name.startswith("flet.") for name in modules)
    assert not any(name.startswith("asdf_hero.ui") for name in modules)


def test_ui_imports_flet():
    # sanity check of the helper
    assert "flet" in imported_modules("asdf_hero.ui")
