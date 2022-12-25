import random

class MarkedAlias():
    def __init__(self, content, key, attached_unit, active = False):
        self.content = content
        self.content_type = "text"
        self.active = active
        self.correct = False
        self.wrong = False
        self.attached_unit = attached_unit
        self.key = key

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

    def __increment(self):
        self.learning_score += 1
            
    def __decrement(self):
        self.learning_score -= 1 
        if self.learning_score <= 100:
            self.learning_score = 100

    def activate(self):
        self.activated = True

    def produce_pair(self):
        if not self.activated:
            return [MarkedAlias(_, self.key, self) for _ in random.sample(self.aliases, 2)]
        else:
            selected = [MarkedAlias(_, self.key, self) for _ in random.sample(self.aliases, 2)]
            active = random.choice(selected)
            active.activate()
            
            return selected

    def deactivate(self, positive_feedback = False):
        if positive_feedback:
            self.__increment()

        if not positive_feedback:
            self.__decrement()

        self.activated = False
