
class Counter():
    def __init__(self, drop_time):
        self.drop_time = drop_time
        self.time_elapsed = drop_time*0.8

    def is_tick(self, time_delta):
        self.time_elapsed += time_delta
        if self.time_elapsed >= self.drop_time:
            self.time_elapsed = 0
            return True
        else:
            return False

    def update_drop(self, new_drop):
        self.drop_time = new_drop

def global_timer(pygame_instance):
    last_frame_timestamp = 0
    current_frame_timestamp = pygame_instance.time.get_ticks()
    frame_timedelta = 0
    while True:
        current_frame_timestamp = pygame_instance.time.get_ticks()
        frame_timedelta = (current_frame_timestamp - last_frame_timestamp)
        last_frame_timestamp = current_frame_timestamp
        yield frame_timedelta

class Progression():
    def __init__(self,
                 value_constraint,
                 time_to_see,
                 time_to_update,
                 update_counter,
                 ui_ref):

        self.correct = 18
        self.missed  = 2
        self.offset  = 30 
        self.new_event = False
        self.correct_event = False
        self.combo = 0

        self.value_constraint = value_constraint
        self.time_to_see = time_to_see
        self.time_to_update = time_to_update
        self.update_counter = update_counter

        self.speed = value_constraint / time_to_see

        self.ui_ref = ui_ref

    def get_percent(self):
        percent = self.correct / (self.correct + self.missed)
        self.ui_ref.percent = percent
        return percent

    def register_correct(self):
        if self.correct <= 20:
            self.correct += 1
        else:
            if self.missed > 0:
                self.missed -= 1
        self.new_event = True
        self.correct_event = True
        self.combo += 1
        self.ui_ref.combo = self.combo

    def register_miss(self):
        if self.missed <= 20:
            self.missed += 1
        else:
            if self.correct >0:
                self.correct -= 1
        self.new_event = True
        self.correct_event = False
        self.combo = 0
        self.ui_ref.combo = self.combo

    def register_event(self, value):
        if value > 0:
            self.register_correct()
        elif value < 0:
            self.register_miss()


        if self.get_percent() == 0:
            return False

        return True

    def is_more_intense_required(self):

        if self.get_percent() > 0.75:
            return True

        return False

    def is_less_intense_required(self):

        if self.get_percent() < 0.70:
            return True

        return False

    def synchronize_speed(self):
        if self.new_event:
            self.new_event = False

            if self.is_more_intense_required() and self.correct_event:
                self.time_to_see -= 1000 
                self.time_to_update -= 250 

                if self.time_to_see < 6000:
                    self.time_to_see = 6000

                if self.time_to_update < 2500:
                    self.time_to_update = 2500

            elif self.is_less_intense_required() and not self.correct_event:
                self.time_to_see += 1000
                self.time_to_update += 250
                
                if self.time_to_see > 10000:
                    self.time_to_see = 10000

                if self.time_to_update > 5000:
                    self.time_to_update = 5000

            self.speed = self.value_constraint / self.time_to_see    
            self.ui_ref.speed_index = self.time_to_see
            self.update_counter.update_drop(self.time_to_update)
        return self.speed
