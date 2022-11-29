class Button:
    X = 0
    Y = 0
    H = 35
    W = 200

    # COLORS
    background_color = color(0, 0, 0)
    foreground_color = color(255, 255, 255)
    background_color_clicked = color(50, 50, 50)
    border = color(30, 30, 30)

    border_enable = False
    border_weight = 1

    clicked = False
    action = None  # method to be called when this button is pressed

    button_text = ""
    text_size = 24

    def __init__(self, x, y, w, h):
        self.X = x
        self.Y = y
        self.W = w
        self.H = h

    def draw(self):
        # DRAWING THE background_color
        if self.clicked:
            fill(self.background_color_clicked)
        else:
            fill(self.background_color)

        if self.border_enable:
            strokeWeight(self.border_weight)
            stroke(self.border)
        else:
            noStroke()

        rect(self.X, self.Y, self.W, self.H)

        fill(self.foreground_color)
        textAlign(LEFT)
        textSize(self.text_size)
        text(
            self.button_text,
            self.X + (self.W - textWidth(self.button_text)) / 2,
            self.Y + self.text_size,
        )

    def _overBox(self, x, y):
        if x >= self.X and x <= self.X + self.W:
            if y >= self.Y and y <= self.Y + self.H:
                return True

        return False

    def pressed(self, x, y):
        if self._overBox(x, y):
            self.clicked = True
            if self.action:
                self.action()

    def released(self):
        self.clicked = False
