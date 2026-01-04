import random

class TambolaGame:
    def __init__(self):
        self.numbers = list(range(1, 91))
        random.shuffle(self.numbers)

    def draw(self):
        if self.numbers:
            return self.numbers.pop()
        return None
