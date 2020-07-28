import random
import math
import re

class World():
    class Nutrition:
        ANY_ANIMAL = -1
        VEGETATION = 2

    all_animals = []
    day = 1

    @staticmethod
    def hunt(hunter):
        nutrition = hunter.hunting_kinds()
        if nutrition == World.Nutrition.ANY_ANIMAL:
            # three picks from the world
            if not World.all_animals:
                return None
            for attempt in range(3):
                animal = random.choice(World.all_animals)
                if animal.kind == hunter.kind:
                    continue
                success = False
                if animal.weight < hunter.weight:
                    if random.uniform(0.0, 1.0) > 0.2:
                        success = True
                else:
                    if random.uniform(0.0, 1.0) > 0.4:
                        success = True
                if success:
                    World.remove_animal(animal)
                    animal.mortal(0.0, "hunted by {}".format(hunter.kind))
                    return animal
        elif nutrition == World.Nutrition.VEGETATION:
            if random.uniform(0.0, 1.0) > 0.5:
                return Grass()
        return None

    @staticmethod
    def find_nest(hunter):
        if hunter.hunting_kinds() == World.Nutrition.VEGETATION:
            print("{} made a nest!".format(hunter.kind))
            return Nest(hunter)
        animal = World.hunt(hunter)
        if animal is not None:
            print("Found a {} nest!".format(animal.kind))
            return Nest(animal)
        return None

    @staticmethod
    def find_mate(kind, male):
        candidates = [animal for animal in World.all_animals if animal.kind == kind and animal.male == male]
        if not candidates:
            return None
        return random.choice(candidates)

    @staticmethod
    def remove_animal(animal):
        World.all_animals.remove(animal)
        return animal

    @staticmethod
    def add_animal(animal):
        World.all_animals.append(animal)
        return animal

    @staticmethod
    def live():
        someone_alive = False
        for animal in World.all_animals:
            if animal.is_alive():
                someone_alive = True
                animal.routine()
        World.day += 1
        return someone_alive

    @staticmethod
    def day_of_year():
        return World.day % 360

    @staticmethod
    def print_stats():
        kinds = {}
        for animal in World.all_animals:
            if animal.is_alive():
                if animal.kind not in kinds:
                    kinds[animal.kind] = 0
                kinds[animal.kind] += 1
        for k, v in kinds.items():
            print("    {} {}{}".format(v, k, "" if v==1 else "s"))


class Nest():
    def __init__(self, previous_owner):
        self.previous_owner = previous_owner
        self.store = list(filter(lambda x: x is not None, [World.hunt(previous_owner) for a in range(random.randint(0, 8))]))

