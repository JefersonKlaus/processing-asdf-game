from asdf_hero.game import GamePage, Highlight, LetterStatus


def test_game_pages():
    assert [page.name for page in GamePage] == ["START", "RUNNING", "GAME_OVER"]


def test_letter_statuses():
    assert [status.name for status in LetterStatus] == [
        "WAITING",
        "NEED_BE_PRESSED",
        "WAS_PRESSED",
        "FAILED",
    ]


def test_highlights():
    assert [highlight.name for highlight in Highlight] == ["NONE", "PRESSED", "WRONG"]
