import random

class MarkedAlias():
    def __init__(self, content, key, attached_unit, active = False, image = None, add_meaning = None):
        self.content = content
        self.content_type = "text"
        self.active = active
        self.correct = False
        self.wrong = False
        self.attached_unit = attached_unit
        self.key = key
        self.image = image 
        self.add_meaning = add_meaning

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def register_match(self):
        self.attached_unit.deactivate(positive_feedback = True)

    def register_error(self):
        self.attached_unit.deactivate(positive_feedback = False)

class SemanticUnit():
    def __init__(self, aliases):
        self.aliases = aliases
        self.activated = False
        self.learning_score = 100 
        self.key = id(self)
        self.images = []
        self.add_meanings = []

    def __increment(self):
        self.learning_score += 1
            
    def __decrement(self):
        self.learning_score -= 1 
        if self.learning_score <= 100:
            self.learning_score = 100

    def set_images(self, images_list):
        self.images = images_list

    def set_add_meanings(self, add_meanings):
        self.add_meanings = add_meanings

    def activate(self):
        self.activated = True

    def produce_pair(self):
        add_meaning = random.choice(self.add_meanings) if self.add_meanings and random.randint(1,10) > 8 else None
        add_meaning = add_meaning if self.learning_score <= 101 else None
        if not self.activated:
            selected = [MarkedAlias(_, self.key, self) for _ in random.sample(self.aliases, 2)]
            mean = random.choice(selected)
            mean.add_meaning = add_meaning
            return selected
        else:
            image = random.choice(self.images) if self.images and random.randint(1,10) > 5 else None
            image = image if self.learning_score <= 101 else None
            selected = [MarkedAlias(_, self.key, self, image=image) for _ in random.sample(self.aliases, 2)]

            mean = random.choice(selected)
            mean.add_meaning = add_meaning

            active = random.choice(selected)
            active.activate()
            active.add_meaning = None

            
            return selected

    def deactivate(self, positive_feedback = False):
        if positive_feedback:
            self.__increment()

        if not positive_feedback:
            self.__decrement()

        self.activated = False
