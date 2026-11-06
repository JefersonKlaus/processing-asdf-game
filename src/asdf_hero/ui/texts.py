"""
The texts of the screen in each language (Portuguese and English).

The views receive one ``Texts``; ``texts_for()`` chooses it from the language
of the phone / browser. To add a language: create a ``Texts`` and add it to
``LANGUAGES``.
"""

from dataclasses import dataclass

from asdf_hero import config
from asdf_hero.game.states import GamePage, Hand


@dataclass(frozen=True)
class Texts:
    language: str  # language code: "pt", "en"
    # buttons
    start_button: str
    retry_button: str
    left_hand_button: str
    right_hand_button: str
    # start (home) / running / game over
    home_title: str  # big title of the start page, above the best results
    points: str  # "{}": the points
    game_over: str
    # best results
    scoreboard_title: str
    scoreboard_empty: str
    anonymous: str  # name of a result saved without a name
    date_format: str
    time_format: str
    # congratulations page
    congratulations_title: str
    congratulations_subtitle: str
    congratulations_text: str  # "{}": the points, "{}": the number of results
    name_label: str
    save_button: str
    anonymous_button: str

    def button(self, page: GamePage) -> str:
        """Text of the main button: start (start page) or retry (game over)."""
        return self.retry_button if page == GamePage.GAME_OVER else self.start_button

    def hand_button(self, hand: Hand) -> str:
        return self.left_hand_button if hand == Hand.LEFT else self.right_hand_button

    def name(self, name: str) -> str:
        """The name shown in the best results (anonymous when empty)."""
        return name or self.anonymous


PORTUGUESE = Texts(
    language="pt",
    start_button="Iniciar ASDF Hero",
    retry_button="Falhar novamente",
    left_hand_button="Mão esquerda: ASDF",
    right_hand_button="Mão direita: JKLÇ",
    home_title="ASDF HERO",
    points="Pontos: {}",
    game_over="GAME OVER",
    scoreboard_title="Melhores resultados",
    scoreboard_empty="Nenhum resultado ainda",
    anonymous="Anônimo",
    date_format="%d/%m/%Y",
    time_format="%H:%M",
    congratulations_title="NADA MAL!",
    congratulations_subtitle="Novo recorde!",
    congratulations_text="Você fez {} pontos e entrou nos {} melhores resultados.",
    name_label="Seu nome",
    save_button="Salvar",
    anonymous_button="Salvar como anônimo",
)

ENGLISH = Texts(
    language="en",
    start_button="Start ASDF Hero",
    retry_button="Fail again",
    left_hand_button="Left hand: ASDF",
    right_hand_button="Right hand: JKLÇ",
    home_title="ASDF HERO",
    points="Points: {}",
    game_over="GAME OVER",
    scoreboard_title="Best results",
    scoreboard_empty="No results yet",
    anonymous="Anonymous",
    date_format="%m/%d/%Y",
    time_format="%H:%M",
    congratulations_title="NOT BAD!",
    congratulations_subtitle="New record!",
    congratulations_text="You scored {} points and entered the {} best results.",
    name_label="Your name",
    save_button="Save",
    anonymous_button="Save as anonymous",
)

LANGUAGES = {texts.language: texts for texts in (PORTUGUESE, ENGLISH)}


def texts_for(language: str | None) -> Texts:
    """
    The texts of a language code ("pt", "pt-BR", "en_US"...). Other languages
    (or no language) use config.DEFAULT_LANGUAGE.
    """
    code = (language or "").replace("_", "-").split("-")[0].lower()
    return LANGUAGES.get(code, LANGUAGES[config.DEFAULT_LANGUAGE])
