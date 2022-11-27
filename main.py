from letter import Letter
# from background import Background


class MainGame:
    __INIT_DISTANCE_LEVEL = 500
    __DISPLAY_HEIGHT = None

    points_in_game = 0
    distance_level = __INIT_DISTANCE_LEVEL
    letters = []
    to_be_pressed = None
    
    def __init__(self, display_height = 800):
        self.__DISPLAY_HEIGHT = display_height

    def run_game(self):
        self._run()


    def key_pressed(self, key, key_code):
        _point = False
        for letter in self.letters:
            if letter.key_pressed(key=key):
                _point = True
        self.__update_game_points(point=_point)

    def _run(self):
        try:
            self.__add_letter(random=self.points_in_game>=25)
                
            for letter in self.letters:
                letter.display()
                letter.move()

                # remove letter from list
                if letter.y > (self.__DISPLAY_HEIGHT + letter.size):
                    self.letters.remove(letter)

            # update points bar
            self.__update_points_label()
            
        except Exception as error:
            print('Main._run: error')
            print(error)
    
    def __update_game_points(self, point):
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


    def __add_letter(self, random=False):
        """
        Add a new letter on game or waite for the time to create
        """
        if self.letters:
            if self.letters[-1].y >= self.distance_level + self.letters[-1].size:
                self.letters.append(Letter(letter_random=random, range_y_to_press=[600, 680])) 
        else:
            self.letters.append(Letter(letter_random=random, range_y_to_press=[600, 680])) 

    def __update_points_label(self):
        # points bar
        fill(255,255,255,220)
        rect(0, self.__DISPLAY_HEIGHT - 35, 282, 35)

        fill(0, 0, 0)          
        textSize(30)
        textAlign(LEFT)
        text('Pontos: ' + str(self.points_in_game), 10, self.__DISPLAY_HEIGHT - 10)
        fill(255, 255, 255)

        