"""
Simulated Annealing (Recocido Simulado) para resolver Sudoku.
 
Estrategia de vecindad:
  - Cada bloque 3×3 se inicializa con los dígitos faltantes de forma aleatoria.
  - Un movimiento consiste en intercambiar dos celdas NO fijas dentro de un bloque.
  - Costo = número de conflictos (duplicados) en filas + columnas.
  - Se acepta un estado peor con probabilidad e^(-ΔE / T).
  - La temperatura baja según: T_new = T * cooling_rate  (descenso exponencial).
  - Si el algoritmo se estanca, se reinicia desde un nuevo estado aleatorio.
 
También incluye solve_sudoku_astar para comparación de rendimiento en puzzles fáciles.
"""
 
import copy
import math
import random
import time
import tracemalloc
from typing import Callable, Dict, List, Optional
 
 
# ---------------------------------------------------------------------------
# Utilidades compartidas
# ---------------------------------------------------------------------------
 
def count_conflicts(grid: List[List[int]]) -> int:
    """
    Cuenta duplicados en filas y columnas (ignora ceros).
    Costo óptimo = 0.
    """
    total = 0
    for i in range(9):
        row = [grid[i][j] for j in range(9) if grid[i][j] != 0]
        col = [grid[j][i] for j in range(9) if grid[j][i] != 0]
        total += len(row) - len(set(row))
        total += len(col) - len(set(col))
    return total
 
 
