import time

from button import Button
from game_page import GamePage
from letter import Letter
from letter_status import LetterStatus


class MainGame:
    __INIT_DISTANCE_LEVEL = 500
    __MIN_DISTANCE_LEVEL = Letter.size
    __DISPLAY_HEIGHT = None
    __DISPLAY_WIDTH = None
    __FRAMES_BEFORE_GAME_OVER = 12

    game_page = None

    # start page
    btn_start = None

    # runing page
    points_in_game = 0
    distance_level = __INIT_DISTANCE_LEVEL
    letters = []
    to_be_pressed = None

    # game over page
    transition_to_game_over = False
    counter_to_show_game_over = 0

    def __init__(self, display_width=282, display_height=800):
        self.__DISPLAY_HEIGHT = display_height
        self.__DISPLAY_WIDTH = display_width
        self.game_page = GamePage.START

    def run_game(self):
        # Start game page
        if self.game_page == GamePage.START:
            self._start()

        elif self.game_page == GamePage.RUNING:
            # Move to game over
            if self.transition_to_game_over:
                if self.counter_to_show_game_over <= self.__FRAMES_BEFORE_GAME_OVER:
                    self.counter_to_show_game_over = self.counter_to_show_game_over + 1

                    time.sleep(0.2)
                else:
                    self.game_page = GamePage.GAME_OVER
            # Run game
            self._run()

        # Game Over Page
        elif self.game_page == GamePage.GAME_OVER:
            self._game_over()

    def key_pressed(self, key, key_code):
        """
        When one key board is pressed this method is called by game.pyde
        """
        # if transaction to game over start this method can not work
        if self.transition_to_game_over:
            return

        _point = False
        for letter in self.letters:
            if letter.key_pressed(key=key):
                _point = True
        self.__update_game_points(point=_point)

    def mouse_pressed(self, mouse_x, mouse_y):
        """
        When the mouse is pressed this method is called by game.pyde
        """
        if not self.game_page == GamePage.RUNING:
            self.btn_start.pressed(mouse_x, mouse_y)

    def mouse_released(self):
        """
        When the mouse is released this method is called by game.pyde
        """
        if not self.game_page == GamePage.RUNING:
            self.btn_start.released()

    def _start(self):
        self.__start_new_game(button_text="Iniciar ASDF Hero")

    def _game_over(self):
        self.__start_new_game(button_text="Falhar novamente")
        self.__update_points_label()

    def _run(self):
        try:
            self.__add_letter(random=self.points_in_game >= 25)

            for letter in self.letters:
                letter.display()
                letter.move()

                # remove letter from list
                if letter.y > (self.__DISPLAY_HEIGHT + letter.size):
                    self.letters.remove(letter)

                # Game Over
                if letter.status == LetterStatus.FAILED:
                    self.transition_to_game_over = True

            # update points bar
            self.__update_points_label()

        except Exception as error:
            print("Main._run: error")
            print(error)

    def __update_game_points(self, point):
        """
        Update the points of the game and change the game level.
        Game level is distance between the next letter
        """
        if point:
            self.points_in_game = self.points_in_game + 1
        else:
            self.points_in_game = self.points_in_game - 1

        _helper_number = self.points_in_game * 5
        self.distance_level = self.__INIT_DISTANCE_LEVEL - _helper_number

        if self.distance_level <= 31:
            self.distance_level = 31
        elif self.distance_level >= self.__INIT_DISTANCE_LEVEL:
            self.distance_level = self.__INIT_DISTANCE_LEVEL
        elif self.distance_level <= self.__MIN_DISTANCE_LEVEL:
            self.distance_level = self.__MIN_DISTANCE_LEVEL

    def __add_letter(self, random=False):
        """
        Add a new letter on game or waite for the time to create
        """
        if self.letters:
            if self.letters[-1].y >= self.distance_level + self.letters[-1].size:
                self.letters.append(
                    Letter(letter_random=random, range_y_to_press=[600, 680])
                )
        else:
            self.letters.append(
                Letter(letter_random=random, range_y_to_press=[600, 680])
            )

    def __update_points_label(self):
        if self.game_page == GamePage.RUNING:
            # points bar
            fill(255, 255, 255, 220)
            rect(0, self.__DISPLAY_HEIGHT - 35, 282, 35)

            fill(0, 0, 0)
            textSize(30)
            textAlign(LEFT)
            text("Pontos: " + str(self.points_in_game), 10, self.__DISPLAY_HEIGHT - 10)
            fill(255, 255, 255)

        elif self.game_page == GamePage.GAME_OVER:
            fill(0, 0, 0)
            textSize(30)
            textAlign(CENTER)
            text("Pontos: " + str(self.points_in_game), self.__DISPLAY_WIDTH / 2, 300)
            fill(255, 255, 255)

    def __start_new_game(self, button_text):
        def start_game():
            self.letters = []
            self.counter_to_show_game_over = 0
            self.transition_to_game_over = False
            self.points_in_game = 0
            self.game_page = GamePage.RUNING

        self.btn_start = Button(
            x=self.__DISPLAY_WIDTH / 2 - 100,
            y=self.__DISPLAY_HEIGHT / 2 - 40,
            w=200,
            h=40,
        )
        self.btn_start.button_text = button_text
        self.btn_start.action = lambda: start_game()
        self.btn_start.draw()
