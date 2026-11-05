"""A clickable area (start / retry button)."""


class Button:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.clicked = False  # held down (start / hand buttons)
        self.presses = 0  # number of presses (the view shows a press effect)

    def press(self) -> None:
        self.presses += 1

    def contains(self, x: float, y: float) -> bool:
        return (
            self.x <= x <= self.x + self.width
            and self.y <= y <= self.y + self.height
        )
