"""The game rules must not depend on the user interface (Flet)."""

import os
import subprocess
import sys

import pytest

SRC = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src")


def imported_modules(module):
    """Import a module in a new Python and return all the loaded modules."""
    code = f"import sys, {module}; print('\\n'.join(sys.modules))"
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


@pytest.mark.parametrize(
    "module", ["asdf_hero.storage", "asdf_hero.performance", "asdf_hero.logs"]
)
def test_database_and_logs_do_not_import_flet(module):
    # they work without the user interface (and the rules without them)
    modules = imported_modules(module)

    assert not any(name == "flet" or name.startswith("flet.") for name in modules)
    assert not any(name.startswith("asdf_hero.ui") for name in modules)
    assert module not in imported_modules("asdf_hero.game")


def test_ui_imports_flet():
    # sanity check of the helper
    assert "flet" in imported_modules("asdf_hero.ui")
