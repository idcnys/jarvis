import random

class Compliment:
    def __init__(self):
        self.compliments = [
            "You're an awesome person!",
            "You have a great sense of humor!",
            "You're a joy to be around!",
            "Your perspective is refreshing!",
            "You're a great listener!",
            "You have impeccable manners!",
            "You're even more beautiful on the inside than on the outside!",
            "You're like sunshine on a rainy day!",
            "You bring out the best in other people!",
            "You're a smart cookie!",
            "You are awesome!",
            "You have a good heart!",
            "You light up the room!",
            "You deserve a hug right now!",
            "You should be proud of yourself!"
        ]
        self.compliment_text = None
    
    def make_compliment(self):
        self.compliment_text = random.choice(self.compliments)
        return self.compliment_text

def get_compliment():
    return Compliment().make_compliment()