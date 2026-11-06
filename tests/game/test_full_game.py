"""End to end games with real letters."""

import random

from asdf_hero import config
from asdf_hero.game import Game, GamePage
from tests.helpers import GAME_OVER_FRAMES, center, fill_scoreboard, play, set_points


def test_play_level_up_and_lose(game):
    game.mouse_pressed(*center(game.button))

    play(game, 60 * 60)  # a perfect player for 1 minute
    assert game.page == GamePage.RUNNING
    assert game.speed > config.INIT_SPEED  # the game gets faster
    assert len(game.letters) >= 3  # more than one letter at the same time

    play(game, 60 * 30, press=False)  # stop playing
    assert game.page == GamePage.CONGRATULATIONS  # first game: a best result

    game.type_name("Ana")
    game.mouse_pressed(*center(game.save_button))
    assert game.page == GamePage.GAME_OVER
    assert game.scoreboard.best == [game.last_result]

    game.mouse_pressed(*center(game.button))  # retry: slow again
    assert game.page == GamePage.RUNNING
    assert (game.points, game.speed) == (0, config.INIT_SPEED)


def test_wrong_press_ends_the_game(game):
    fill_scoreboard(game.scoreboard)  # not a best result: game over page
    game.mouse_pressed(*center(game.button))
    play(game, 60 * 10)
    points = game.points

    game.key_pressed(game.letters[-1].char)  # newest letter: at the top
    play(game, GAME_OVER_FRAMES, press=False)

    assert game.page == GamePage.GAME_OVER
    assert game.points == points > 0


def test_challenges_in_a_perfect_game():
    game = Game(rng=random.Random(3))
    game.start_new_game()
    set_points(game, config.SILVER_FROM_POINTS)  # gold and silver letters
    between, normal_count, seen, silver = [], 0, set(), set()

    for _ in range(60 * 2):  # 2 minutes, one second at a time
        play(game, 60)
        assert game.page == GamePage.RUNNING  # a perfect player never loses
        silver.update(letter.id for letter in game.letters if letter.silver)
        for letter in game.letters:
            if letter.id not in seen:
                seen.add(letter.id)
                if letter.gold:
                    between.append(normal_count)
                    normal_count = 0
                else:
                    normal_count += 1

    assert len(between) >= 5
    assert all(5 <= count <= 10 for count in between)  # gold every 5-10 letters
    assert len(silver) >= 10  # silver letters (two for each challenge)
