import requests
import json
import os
import io
from PIL import Image, ImageTk

class DataManager:
    CACHE_FILE = "pokespire_data.json"

    def __init__(self):
        self.pokedex = {}
        self.card_pool = []
        self.img_cache = {}
        self.load_or_fetch()

    def load_or_fetch(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self.pokedex = data['pokedex']
                    self.card_pool = data['cards']
                return
            except: pass

        # 模拟下载数据
        self.pokedex = {}
        # 下载前30只
        for i in range(1, 31):
            try:
                res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}", timeout=2)
                d = res.json()
                self.pokedex[d['name']] = {
                    'name': d['name'],
                    'hp': d['stats'][0]['base_stat'],
                    'img_front': d['sprites']['front_default'],
                    'img_back': d['sprites']['back_default']
                }
            except: pass

        # === 扩展卡牌库 ===
        self.card_pool = [
            {"name": "Scratch", "cost": 1, "val": 6, "type": "attack", "effect": "deal", "desc": "Deal 6 Dmg"},
            {"name": "Tackle", "cost": 1, "val": 6, "type": "attack", "effect": "deal", "desc": "Deal 6 Dmg"},
            {"name": "Quick Atk", "cost": 0, "val": 4, "type": "attack", "effect": "deal", "desc": "Deal 4 Dmg"},
            {"name": "Harden", "cost": 1, "val": 6, "type": "skill", "effect": "block", "desc": "Gain 6 Block"},
            {"name": "Iron Def", "cost": 2, "val": 12, "type": "skill", "effect": "block", "desc": "Gain 12 Block"},
            {"name": "Double Hit", "cost": 1, "val": 4, "type": "attack", "effect": "multi", "desc": "Deal 4 Dmg x2"},
            {"name": "Meditate", "cost": 0, "val": 2, "type": "skill", "effect": "energy", "desc": "Gain 2 Energy"},
            {"name": "Leer", "cost": 0, "val": 2, "type": "skill", "effect": "vulnerable", "desc": "Enemy Vuln 2 trns"},
            {"name": "Growl", "cost": 1, "val": 2, "type": "skill", "effect": "weak", "desc": "Enemy Weak 2 trns"},
            {"name": "Potion", "cost": 1, "val": 8, "type": "skill", "effect": "heal", "desc": "Heal 8 HP"},
            {"name": "Planning", "cost": 1, "val": 2, "type": "skill", "effect": "draw", "desc": "Draw 2 Cards"},
            {"name": "Hyper Beam", "cost": 3, "val": 25, "type": "attack", "effect": "deal", "desc": "Deal 25 Dmg"}
        ]

        with open(self.CACHE_FILE, 'w') as f:
            json.dump({'pokedex': self.pokedex, 'cards': self.card_pool}, f)

    def get_image(self, url, size=(160, 160)):
        if not url: return None
        if url in self.img_cache: return self.img_cache[url]
        try:
            res = requests.get(url, timeout=3)
            img = Image.open(io.BytesIO(res.content)).resize(size, Image.Resampling.NEAREST)
            tk_img = ImageTk.PhotoImage(img)
            self.img_cache[url] = tk_img
            return tk_img
        except: return None