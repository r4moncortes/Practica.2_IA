"""
Interfaz gráfica Tkinter para resolver Sudoku con A* y Simulated Annealing.
 
Características:
  - Selector de nivel: Fácil (20) / Intermedio (35) / Difícil (45) celdas vacías.
  - Selector de algoritmo: A* (backtracking+MRV) o Simulated Annealing.
  - Visualización paso a paso del proceso de resolución.
  - Tabla comparativa de métricas entre algoritmos y niveles.
  - Celdas fijas en color diferente a las resueltas por el algoritmo.
"""
 
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
 
from src.algorithms.annealing import solve_sudoku_annealing, solve_sudoku_astar
from src.utils.metrics import (
    SUDOKU_LEVELS, SUDOKU_EASY, SUDOKU_MEDIUM, SUDOKU_HARD,
    run_sudoku_benchmark, format_table
)
 
# ── Paleta ───────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#313244"
FIXED_BG  = "#45475a"
FIXED_FG  = "#cdd6f4"
SOLVED_BG = "#1e4a2e"
SOLVED_FG = "#a6e3a1"
EMPTY_BG  = "#2a2a3e"
EMPTY_FG  = "#6c7086"
GRID_LINE = "#585b70"
BLOCK_LINE= "#89b4fa"
ACCENT    = "#a6e3a1"
TEXT_PRI  = "#cdd6f4"
TEXT_SEC  = "#6c7086"
BTN_CLR   = "#585b70"
BTN_HOVER = "#7f849c"
CONFLICT  = "#f38ba8"
 
