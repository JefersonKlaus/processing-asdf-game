from main import MainGame
from background import Background

game = MainGame(282, 800)
bg = None

def setup():
    size(282, 800)
       

def draw():
    try:
        background(loadImage("./imgs/back.jpg"))

        Background().display(game.game_page)
        game.run_game()        

    except Exception as error:
        print(error)


def keyPressed():
    game.key_pressed(key, keyCode)

def mousePressed():
    game.mouse_pressed(mouseX, mouseY)

def mouseReleased():
    game.mouse_released()