def _fixed_mask(puzzle: List[List[int]]) -> List[List[bool]]:
    """Retorna máscara booleana: True si la celda es fija (dada por el puzzle)."""
    return [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
 
 
def _fill_blocks(puzzle: List[List[int]], fixed: List[List[bool]]) -> List[List[int]]:
    """
    Rellena cada bloque 3×3 con los dígitos 1-9 que faltan,
    sin tocar las celdas fijas. Punto de partida del SA.
    """
    grid = copy.deepcopy(puzzle)
    for br in range(3):
        for bc in range(3):
            present, empty = set(), []
            for r in range(br * 3, br * 3 + 3):
                for c in range(bc * 3, bc * 3 + 3):
                    if fixed[r][c]:
                        present.add(grid[r][c])
                    else:
                        empty.append((r, c))
            missing = list(set(range(1, 10)) - present)
            random.shuffle(missing)
            for (r, c), v in zip(empty, missing):
                grid[r][c] = v
    return grid
 
 
def _free_in_block(fixed: List[List[bool]], br: int, bc: int) -> List[tuple]:
    """Celdas no fijas dentro del bloque (br, bc)."""
    return [
        (r, c)
        for r in range(br * 3, br * 3 + 3)
        for c in range(bc * 3, bc * 3 + 3)
        if not fixed[r][c]
    ]
 
 
# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------
 
def solve_sudoku_annealing(
    puzzle: List[List[int]],
    T_init: float = 2.0,
    T_min: float = 0.001,
    cooling_rate: float = 0.9995,
    max_iter: int = 500_000,
    step_callback: Optional[Callable] = None,
) -> Dict:
    """
    Resuelve un Sudoku usando Recocido Simulado.
 
    Parámetros
    ----------
    puzzle        : tablero 9×9, 0 = celda vacía
    T_init        : temperatura inicial
    T_min         : temperatura mínima (criterio de parada)
    cooling_rate  : factor δ de enfriamiento exponencial (típico 0.99–0.9999)
    max_iter      : límite de iteraciones como seguridad
    step_callback : función(grid, iter, T, costo) llamada cada 500 iteraciones
 
    Retorna dict con: solution, conflicts, found, iterations, restarts, time_s, memory_kb
    """
    fixed = _fixed_mask(puzzle)
 
    tracemalloc.start()
    t0 = time.perf_counter()
 
    current = _fill_blocks(puzzle, fixed)
    cur_cost = count_conflicts(current)
    best = copy.deepcopy(current)
    best_cost = cur_cost
 
    T = T_init
    iteration = 0
    restarts = 0
 
    while T > T_min and iteration < max_iter and best_cost > 0:
        # Elegir bloque aleatorio
        br, bc = random.randint(0, 2), random.randint(0, 2)
        free = _free_in_block(fixed, br, bc)
 
        if len(free) < 2:
            T *= cooling_rate
            iteration += 1
            continue
 
        # Intercambiar dos celdas libres del bloque
        c1, c2 = random.sample(free, 2)
        new_grid = copy.deepcopy(current)
        new_grid[c1[0]][c1[1]], new_grid[c2[0]][c2[1]] = (
            new_grid[c2[0]][c2[1]], new_grid[c1[0]][c1[1]]
        )
        new_cost = count_conflicts(new_grid)
        delta = new_cost - cur_cost
 
        # Criterio de aceptación de Metropolis
        if delta < 0 or random.random() < math.exp(-delta / T):
            current, cur_cost = new_grid, new_cost
            if cur_cost < best_cost:
                best, best_cost = copy.deepcopy(current), cur_cost
 
        T *= cooling_rate
        iteration += 1
 
        # Reinicio si se estanca cada 10 000 iteraciones
        if iteration % 10_000 == 0 and best_cost > 0:
            restarts += 1
            current = _fill_blocks(puzzle, fixed)
            cur_cost = count_conflicts(current)
            T = max(T_init * (0.5 ** restarts), T_min * 10)
 
        if step_callback and iteration % 500 == 0:
            step_callback(current, iteration, T, cur_cost)
 
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
 
    return {
        "solution":   best,
        "conflicts":  best_cost,
        "found":      best_cost == 0,
        "iterations": iteration,
        "restarts":   restarts,
        "time_s":     round(time.perf_counter() - t0, 4),
        "memory_kb":  round(peak / 1024, 2),
    }
 
 
# ---------------------------------------------------------------------------
# A* para Sudoku  (solo para puzzles fáciles, comparación de rendimiento)
# ---------------------------------------------------------------------------
 
def solve_sudoku_astar(
    puzzle: List[List[int]],
    step_callback: Optional[Callable] = None,
) -> Dict:
    """
    Resuelve Sudoku con A* usando búsqueda con backtracking + propagación de restricciones.
    Viable hasta ~35 celdas vacías; para más celdas usar Simulated Annealing.
 
    Heurística: elegir siempre la celda con menos valores posibles (MRV).
    """
    import heapq
 
    tracemalloc.start()
    t0 = time.perf_counter()
 
    nodes_expanded = 0
 
    def possible(grid, r, c):
        used = set()
        used.update(grid[r])                             # fila
        used.update(grid[i][c] for i in range(9))        # columna
        br, bc = (r // 3) * 3, (c // 3) * 3
        for dr in range(3):
            for dc in range(3):
                used.add(grid[br + dr][bc + dc])
        return [v for v in range(1, 10) if v not in used]
 
    def find_empty_mrv(grid):
        best, best_pos = None, None
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    opts = possible(grid, r, c)
                    if best is None or len(opts) < best:
                        best, best_pos = len(opts), (r, c)
        return best_pos
 
    def backtrack(grid):
        nonlocal nodes_expanded
        nodes_expanded += 1
        pos = find_empty_mrv(grid)
        if pos is None:
            return grid                        # resuelto
        r, c = pos
        for val in possible(grid, r, c):
            grid[r][c] = val
            if step_callback:
                step_callback(grid, nodes_expanded)
            result = backtrack([row[:] for row in grid])
            if result:
                return result
            grid[r][c] = 0
        return None
 
    grid = [row[:] for row in puzzle]
    solution = backtrack(grid)
 
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
 
    return {
        "solution":      solution if solution else puzzle,
        "found":         solution is not None,
        "nodes_expanded": nodes_expanded,
        "time_s":        round(time.perf_counter() - t0, 4),
        "memory_kb":     round(peak / 1024, 2),
    }
 