import random

class Ticket:
    def __init__(self):
        numbers = random.sample(range(1, 91), 15)
        self.rows = [
            numbers[0:5],
            numbers[5:10],
            numbers[10:15]
        ]
        self.marked = set()

    def mark(self, number):
        if number in self.all_numbers():
            self.marked.add(number)

    def all_numbers(self):
        return [num for row in self.rows for num in row]

    def check_row(self, index):
        return all(num in self.marked for num in self.rows[index])

    def full_house(self):
        return len(self.marked) == 15
