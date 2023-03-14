class UpperLayout():
    def __init__(self, pygame_instance, display_instance, W, H):
        self.W = W
        self.H = H
        self.y1 = 0
        self.y2 = self.H//16
        self.y3 = self.H - self.H//32
        self.higher_center = (self.y1 + self.y2)/2
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.backgroudn_color = (60, 60, 60)
        font_file = pygame_instance.font.match_font("setofont")
        self.font = pygame_instance.font.Font(font_file, 50)
        self.large_font = pygame_instance.font.Font(font_file, 80)
        self.combo = 1

        self.speed_index = 5000
        self.percent = 0.8
        self.progress_ratio = 0.0
        self.mastered = 0
        self.to_master = 0

    def place_text(self, text, x, y, transparent=False, renderer=None, base_col=(80, 80, 80)):
        if renderer is None:
            renderer = self.font
        if not transparent:
            text = renderer.render(text, True, base_col, (150, 150, 151))
        else:
            text = renderer.render(text, True, base_col)
        textRect = text.get_rect()
        textRect.center = (x, y)
        self.display_instance.blit(text, textRect)

    def redraw(self):
        self.pygame_instance.draw.rect(self.display_instance,
                                       self.backgroudn_color,
                                       (0, self.y1, self.W, self.y2))

        self.pygame_instance.draw.rect(self.display_instance,
                                       self.backgroudn_color,
                                       (0, self.y3, self.W, self.H))

        # self.place_text(str(int(self.percent*100))+"%", self.W//10*2, self.higher_center)
        line_color = (int(255*(1-self.percent)), int(255*(self.percent)), 0)
        self.pygame_instance.draw.rect(self.display_instance,
                                       line_color,
                                       (0,
                                        self.y3,
                                        self.W*self.percent,
                                        self.H))
        self.place_text(str(self.combo)+"x", self.W//2, self.H//4-self.H//16,
                        transparent=True, renderer=self.large_font, base_col=(10, 10, 10))

        line_color = (int(255*(1-self.progress_ratio)),
                      int(255*(self.progress_ratio)), 0)
        self.pygame_instance.draw.rect(self.display_instance,
                                       line_color,
                                       (0,
                                        self.y1,
                                        self.W*self.progress_ratio,
                                        self.y2))

        self.place_text(str(self.mastered)+"/"+str(self.to_master),
                        self.W/2, (self.y1 + self.y2)/2)
        self.place_text(str(self.speed_index//1000)+"s",
                        self.W - self.W//10, self.higher_center)
