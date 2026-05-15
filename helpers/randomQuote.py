import requests
import random


def myQuote():
    try:
        rand = random.randint(1, 100)
        response = requests.get("https://dummyjson.com/quotes/{}".format(rand))
        data = response.json()

        delays= ["boss","captain","chief","Ummm did u know that","Hey","So","Guess what","By the way","Oh and also","Also did you know that","Here's a fun fact for you"]
        delay2 = ["it is said by","it is believed by","it is said by","it is believed by","some say that","many say that","it is often said that","it is often believed that","rumor has it that","legend has it that"]
        rand = random.choice(delays)
        rand2 = random.choice(delay2)

        return f"{rand},,,.. {data['quote']}\n  {rand2}... {data['author']}"
    except:
        return "Sorry boss, I couldn't fetch a quote right now."
    