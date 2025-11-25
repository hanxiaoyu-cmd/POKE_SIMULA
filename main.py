import tkinter as tk
from tkinter import messagebox
import random
from config import COLORS
from data_manager import DataManager
from game_entities import Player, Enemy
from map_system import MapGenerator, MapScene
from battle_scene import BattleScene

class GameManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PokeSpire Pro")
        self.root.geometry("1100x800")
        self.root.configure(bg=COLORS["bg"])

        self.data_mgr = DataManager()
        self.player = None

        self.map_data = None
        self.current_floor = -1
        self.current_node = None

        self.container = tk.Frame(root, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)

        self.show_title()

    def clear(self):
        for w in self.container.winfo_children(): w.destroy()

    def show_title(self):
        self.clear()
        tk.Label(self.container, text="POKE SPIRE", font=("Impact", 50), fg=COLORS["gold"], bg=COLORS["bg"]).pack(pady=100)
        tk.Button(self.container, text="START GAME", font=("Arial", 20), bg=COLORS["shield"], fg="white",
                  command=self.start_game).pack()

    def start_game(self):
        starter = list(self.data_mgr.pokedex.values())[3]
        self.player = Player(starter, self.data_mgr.card_pool)
        self.map_data = MapGenerator.generate()
        self.current_floor = -1
        self.current_node = None
        self.show_map()

    def show_map(self):
        self.clear()
        MapScene(self.container, self).pack(fill="both", expand=True)

    def advance_node(self, node):
        self.current_node = node
        self.current_floor = node.r

        if node.type in ["battle", "elite", "boss"]:
            self.start_battle(node.type)
        elif node.type == "rest":
            self.do_rest()

    def start_battle(self, type_):
        self.clear()
        keys = list(self.data_mgr.pokedex.keys())
        data = self.data_mgr.pokedex[random.choice(keys)]
        enemy = Enemy(data, self.current_floor)

        if type_ == "boss": enemy.max_hp *= 2; enemy.hp = enemy.max_hp; enemy.name = f"[BOSS] {enemy.name}"

        BattleScene(self.container, self, enemy).pack(fill="both", expand=True)

    def victory(self, enemy):
        self.current_node.completed = True
        self.player.xp += 20
        if self.player.xp >= 100:
            self.player.level_up()
            messagebox.showinfo("Level Up", "Max HP Increased!")

        self.card_reward()

    def card_reward(self):
        self.clear()
        tk.Label(self.container, text="Choose a Card", font=("Arial", 30), fg="white", bg=COLORS["bg"]).pack(pady=30)

        cards = random.sample(self.data_mgr.card_pool, 3)
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack()

        for c in cards:
            # Fix: use proper f-string escaping
            btn = tk.Button(frame, text=f"{c['name']}\n{c['desc']}", font=("Arial", 12), width=15, height=6, bg=COLORS["card_bg"],
                            command=lambda x=c: [self.player.deck.append(x), self.show_map()])
            btn.pack(side="left", padx=20)

    def do_rest(self):
        self.current_node.completed = True
        self.player.heal(int(self.player.max_hp * 0.4))
        messagebox.showinfo("Rest", "Restored 40% HP")
        self.show_map()

    def return_to_title(self):
        self.show_title()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameManager(root)
    root.mainloop()