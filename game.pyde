from main import MainGame
from background import Background

game = MainGame(800)
bg = None

def setup():
    size(282, 800)
       

def draw():
    try:
        background(loadImage("back.jpg"))

        Background().display()
        game.run_game()        

    except Exception as error:
        print(error)


def keyPressed():
    game.key_pressed(key, keyCode)
