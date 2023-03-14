from collections import OrderedDict
from itertools import compress
from math import sqrt
import os
import random
import re

from utils import extract_bijection_csv, crop_data
from learning_model import SemanticUnit
from config import ABSOLUTE_LOCATION
from config import BACKGROUNDS_DIR
from text_morfer import textMorfer

LAST_EVENT = "POSITIVE"
morfer = textMorfer()
N_ROWS = 8


def hex_to_rgb(h):
    h = h[1:]
    resulting = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return resulting
######################################
# DATA PRODUCER
######################################


class SixtletsProducer():
    def __init__(S, label, csv_path, ui_ref=None):
        S.csv_path = csv_path
        S.label = label
        S.semantic_units = S.prepare_data()
        S.batch = random.sample(S.semantic_units, 20)
        S.background_images = S.list_images(BACKGROUNDS_DIR)

        S.ui_ref = ui_ref

    def list_images(S, target_directory):
        selected_files = []
        for _r, _d, _f in os.walk(target_directory):
            for f in _f:
                selected_files.append(os.path.join(_r, f))
        return selected_files

    def produce_background_image(S):
        if S.background_images:
            return random.choice(S.background_images)

    def prepare_data(S):
        crop_data(S.csv_path)
        return [SemanticUnit(bijection) for bijection in extract_bijection_csv(S.csv_path)]

    def update_progress(S):
        if not S.ui_ref is None:
            target_min_score = 102
            all_units = len(S.batch)
            units_before_score = len(
                [_ for _ in S.batch if _.learning_score >= target_min_score])

            if units_before_score + 3 >= all_units:
                S.ui_ref.progress_ratio = 0.0
                S.ui_ref.mastered = 0
                S.ui_ref.all_units = all_units
                S.resample()

            ratio = units_before_score / all_units

            S.ui_ref.progress_ratio = ratio
            S.ui_ref.mastered = units_before_score
            S.ui_ref.to_master = all_units

    def resample(S):
        S.semantic_units.sort(key=lambda _: _.learning_score)
        # S.batch = random.sample(S.semantic_units[:len(S.semantic_units)//2], 15)
        S.batch = S.semantic_units[:len(S.semantic_units)//2]

    def is_finished(S):
        if len([_ for _ in S.semantic_units if _.learning_score >= 102])\
                >= len(S.semantic_units) - 4:
            return True
        return False

    def produce_three_pairs(S):
        S.update_progress()
        # selected = random.sample(S.semantic_units, THREE_PAIRS)
        average = sum(_.learning_score for _ in S.batch)/len(S.batch)
        worst_perfomance = list(
            filter(lambda _: _.learning_score < average, S.batch))
        best_perfomance = list(
            filter(lambda _: _.learning_score >= average, S.batch))

        worst_picks = 0
        best_picks = 0

        if len(worst_perfomance) < (N_ROWS//2)+1:
            worst_picks = len(worst_perfomance)
            best_picks = N_ROWS//2 - worst_picks
        else:
            worst_picks = N_ROWS//2
            best_picks = 0

        selected = []

        if worst_picks != 0:
            selected += random.sample(worst_perfomance, worst_picks)
        if best_picks != 0:
            selected += random.sample(best_perfomance, best_picks)

        for unit in selected:
            unit.activated = False

        active = random.choice(selected)
        active.activate()
        three_pairs = []

        for unit in selected:
            three_pairs += unit.produce_pair()
        random.shuffle(three_pairs)

        return three_pairs

######################################
# LINES HANDLER TEXT_AND_POSE
######################################


class SemanticsLine():
    def __init__(S, semantic_units, pygame_instance, W, H, init_y):
        S.W, S.H = W, H
        S.position_y = init_y

        S.x_positions = [S.W//N_ROWS *
                         (i+1) - S.W//(N_ROWS*2) for i in range(N_ROWS)]

        S.semantic_units = semantic_units
        S.pygame_instance = pygame_instance

        S.active = False
        S.correct = False
        S.error = False
        S.triggered = False

        S.base_color = random.choice([hex_to_rgb("#006663"),
                                      hex_to_rgb("#18818C"), hex_to_rgb(
            "#343D59"),
            hex_to_rgb("#020659"), hex_to_rgb(
            "#204127"),
            hex_to_rgb("#3B42BF"), hex_to_rgb(
            "#092140"),
            hex_to_rgb("#89199E")])
        S.rrise = False
        S.grise = True
        S.brise = True

        S.keys_assotiated = [False for i in range(N_ROWS)]

        S.feedback = None

    def move_vertically(S, delta_y):

        if S.position_y <= S.H//3:
            delta_y *= 0.75
        else:
            delta_y *= 1.5
        S.position_y += delta_y

    def produce_geometries(S):
        graphical_objects = []
        if not S.triggered:
            for unit, position_x in zip(S.semantic_units, S.x_positions):
                if unit.active:
                    color = hex_to_rgb("#A60321")
                else:
                    color = S.base_color
                graphical_objects.append(WordGraphical(unit.content,
                                                       position_x,
                                                       S.position_y,
                                                       color))
        else:
            active_unit = None
            for unit in S.semantic_units:
                if unit.active:
                    active_unit = unit
            color = hex_to_rgb("#022873")
            for unit, position_x in zip(S.semantic_units, S.x_positions):
                if unit.key == active_unit.key:
                    graphical_objects.append(WordGraphical(unit.content,
                                                           position_x,
                                                           S.position_y,
                                                           color))
        return graphical_objects

    def activate(S):
        S.active = True

    def deactivate(S):
        S.register_error()

    def register_keys(S, key_codes):
        S.keys_assotiated = [a or b for (a, b) in zip(
            key_codes, S.keys_assotiated)]
        S.validate_keys()

    def check_answers(S):
        selected_units = list(
            compress(S.semantic_units, S.keys_assotiated))
        if len(selected_units) != 2:
            return False
        first_unit, second_unit = selected_units
        if not any([first_unit.active, second_unit.active]):
            return False
        if not first_unit.key == second_unit.key:
            return False
        return True

    def register_event(S):
        S.triggered = True
        S.active = False

    def feedback_positive(S):
        for unit in S.semantic_units:
            if unit.active:
                unit.register_match()
                break
        S.feedback = 1

    def feedback_negative(S):
        for unit in S.semantic_units:
            if unit.active:
                unit.register_error()
        S.feedback = -1

    def register_error(S):
        S.correct = False
        S.error = True
        S.register_event()
        S.feedback_negative()

    def register_correct(S):
        S.correct = True
        S.error = False
        S.register_event()
        S.feedback_positive()

    def validate_keys(S):

        if S.keys_assotiated.count(True) == 2:
            if (S.check_answers()):
                S.register_correct()
            else:
                S.register_error()

        elif S.keys_assotiated.count(True) >= 3:
            S.register_error()

    def fetch_feedback(S):
        to_return = S.feedback
        S.feedback = None
        return to_return


######################################
# LINES HANDLER GRAPHICS
######################################

class WordGraphical():
    def __init__(S, text, x, y, color):
        S.text = text
        S.x = x
        S.y = y
        S.color = color


class SixtletDrawer():
    def __init__(S, pygame_instance, display_instance, W, H):
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.W = W
        S.H = H
        notto_font_location = os.path.join(
            ABSOLUTE_LOCATION, "NotoSans-SemiBold.ttf")
        S.nottofont60 = S.pygame_instance.font.Font(
            notto_font_location, 75, bold=True)
        S.nottofont30 = S.pygame_instance.font.Font(
            notto_font_location, 55, bold=True)
        S.nottofont40 = S.pygame_instance.font.Font(
            notto_font_location, 35, bold=True)
        S.nottofont20 = S.pygame_instance.font.Font(
            notto_font_location, 25, bold=True)

        simhei_font_location = os.path.join(ABSOLUTE_LOCATION, "simhei.ttf")
        S.simhei60 = S.pygame_instance.font.Font(
            simhei_font_location, 85, bold=True)
        S.simhei30 = S.pygame_instance.font.Font(
            simhei_font_location, 65, bold=True)
        S.simhei40 = S.pygame_instance.font.Font(
            simhei_font_location, 45, bold=True)
        S.simhei20 = S.pygame_instance.font.Font(
            simhei_font_location, 35, bold=True)

    def draw_static_ui_elements(S, horisontals):
        for i in range(1, 8):
            S.pygame_instance.draw.line(S.display_instance,
                                        (10, 10, 10),
                                        (S.W//N_ROWS*i, 0),
                                        (S.W//N_ROWS*i, S.H),
                                        width=3)

        S.pygame_instance.draw.line(S.display_instance,
                                    (20, 20, 20),
                                    (S.W//N_ROWS*(N_ROWS//2)-5, 0),
                                    (S.W//N_ROWS*(N_ROWS//2)-5, S.H),
                                    width=2)
        S.pygame_instance.draw.line(S.display_instance,
                                    (20, 20, 20),
                                    (S.W//N_ROWS*(N_ROWS//2)+5, 0),
                                    (S.W//N_ROWS*(N_ROWS//2)+5, S.H),
                                    width=2)
        for line_y in horisontals:
            S.pygame_instance.draw.line(S.display_instance,
                                        (10, 10, 10),
                                        (0, line_y),
                                        (S.W, line_y),
                                        width=3)

    def draw_line(S, line):
        geometries = line.produce_geometries()
        color = hex_to_rgb("#404040")
        if line.active and line.triggered:
            color = hex_to_rgb("#F2790F")
        elif line.correct:
            color = hex_to_rgb("#61A61C")
        elif line.error:
            color = hex_to_rgb("#D91604")

        for geometry in geometries:
            message = geometry.text
            if re.findall(r'[\u4e00-\u9fff]+', message):
                renderer = S.simhei60 if len(message) == 1 else S.simhei30 if len(
                    message) < 5 else S.simhei40 if len(message) < 8 else S.simhei20
            else:
                renderer = S.nottofont60 if len(message) == 1 else S.nottofont30 if len(
                    message) < 5 else S.nottofont40 if len(message) < 8 else S.nottofont20

            if not re.findall(r'[\u4e00-\u9fff]+', message):
                message = morfer.morf_text(message)

            if line.triggered:
                text = renderer.render(message, True, geometry.color, color)
            else:
                text = renderer.render(message, True, geometry.color)
            txt_rect = text.get_rect()
            txt_rect.center = (geometry.x, geometry.y)

            S.display_instance.blit(text, txt_rect)

    def display_keys(S, keys):
        for i, key_state in enumerate(keys):
            color = (255, 255, 255)
            if key_state == "up":
                if not i in [0, 2,  5, 7]:
                    color = (200, 170, 200) if LAST_EVENT == "POSITIVE" else (
                        200, 170, 170)
                else:
                    color = (170, 200, 200) if LAST_EVENT == "POSITIVE" else (
                        170, 150, 150)
            elif key_state == "down":
                if not i in [0, 2,  5, 7]:
                    color = (150, 0, 150) if LAST_EVENT == "POSITIVE" else (
                        150, 0, 100)
                else:
                    color = (0, 150, 150) if LAST_EVENT == "POSITIVE" else (
                        50, 100, 100)
            else:
                color = (0, 150, 100)

            S.pygame_instance.draw.rect(S.display_instance,
                                        color,
                                        (S.W//N_ROWS*i, 0,
                                         S.W//N_ROWS*(i+1), S.H))


######################################
# SIX MODE CONTROLLER
######################################

class KeyboardSixModel():
    def __init__(S, pygame_instance):
        S.pygame_instance = pygame_instance
        S.up = 'up'
        S.down = 'down'
        S.pressed = 'pressed'
        S.mapping = OrderedDict()
        S.mapping[S.pygame_instance.K_a] = S.up
        S.mapping[S.pygame_instance.K_s] = S.up
        S.mapping[S.pygame_instance.K_d] = S.up
        S.mapping[S.pygame_instance.K_f] = S.up

        S.mapping[S.pygame_instance.K_j] = S.up
        S.mapping[S.pygame_instance.K_k] = S.up
        S.mapping[S.pygame_instance.K_l] = S.up
        S.mapping[S.pygame_instance.K_SEMICOLON] = S.up

        S.keys = [S.up for _ in range(N_ROWS)]

    def process_button(S, current_state, new_state):
        if current_state == S.up and new_state == S.down:
            return S.down
        if current_state == S.down and new_state == S.down:
            return S.down
        if current_state == S.down and new_state == S.up:
            return S.pressed
        if current_state == S.pressed and new_state == S.up:
            return S.up
        return S.up

    def prepare_inputs(S):
        S.keys = list(S.mapping.values())

    def get_inputs(S):
        keys = S.pygame_instance.key.get_pressed()
        for control_key in S.mapping:
            if keys[control_key]:
                S.mapping[control_key] = S.process_button(
                    S.mapping[control_key], S.down)
            else:
                S.mapping[control_key] = S.process_button(
                    S.mapping[control_key], S.up)

    def get_keys(S):
        S.get_inputs()
        S.prepare_inputs()
        return S.keys


class SixtletsProcessor():
    def __init__(S, W, H, pygame_instance, display_instance, ui_ref, data_label, data_path):
        S.W = W
        S.H = H
        S.cast_point = 0 - S.H//8
        S.despawn_point = S.H + S.H//8
        S.exit_trigger = S.H - S.H//4 - S.H//8 - S.H//16 + S.H//8
        S.entry_trigger = S.H - S.H//4 - S.H//4 + S.H//8
        S.action_trigger = (S.entry_trigger + S.exit_trigger)//2
        S.producer = SixtletsProducer(data_label, data_path, ui_ref)
        S.drawer = SixtletDrawer(pygame_instance, display_instance, W, H)
        S.control = KeyboardSixModel(pygame_instance)
        S.stack = []
        S.active_line = None
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance

        S.trans_surface = S.pygame_instance.Surface((W, H))
        S.trans_surface.set_alpha(100)
        S.trans_surface.fill((30, 0, 30))
        S.image = None
        S.image_y = -H

        active_image_path = S.producer.produce_background_image()
        if active_image_path:
            image_converted = S.pygame_instance.image.load(
                active_image_path).convert()
            image_converted = S.pygame_instance.transform.flip(
                image_converted,
                random.choice([True, False]),
                random.choice([True, False]))
            S.image = S.pygame_instance.transform.scale(
                image_converted, (W, H*2))

    def add_line(S):
        line_units = S.producer.produce_three_pairs()
        S.stack.append(SemanticsLine(line_units,
                                     S.pygame_instance,
                                     S.W,
                                     S.H,
                                     S.cast_point))
        return S.producer.is_finished()

    def update_positions(S, delta_y):
        for line in S.stack:
            line.move_vertically(delta_y)

    def select_active_line(S, key_states):

        if "down" not in key_states and S.stack:
            halfway = list(filter(lambda _: _.position_y >
                           S.entry_trigger, S.stack))
            active = min(list(filter(lambda _: not _.triggered,
                                     halfway)),
                         key=lambda _: sqrt(
                             (S.action_trigger - _.position_y)**2),
                         default=None)

            if active is not None:
                active.activate()
                S.active_line = active

        for passed in filter(lambda _: _.position_y > S.exit_trigger and not _.triggered,
                             S.stack):
            passed.deactivate()
            if S.active_line == passed:
                S.active_line = None

    def redraw(S):
        for line in S.stack:
            S.drawer.draw_line(line)
        S.drawer.draw_static_ui_elements([S.entry_trigger,
                                          S.exit_trigger,
                                          S.action_trigger])

    def clean(S):
        S.stack = list(filter(lambda _: _.position_y < S.despawn_point,
                              S.stack))

    def get_pressed(S, key_states):
        def mark_pressed(_): return True if _ == "pressed" else False
        return [mark_pressed(_) for _ in key_states]

    def get_feedback(S):
        feedback = sum(_.fetch_feedback()
                       for _ in S.stack if _.feedback is not None)
        global LAST_EVENT
        if feedback > 0:
            LAST_EVENT = "POSITIVE"
        elif feedback < 0:
            LAST_EVENT = "NEGATIVE"
        return feedback

    def process_inputs(S):
        key_states = S.control.get_keys()
        S.drawer.display_keys(key_states)
        S.select_active_line(key_states)

        pressed_keys = S.get_pressed(key_states)

        if S.active_line is not None and any(pressed_keys):
            S.active_line.register_keys(pressed_keys)

    def tick(S, delta_y):
        S.update_positions(delta_y)
        S.clean()
        S.process_inputs()
        S.redraw()

        if S.image:
            S.trans_surface.blit(S.image, (0, S.image_y))
            S.display_instance.blit(S.trans_surface, (0, 0))
            S.image_y += delta_y/3

            if S.image_y >= 0:
                active_image_path = S.producer.produce_background_image()
                if active_image_path:
                    image_converted = S.pygame_instance.image.load(
                        active_image_path).convert()
                    image_converted = S.pygame_instance.transform.flip(
                        image_converted,
                        random.choice([True, False]),
                        random.choice([True, False]))

                    S.image = S.pygame_instance.transform.scale(
                        image_converted, (S.W, S.H*2))
                S.image_y = -1*S.H

        feedback = S.get_feedback()
        return feedback
