import pygame
from time_utils import global_timer, Counter, Progression
from six_words_mode import SixtletsProcessor
from config import TEST_LANG_DATA
from ui_elements import UpperLayout

def hex_to_rgb(h, cache = False):
    h = h[1:]
    resulting =  tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return resulting
 
pygame.init()
 
# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
 
X = 1050 
Y = 1440 

quadra_r = 0
quadra_phase = "INHALE"
clip_color = lambda _ : 0 if _ <=0 else 255 if _ >=255 else int(_)
inter_color = lambda v1, v2, p: clip_color(v1 + (v2-v1)*p)
interpolate = lambda col1, col2, percent: (inter_color(col1[0], col2[0], percent),
                                           inter_color(col1[1], col2[1], percent),
                                           inter_color(col1[2], col2[2], percent))
feature_bg = hex_to_rgb("#2E849E")
col_bt_pressed = hex_to_rgb("#4E52AF")
red2 = hex_to_rgb("#700F3C")
option_fg = hex_to_rgb("#68A834")
quadra_col_1 = feature_bg 
quadra_col_2 = col_bt_pressed
 
display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Experimental')

trans_surface = pygame.Surface((X, Y))
trans_surface.set_alpha(50)
trans_surface.fill((40,0,40))
trans_surface2 = pygame.Surface((X, Y))
trans_surface2.set_alpha(25)
trans_surface2.fill((40,0,40))

time_to_cross_screen = 16000
time_to_appear = 4000
pixels_per_ms = Y/time_to_cross_screen

delta_timer = global_timer(pygame)

new_line_counter = Counter(time_to_appear)
quadra_timer = Counter(5000)

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
    fpsClock.tick(140)
    display_surface.fill(white)

    if new_line_counter.is_tick(time_delta):
        is_finished = sixtlets.add_line()

    feedback = sixtlets.tick(pixels_per_ms * time_delta)

    resume_game = progression.register_event(feedback)
    if not resume_game or is_finished:
        break

    pixels_per_ms = progression.synchronize_speed()

    upper_stats.redraw()

    if quadra_timer.is_tick(time_delta):
        if quadra_phase == "INHALE":
            quadra_phase = "HOLD_IN"
            quadra_col_1 = col_bt_pressed
            quadra_col_2 = red2
        elif quadra_phase == "HOLD_IN":
            quadra_phase = "EXHALE"
            quadra_col_1 = red2
            quadra_col_2 = option_fg
        elif quadra_phase == "EXHALE":
            quadra_phase = "HOLD_OUT"
            quadra_col_1 = option_fg
            quadra_col_2 = feature_bg
        else:
            quadra_phase = "INHALE"
            quadra_col_1 = feature_bg
            quadra_col_2 = col_bt_pressed

    if quadra_phase == "INHALE":
        quadra_w_perce1 = quadra_timer.get_percent()
        quadra_w_perce2 = 1.0
    elif quadra_phase == "HOLD_IN":
        quadra_w_perce1 = 1.0
        quadra_w_perce2 = 1 - quadra_timer.get_percent()
    elif quadra_phase == "EXHALE":
        quadra_w_perce1 = 1 - quadra_timer.get_percent()
        quadra_w_perce2 = 0.0
    else:
        quadra_w_perce1 = 0.0
        quadra_w_perce2 = quadra_timer.get_percent()

    trans_surface.fill((40,0,40))
    trans_surface2.fill((40,0,40))

    exit_trigger = Y - Y//4 - Y//8 - Y//16 + Y//8
    entry_trigger  = Y - Y//4 - Y//4 + Y//8
    action_trigger = (entry_trigger + exit_trigger)//2
    pygame.draw.circle(trans_surface,
                          interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
                          (X//2, action_trigger),
                           (X//2-100)*quadra_w_perce1+100)
    pygame.draw.circle(trans_surface,
                          interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()**2),
                          (X//2, action_trigger),
                           (X//2-50)*quadra_w_perce2+50, width = 3)



    display_surface.blit(trans_surface, (0,0))
    display_surface.blit(trans_surface2, (0,0))

    pygame.display.update()
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
pygame.quit() 
