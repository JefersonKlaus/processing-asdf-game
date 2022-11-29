from game_page import GamePage


class Background:
    __DISPLAY_HEIGHT = None
    __DISPLAY_WIDTH = None

    def __init__(self, display_width=282, display_height=800):
        self.__DISPLAY_HEIGHT = display_height
        self.__DISPLAY_WIDTH = display_width

    def display(self, page):
        if page == GamePage.START:
            pass

        elif page == GamePage.RUNING:
            stroke(0)
            rect(0, 0, 5, self.__DISPLAY_HEIGHT)
            rect(69, 0, 5, self.__DISPLAY_HEIGHT)
            rect(138, 0, 5, self.__DISPLAY_HEIGHT)
            rect(207, 0, 5, self.__DISPLAY_HEIGHT)
            rect(276, 0, 5, self.__DISPLAY_HEIGHT)

            # action bar
            fill(255, 255, 255, 200)
            rect(0, 600, self.__DISPLAY_WIDTH, 80)

        elif page == GamePage.GAME_OVER:
            # game over bar
            noStroke()
            fill(255, 255, 255, 200)
            rect(0, 200, self.__DISPLAY_WIDTH, 120)

            fill(0, 0, 0)
            textSize(50)
            textAlign(CENTER)
            text("GAME OVER", self.__DISPLAY_WIDTH / 2, 260)
            fill(255, 255, 255)
