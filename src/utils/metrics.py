"""
Utilidades para medir y mostrar rendimiento de los algoritmos.
 
Funciones principales:
  - run_puzzle_benchmark : ejecuta A* con las 3 heurísticas y devuelve tabla comparativa.
  - run_sudoku_benchmark : ejecuta A* y SA en los 3 niveles de Sudoku.
  - format_table         : imprime tabla ASCII en consola.
"""
 
import random
import time
from typing import Dict, List, Tuple
 
from src.algorithms.a_star import solve_puzzle, is_solvable
from src.algorithms.annealing import solve_sudoku_annealing, solve_sudoku_astar
from src.algorithms.heuristics import HEURISTICS
 
# ---------------------------------------------------------------------------
# Puzzles de ejemplo
# ---------------------------------------------------------------------------
 
GOAL_8  = tuple(range(1, 9)) + (0,)          # (1,2,3,4,5,6,7,8,0)
GOAL_15 = tuple(range(1, 16)) + (0,)          # (1,2,...,15,0)
 
# Configuraciones con dificultad conocida
EASY_8   = (1, 2, 3, 4, 5, 6, 7, 0, 8)
MEDIUM_8 = (1, 2, 3, 4, 0, 6, 7, 5, 8)
HARD_8   = (8, 6, 7, 2, 5, 4, 3, 0, 1)
 
EASY_15   = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
MEDIUM_15 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 14, 15)
HARD_15   = (5, 1, 3, 4, 9, 2, 7, 8, 13, 6, 10, 12, 0, 14, 11, 15)
 
 
def random_puzzle(size: int, moves: int = 30) -> tuple:
    """Genera un puzzle aleatorio resoluble haciendo `moves` movimientos desde el goal."""
    goal = tuple(range(1, size * size)) + (0,)
    state = list(goal)
    for _ in range(moves):
        idx = state.index(0)
        row, col = divmod(idx, size)
        candidates = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < size and 0 <= nc < size:
                candidates.append(nr * size + nc)
        swap = random.choice(candidates)
        state[idx], state[swap] = state[swap], state[idx]
    return tuple(state)
 
 
# ---------------------------------------------------------------------------
# Benchmark puzzle
# ---------------------------------------------------------------------------
 
def run_puzzle_benchmark(
    puzzle_size: int = 3,
    start: tuple = None,
) -> List[Dict]:
    """
    Ejecuta A* con las 3 heurísticas sobre un estado dado (o uno aleatorio).
    Devuelve lista de dicts con métricas por heurística.
    """
    size = puzzle_size
    goal = tuple(range(1, size * size)) + (0,)
    if start is None:
        start = random_puzzle(size, moves=20 if size == 3 else 15)
 
    rows = []
    for name in HEURISTICS:
        res = solve_puzzle(start, goal, size, heuristic_name=name)
        rows.append({
            "Heurística":        name,
            "Movimientos":       res["moves"] if res["found"] else "—",
            "Nodos expandidos":  res["nodes_expanded"],
            "Tiempo (s)":        res["time_s"],
            "Memoria (KB)":      res["memory_kb"],
            "Solución":          "✓" if res["found"] else "✗",
        })
    return rows
 
 
# ---------------------------------------------------------------------------
# Sudoku de ejemplo (los 3 niveles)
# ---------------------------------------------------------------------------
 
SUDOKU_EASY = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]  # 20 celdas vacías
 
SUDOKU_MEDIUM = [
    [0, 0, 0, 2, 6, 0, 7, 0, 1],
    [6, 8, 0, 0, 7, 0, 0, 9, 0],
    [1, 9, 0, 0, 0, 4, 5, 0, 0],
    [8, 2, 0, 1, 0, 0, 0, 4, 0],
    [0, 0, 4, 6, 0, 2, 9, 0, 0],
    [0, 5, 0, 0, 0, 3, 0, 2, 8],
    [0, 0, 9, 3, 0, 0, 0, 7, 4],
    [0, 4, 0, 0, 5, 0, 0, 3, 6],
    [7, 0, 3, 0, 1, 8, 0, 0, 0],
]  # 35 celdas vacías
 
SUDOKU_HARD = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 8, 5],
    [0, 0, 1, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 5, 0, 7, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 1, 0, 0],
    [0, 9, 0, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 7, 3],
    [0, 0, 2, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 9],
]  # 45 celdas vacías
 
SUDOKU_LEVELS = {
    "Fácil (20 vacías)":      SUDOKU_EASY,
    "Intermedio (35 vacías)": SUDOKU_MEDIUM,
    "Difícil (45 vacías)":    SUDOKU_HARD,
}
 
 
def run_sudoku_benchmark() -> List[Dict]:
    """
    Ejecuta A* y Simulated Annealing en los 3 niveles de Sudoku.
    Devuelve lista de dicts con métricas.
    """
    rows = []
    for level, puzzle in SUDOKU_LEVELS.items():
        # Simulated Annealing
        sa = solve_sudoku_annealing(puzzle)
        rows.append({
            "Nivel":       level,
            "Algoritmo":   "Simulated Annealing",
            "Conflictos":  sa["conflicts"],
            "Iteraciones": sa["iterations"],
            "Reinicios":   sa["restarts"],
            "Tiempo (s)":  sa["time_s"],
            "Memoria (KB)": sa["memory_kb"],
            "Solución":    "✓" if sa["found"] else "✗",
        })
        # A* (solo fácil e intermedio para evitar timeout)
        if "Difícil" not in level:
            astar = solve_sudoku_astar(puzzle)
            rows.append({
                "Nivel":       level,
                "Algoritmo":   "A*",
                "Conflictos":  0 if astar["found"] else "—",
                "Iteraciones": astar["nodes_expanded"],
                "Reinicios":   "—",
                "Tiempo (s)":  astar["time_s"],
                "Memoria (KB)": astar["memory_kb"],
                "Solución":    "✓" if astar["found"] else "✗",
            })
        else:
            rows.append({
                "Nivel":       level,
                "Algoritmo":   "A*",
                "Conflictos":  "N/A",
                "Iteraciones": "N/A",
                "Reinicios":   "N/A",
                "Tiempo (s)":  "N/A",
                "Memoria (KB)": "N/A",
                "Solución":    "N/A (muy costoso)",
            })
    return rows
 
 
# ---------------------------------------------------------------------------
# Formateador de tabla
# ---------------------------------------------------------------------------
 
def format_table(rows: List[Dict]) -> str:
    """Devuelve una tabla ASCII a partir de una lista de dicts."""
    if not rows:
        return ""
    headers = list(rows[0].keys())
    col_w = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    sep = "+" + "+".join("-" * (col_w[h] + 2) for h in headers) + "+"
    header_row = "|" + "|".join(f" {h:<{col_w[h]}} " for h in headers) + "|"
    lines = [sep, header_row, sep]
    for row in rows:
        lines.append("|" + "|".join(f" {str(row[h]):<{col_w[h]}} " for h in headers) + "|")
    lines.append(sep)
    return "\n".join(lines)
 