class Mammal():
    def __init__(self, parent, kind):
        self.kind = kind
        self.parent = parent
        self.age = 0
        self.length = self.birth_length()
        self.weight = self.birth_weight()
        self.male = random.choice([True, False])
        factor = 0.8 if not self.male else 1.0
        self.growth_per_day = {
            "length": random.uniform(0.05, 0.07) * factor,
            "weight": random.uniform(0.22, 0.30) * factor
        }
        self.nest = None
        self.hunger = 0
        self.children = []
        self.status = None
        self.alive = True
        self.name = self.generate_name()
        self.set_status("newborn")

    def birth_length(self):
        return 1.0  # cm

    def birth_weight(self):
        return 0.001  # cm

    def adult_in_days(self):
        return 60

    def hunting_kinds(self):
        return World.Nutrition.VEGETATION

    def generate_name(self):
        syllables = ["hiss", "his", "sis", "shis", "is", "s", "sss", "ssk"]
        name = ""
        for a in range(random.randint(1,4)):
            name += random.choice(syllables)
        return name.capitalize()

    def is_mating_season(self):
        doy = World.day_of_year()
        return doy > 60 and doy < 260

    def what_does_it_say(self, circumstance):
        if not self.is_adult:
            return "peep"
        else:
            return "hisss"

    def set_status(self, status):
        self.status = status
        print("{} {} is {}".format(self.kind.capitalize(), self.name, self.status))

    def is_adult(self):
        return self.age >= self.adult_in_days()

    def is_alive(self):
        return self.alive

    def sleep(self):
        self.age += 1

    def wake(self):
        self.set_status("awake")

    def grow(self):
        if not self.is_adult():
            self.length += self.growth_per_day["length"]
            self.weight += self.growth_per_day["weight"]
        if self.age == 180:
            self.set_status("adult")
            self.sound(self.what_does_it_say("became_adult"))

    def routine(self):
        self.grow()
        if self.mortal(0.998, "randomly"):
            return
        self.wake()
        if not self.is_adult():
            if self.eat(self.parent.feed()):
                self.sound(self.what_does_it_say("eating"))
            else:
                self.sound(self.what_does_it_say("hungry"))
                if self.mortal(0.999, "poisoning"):
                    return
            self.sleep()
            return
        self.eat(World.hunt(self))
        if self.hunger > 32:
            if self.mortal(0.5, "hunger"):
                return
        if self.children:
            try:
                self.cache(World.hunt(self))
                self.set_status("happy")
            except:
                self.set_status("sad")
                self.sound(self.what_does_it_say("miss"))
        if self.nest is None:
            self.nest = World.find_nest(self)
            if self.nest is not None:
                self.set_status("happy")
                self.sound(self.what_does_it_say("nest"))
        if self.age > 4 * 360:
            if self.mortal(0.998, "old age"):
                return
        else:
            if self.mortal(0.999, "randomly"):
                return
        if self.is_adult():
            if self.is_mating_season():
                if random.uniform(0.0, 1.0) > 0.99:
                    self.mate(World.find_mate(self.kind, not self.male))
        self.sleep()

    def mortal(self, rate, cause):
        if random.uniform(0.0, 1.0) > rate:
            self.alive = False
            self.sound(self.what_does_it_say("dying"))
            self.set_status("dead ({})".format(cause))
            print("{} {} lived {} days.".format(self.kind.capitalize(), self.name, self.age))
            if self.children:
                nc = len(self.children)
                print("  It had {} child{}.".format(nc, "ren" if nc > 1 else "",))
                for child in self.children:
                    print("    {} ({} {} days)".format(child.name, "alive and" if child.is_alive() else "dead at", child.age))
            return True
        return False

    def mate(self, other):
        if other is None:
            self.sound(self.what_does_it_say("no_mate"))
            self.set_status("unhappy")
            return
        else:
            if not self.male:
                for a in range(random.randint(4, 9)):
                    new_mammal = World.add_animal(self.__class__(self))
                    self.children.append(new_mammal)

    def eat(self, food):
        if food is None:
            self.hunger += 1
            self.set_status("hungry")
            return False
        print("{} {} eats a {}: {}".format(self.kind.capitalize(), self.name, food.kind, food.name))
        self.set_status("content")
        self.hunger = 0
        return True

    def cache(self, prey):
        if prey is None:
            raise Exception()
        if self.nest is None:
            raise Exception()
        self.nest.store.append(prey)

    def feed(self):
        if self.nest is not None:
            if self.nest.store:
                return self.nest.store.pop(0)
        return None

    def sound(self, text):
        print("{} {} says: {}".format(self.kind.capitalize(), self.name, text))



class Weasel(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "weasel")

    def birth_length(self):
        return 2.0  # cm

    def birth_weight(self):
        return 0.003  # cm

    def adult_in_days(self):
        return 180

    def hunting_kinds(self):
        return World.Nutrition.ANY_ANIMAL

    def what_does_it_say(self, circumstance):
        if not self.is_adult:
            return "squeak"
        else:
            return "growl"

    def generate_name(self):
        syllables = ["ma", "wa", "sha", "bi", "gu", "di", "du", "bi", "la", "qui", "bo", "zi", "za"]
        name = ""
        for a in range(random.randint(2,4)):
            name += random.choice(syllables)
        return name.capitalize()

    def is_mating_season(self):
        doy = World.day_of_year()
        return doy > 20 and doy < 60



class Mouse(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "mouse")

class Rat(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "rat")

class Squirrel(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "squirrel")

class Chipmunk(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "chipmunk")

class Shrew(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "shrew")

class Mole(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "mole")

class Rabbit(Mammal):
    def __init__(self, parent):
        Mammal.__init__(self, parent, "rabbit")


# nutrition
class Grass():
    def __init__(self):
        self.kind = "grass"
        self.name = random.choice(["bahia", "bermuda", "buffalo", "centipede", "fescue", "zoysia"])



for p in range(32):
    for kind in [Mouse, Rat, Squirrel, Chipmunk, Shrew, Mole, Rabbit]:
        parent = kind(None)
        parent.male = p % 2 == 0
        parent.age = 180 + random.randint(0, 180)
        World.add_animal(parent)

for p in range(4):
    parent = Weasel(None)
    parent.male = p % 2 == 0
    parent.age = 180 + random.randint(0, 180)
    World.add_animal(parent)


day = 1
while World.live():
    print("Another day passes. It is day {}.".format(day))
    print("The world consists of: ")
    World.print_stats()
    day += 1

print("All followed animal populations are dead.")
