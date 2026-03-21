"""
Algoritmo A* para resolver el N-Puzzle (8-puzzle y 15-puzzle).
 
Flujo:
  1. Se inicia con el estado inicial en la cola de prioridad (OPEN).
  2. En cada iteración se extrae el nodo con menor f(n) = g(n) + h(n).
  3. Se generan vecinos moviendo el espacio vacío (arriba/abajo/izq/der).
  4. Si un vecino tiene mejor g que el registrado, se actualiza y re-encola.
  5. El proceso termina al alcanzar el estado objetivo o agotar la cola.
"""
 
import heapq
import time
import tracemalloc
from typing import Callable, Dict, List, Optional, Tuple
 
from .heuristics import misplaced_tiles, manhattan_distance, linear_conflict
 
 
def get_neighbors(state: tuple, size: int) -> List[Tuple[tuple, str]]:
    """Genera estados vecinos desplazando el espacio vacío en las 4 direcciones."""
    neighbors = []
    idx = state.index(0)
    row, col = divmod(idx, size)
    for dr, dc, label in [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size:
            ns = list(state)
            ns[idx], ns[nr * size + nc] = ns[nr * size + nc], ns[idx]
            neighbors.append((tuple(ns), label))
    return neighbors
 
 
def is_solvable(state: tuple, size: int) -> bool:
    """
    Verifica si el puzzle tiene solución contando inversiones.
    - Tablero impar (3x3): resoluble si inversiones es par.
    - Tablero par  (4x4): resoluble si (inversiones + fila_vacío_desde_abajo) es impar.
    """
    flat = [x for x in state if x != 0]
    inversions = sum(
        1 for i in range(len(flat))
        for j in range(i + 1, len(flat))
        if flat[i] > flat[j]
    )
    if size % 2 == 1:
        return inversions % 2 == 0
    else:
        blank_row_from_bottom = size - state.index(0) // size
        return (inversions + blank_row_from_bottom) % 2 == 1
 
 
def reconstruct_path(came_from: dict, current: tuple) -> List[tuple]:
    """Reconstruye la secuencia de estados desde inicio hasta el objetivo."""
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
 
 
def solve_puzzle(
    start: tuple,
    goal: tuple,
    size: int,
    heuristic_name: str = "Distancia Manhattan",
    step_callback: Optional[Callable] = None,
) -> Dict:
    """
    Resuelve el N-Puzzle con A* y devuelve métricas de rendimiento.
 
    Parámetros
    ----------
    start          : estado inicial como tupla plana, ej. (1,2,3,4,5,6,7,8,0)
    goal           : estado objetivo
    size           : lado del tablero (3 para 8-puzzle, 4 para 15-puzzle)
    heuristic_name : nombre de la heurística a usar
    step_callback  : función(estado, nodos_expandidos) para animación
 
    Retorna dict con: solution, moves, nodes_expanded, time_s, memory_kb, found
    """
    def h(state: tuple) -> int:
        if heuristic_name == "Fichas fuera de lugar":
            return misplaced_tiles(state, goal, size)
        elif heuristic_name == "Distancia Manhattan":
            return manhattan_distance(state, goal, size)
        else:
            return linear_conflict(state, goal, size)
 
    tracemalloc.start()
    t0 = time.perf_counter()
 
    open_heap: List[Tuple[int, int, tuple]] = []
    heapq.heappush(open_heap, (h(start), 0, start))
    came_from: Dict[tuple, tuple] = {}
    g_score: Dict[tuple, int] = {start: 0}
    nodes_expanded = 0
 
    result = dict(solution=[], moves=0, nodes_expanded=0,
                  time_s=0.0, memory_kb=0.0, found=False)
 
    while open_heap:
        f, g, current = heapq.heappop(open_heap)
        nodes_expanded += 1
 
        if step_callback:
            step_callback(current, nodes_expanded)
 
        if current == goal:
            path = reconstruct_path(came_from, current)
            path.append(goal)
            result.update(solution=path, moves=len(path) - 1, found=True)
            break
 
        if g > g_score.get(current, float("inf")):
            continue
 
        for neighbor, _ in get_neighbors(current, size):
            tg = g + 1
            if tg < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tg
                heapq.heappush(open_heap, (tg + h(neighbor), tg, neighbor))
 
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
 
    result["nodes_expanded"] = nodes_expanded
    result["time_s"]    = round(time.perf_counter() - t0, 4)
    result["memory_kb"] = round(peak / 1024, 2)
    return result
 