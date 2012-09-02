import random
import livemonitor.measures
import time


class Random(livemonitor.measures.Measure):

    min = 0
    max = 1000

    def update(self):
        new = time.time()
        if new - self.timestamp < 5:
            return
        self.value = random.randint(self.min, self.max)
        self.timestamp = time.time()


def configure():
    return [Random()]
