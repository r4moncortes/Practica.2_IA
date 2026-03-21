"""
Punto de entrada de la Práctica 2.
 
Lanza una ventana Tkinter con dos pestañas:
  - Puzzle  : 8-puzzle y 15-puzzle con A* y 3 heurísticas.
  - Sudoku  : Sudoku en 3 niveles con A* y Simulated Annealing.
 
Uso:
    python main.py
"""
 
import tkinter as tk
from tkinter import ttk
import sys
import os
 
# Asegurar que src/ esté en el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
 
from src.gui.puzzle_gui import PuzzleGUI
from src.gui.sudoku_gui import SudokuGUI
 
# ── Paleta global ─────────────────────────────────────────────────────────────
BG     = "#1e1e2e"
ACCENT = "#89b4fa"
FG     = "#cdd6f4"
 
 
def apply_dark_theme(root: tk.Tk):
    """Aplica tema oscuro a los widgets ttk."""
    style = ttk.Style(root)
    style.theme_use("clam")
 
    style.configure(".",
        background=BG, foreground=FG,
        fieldbackground="#313244",
        troughcolor="#313244",
        selectbackground="#585b70",
        selectforeground=FG,
        font=("Courier", 10)
    )
    style.configure("TNotebook",       background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",   background="#313244", foreground=FG,
                    padding=[14, 6], font=("Courier", 11))
    style.map("TNotebook.Tab",
        background=[("selected", "#585b70")],
        foreground=[("selected", "#a6e3a1")]
    )
    style.configure("TCombobox",
        fieldbackground="#313244", background="#313244",
        foreground=FG, arrowcolor=FG, borderwidth=0
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", "#313244")],
        background=[("readonly", "#313244")]
    )
    style.configure("Horizontal.TScrollbar",
        background="#585b70", troughcolor="#313244",
        arrowcolor=FG, borderwidth=0
    )
 
 
def main():
    root = tk.Tk()
    root.title("Inteligencia Artificial — Búsqueda Informada | Práctica 2")
    root.geometry("1280x760")
    root.minsize(960, 600)
    root.configure(bg=BG)
 
    apply_dark_theme(root)
 
    # ── Encabezado ──────────────────────────────────────────────────────────
    header = tk.Frame(root, bg=BG, pady=8)
    header.pack(fill=tk.X, padx=20)
 
    tk.Label(
        header,
        text="Búsqueda Informada",
        bg=BG, fg=ACCENT,
        font=("Courier", 18, "bold")
    ).pack(side=tk.LEFT)
 
    tk.Label(
        header,
        text="  A* · Recocido Simulado · 8-Puzzle · 15-Puzzle · Sudoku",
        bg=BG, fg="#6c7086",
        font=("Courier", 11)
    ).pack(side=tk.LEFT, pady=(6, 0))
 
    # ── Pestañas ────────────────────────────────────────────────────────────
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
 
    tab_puzzle = tk.Frame(notebook, bg=BG)
    tab_sudoku = tk.Frame(notebook, bg=BG)
 
    notebook.add(tab_puzzle, text="  🧩  Puzzle (8 / 15)  ")
    notebook.add(tab_sudoku, text="  🔢  Sudoku  ")
 
    PuzzleGUI(tab_puzzle)
    SudokuGUI(tab_sudoku)
 
    # ── Pie de página ───────────────────────────────────────────────────────
    footer = tk.Frame(root, bg="#181825", pady=4)
    footer.pack(fill=tk.X, side=tk.BOTTOM)
    tk.Label(
        footer,
        text="IA  ·  A*  ·  Búsqueda informada  ·  Simulated Annealing",
        bg="#181825", fg="#45475a",
        font=("Courier", 9)
    ).pack()
 
    root.mainloop()
 
 
if __name__ == "__main__":
    main()
 