"""
Tests para el algoritmo A* aplicado al 8-puzzle y 15-puzzle.
 
Cubre:
  - Verificación de solubilidad.
  - Resolución con las 3 heurísticas en estados fáciles y difíciles.
  - Comprobación de que la solución es válida (conectividad de estados).
  - Métricas de rendimiento (que A* con Conflicto Lineal sea >= Manhattan en nodos).
"""
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
 
import pytest
from src.algorithms.a_star import solve_puzzle, is_solvable, get_neighbors
from src.algorithms.heuristics import misplaced_tiles, manhattan_distance, linear_conflict
 
GOAL_8  = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_15 = tuple(range(1, 16)) + (0,)
 
# ── Estados de prueba ────────────────────────────────────────────────────────
 
EASY   = (1, 2, 3, 4, 5, 6, 7, 0, 8)   # 1 movimiento
MEDIUM = (1, 2, 3, 4, 0, 6, 7, 5, 8)   # ~4 movimientos
HARD   = (8, 6, 7, 2, 5, 4, 3, 0, 1)   # ~26 movimientos
ALREADY_SOLVED = GOAL_8
 
# ── is_solvable ──────────────────────────────────────────────────────────────
 
def test_goal_is_solvable():
    assert is_solvable(GOAL_8, 3)
 
def test_easy_is_solvable():
    assert is_solvable(EASY, 3)
 
def test_unsolvable_detected():
    # Intercambiar dos fichas (no el cero) crea un puzzle no resoluble
    unsolvable = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    assert not is_solvable(unsolvable, 3)
 
# ── get_neighbors ────────────────────────────────────────────────────────────
 
def test_neighbors_center():
    # 0 en el centro tiene 4 vecinos
    state = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    nbrs = get_neighbors(state, 3)
    assert len(nbrs) == 4
 
def test_neighbors_corner():
    # 0 en una esquina tiene 2 vecinos
    state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    nbrs = get_neighbors(state, 3)
    assert len(nbrs) == 2
 
def test_neighbors_edge():
    # 0 en un borde lateral tiene 3 vecinos
    state = (1, 0, 2, 3, 4, 5, 6, 7, 8)
    nbrs = get_neighbors(state, 3)
    assert len(nbrs) == 3
 
# ── Heurísticas ──────────────────────────────────────────────────────────────
 
def test_misplaced_zero_at_goal():
    assert misplaced_tiles(GOAL_8, GOAL_8) == 0
 
def test_manhattan_zero_at_goal():
    assert manhattan_distance(GOAL_8, GOAL_8, 3) == 0
 
def test_linear_conflict_zero_at_goal():
    assert linear_conflict(GOAL_8, GOAL_8, 3) == 0
 
def test_heuristics_admissible_easy():
    """Las heurísticas no deben sobreestimar el costo real (1 movimiento)."""
    assert misplaced_tiles(EASY, GOAL_8) <= 2
    assert manhattan_distance(EASY, GOAL_8, 3) <= 2
    assert linear_conflict(EASY, GOAL_8, 3) <= 2
 
def test_linear_conflict_geq_manhattan():
    """Conflicto Lineal debe ser >= Manhattan (más informativa)."""
    for state in [EASY, MEDIUM, HARD]:
        lc = linear_conflict(state, GOAL_8, 3)
        md = manhattan_distance(state, GOAL_8, 3)
        assert lc >= md, f"LC={lc} < MD={md} para {state}"
 
# ── solve_puzzle ─────────────────────────────────────────────────────────────
 
@pytest.mark.parametrize("heuristic", [
    "Fichas fuera de lugar",
    "Distancia Manhattan",
    "Conflicto Lineal",
])
def test_solve_easy(heuristic):
    res = solve_puzzle(EASY, GOAL_8, 3, heuristic)
    assert res["found"]
    assert res["moves"] == 1
    assert res["nodes_expanded"] >= 1
 
@pytest.mark.parametrize("heuristic", [
    "Fichas fuera de lugar",
    "Distancia Manhattan",
    "Conflicto Lineal",
])
def test_solve_already_solved(heuristic):
    res = solve_puzzle(ALREADY_SOLVED, GOAL_8, 3, heuristic)
    assert res["found"]
    assert res["moves"] == 0
 
@pytest.mark.parametrize("heuristic", [
    "Fichas fuera de lugar",
    "Distancia Manhattan",
    "Conflicto Lineal",
])
def test_solve_medium(heuristic):
    res = solve_puzzle(MEDIUM, GOAL_8, 3, heuristic)
    assert res["found"]
    assert res["moves"] >= 1
 
def test_solution_path_valid():
    """Cada estado de la solución debe ser vecino del anterior."""
    res = solve_puzzle(MEDIUM, GOAL_8, 3, "Distancia Manhattan")
    assert res["found"]
    path = res["solution"]
    for i in range(1, len(path)):
        neighbors = [s for s, _ in get_neighbors(path[i-1], 3)]
        assert path[i] in neighbors, f"Paso {i} inválido en la solución"
 
def test_solve_returns_metrics():
    res = solve_puzzle(EASY, GOAL_8, 3, "Distancia Manhattan")
    assert "time_s" in res and res["time_s"] >= 0
    assert "memory_kb" in res and res["memory_kb"] >= 0
    assert "nodes_expanded" in res and res["nodes_expanded"] >= 1
 
def test_linear_conflict_expands_fewer_nodes():
    """Con Conflicto Lineal se deben expandir <= nodos que con Fichas fuera de lugar."""
    r_lc  = solve_puzzle(HARD, GOAL_8, 3, "Conflicto Lineal")
    r_mis = solve_puzzle(HARD, GOAL_8, 3, "Fichas fuera de lugar")
    assert r_lc["nodes_expanded"] <= r_mis["nodes_expanded"]
 
# ── 15-puzzle básico ─────────────────────────────────────────────────────────
 
def test_solve_15_easy():
    start = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    res = solve_puzzle(start, GOAL_15, 4, "Distancia Manhattan")
    assert res["found"]
    assert res["moves"] == 1
 