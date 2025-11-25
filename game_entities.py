import random

class Entity:
    def __init__(self, name, max_hp, img_url):
        self.name = name.upper()
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.img_url = img_url
        self.statuses = {"vulnerable": 0, "weak": 0}

    def take_damage(self, amount):
        if self.statuses["vulnerable"] > 0:
            amount = int(amount * 1.5)

        if self.block >= amount:
            self.block -= amount
            return 0
        else:
            dmg = amount - self.block
            self.block = 0
            self.hp -= dmg
            return dmg

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def tick_status(self):
        for k in self.statuses:
            if self.statuses[k] > 0: self.statuses[k] -= 1

class Player(Entity):
    def __init__(self, data, deck_pool):
        super().__init__(data['name'], 50, data['img_back'])
        self.energy = 3
        self.max_energy = 3
        self.xp = 0
        self.level = 1
        self.deck = []
        for _ in range(4): self.deck.append(deck_pool[0].copy()) # Scratch
        for _ in range(4): self.deck.append(deck_pool[3].copy()) # Harden
        self.deck.append(deck_pool[2].copy()) # Quick Atk

    def level_up(self):
        self.level += 1
        self.max_hp += 8
        self.hp = self.max_hp

class Enemy(Entity):
    def __init__(self, data, floor):
        scale = 1.0 + (floor * 0.15)
        hp = int(data['hp'] * scale * 0.7)
        super().__init__(data['name'], hp, data['img_front'])
        self.intent = None
        self.base_dmg = 6 + (floor // 2)

    def plan_turn(self):
        r = random.random()
        if r < 0.6:
            dmg = self.base_dmg
            if self.statuses["weak"] > 0: dmg = int(dmg * 0.75)
            self.intent = ("attack", dmg)
        elif r < 0.8:
            self.intent = ("block", self.base_dmg)
        else:
            self.intent = ("buff", 0)