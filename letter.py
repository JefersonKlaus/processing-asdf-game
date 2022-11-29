import random

from letter_status import LetterStatus


class Letter:
    status = LetterStatus.WAITING
    range_y_to_press = []
    letter_color = []
    y = 0
    x = 0
    size = 62
    char = None

    _dy = 5
    __position_options = [37, 106, 175, 244]
    __colors_options = [[66, 133, 244], [219, 68, 55], [244, 160, 0], [15, 157, 88]]
    __leter_options = ["A", "S", "D", "F"]

    def __init__(self, letter_random, range_y_to_press):
        self.range_y_to_press = range_y_to_press

        _random_x = random.randrange(0, 4)
        self.x = self.__position_options[_random_x]
        self.letter_color = self.__colors_options[_random_x]

        if letter_random:
            self.char = self.__leter_options[random.randrange(0, 4)]
        else:
            self.char = self.__leter_options[_random_x]

    def move(self):
        self.y = self.y + self._dy
        self._update_status()

    def display(self):
        # big colored ellipse
        if self.status == LetterStatus.FAILED:
            fill(255, 255, 255)
            stroke(0)
        else:
            fill(self.letter_color[0], self.letter_color[1], self.letter_color[2])
            noStroke()
        ellipse(self.x, self.y, self.size, self.size)

        # white ellipse
        if self.status == LetterStatus.WAS_PRESSED:
            noStroke()
            fill(self.letter_color[0], self.letter_color[1], self.letter_color[2])
        elif self.status == LetterStatus.FAILED:
            stroke(0)
            fill(255, 255, 255)
        else:
            noStroke()
            fill(255, 255, 255)
        ellipse(self.x, self.y, (self.size * 0.7), (self.size * 0.7))

        # letter
        if self.status == LetterStatus.NEED_BE_PRESSED:
            fill(self.letter_color[0], self.letter_color[1], self.letter_color[2])
        elif self.status == LetterStatus.WAS_PRESSED:
            fill(255, 255, 255)
        elif self.status == LetterStatus.FAILED:
            fill(0, 0, 0)
        elif self.status == LetterStatus.WAITING:
            fill(0, 0, 0)
        textSize(45)
        textAlign(CENTER)
        text(self.char, self.x, self.y + 15)
        fill(255, 255, 255)

    def key_pressed(self, key):
        point = False
        if self.status == LetterStatus.NEED_BE_PRESSED:
            if self.char.lower() == key.lower():
                self.status = LetterStatus.WAS_PRESSED
                point = True

        return point

    def _update_status(self):
        if self.y >= self.range_y_to_press[0] and self.y <= self.range_y_to_press[1]:
            if self.status == LetterStatus.WAITING:
                self.status = LetterStatus.NEED_BE_PRESSED
        else:
            if self.status == LetterStatus.NEED_BE_PRESSED:
                self.status = LetterStatus.FAILED
