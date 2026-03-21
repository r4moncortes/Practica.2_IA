"""
Interfaz gráfica Tkinter para el 8-puzzle y 15-puzzle.
 
Características:
  - Selector de tamaño (3×3 / 4×4) y heurística.
  - Tablero interactivo con animación paso a paso de la solución.
  - Tabla de métricas comparativa con las 3 heurísticas.
  - Botones: Nuevo puzzle · Resolver · Paso a paso · Reiniciar.
"""
 
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
 
from src.algorithms.a_star import solve_puzzle, is_solvable
from src.algorithms.heuristics import HEURISTICS
from src.utils.metrics import run_puzzle_benchmark, format_table, GOAL_8, GOAL_15
 
# ── Paleta de colores ────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#313244"
TILE_CLR  = "#89b4fa"
TILE_TXT  = "#1e1e2e"
EMPTY_CLR = "#45475a"
ACCENT    = "#a6e3a1"
TEXT_PRI  = "#cdd6f4"
TEXT_SEC  = "#6c7086"
BTN_CLR   = "#585b70"
BTN_HOVER = "#7f849c"
WARN      = "#f38ba8"
 
 
class PuzzleGUI(tk.Frame):
    """Frame principal del puzzle."""
 
    def __init__(self, master: tk.Widget):
        super().__init__(master, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
 
        self.size       = tk.IntVar(value=3)
        self.heuristic  = tk.StringVar(value="Distancia Manhattan")
        self.speed_ms   = tk.IntVar(value=300)
 
        self._solution: List[tuple] = []
        self._step_idx  = 0
        self._current   = tuple(range(1, 9)) + (0,)
        self._goal      = GOAL_8
        self._animating = False
 
        self._build_ui()
        self._new_puzzle()
 
    # ── Construcción de la UI ────────────────────────────────────────────────
 
    def _build_ui(self):
        # Panel izquierdo: tablero
        left = tk.Frame(self, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)
 
        # Controles superiores
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill=tk.X, pady=(0, 10))
 
        tk.Label(ctrl, text="Tamaño:", bg=BG, fg=TEXT_PRI, font=("Courier", 11)).pack(side=tk.LEFT)
        for val, txt in [(3, "8-Puzzle"), (4, "15-Puzzle")]:
            tk.Radiobutton(
                ctrl, text=txt, variable=self.size, value=val,
                bg=BG, fg=TEXT_PRI, selectcolor=SURFACE, activebackground=BG,
                command=self._on_size_change, font=("Courier", 11)
            ).pack(side=tk.LEFT, padx=6)
 
        tk.Label(ctrl, text="  Heurística:", bg=BG, fg=TEXT_PRI, font=("Courier", 11)).pack(side=tk.LEFT)
        h_menu = ttk.Combobox(
            ctrl, textvariable=self.heuristic,
            values=list(HEURISTICS.keys()), state="readonly", width=24
        )
        h_menu.pack(side=tk.LEFT, padx=6)
 
        # Canvas del tablero
        self.canvas = tk.Canvas(left, bg=SURFACE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_board())
 
        # Barra de botones
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill=tk.X, pady=8)
        for txt, cmd in [
            ("🎲 Nuevo",       self._new_puzzle),
            ("▶ Resolver",     self._solve),
            ("⏭ Siguiente",    self._next_step),
            ("⏩ Auto",         self._auto_play),
            ("↺ Reiniciar",    self._reset),
        ]:
            b = tk.Button(btn_row, text=txt, command=cmd,
                          bg=BTN_CLR, fg=TEXT_PRI, activebackground=BTN_HOVER,
                          relief=tk.FLAT, font=("Courier", 10), padx=10, pady=5,
                          cursor="hand2")
            b.pack(side=tk.LEFT, padx=4)
 
        tk.Label(left, text="Velocidad (ms):", bg=BG, fg=TEXT_SEC, font=("Courier", 9)).pack(anchor=tk.W)
        tk.Scale(left, variable=self.speed_ms, from_=50, to=1000,
                 orient=tk.HORIZONTAL, bg=BG, fg=TEXT_PRI,
                 highlightthickness=0, troughcolor=SURFACE).pack(fill=tk.X)
 
        # Panel derecho: info + métricas
        right = tk.Frame(self, bg=BG, width=360)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)
        right.pack_propagate(False)
 
        tk.Label(right, text="Estado", bg=BG, fg=ACCENT,
                 font=("Courier", 13, "bold")).pack(anchor=tk.W)
        self.lbl_status = tk.Label(right, text="Listo", bg=BG, fg=TEXT_PRI,
                                    font=("Courier", 11), wraplength=340, justify=tk.LEFT)
        self.lbl_status.pack(anchor=tk.W, pady=(0, 12))
 
        tk.Label(right, text="Métricas comparativas", bg=BG, fg=ACCENT,
                 font=("Courier", 13, "bold")).pack(anchor=tk.W)
        self.txt_metrics = tk.Text(right, bg=SURFACE, fg=TEXT_PRI,
                                    font=("Courier", 8), relief=tk.FLAT,
                                    state=tk.DISABLED, wrap=tk.NONE)
        self.txt_metrics.pack(fill=tk.BOTH, expand=True)
 
        sb = ttk.Scrollbar(right, orient=tk.HORIZONTAL, command=self.txt_metrics.xview)
        sb.pack(fill=tk.X)
        self.txt_metrics.configure(xscrollcommand=sb.set)
 
    # ── Dibujo del tablero ───────────────────────────────────────────────────
 
    def _draw_board(self, state: tuple = None):
        if state is None:
            state = self._current
        self.canvas.delete("all")
        size = self.size.get()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
        cell = min(w, h) // size
        ox = (w - cell * size) // 2
        oy = (h - cell * size) // 2
 
        for i, val in enumerate(state):
            row, col = divmod(i, size)
            x0 = ox + col * cell + 4
            y0 = oy + row * cell + 4
            x1 = x0 + cell - 8
            y1 = y0 + cell - 8
 
            if val == 0:
                color = EMPTY_CLR
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags="tile")
            else:
                # Color diferente si está en posición correcta
                in_place = (state == self._goal)
                color = ACCENT if in_place else TILE_CLR
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color,
                                              outline=BG, width=2, tags="tile")
                fs = max(cell // 3, 12)
                self.canvas.create_text(
                    (x0 + x1) // 2, (y0 + y1) // 2,
                    text=str(val), fill=TILE_TXT,
                    font=("Courier", fs, "bold"), tags="tile"
                )
 
    # ── Lógica de control ────────────────────────────────────────────────────
 
    def _on_size_change(self):
        self._goal = GOAL_8 if self.size.get() == 3 else GOAL_15
        self._new_puzzle()
 
    def _new_puzzle(self):
        self._animating = False
        self._solution  = []
        self._step_idx  = 0
        size = self.size.get()
        self._goal = GOAL_8 if size == 3 else GOAL_15
        # Generar puzzle resoluble
        goal = list(self._goal)
        state = goal[:]
        for _ in range(80 if size == 3 else 40):
            idx = state.index(0)
            r, c = divmod(idx, size)
            moves = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < size and 0 <= nc < size:
                    moves.append(nr*size+nc)
            swap = random.choice(moves)
            state[idx], state[swap] = state[swap], state[idx]
        self._current = tuple(state)
        self._draw_board()
        self._set_status("Puzzle generado. Pulsa ▶ Resolver.")
        self._clear_metrics()
 
    def _solve(self):
        if self._animating:
            return
        self._set_status("⏳ Resolviendo…")
        self.update_idletasks()
 
        size = self.size.get()
        start = self._current
        goal  = self._goal
 
        def worker():
            res = solve_puzzle(start, goal, size, self.heuristic.get())
            self.after(0, lambda: self._on_solved(res))
            # Benchmark en segundo plano
            bench = run_puzzle_benchmark(size, start)
            self.after(0, lambda: self._show_metrics(bench))
 
        threading.Thread(target=worker, daemon=True).start()
 
    def _on_solved(self, res: dict):
        if res["found"]:
            self._solution = res["solution"]
            self._step_idx = 0
            self._set_status(
                f"✓ Solución encontrada\n"
                f"Movimientos: {res['moves']}  |  "
                f"Nodos: {res['nodes_expanded']}\n"
                f"Tiempo: {res['time_s']} s  |  "
                f"Memoria: {res['memory_kb']} KB"
            )
        else:
            self._set_status("✗ No se encontró solución.")
 
    def _next_step(self):
        if not self._solution or self._step_idx >= len(self._solution):
            return
        self._current = self._solution[self._step_idx]
        self._draw_board()
        self._step_idx += 1
 
    def _auto_play(self):
        if not self._solution:
            messagebox.showinfo("Aviso", "Primero pulsa ▶ Resolver.")
            return
        self._animating = True
        self._step_idx  = 0
        self._animate_step()
 
    def _animate_step(self):
        if not self._animating or self._step_idx >= len(self._solution):
            self._animating = False
            return
        self._current = self._solution[self._step_idx]
        self._draw_board()
        self._step_idx += 1
        self.after(self.speed_ms.get(), self._animate_step)
 
    def _reset(self):
        self._animating = False
        self._solution  = []
        self._step_idx  = 0
        if self._solution:
            self._current = self._solution[0]
        self._draw_board()
        self._set_status("Reiniciado.")
 
    # ── Auxiliares UI ────────────────────────────────────────────────────────
 
    def _set_status(self, msg: str):
        self.lbl_status.config(text=msg)
 
    def _clear_metrics(self):
        self.txt_metrics.config(state=tk.NORMAL)
        self.txt_metrics.delete("1.0", tk.END)
        self.txt_metrics.config(state=tk.DISABLED)
 
    def _show_metrics(self, rows: list):
        table = format_table(rows)
        self.txt_metrics.config(state=tk.NORMAL)
        self.txt_metrics.delete("1.0", tk.END)
        self.txt_metrics.insert(tk.END, table)
        self.txt_metrics.config(state=tk.DISABLED)
 