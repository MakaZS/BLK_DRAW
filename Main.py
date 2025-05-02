
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import turtle

class BlocklyLogo:
    def __init__(self, root):
        self.root = root
        self.root.title("图形化LOGO")  
        self.root.geometry("400x700")
        self.root.minsize(360, 640)
        self.root.configure(bg="#F5F5F5")
        
        # 初始化数据结构
        self.code = []
        self.repeat_stack = []
        self.current_indent = 0
        
        # 创建界面
        self.create_widgets()
        self.setup_turtle()
        self.setup_gestures()

    # ========= 核心功能方法 =========
    def add_forward(self, steps):
        if not steps.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"FORWARD {steps}")

    def add_backward(self, steps):
        if not steps.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"BACKWARD {steps}")

    def add_right(self, degrees):
        if not degrees.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"RIGHT {degrees}")

    def add_left(self, degrees):
        if not degrees.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"LEFT {degrees}")

    def add_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self._add_command(f"COLOR {color}")

    def add_bgcolor(self):
        color = colorchooser.askcolor()[1]
        if color:
            self._add_command(f"BGCOLOR {color}")
            self.screen.bgcolor(color)

    def add_pensize(self, size):
        if not size.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"PENSIZE {size}")

    def add_circle(self, radius):
        if not radius.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"CIRCLE {radius}")

    def add_dot(self, size):
        if not size.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        self._add_command(f"DOT {size}")

    def add_penup(self):
        self._add_command("PENUP")

    def add_pendown(self):
        self._add_command("PENDOWN")

    def add_repeat(self, times):
        if not times.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字")
            return
        indent = "    " * self.current_indent
        self.code.append(f"{indent}REPEAT {times}")
        self.code.append(f"{indent}  BEGIN")
        self.repeat_stack.append(len(self.code)-1)
        self.current_indent += 1
        self.code.append(f"{indent}ENDREPEAT")
        self.update_code_display()

    def _add_command(self, cmd):
        indent = "    " * self.current_indent
        if self.repeat_stack:
            self.code.insert(self.repeat_stack[-1], f"{indent}{cmd}")
        else:
            self.code.append(f"{indent}{cmd}")
        self.update_code_display()

    # ========= 界面构建方法 =========
    def create_widgets(self):
        main_paned = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=8, bg="#F5F5F5")
        main_paned.pack(fill=tk.BOTH, expand=True)

        # === 指令积木面板 ===
        block_frame = ttk.Frame(main_paned)
        main_paned.add(block_frame, sticky="nsew", minsize=200)

        self.scroll_frame = ttk.Frame(block_frame)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)

        # === 分类积木块 ===
        blocks = [
            ("移动", [
                ("前进", ["步数"], lambda e=None: self.add_forward(e.get())),
                ("后退", ["步数"], lambda e=None: self.add_backward(e.get())),
                ("右转", ["角度"], lambda e=None: self.add_right(e.get())),
                ("左转", ["角度"], lambda e=None: self.add_left(e.get()))
            ]),
            ("画笔", [
                ("颜色", [], lambda: self.add_color()),
                ("背景色", [], lambda: self.add_bgcolor()),
                ("线宽", ["宽度"], lambda e=None: self.add_pensize(e.get())),
                ("抬笔", [], lambda: self.add_penup()),
                ("落笔", [], lambda: self.add_pendown())
            ]),
            ("图形", [
                ("圆形", ["半径"], lambda e=None: self.add_circle(e.get())),
                ("圆点", ["大小"], lambda e=None: self.add_dot(e.get()))
            ]),
            ("控制", [
                ("重复", ["次数"], lambda e=None: self.add_repeat(e.get()))
            ])
        ]

        for category, items in blocks:
            cat_frame = ttk.LabelFrame(self.scroll_frame, text=category, padding=5)
            cat_frame.pack(fill=tk.X, pady=3, padx=2)
            
            for name, fields, cmd in items:
                frame = ttk.Frame(cat_frame)
                frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(frame, text=name, width=4).pack(side=tk.LEFT)
                
                entries = []
                for field in fields:
                    entry = ttk.Entry(frame, width=6)
                    entry.pack(side=tk.LEFT, padx=2)
                    entries.append(entry)
                
                # 修复闭包问题
                if fields:
                    cmd_with_entry = lambda e=entries[0], c=cmd: c(e)
                    ttk.Button(frame, text="＋", width=3, command=cmd_with_entry).pack(side=tk.RIGHT)
                else:
                    ttk.Button(frame, text="＋", width=3, command=cmd).pack(side=tk.RIGHT)

        # === 代码执行区 ===
        bottom_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(bottom_paned, sticky="nsew", minsize=300)

        # 代码编辑器
        code_frame = ttk.Frame(bottom_paned)
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        self.code_text = tk.Text(code_frame, height=8, font=('Microsoft YaHei', 12), wrap=tk.NONE)
        code_scrollx = ttk.Scrollbar(code_frame, orient=tk.HORIZONTAL, command=self.code_text.xview)
        code_scrolly = ttk.Scrollbar(code_frame, command=self.code_text.yview)
        self.code_text.configure(xscrollcommand=code_scrollx.set, yscrollcommand=code_scrolly.set)
        
        self.code_text.grid(row=0, column=0, sticky="nsew")
        code_scrolly.grid(row=0, column=1, sticky="ns")
        code_scrollx.grid(row=1, column=0, sticky="ew")
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(0, weight=1)

        # 功能按钮
        btn_frame = ttk.Frame(bottom_paned)
        btn_frame.pack(fill=tk.X, pady=5, anchor='s')
        
        buttons = [
            ("执行", self.execute_code),
            ("复制", self.copy_code),
            ("清空", self.clear_code),
            ("重置", self.force_restart)
        ]
        
        for text, cmd in buttons:
            btn = ttk.Button(btn_frame, text=text, command=cmd, width=6)
            btn.pack(side=tk.LEFT, padx=3, expand=True)

        # Turtle画布
        self.canvas = tk.Canvas(bottom_paned, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    # ========= 其他方法 =========
    def setup_turtle(self):
        self.screen = turtle.TurtleScreen(self.canvas)
        self.t = turtle.RawTurtle(self.screen)
        self.t.speed(1)
        self.t.pensize(2)
        self.screen.bgcolor("white")

    def setup_gestures(self):
        self.clear_timer = None
        self.code_text.bind("<ButtonPress-1>", self.start_clear_timer)
        self.code_text.bind("<ButtonRelease-1>", self.stop_clear_timer)

    def start_clear_timer(self, event):
        self.clear_timer = self.root.after(1000, self.clear_code)
    
    def stop_clear_timer(self, event):
        if self.clear_timer:
            self.root.after_cancel(self.clear_timer)
            self.clear_timer = None

    def copy_code(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.code_text.get(1.0, tk.END))
        messagebox.showinfo("复制成功", "代码已复制到剪贴板")

    def clear_code(self):
        self.code.clear()
        self.repeat_stack.clear()
        self.current_indent = 0
        self.update_code_display()

    def force_restart(self):
        self.t.clear()
        self.t.reset()
        self.screen.bgcolor("white")
        self.canvas.delete("all")
        self.setup_turtle()

    def update_code_display(self):
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, "\n".join(self.code))

    def execute_code(self):
        self.t.reset()
        self.t.speed(1)
        self.current_indent = 0
        ptr = 0
        
        while ptr < len(self.code):
            line = self.code[ptr].strip()
            try:
                if line.startswith("FORWARD"):
                    self.t.forward(int(line.split()[1]))
                elif line.startswith("BACKWARD"):
                    self.t.backward(int(line.split()[1]))
                elif line.startswith("RIGHT"):
                    self.t.right(int(line.split()[1]))
                elif line.startswith("LEFT"):
                    self.t.left(int(line.split()[1]))
                elif line.startswith("COLOR"):
                    self.t.pencolor(line.split()[1])
                elif line.startswith("BGCOLOR"):
                    self.screen.bgcolor(line.split()[1])
                elif line.startswith("PENSIZE"):
                    self.t.pensize(int(line.split()[1]))
                elif line.startswith("CIRCLE"):
                    self.t.circle(int(line.split()[1]))
                elif line.startswith("DOT"):
                    self.t.dot(int(line.split()[1]))
                elif line.startswith("PENUP"):
                    self.t.penup()
                elif line.startswith("PENDOWN"):
                    self.t.pendown()
                elif line.startswith("REPEAT"):
                    times = int(line.split()[1])
                    start_ptr = ptr
                    end_ptr = self._find_matching_end(start_ptr)
                    loop_body = self.code[start_ptr+1:end_ptr]
                    for _ in range(times):
                        self._execute_block(loop_body)
                    ptr = end_ptr
                elif line == "ENDREPEAT":
                    self.current_indent -= 1
            except Exception as e:
                messagebox.showerror("执行错误", f"第{ptr+1}行: {str(e)}")
                break
            ptr += 1

    def _find_matching_end(self, start):
        nest_level = 1
        for i in range(start+1, len(self.code)):
            if "REPEAT" in self.code[i]:
                nest_level += 1
            elif "ENDREPEAT" in self.code[i]:
                nest_level -= 1
                if nest_level == 0:
                    return i
        return len(self.code)

    def _execute_block(self, block):
        for line in block:
            clean_line = line.strip()
            if clean_line == "BEGIN" or clean_line == "ENDREPEAT":
                continue
            try:
                if clean_line.startswith("FORWARD"):
                    self.t.forward(int(clean_line.split()[1]))
                elif clean_line.startswith("BACKWARD"):
                    self.t.backward(int(clean_line.split()[1]))
                elif clean_line.startswith("RIGHT"):
                    self.t.right(int(clean_line.split()[1]))
                elif clean_line.startswith("LEFT"):
                    self.t.left(int(clean_line.split()[1]))
                elif clean_line.startswith("COLOR"):
                    self.t.pencolor(clean_line.split()[1])
                elif clean_line.startswith("BGCOLOR"):
                    self.screen.bgcolor(clean_line.split()[1])
                elif clean_line.startswith("PENSIZE"):
                    self.t.pensize(int(clean_line.split()[1]))
                elif clean_line.startswith("CIRCLE"):
                    self.t.circle(int(clean_line.split()[1]))
                elif clean_line.startswith("DOT"):
                    self.t.dot(int(clean_line.split()[1]))
                elif clean_line.startswith("PENUP"):
                    self.t.penup()
                elif clean_line.startswith("PENDOWN"):
                    self.t.pendown()
                elif "REPEAT" in clean_line:
                    times = int(clean_line.split()[1])
                    sub_block = block[block.index(line)+1 : block.index("ENDREPEAT")]
                    for _ in range(times):
                        self._execute_block(sub_block)
            except Exception as e:
                messagebox.showerror("循环错误", f"执行指令时出错: {str(e)}")
                return

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*Font', ('Microsoft YaHei', 12))
    root.option_add('*TCombobox*Listbox.font', ('Microsoft YaHei', 12))
    app = BlocklyLogo(root)
    root.mainloop()