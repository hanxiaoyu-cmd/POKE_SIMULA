import os

# 目标文件
target_file = "map_system.py"

# 新的 map_system.py 代码
new_code = r"""
import random
import tkinter as tk
from config import COLORS

class MapNode:
    def __init__(self, r, c, type_):
        self.r = r
        self.c = c
        self.type = type_ # battle, rest, elite, boss
        self.next_nodes = []
        self.completed = False

class MapGenerator:
    ROWS = 10 # 10 层
    COLS = 5  # 5 列宽

    @staticmethod
    def generate():
        map_data = []
        # 1. 生成节点
        for r in range(MapGenerator.ROWS):
            row_nodes = []
            for c in range(MapGenerator.COLS):
                # 生成逻辑
                if r == 0 or r == MapGenerator.ROWS - 1 or random.random() > 0.35:
                    ntype = "battle"
                    if r == MapGenerator.ROWS - 1: ntype = "boss"
                    elif r % 4 == 0 and r != 0: ntype = "rest"
                    elif random.random() < 0.15: ntype = "elite"

                    row_nodes.append(MapNode(r, c, ntype))
                else:
                    row_nodes.append(None)
            map_data.append(row_nodes)

        # 2. 建立连接
        for r in range(MapGenerator.ROWS - 1):
            for c, node in enumerate(map_data[r]):
                if node is None: continue
                potential_next = []
                start_k = max(0, c - 1)
                end_k = min(MapGenerator.COLS, c + 2)
                for k in range(start_k, end_k):
                    if map_data[r+1][k] is not None:
                        potential_next.append(k)

                # 保底连接
                if not potential_next:
                    # 如果前方无路，强制在正前方生成一个战斗节点
                    map_data[r+1][c] = MapNode(r+1, c, "battle")
                    potential_next.append(c)

                node.next_nodes = potential_next

        # 3. Boss 汇聚
        boss_node = MapNode(MapGenerator.ROWS-1, 2, "boss")
        map_data[MapGenerator.ROWS-1] = [None, None, boss_node, None, None]
        for node in map_data[MapGenerator.ROWS-2]:
            if node: node.next_nodes = [2]

        return map_data

class MapScene(tk.Frame):
    def __init__(self, master, game_manager):
        super().__init__(master, bg=COLORS["bg"])
        self.gm = game_manager
        self.canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_map()

    def draw_map(self):
        self.canvas.delete("all")
        data = self.gm.map_data
        cw = 1000
        ch = 700
        y_step = ch / (len(data) + 1)
        x_step = cw / (len(data[0]) + 1)

        # === 1. 绘制连线 ===
        for r, row in enumerate(data):
            for c, node in enumerate(row):
                if not node: continue
                x = (c + 1) * x_step
                y = ch - (r + 1) * y_step

                # 确定当前节点是否是“活跃路径”的一部分
                # 简单逻辑：如果节点已完成，或者是当前可选节点，线画亮一点
                line_color = COLORS["map_path"]

                for next_c in node.next_nodes:
                    nx = (next_c + 1) * x_step
                    ny = ch - (r + 2) * y_step

                    # 虚线效果
                    self.canvas.create_line(x, y, nx, ny, fill=line_color, width=2, dash=(4, 2))

        # === 2. 绘制 Emoji 节点 ===
        # Emoji 映射表
        ICONS = {
            "battle": "⚔️",   # 双剑
            "elite": "👹",    # 鬼脸 (强敌)
            "rest": "🔥",     # 火堆
            "boss": "👑"      # 皇冠
        }

        for r, row in enumerate(data):
            for c, node in enumerate(row):
                if not node: continue
                x = (c + 1) * x_step
                y = ch - (r + 1) * y_step

                icon = ICONS.get(node.type, "❓")
                state = "disabled"

                # 视觉样式逻辑
                # 默认为灰色/暗色
                fill_color = "#555" 
                font_size = 24

                # 逻辑判断：是否可选
                is_accessible = False

                if r == 0 and self.gm.current_floor == -1:
                    is_accessible = True
                elif self.gm.current_node and r == self.gm.current_node.r + 1:
                    if c in self.gm.current_node.next_nodes:
                        is_accessible = True

                # 状态机
                if node.completed:
                    icon = "✅" # 已完成变为对勾，或者保持原样变暗
                    fill_color = "#2ecc71" # 绿色
                    font_size = 20
                elif is_accessible:
                    state = "normal"
                    fill_color = "#fff" # 高亮白色
                    font_size = 36 # 变大，产生"跳动"的视觉感
                    # 给可选节点加一个光圈背景
                    self.canvas.create_oval(x-25, y-25, x+25, y+25, outline="#f1c40f", width=2, dash=(2,2))
                else:
                    # 未解锁的层级
                    fill_color = "#7f8c8d" 

                # 特殊：Boss 总是显眼一点
                if node.type == "boss" and not node.completed:
                    font_size = 40
                    if is_accessible: fill_color = "#f1c40f"

                tag = f"node_{r}_{c}"

                # 绘制 Emoji
                # 注意：Windows 上 Tkinter 有时需要特定字体才能显示彩色 Emoji，
                # 这里使用 Segoe UI Emoji (Win) 或 Apple Color Emoji (Mac) 兜底
                self.canvas.create_text(x, y, text=icon, fill=fill_color, 
                                      font=("Segoe UI Emoji", font_size), tags=tag)

                if state == "normal":
                    self.canvas.tag_bind(tag, "<Button-1>", lambda e, n=node: self.on_node_click(n))
                    # 鼠标悬停效果
                    self.canvas.tag_bind(tag, "<Enter>", lambda e, t=tag: self.canvas.itemconfig(t, fill="#3498db"))
                    self.canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: self.canvas.itemconfig(t, fill="#fff"))

    def on_node_click(self, node):
        self.gm.advance_node(node)
"""

# 写入文件
with open(target_file, "w", encoding="utf-8") as f:
    f.write(new_code.strip())

print(f"成功升级 {target_file}！现在地图将显示 Emoji 图标。")
print("请运行 python main.py 查看效果。")