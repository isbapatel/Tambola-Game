from ticket import Ticket

class Player:
    def __init__(self, name):
        self.name = name
        self.ticket = Ticket()
        self.claims = {
            "row1": False,
            "row2": False,
            "row3": False,
            "full_house": False
        }
