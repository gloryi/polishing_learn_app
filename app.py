import pygame
from time_utils import global_timer, Counter, Progression
from six_words_mode import SixtletsProcessor
from config import TEST_LANG_DATA
from ui_elements import UpperLayout
 
pygame.init()
 
# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
 
X = 700 
Y = 1000 
 
display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Experimental')

time_to_cross_screen = 16000
time_to_appear = 4000
pixels_per_ms = Y/time_to_cross_screen

delta_timer = global_timer(pygame)
new_line_counter = Counter(time_to_appear)
upper_stats = UpperLayout(pygame, display_surface, X, Y)

sixtlets = SixtletsProcessor(X, Y, pygame, display_surface, upper_stats, "latvian_words", TEST_LANG_DATA)


progression = Progression(Y,
                          time_to_cross_screen,
                          time_to_appear,
                          new_line_counter,
                          upper_stats)
is_finished = False
 
fpsClock = pygame.time.Clock()
for time_delta in delta_timer:
    fpsClock.tick(60)
    display_surface.fill(white)

    if new_line_counter.is_tick(time_delta):
        is_finished = sixtlets.add_line()

    feedback = sixtlets.tick(pixels_per_ms * time_delta)

    resume_game = progression.register_event(feedback)
    if not resume_game or is_finished:
        break

    pixels_per_ms = progression.synchronize_speed()

    upper_stats.redraw()

    pygame.display.update()
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
pygame.quit() 
