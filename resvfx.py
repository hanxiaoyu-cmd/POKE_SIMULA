import os

# 目标文件：战斗场景逻辑
target_file = "battle_scene.py"

# 包含完整 VFX 的代码
new_code = r"""
import tkinter as tk
import random
from config import COLORS, FONTS
from tkinter import messagebox

class BattleScene(tk.Frame):
    def __init__(self, master, game_manager, enemy):
        super().__init__(master, bg=COLORS["bg"])
        self.gm = game_manager
        self.player = game_manager.player
        self.enemy = enemy

        self.hand = []
        self.draw_pile = self.player.deck.copy()
        random.shuffle(self.draw_pile)
        self.discard_pile = []

        self.setup_ui()
        self.start_turn()

    def setup_ui(self):
        # === 布局配置 ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=3) # 战场高
        self.grid_rowconfigure(1, weight=2) # 手牌低

        # === 战场区域 ===
        self.arena = tk.Frame(self, bg=COLORS["bg"])
        self.arena.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)

        # --- 玩家 (左) ---
        self.p_frame = tk.Frame(self.arena, bg=COLORS["bg"])
        self.p_frame.pack(side="left", fill="y", padx=50)

        self.p_img_lbl = tk.Label(self.p_frame, bg=COLORS["bg"])
        # 图片稍大一点，视觉更佳
        img = self.gm.data_mgr.get_image(self.player.img_url, (220, 220))
        self.p_img_lbl.config(image=img)
        self.p_img_lbl.image = img
        self.p_img_lbl.pack()

        self.p_stats = tk.Label(self.p_frame, text="", font=FONTS["h2"], fg="white", bg=COLORS["bg"])
        self.p_stats.pack()

        # --- 敌人 (右) ---
        self.e_frame = tk.Frame(self.arena, bg=COLORS["bg"])
        self.e_frame.pack(side="right", fill="y", padx=50)

        self.e_img_lbl = tk.Label(self.e_frame, bg=COLORS["bg"])
        e_img = self.gm.data_mgr.get_image(self.enemy.img_url, (220, 220))
        self.e_img_lbl.config(image=e_img)
        self.e_img_lbl.image = e_img
        self.e_img_lbl.pack()

        self.e_intent = tk.Label(self.e_frame, text="", font=("Arial", 16, "bold"), fg=COLORS["enemy_hp"], bg=COLORS["bg"])
        self.e_intent.pack()
        self.e_stats = tk.Label(self.e_frame, text="", font=FONTS["h2"], fg="white", bg=COLORS["bg"])
        self.e_stats.pack()

        # === 控制面板 ===
        self.ctrl_panel = tk.Frame(self, bg=COLORS["panel"], height=280)
        self.ctrl_panel.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.ctrl_panel.pack_propagate(False)

        # 信息区
        info_box = tk.Frame(self.ctrl_panel, bg=COLORS["panel"])
        info_box.pack(side="left", padx=20, fill="y", pady=10)

        self.lbl_energy = tk.Label(info_box, text="E: 3/3", font=("Impact", 28), fg=COLORS["energy"], bg=COLORS["panel"])
        self.lbl_energy.pack(pady=10)

        tk.Button(info_box, text="END TURN", bg="#c0392b", fg="white", font=("Arial", 12, "bold"), width=12,
                  command=self.end_turn).pack(pady=5)

        self.btn_catch = tk.Button(info_box, text="CATCH (2E)", bg=COLORS["gold"], state="disabled", width=12,
                                   command=self.try_catch)
        self.btn_catch.pack(pady=5)

        # 手牌容器
        self.hand_box = tk.Frame(self.ctrl_panel, bg=COLORS["panel"])
        self.hand_box.pack(side="left", fill="both", expand=True, padx=20)

    # ==========================
    #  核心 VFX (视觉特效) 函数
    # ==========================
    def vfx_float_text(self, parent_frame, text, color):
        # 创建一个临时 Label
        lbl = tk.Label(parent_frame, text=text, fg=color, bg=COLORS["bg"], font=("Impact", 24))
        # 使用 place 绝对定位，初始位置在中间偏上
        lbl.place(relx=0.5, rely=0.3, anchor="center")

        def _anim(step):
            if step > 20: 
                lbl.destroy()
                return
            # 向上飘动: 减小 rely
            lbl.place(relx=0.5, rely=0.3 - (step*0.015), anchor="center")
            self.after(30, lambda: _anim(step+1))
        _anim(0)

    def vfx_flash(self, widget, color, times=2):
        orig = widget.cget("bg")
        def _step(n):
            if n <= 0: widget.config(bg=orig); return
            # 偶数次显示颜色，奇数次还原
            curr = color if n % 2 != 0 else orig
            widget.config(bg=curr)
            self.after(80, lambda: _step(n-1))
        _step(times*2)

    def vfx_shake(self, widget):
        orig_pad = int(widget.pack_info().get('padx', 0))
        def _step(n):
            if n <= 0: widget.pack_configure(padx=orig_pad); return
            # 左右摆动 padding
            off = 10 if n % 2 == 0 else -10
            try: widget.pack_configure(padx=orig_pad + off)
            except: pass
            self.after(50, lambda: _step(n-1))
        _step(6)

    # ==========================
    #  逻辑与更新
    # ==========================
    def update_ui(self):
        # 玩家
        p = self.player
        p_ex = ""
        if p.statuses['vulnerable']: p_ex += " [Vuln]"
        if p.statuses['weak']: p_ex += " [Weak]"
        self.p_stats.config(text=f"{p.name}\nHP: {p.hp}/{p.max_hp}\nShield: {p.block}{p_ex}")
        self.lbl_energy.config(text=f"E: {p.energy}/{p.max_energy}")

        # 敌人
        e = self.enemy
        e_ex = ""
        if e.statuses['vulnerable']: e_ex += " [Vuln]"
        if e.statuses['weak']: e_ex += " [Weak]"

        itype, val = e.intent
        if itype == "attack": intent = f"⚔️ Attack {val}"
        elif itype == "block": intent = f"🛡️ Block {val}"
        else: intent = "💪 Buffing"
        self.e_intent.config(text=intent)
        self.e_stats.config(text=f"{e.name}\nHP: {e.hp}/{e.max_hp}\nShield: {e.block}{e_ex}")

        # 按钮状态
        if p.energy >= 2: self.btn_catch.config(state="normal", bg=COLORS["gold"])
        else: self.btn_catch.config(state="disabled", bg="#7f8c8d")

        # 手牌
        for w in self.hand_box.winfo_children(): w.destroy()
        for i, card in enumerate(self.hand):
            self.draw_card(card, i)

    def draw_card(self, card, index):
        cf = tk.Frame(self.hand_box, bg=COLORS["card_bg"], bd=2, relief="raised", width=110, height=180)
        cf.pack_propagate(False)
        cf.pack(side="left", padx=5, pady=10)

        h_col = COLORS["panel"]
        if card['type'] == 'attack': h_col = COLORS["enemy_hp"]
        elif card['type'] == 'skill': h_col = COLORS["shield"]

        tk.Label(cf, text=card['name'], bg=h_col, fg="white", font=FONTS["card_title"]).pack(fill="x")
        tk.Label(cf, text=f"{card['cost']} Energy", bg="#95a5a6", fg="white", font=("Arial", 8)).pack(fill="x")
        tk.Label(cf, text=card['desc'], bg=COLORS["card_bg"], wraplength=100, font=FONTS["card_desc"]).pack(expand=True)

        state = "normal" if self.player.energy >= card['cost'] else "disabled"
        btn_bg = h_col if state == "normal" else "#bdc3c7"
        tk.Button(cf, text="PLAY", bg=btn_bg, fg="white", state=state,
                  command=lambda: self.play_card(card, index)).pack(fill="x", side="bottom")

    def start_turn(self):
        self.player.energy = self.player.max_energy
        self.player.block = 0
        for _ in range(5):
            if not self.draw_pile:
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                random.shuffle(self.draw_pile)
            if self.draw_pile:
                self.hand.append(self.draw_pile.pop())
        self.enemy.plan_turn()
        self.update_ui()

    def play_card(self, card, index):
        self.player.energy -= card['cost']
        self.hand.pop(index)
        self.discard_pile.append(card)

        eff = card['effect']
        val = card['val']

        if eff == 'deal':
            self.deal_damage_to_enemy(val)
        elif eff == 'multi':
            self.deal_damage_to_enemy(val)
            self.after(300, lambda: self.deal_damage_to_enemy(val))
        elif eff == 'block':
            self.player.block += val
            self.vfx_flash(self.p_img_lbl, COLORS["shield"])
            self.vfx_float_text(self.p_frame, f"+{val} Shield", COLORS["shield"])
        elif eff == 'heal':
            self.player.heal(val)
            self.vfx_flash(self.p_img_lbl, "#2ecc71")
            self.vfx_float_text(self.p_frame, f"+{val} HP", "#2ecc71")
        elif eff == 'energy':
            self.player.energy += val
            self.vfx_float_text(self.p_frame, f"+{val} Energy", COLORS["energy"])
        elif eff == 'draw':
            self.vfx_float_text(self.p_frame, f"Draw {val}", "white")
            for _ in range(val):
                if self.draw_pile or self.discard_pile:
                    if not self.draw_pile:
                        self.draw_pile = self.discard_pile.copy()
                        self.discard_pile = []
                        random.shuffle(self.draw_pile)
                    self.hand.append(self.draw_pile.pop())
        elif eff == 'vulnerable':
            self.enemy.statuses['vulnerable'] += val
            self.vfx_float_text(self.e_frame, "VULN!", "purple")
        elif eff == 'weak':
            self.enemy.statuses['weak'] += val
            self.vfx_float_text(self.e_frame, "WEAK!", "gray")

        self.update_ui()
        self.check_win()

    def deal_damage_to_enemy(self, base):
        dmg = base
        if self.player.statuses['weak'] > 0: dmg = int(dmg * 0.75)
        real = self.enemy.take_damage(dmg)

        # 触发特效
        self.vfx_shake(self.e_img_lbl)
        self.vfx_flash(self.e_img_lbl, COLORS["enemy_hp"])
        self.vfx_float_text(self.e_frame, f"-{real}", COLORS["enemy_hp"])

    def end_turn(self):
        self.discard_pile.extend(self.hand)
        self.hand = []

        etype, val = self.enemy.intent
        if etype == "attack":
            dmg = val
            if self.player.statuses['vulnerable'] > 0: dmg = int(dmg * 1.5)
            real = self.player.take_damage(dmg)

            # 玩家受击特效
            self.vfx_shake(self.p_img_lbl)
            self.vfx_flash(self.p_img_lbl, COLORS["enemy_hp"])
            self.vfx_float_text(self.p_frame, f"-{real}", "red")

        elif etype == "block":
            self.enemy.block += val
            self.vfx_flash(self.e_img_lbl, COLORS["shield"])
            self.vfx_float_text(self.e_frame, f"+{val} Shield", COLORS["shield"])

        elif etype == "buff":
            self.vfx_float_text(self.e_frame, "BUFF!", "yellow")

        self.player.tick_status()
        self.enemy.tick_status()

        if self.player.hp <= 0:
            messagebox.showerror("Defeat", "You fainted...")
            self.gm.return_to_title()
            return

        self.start_turn()

    def try_catch(self):
        self.player.energy -= 2
        rate = (self.enemy.max_hp - self.enemy.hp) / self.enemy.max_hp + 0.2
        self.vfx_float_text(self.e_frame, "Pokeball!", COLORS["gold"])

        if random.random() < rate:
            self.after(600, lambda: [
                messagebox.showinfo("Gotcha!", f"{self.enemy.name} caught!"),
                self.player.deck.append({"name": f"{self.enemy.name} Soul", "cost": 1, "val": 15, "type": "attack", "effect": "deal", "desc": "Soul Attack 15"}),
                self.gm.victory(self.enemy)
            ])
        else:
            self.after(600, lambda: self.vfx_float_text(self.e_frame, "Escaped!", "white"))
            self.update_ui()

    def check_win(self):
        if self.enemy.hp <= 0:
            self.vfx_flash(self.e_img_lbl, "black", 4)
            self.after(800, lambda: self.gm.victory(self.enemy))
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(new_code.strip())

print(f"特效已修复：{target_file} 更新完毕。")
print("请重新运行 python main.py")