CELL_SIZE = 56
GRID_OFF  = 20
 
 
class SudokuGUI(tk.Frame):
    """Frame principal del Sudoku."""
 
    def __init__(self, master: tk.Widget):
        super().__init__(master, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
 
        self.level_var = tk.StringVar(value="Fácil (20 vacías)")
        self.algo_var  = tk.StringVar(value="Simulated Annealing")
 
        self._puzzle:   List[List[int]] = [row[:] for row in SUDOKU_EASY]
        self._fixed:    List[List[bool]] = [[v != 0 for v in row] for row in SUDOKU_EASY]
        self._display:  List[List[int]] = [row[:] for row in SUDOKU_EASY]
        self._animating = False
 
        self._build_ui()
        self._draw_grid()
 
    # ── Construcción de la UI ────────────────────────────────────────────────
 
    def _build_ui(self):
        total_size = CELL_SIZE * 9 + GRID_OFF * 2
 
        # Panel izquierdo: tablero
        left = tk.Frame(self, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=16, pady=16)
 
        # Controles
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill=tk.X, pady=(0, 8))
 
        tk.Label(ctrl, text="Nivel:", bg=BG, fg=TEXT_PRI, font=("Courier", 11)).pack(side=tk.LEFT)
        level_cb = ttk.Combobox(
            ctrl, textvariable=self.level_var,
            values=list(SUDOKU_LEVELS.keys()), state="readonly", width=22
        )
        level_cb.pack(side=tk.LEFT, padx=6)
        level_cb.bind("<<ComboboxSelected>>", lambda e: self._load_level())
 
        tk.Label(ctrl, text="  Algoritmo:", bg=BG, fg=TEXT_PRI, font=("Courier", 11)).pack(side=tk.LEFT)
        algo_cb = ttk.Combobox(
            ctrl, textvariable=self.algo_var,
            values=["Simulated Annealing", "A*"], state="readonly", width=20
        )
        algo_cb.pack(side=tk.LEFT, padx=6)
 
        # Canvas del Sudoku
        self.canvas = tk.Canvas(
            left, width=total_size, height=total_size,
            bg=SURFACE, highlightthickness=0
        )
        self.canvas.pack()
 
        # Botones
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill=tk.X, pady=8)
        for txt, cmd in [
            ("▶ Resolver",  self._solve),
            ("⏩ Auto",      self._auto_play),
            ("↺ Reiniciar", self._reset),
            ("📊 Benchmark", self._benchmark),
        ]:
            tk.Button(
                btn_row, text=txt, command=cmd,
                bg=BTN_CLR, fg=TEXT_PRI, activebackground=BTN_HOVER,
                relief=tk.FLAT, font=("Courier", 10), padx=10, pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=4)
 
        # Panel derecho
        right = tk.Frame(self, bg=BG, width=420)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)
        right.pack_propagate(False)
 
        tk.Label(right, text="Estado", bg=BG, fg=ACCENT,
                 font=("Courier", 13, "bold")).pack(anchor=tk.W)
        self.lbl_status = tk.Label(
            right, text="Selecciona un nivel y pulsa ▶ Resolver.",
            bg=BG, fg=TEXT_PRI, font=("Courier", 11),
            wraplength=400, justify=tk.LEFT
        )
        self.lbl_status.pack(anchor=tk.W, pady=(0, 12))
 
        tk.Label(right, text="Métricas comparativas", bg=BG, fg=ACCENT,
                 font=("Courier", 13, "bold")).pack(anchor=tk.W)
        self.txt_metrics = tk.Text(
            right, bg=SURFACE, fg=TEXT_PRI,
            font=("Courier", 8), relief=tk.FLAT,
            state=tk.DISABLED, wrap=tk.NONE
        )
        self.txt_metrics.pack(fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(right, orient=tk.HORIZONTAL, command=self.txt_metrics.xview)
        sb.pack(fill=tk.X)
        self.txt_metrics.configure(xscrollcommand=sb.set)
 
    # ── Dibujo del tablero ───────────────────────────────────────────────────
 
    def _draw_grid(self, grid: List[List[int]] = None):
        if grid is None:
            grid = self._display
        self.canvas.delete("all")
        off = GRID_OFF
        cs  = CELL_SIZE
 
        for r in range(9):
            for c in range(9):
                x0 = off + c * cs
                y0 = off + r * cs
                x1 = x0 + cs
                y1 = y0 + cs
                val = grid[r][c]
 
                if self._fixed[r][c]:
                    bg_c, fg_c = FIXED_BG, FIXED_FG
                    font_w = "bold"
                elif val != 0:
                    bg_c, fg_c = SOLVED_BG, SOLVED_FG
                    font_w = "normal"
                else:
                    bg_c, fg_c = EMPTY_BG, EMPTY_FG
                    font_w = "normal"
 
                self.canvas.create_rectangle(x0+1, y0+1, x1-1, y1-1,
                                              fill=bg_c, outline="")
                if val != 0:
                    self.canvas.create_text(
                        x0 + cs//2, y0 + cs//2,
                        text=str(val), fill=fg_c,
                        font=("Courier", 20, font_w)
                    )
 
        # Líneas de celda
        total = cs * 9 + off * 2
        for i in range(10):
            x = off + i * cs
            y = off + i * cs
            lw = 2 if i % 3 == 0 else 0.5
            lc = BLOCK_LINE if i % 3 == 0 else GRID_LINE
            self.canvas.create_line(x, off, x, total - off, fill=lc, width=lw)
            self.canvas.create_line(off, y, total - off, y, fill=lc, width=lw)
 
    # ── Lógica de control ────────────────────────────────────────────────────
 
    def _load_level(self):
        self._animating = False
        level = self.level_var.get()
        puzzles = {
            "Fácil (20 vacías)":      SUDOKU_EASY,
            "Intermedio (35 vacías)": SUDOKU_MEDIUM,
            "Difícil (45 vacías)":    SUDOKU_HARD,
        }
        p = puzzles[level]
        self._puzzle  = [row[:] for row in p]
        self._fixed   = [[v != 0 for v in row] for row in p]
        self._display = [row[:] for row in p]
        self._draw_grid()
        self._set_status(f"Nivel: {level}. Pulsa ▶ Resolver.")
 
    def _solve(self):
        if self._animating:
            return
        algo = self.algo_var.get()
        if algo == "A*" and "Difícil" in self.level_var.get():
            messagebox.showwarning(
                "Advertencia",
                "A* no es viable para el nivel difícil (45 celdas vacías).\n"
                "Usa Simulated Annealing."
            )
            return
 
        self._set_status("⏳ Resolviendo…")
        self.update_idletasks()
        puzzle = [row[:] for row in self._puzzle]
 
        def worker():
            if algo == "Simulated Annealing":
                res = solve_sudoku_annealing(
                    puzzle,
                    step_callback=lambda g, it, T, c: self.after(
                        0, lambda g=g: self._update_display(g)
                    )
                )
                sol  = res["solution"]
                info = (
                    f"{'✓' if res['found'] else '~'} SA  |  "
                    f"Conflictos: {res['conflicts']}  |  "
                    f"Iter: {res['iterations']}  |  "
                    f"Reinicios: {res['restarts']}\n"
                    f"Tiempo: {res['time_s']} s  |  Memoria: {res['memory_kb']} KB"
                )
            else:
                res = solve_sudoku_astar(
                    puzzle,
                    step_callback=lambda g, n: self.after(
                        0, lambda g=g: self._update_display(g)
                    )
                )
                sol  = res["solution"]
                info = (
                    f"{'✓' if res['found'] else '✗'} A*  |  "
                    f"Nodos: {res['nodes_expanded']}\n"
                    f"Tiempo: {res['time_s']} s  |  Memoria: {res['memory_kb']} KB"
                )
            self.after(0, lambda: self._on_solved(sol, info))
 
        threading.Thread(target=worker, daemon=True).start()
 
    def _on_solved(self, grid, info: str):
        self._display = [row[:] for row in grid]
        self._draw_grid()
        self._set_status(info)
 
    def _update_display(self, grid):
        self._display = [row[:] for row in grid]
        self._draw_grid()
 
    def _auto_play(self):
        messagebox.showinfo(
            "Auto-play",
            "La visualización paso a paso se muestra automáticamente\n"
            "durante la resolución (cada 500 iteraciones en SA)."
        )
 
    def _reset(self):
        self._animating = False
        self._display = [row[:] for row in self._puzzle]
        self._draw_grid()
        self._set_status("Reiniciado.")
 
    def _benchmark(self):
        self._set_status("⏳ Ejecutando benchmark completo…")
        self.update_idletasks()
 
        def worker():
            rows = run_sudoku_benchmark()
            table = format_table(rows)
            self.after(0, lambda: self._show_metrics(table))
 
        threading.Thread(target=worker, daemon=True).start()
 
    def _set_status(self, msg: str):
        self.lbl_status.config(text=msg)
 
    def _show_metrics(self, table: str):
        self.txt_metrics.config(state=tk.NORMAL)
        self.txt_metrics.delete("1.0", tk.END)
        self.txt_metrics.insert(tk.END, table)
        self.txt_metrics.config(state=tk.DISABLED)
        self._set_status("Benchmark completado.")
 